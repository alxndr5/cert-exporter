
from metrics import *
from server import *

import os
import sys
import yaml
import time

def config_read():
    config_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'exporter.yaml'
    )
    with open(config_path) as file:
        return yaml.load(file, Loader=yaml.FullLoader)

if __name__ == '__main__':
    config = config_read()
    mode = Mode.local
    metricsThread = None
    
    if len(sys.argv) > 1:
        if sys.argv[1] in Mode.__members__.keys():
            mode = Mode[sys.argv[1]]

    print("Mode:", mode)

    if mode == Mode.local:
        metricsThread = MetricsLocal(config)
    if mode == Mode.remote:
        metricsThread = MetricsRemote(config)
    if mode == Mode.kubernetes:
        metricsThread = MetricsKubernetes(config)

    serverThread = Server(metricsThread)

    try:
        metricsThread.start()
        serverThread.start()
    except KeyboardInterrupt:
        pass
        
    sys.exit()
