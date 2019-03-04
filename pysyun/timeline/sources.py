import ssl
import json
import urllib.request

class GoogleObserver:

    def __init__(self, storageUri, kernelIdentifier):
        self.storageUri = storageUri
        self.kernelIdentifier = kernelIdentifier

    def process(self):
        sslContext = ssl.create_default_context();
        sslContext.check_hostname = False
        sslContext.verify_mode = ssl.CERT_NONE
        uriString = self.storageUri + '/api/event/list?kernelIdentifier=' + self.kernelIdentifier
        with urllib.request.urlopen(uriString, context = sslContext) as url:
            data = json.loads(url.read().decode())
            return data
