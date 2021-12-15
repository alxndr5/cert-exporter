import os
import time
import socket
import threading
from certificate import Certificate
from enum import Enum

class Mode(Enum):
    local = 1
    remote = 2
    kubernetes = 3

class Metrics(threading.Thread):
    def __init__(self, config):
        threading.Thread.__init__(self)
        self._config = config
        self._data = []
        self._lock = threading.Lock()
        self._sleep = self._config['update_period'] if 'update_period' in self._config else 60

    def fetch(self):
        pass

    def run(self):
        while (True):
            self._lock.acquire()
            self.fetch()
            self._lock.release()
            time.sleep(self._sleep)
            
    def get(self):
        self._lock.acquire()
        res = []
        for i in self._data:
            # Prepare string with exporter-specific labels
            labels = ""
            for key, val in i['metadata'].items():
                labels += " {0}=\"{1}\"".format(key, val)
            
            # Prometheus formated line
            line = "certexporter{{cn=\"{cn}\" exp_date=\"{exp_date}\"{labels}}} {value}".format(
                cn = i['cert'].getCN(),
                exp_date = i['cert'].notValidAfter().strftime("%d.%m.%Y"),
                labels = labels,
                value = i['cert'].getExpired()
                )
            
            res.append(line)
        self._lock.release()
        return res

    def add(self, cert, metadata):
        item = {
            "cert": cert,
            "metadata": metadata
        }
        self._data.append(item)

class MetricsLocal(Metrics):
    def __init__(self, config):
        super().__init__(config)
        self._allowed_file_extensions = [
            'crt', 'pem'
        ]

    def fetch(self):
        self._data = []
        for dir in self._config['local']:
            for root, dirs, files in os.walk(dir):
                for file in files:
                    if file[-3:] in self._allowed_file_extensions:
                        try:
                            cert = Certificate()
                            cert.loadFile(os.path.join(root, file))
                            metadata = {
                                'type': 'node',
                                'location': "{host}:{file}".format(
                                    host=os.uname()[1], file=os.path.join(root, file)
                                )
                            }
                            self.add(cert, metadata)
                        except Exception as e:
                            print("Error parsing file '", file, "':", e)
        return

# import ssl
from urllib.parse import urlparse
from socket import *

class MetricsRemote(Metrics):
    def __init__(self, config):
        super().__init__(config)
        setdefaulttimeout(3)

    def fetch(self):
        self._data = []
        for url in self._config['remote']:
            try:
                u = urlparse(url)
                cert = Certificate()
                cert.loadRemote(url)
                metadata = {
                    'type': 'remote',
                    'location': "{host}:{port}".format(
                        host=u.hostname, port=u.port if u.port else 443
                    )
                }
                self.add(cert, metadata)
            except (error, timeout) as e:
                print("Error:", url, e)
        return

from kubernetes import client as k8s_client
from kubernetes import config as k8s_config
from base64 import b64decode

class MetricsKubernetes(Metrics):
    def __init__(self, config):
        super().__init__(config)
        
        # assume that if KUBERNETES_SERVICE_HOST env var is set,
        # then we are running inside pod
        if "KUBERNETES_SERVICE_HOST" in os.environ:
            k8s_config.load_incluster_config()
        else:
            k8s_config.load_kube_config()
        
        self.api = k8s_client.CoreV1Api()

    def fetch(self):
        self._data = []
        
        s = self.api.list_secret_for_all_namespaces(watch=False)

        for secret in s.items:
            # Ignore some types of secrets
            if secret.metadata.name.startswith('default-token'):
                continue
            if secret.metadata.name.startswith('sh.helm.release'):
                continue
            if secret.type == 'kubernetes.io/dockerconfigjson':
                continue
            if secret.type == 'kubernetes.io/service-account-token':
                continue
            if secret.data == None:
                continue

            for key, val in secret.data.items():
                if key.endswith('.crt'):
                    pem = b64decode(val)
                    cert = Certificate()
                    cert.loadBytes(pem)
                    metadata = {
                        'type': 'kube',
                        'location': "{namespace}/{name}".format(
                            name=secret.metadata.name, namespace=secret.metadata.namespace
                        )
                    }
                    self.add(cert, metadata)

        return
