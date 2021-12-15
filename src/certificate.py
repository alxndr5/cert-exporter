from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend

class Certificate():

    def loadBytes(self, pem):
        self.cert = x509.load_pem_x509_certificate(pem, default_backend())

    def loadString(self, pem):
        self.cert = x509.load_pem_x509_certificate(
            bytes(pem, 'utf-8'), default_backend())

    def loadFile(self, filename):
        f = open(filename, 'rb')
        pem = f.read()
        f.close()
        self.loadBytes(pem)

    def loadRemote(self, url):
        import ssl
        import OpenSSL
        from urllib.parse import urlparse

        u = urlparse(url)
        conn = ssl.create_connection((u.hostname, u.port if u.port else 443))
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        sock = context.wrap_socket(conn, server_hostname=u.hostname)
        pem = ssl.DER_cert_to_PEM_cert(sock.getpeercert(True))
        self.loadString(pem)

    def notValidAfter(self):
        return self.cert.not_valid_after

    def notValidBefore(self):
        return self.cert.not_valid_before
    
    def getCN(self):
        attrs = self.cert.subject.get_attributes_for_oid(x509.OID_COMMON_NAME)
        if len(attrs) > 0:
            return attrs[0].value.strip()
        else:
            return None
    
    def getExpired(self):
        a = (self.cert.not_valid_after - self.cert.not_valid_before).total_seconds()
        b = (datetime.now() - self.cert.not_valid_before).total_seconds()
        return round(100 / (a / b))
