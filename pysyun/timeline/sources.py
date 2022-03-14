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

class CoinMarketCapList:
    
    def __init__(self, page):
        self.page = page
    
    def __response(self, uri):
        session = requests.Session()
        headers = {'accept' : '*/*', 
                   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36 OPR/60.0.3255.36'}
        request = session.get(uri, headers=headers)
        document = bs(request.content, 'html.parser')
        return document
    
    def __parse_number(self, value):
        value = str.replace(value, ",", "")
        value = str.replace(value, "$", "")
        return float(value)
    
    def __parse(self, document):
        elements = document.select('.cmc-table tr')
        timeLine = []
        timeStamp = int(time.time())
        exceptionCounter = 0
        for element in elements:
            try:
                soup = bs(str(element), 'html.parser')
                symbol = soup.select('.coin-item-symbol')[0].text
                price = soup.select('td:nth-child(4)')[0].text
                price = self.__parse_number(price)
                capitalization = soup.select('td:nth-child(7) span')[1].text
                capitalization = self.__parse_number(capitalization)
                circulatingSupply = soup.select('td:nth-child(9)')[0].text
                circulatingSupply = str.replace(circulatingSupply, symbol, "")
                circulatingSupply = self.__parse_number(circulatingSupply)
                value = {
                    "symbol": symbol,
                    "price": price, 
                    "capitalization": capitalization, 
                    "circulatingSupply": circulatingSupply
                }
                data = {
                    "time": timeStamp,
                    "value": value
                }
                timeLine.append(data)
            except Exception:
                exceptionCounter = exceptionCounter + 1
        return timeLine
           
    def process(self):
        uri = 'https://coinmarketcap.com/?page=' + str(self.page)
        document = self.__response(uri)
        timeLine = self.__parse(document)
        return timeLine


class CopyAI:

  def __init__(self, token, project_identifier, product_identifier):
    self.token = token
    self.project_identifier = project_identifier
    self.product_identifier = product_identifier

  def uri(self):
    return "https://api.copy.ai/v1/text-gen/generate"

  def headers(self):
    return {
      'accept': "application/json, text/plain, */*",
      'content-type': "application/json",
      'user-agent': "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
      'referer': "https://app.copy.ai/",
      'accept-language': "en-US,en;q=0.9",
      'cookie': "UserJWT={0};".format(self.token)
    }

  def data(self, name, description, tone, input_language, output_language):
    value = {
      "projectId": self.project_identifier,
      "toolKey": self.product_identifier,
      "promptParams": {
          "name": name,
          "description": description,
          "tone": tone
      },
      "inputLang": input_language,
      "outputLang": output_language,
      "supercharge": False
    }
    return json.dumps(value)

  def process(self, data):
    results = []
    for item in data:
      response = requests.post(self.uri(), headers=self.headers(), data=self.data(item["name"], item["description"], item["tone"], item["input_language"], item["output_language"]))
      response = json.loads(response.text)
      response = response["data"]["choices"]
      results.append(response)
    return results
