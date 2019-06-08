import re
import ssl
import json
import time
import requests
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

class EthereumGasStation:

    def process():

        uri = 'https://ethgasstation.info/gasguzzlers.php'
        file = requests.get(uri)
        text = file.text

        result = []
        search = re.findall('https:\/\/etherscan.io\/address\/[a-zA-Z0-9_]*', text)

        for index in search:
            data = {
                'time': int(time.time()),
                'value': {
                    'uri': index + '#contracts'
                }
            }
            result.append(data)

        return result
