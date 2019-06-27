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

    def process(self):

        uri = 'https://ethgasstation.info/gasguzzlers.php'
        file = requests.get(uri)
        text = file.text

        result = []
        searchUri = re.findall('https:\/\/etherscan.io\/address\/[a-zA-Z0-9_]*', text)
        searchLoad = re.findall('(?:<td>)([0-9]+\.[0-9]+)(?:<\/td>)', text)

        for index in range(len(searchUri)):
            data = {
                'time': int(time.time()),
                'value': {
                    'uri': searchUri[index] + '#contracts',
                    'load': searchLoad[index],
                }
            }
            result.append(data)

        return result

class CVEIdentifiers:

    def __readFile(self, url):
        file = requests.get(url)
        text = file.text
        return text

    def __restoreUris(self, fragments, baseUri, result):
        for fragment in fragments:
            url = baseUri + fragment
            result.append(url)

    def process(self):

        result = []
        
        baseUri = 'https://www.cvedetails.com'
        
        # Load year URIs
        yearUris = []
        listingUri = 'https://www.cvedetails.com/browse-by-date.php'
        fragments = re.findall('\/vulnerability-list\/year-[0-9]{4}\/vulnerabilities.html', self.__readFile(listingUri))
        self.__restoreUris(fragments, baseUri, yearUris)

        # Load CVE page URIs
        pageUris = []
        for uri in yearUris:
            fragments = re.findall('(\/vulnerability-list.php\?[0-9a-zA-Z_=&;]+)(?:\"\t title=\"Go to page [0-9\">]+)', self.__readFile(uri))
            self.__restoreUris(fragments, baseUri, pageUris)

        # Load CVE items
        for uri in pageUris:
            fragments = re.findall('(?:[\<a-z0-9 =\"/]+)([0-9A-Z-]+)/(?:\")', self.__readFile(uri))
            for identifier in fragments:
                result.append({
                    'id': identifier
                }) 

        return result
