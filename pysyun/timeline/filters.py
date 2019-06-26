# Python imports
import re
import requests
from urllib.parse import urlparse

# Data science imports
from pandas import DataFrame
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import *
import numpy as np
from sklearn.cluster import KMeans
from sklearn import preprocessing

# Removes all exact matches from a time-line according to the black list
class BlackList:
    
    def __init__(self, expressions):
        self.expressions = expressions
    
    def process(self, timeLine):
        results = []
        for j in range(len(timeLine)):
            segment = timeLine[j]['value']
            for k in range(len(self.expressions)):
                segment.discard(self.expressions[k])   
            if len(segment) != 0:
                results.append ({
                    'time': timeLine[j]['time'],
                    'value': segment
                })
        return results

class WhiteList:

    def __init__(self, values):
        self.values = values

    def process(self, timeLine):
        results = []
        for i in range(len(timeLine)):
            segment = timeLine[i]['value']
            segment = filter(lambda x: x in self.values, segment)
            segment = list(segment)
            if len(segment) != 0:
                results.append ({
                    'time': timeLine[i]['time'],
                    'value': segment
                })
        return results    

# Takes all regular expression matches from a time-line according to the regular expressions white list
class RegularExpressionWhiteList:
    
    def __init__(self, expressions):
        self.expressions = expressions
    
    def process(self, timeLine):
        results = []
        for i in range(len(timeLine)):
            segments = []
            for segment in timeLine[i]['value']:
                for expression in self.expressions:
                    if None != re.match(expression, segment):
                        segments.append(segment)
            if len(segments):
                results.append ({
                    'time': timeLine[i]['time'],
                    'value': segments
                })
        return results

# Takes all Telegram hyperlinks
class TelegramHyperlinks(RegularExpressionWhiteList):
    def __init__(self):
        super().__init__(['https:\/\/t\.me\/'])

# Takes all Telegram group chat hyperlinks
class TelegramChatHyperlinks(RegularExpressionWhiteList):
    def __init__(self):
        super().__init__(['https:\/\/t\.me\/joinchat\/'])

# Takes all Telegram invitation hyperlinks
class TelegramInvitationHyperlinks(RegularExpressionWhiteList):
    def __init__(self):
        # Not a chat, not a sticker, not a robot
        super().__init__(['https:\/\/t\.me\/((?!joinchat|addstickers).(?![a-zA-Z0-9_]*\?start=).[a-zA-Z0-9_]*)'])
        
# Takes all Telegram bot hyperlinks
class TelegramBotHyperlinks(RegularExpressionWhiteList):
    def __init__(self):
        super().__init__(['https:\/\/t\.me\/([a-zA-Z0-9_]*)\?start='])

# Takes all Telegram invitation hyperlinks and removes additional parameters from them
class TelegramInvitationPureHyperlinks(TelegramInvitationHyperlinks):
    def process(self, timeLine):
        timeLine = super(TelegramInvitationPureHyperlinks, self).process(timeLine)
        results = []
        for i in range(len(timeLine)):
            segments = []
            for segment in timeLine[i]['value']:
                parsed = urlparse(segment)
                search = re.search('\/([a-zA-Z0-9_]*)', parsed.path)
                segment = parsed.scheme + '://' + parsed.netloc + '/' + search.group(1)
                segments.append(segment)
            if len(segments):
                results.append ({
                    'time': timeLine[i]['time'],
                    'value': segments
                })
        return results

class TelegramInvitationMetadata:

    def process(self, links):
        channels = []
        for uri in links:
            channel = {}
            channel["uri"] = uri
            file = requests.get(uri)
            text = file.text
            search = re.search('<div class="tgme_page_extra">([0-9 ]+)members', text)
            if None != search:
                channel["members"] = int(search.group(1).replace(' ', ''))
            else:
                channel["members"] = 0
            search = re.search('([0-9 ]+)online<\/div>', text)
            if None != search:
                channel["online"] = int(search.group(1).replace(' ', ''))
            else:
                channel["online"] = 0
            search = re.search('<div class="tgme_page_description">(.*?)<\/div>', text)
            if None != search:
                channel["description"] = search.group(1)
            else:
                channel["description"] = ''
            channels.append(channel)
        channels.sort(key=lambda x: x["members"], reverse=True)
        return channels

class DateRange:

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def process(self, timeLine):
        newTimeLine = []
        for i in range(len(timeLine)):
            value = timeLine[i]
            if self.start <= value['time'] and value['time'] <= self.end:
                newTimeLine.append(value)
        return newTimeLine

class ValueChangeIntervals:

    def process(self, timeLine):

        results = []

        for index in range(len(timeLine)):
            
            time = timeLine[index]['time']
            currentValue = timeLine[index]['value']
            previousValue = currentValue
            if index != 0:
                previousValue = timeLine[index - 1]['value']

            newValue = 0
            if currentValue < previousValue:
                newValue = -1
            elif currentValue > previousValue:
                newValue = 1
            results.append({'time': time, 'value': newValue})

        return results

class KMeansClustering:
          
    def process(self, timeLine):
        
        # Convert to the data frame
        data = {'time':[], 'value':[]}
        for i in range(len(timeLine)):
            data['time'].append(timeLine[i]['time'])
            data['value'].append(timeLine[i]['value'])
        data = DataFrame(data)
        dataForClust = data.values
        
        # Pre-processing (scaling)
        scaler = preprocessing.StandardScaler()
        dataNorm = scaler.fit_transform(dataForClust)
        
        # Convert to the data frame
        dataNorm = DataFrame(dataNorm, columns=['time', 'value'])
        
        # Eucledian distance
        dataDist = pdist(dataNorm, 'euclidean')
        
        # Perform hierarchy clusterization
        dataLinkage = linkage(dataDist, method='average')
        
        # The "elbow" method to evaluate optimal segment count
        last = dataLinkage[-10:, 2]
        acceleration = np.diff(last, 2)
        acceleration_rev = acceleration[::-1]
        k = acceleration_rev.argmax() + 2
        
        # Perform K-means clustering
        km = KMeans(n_clusters=k).fit(dataNorm)
        km = list(km.labels_ +1)
        
        results = []
        for i in range(len(data)):
          results.append({
              'time': data['time'][i],
              'value': km[i]
          })

        return results
