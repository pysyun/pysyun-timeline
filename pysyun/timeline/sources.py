import re
import ssl
import json
import time
import requests
import urllib.request
from bs4 import BeautifulSoup as bs
from storage_timeline_client import Storage
from pysyun.timeline.algebra import Add

class StorageTimelineSchema:
    def __init__(self, uri, schemaName):
        self.schema = Storage(uri).schema(schemaName)
    def process(self, empty):
        result = []
        timeLineNames = self.schema.list()
        for timeLineName in timeLineNames:
            result.append(self.schema.timeLine(timeLineName))
        return result

class StorageTimelineTimeline:
    def __init__(self, uri, schemaName, timeLineName):
        self.timeLine = Storage(uri).schema(schemaName).timeLine(timeLineName)
    def process(self, empty):
        return [self.timeLine]

class StorageTimelineStrings:
    def process(self, timeLines):
        results = []
        cumulation = Add()
        for timeLine in timeLines:
            try:
                values = timeLine.allStrings()
                results = cumulation.process(values)
            except:
                print("Unable to fetch data from Storage.Timeline", timeLine.schema, timeLine.name)
        return results

class GoogleObserver:

    def __init__(self, storageUri, kernelIdentifier):
        self.storageUri = storageUri
        self.kernelIdentifier = kernelIdentifier

    def process(self, formalArgument):
        sslContext = ssl.create_default_context();
        sslContext.check_hostname = False
        sslContext.verify_mode = ssl.CERT_NONE
        uriString = self.storageUri + '/api/event/list?kernelIdentifier=' + self.kernelIdentifier
        with urllib.request.urlopen(uriString, context = sslContext) as url:
            data = json.loads(url.read().decode())
            return data

class GoogleObserverKeys:

    def __init__(self, storageUri, kernelIdentifier):
        self.storageUri = storageUri
        self.kernelIdentifier = kernelIdentifier

    def process(self):
        sslContext = ssl.create_default_context();
        sslContext.check_hostname = False
        sslContext.verify_mode = ssl.CERT_NONE
        uriString = self.storageUri + '/api/key/list?kernelIdentifier=' + self.kernelIdentifier
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

class CVEBase:
    baseUri = 'https://www.cvedetails.com'
    def readFile(self, url):
        file = requests.get(url)
        text = file.text
        return text
    def restoreUris(self, fragments, baseUri, result):
        for fragment in fragments:
            url = baseUri + fragment
            result.append(url)

class CVEIdentifierYear(CVEBase):
    def process(self, items):
        result = []
        listingUri = 'https://www.cvedetails.com/browse-by-date.php'
        fragments = re.findall('\/vulnerability-list\/year-[0-9]{4}\/vulnerabilities.html', self.readFile(listingUri))
        self.restoreUris(fragments, self.baseUri, result)
        return result

class CVEIdentifierPage(CVEBase):
    def process(self, items):
        result = []
        for uri in items:
            fragments = re.findall('(\/vulnerability-list.php\?[0-9a-zA-Z_=&;]+)(?:\"\t title=\"Go to page [0-9\">]+)', self.readFile(uri))
            self.restoreUris(fragments, self.baseUri, result)
        return result

class CVEIdentifier(CVEBase):
    def process(self, items):
        result = []
        for uri in items:
            fragments = re.findall('(?:[\<a-z0-9 =\"/]+)([0-9A-Z-]+)/(?:\")', self.readFile(uri))
            for identifier in fragments:
                result.append({
                    'id': identifier
                }) 
        return result

class CVEDescription:
    
    def __response(self, uri):
      
        session = requests.Session()
        headers = {'accept' : '*/*', 
                   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36 OPR/60.0.3255.36'}
        
        r = session.get(uri, headers=headers)
        soup = bs(r.content, 'html.parser')
        divs = soup.find_all('table', id ='cvssscorestable')
        files = divs[0]
        files = files.text
        return files
           
    def process(self, timeLineIdentifiers):
        
        for i in range(len(timeLineIdentifiers)):
            uri = 'https://www.cvedetails.com/cve/' + timeLineIdentifiers[i]['id']
            description = self.__response(uri) 
            timeLineIdentifiers[i]['description'] = description
            
        return timeLineIdentifiers
