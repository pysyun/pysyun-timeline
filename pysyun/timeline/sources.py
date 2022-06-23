import re
import ssl
import json
import time
import requests
import urllib.request
from bs4 import BeautifulSoup
from pymongo import MongoClient, DESCENDING
from storage_timeline_client import Storage
from pysyun.timeline.algebra import Add


class StorageTimelineSchema:
    def __init__(self, uri, schema_name):
        self.schema = Storage(uri).schema(schema_name)

    def process(self, empty):
        result = []
        time_line_names = self.schema.list()
        for timeLineName in time_line_names:
            result.append(self.schema.timeLine(timeLineName))
        return result


class StorageTimelineTimeline:
    def __init__(self, uri, schema_name, time_line_name):
        self.timeLine = Storage(uri).schema(schema_name).timeLine(time_line_name)

    def process(self, empty):
        return [self.timeLine]


class StorageTimelineStrings:
    def process(self, time_lines):
        results = []
        cumulation = Add()
        for timeLine in time_lines:
            try:
                values = timeLine.allStrings()
                results = cumulation.process(values)
            except:
                print("Unable to fetch data from Storage.Timeline", timeLine.schema, timeLine.name)
        return results


class GoogleObserver:

    def __init__(self, storage_uri, kernel_identifier, from_timestamp=None):
        self.storageUri = storage_uri
        self.kernelIdentifier = kernel_identifier
        self.from_timestamp = from_timestamp

    def process(self, formal_argument):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        uri_string = self.storageUri + '/api/event/list?kernelIdentifier=' + self.kernelIdentifier
        if self.from_timestamp is not None:
            uri_string += "&from=" + str(self.from_timestamp)
        with urllib.request.urlopen(uri_string, context=ssl_context) as url:
            data = json.loads(url.read().decode())
            return data


class GoogleObserverKeys:

    def __init__(self, storage_uri, kernel_identifier):
        self.storageUri = storage_uri
        self.kernelIdentifier = kernel_identifier

    def process(self):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        uri_string = self.storageUri + '/api/key/list?kernelIdentifier=' + self.kernelIdentifier
        with urllib.request.urlopen(uri_string, context=ssl_context) as url:
            data = json.loads(url.read().decode())
            return data


class EthereumGasStation:

    def process(self):
        uri = 'https://ethgasstation.info/gasguzzlers.php'
        file = requests.get(uri)
        text = file.text

        result = []
        search_uri = re.findall('https:\/\/etherscan.io\/address\/[a-zA-Z0-9_]*', text)
        search_load = re.findall('(?:<td>)([0-9]+\.[0-9]+)(?:<\/td>)', text)

        for index in range(len(search_uri)):
            data = {
                'time': int(time.time()),
                'value': {
                    'uri': search_uri[index] + '#contracts',
                    'load': search_load[index],
                }
            }
            result.append(data)

        return result


class CVEBase:
    baseUri = 'https://www.cvedetails.com'

    def read_file(self, url):
        file = requests.get(url)
        text = file.text
        return text

    def restore_uris(self, fragments, base_uri, result):
        for fragment in fragments:
            url = base_uri + fragment
            result.append(url)


class CVEIdentifierYear(CVEBase):
    def process(self, items):
        result = []
        listing_uri = 'https://www.cvedetails.com/browse-by-date.php'
        fragments = re.findall('\/vulnerability-list\/year-[0-9]{4}\/vulnerabilities.html', self.read_file(listing_uri))
        self.restore_uris(fragments, self.baseUri, result)
        return result


class CVEIdentifierPage(CVEBase):
    def process(self, items):
        result = []
        for uri in items:
            fragments = re.findall('(\/vulnerability-list.php\?[0-9a-zA-Z_=&;]+)(?:\"\t title=\"Go to page [0-9\">]+)',
                                   self.read_file(uri))
            self.restore_uris(fragments, self.baseUri, result)
        return result


class CVEIdentifier(CVEBase):
    def process(self, items):
        result = []
        for uri in items:
            fragments = re.findall('(?:[\<a-z0-9 =\"/]+)([0-9A-Z-]+)/(?:\")', self.read_file(uri))
            for identifier in fragments:
                result.append({
                    'id': identifier
                })
        return result


class CVEDescription:

    def __response(self, uri):
        session = requests.Session()
        headers = {'accept': '*/*',
                   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/73.0.3683.86 Safari/537.36 OPR/60.0.3255.36'}

        r = session.get(uri, headers=headers)
        soup = BeautifulSoup(r.content, 'html.parser')
        divs = soup.find_all('table', id='cvssscorestable')
        files = divs[0]
        files = files.text
        return files

    def process(self, time_line_identifiers):
        for i in range(len(time_line_identifiers)):
            uri = 'https://www.cvedetails.com/cve/' + time_line_identifiers[i]['id']
            description = self.__response(uri)
            time_line_identifiers[i]['description'] = description

        return time_line_identifiers


class CoinMarketCapList:

    def __init__(self, page):
        self.page = page

    def __response(self, uri):
        session = requests.Session()
        headers = {'accept': '*/*',
                   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/73.0.3683.86 Safari/537.36 OPR/60.0.3255.36'}
        request = session.get(uri, headers=headers)
        document = BeautifulSoup(request.content, 'html.parser')
        return document

    def __parse_number(self, value):
        value = str.replace(value, ",", "")
        value = str.replace(value, "$", "")
        return float(value)

    def __parse(self, document):
        elements = document.select('.cmc-table tr')
        time_line = []
        time_stamp = int(time.time())
        exception_counter = 0
        for element in elements:
            try:
                soup = BeautifulSoup(str(element), 'html.parser')
                symbol = soup.select('.coin-item-symbol')[0].text
                price = soup.select('td:nth-child(4)')[0].text
                price = self.__parse_number(price)
                capitalization = soup.select('td:nth-child(7) span')[1].text
                capitalization = self.__parse_number(capitalization)
                circulating_supply = soup.select('td:nth-child(9)')[0].text
                circulating_supply = str.replace(circulating_supply, symbol, "")
                circulating_supply = self.__parse_number(circulating_supply)
                value = {
                    "symbol": symbol,
                    "price": price,
                    "capitalization": capitalization,
                    "circulatingSupply": circulating_supply
                }
                data = {
                    "time": time_stamp,
                    "value": value
                }
                time_line.append(data)
            except Exception:
                exception_counter = exception_counter + 1
        return time_line

    def process(self):
        uri = 'https://coinmarketcap.com/?page=' + str(self.page)
        document = self.__response(uri)
        time_line = self.__parse(document)
        return time_line


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
            'user-agent': "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/96.0.4664.110 Safari/537.36",
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
            response = requests.post(self.uri(), headers=self.headers(),
                                     data=self.data(item["name"], item["description"], item["tone"],
                                                    item["input_language"], item["output_language"]))
            response = json.loads(response.text)
            response = response["data"]["choices"]
            results.append(response)
        return results


class MongoDBRecentEventsCollection:

    def __init__(self, connection_string, database, collection, start=0, end=100):
        self.connection = MongoClient(connection_string)
        self.database = database
        self.collection = collection
        self.start = start
        self.end = end

    def process(self, filters):

        if 0 < len(filters) and "time" in filters[0]:

            database = self.connection[self.database]
            events = database[self.collection]

            # The time-line was passed
            for event in filters:
                event_value = event["value"]
                if "_id" in event_value:
                    events.update_one({
                        "_id": event_value["_id"]
                    }, {
                        "$set": event_value
                    })
                else:
                    events.insert_one(event_value)
            return filters

        else:

            # The filter was passed
            results = []
            query_filter = filters
            if 0 < len(filters):
                query_filter = filters[0]
            database = self.connection[self.database]
            events = database[self.collection].find(query_filter).sort([('date', DESCENDING)])[self.start:self.end]
            for event in events:
                date_value = event["date"]
                date_value = int(date_value.timestamp()) * 1000
                results.append({
                    'time': date_value,
                    'value': event
                })
            return results


class CopyAIReference:

    def __init__(self, uri):
        self.uri = uri

    def process(self, data):
        results = []
        for item in data:
            response = requests.post(self.uri, json.dumps(item), headers={"Content-type": "application/json"})
            response = json.loads(response.text)
            results += response
        return results
