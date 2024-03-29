# Python imports
import re
import json
import math
import time
import requests
from urllib.parse import urlparse
from datetime import datetime, timedelta

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
                results.append({
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
            if isinstance(segment, int) or isinstance(segment, str):
                if segment in self.values:
                    results.append({
                        'time': timeLine[i]['time'],
                        'value': segment
                    })
            else:
                segment = filter(lambda x: x in self.values, segment)
                segment = list(segment)
                if len(segment) != 0:
                    results.append({
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
                results.append({
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
                results.append({
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


class InverseDateRange:

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def process(self, timeLine):
        newTimeLine = []
        for i in range(len(timeLine)):
            value = timeLine[i]
            if value['time'] < self.start and self.end > value['time']:
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


class ValueChanges:
    def process(self, timeLine):
        results = []

        for index in range(len(timeLine)):
            if index == 0:
                results.append(timeLine[index])
            else:
                currentValue = timeLine[index]['value']
                previousValue = timeLine[index - 1]['value']
                if currentValue != previousValue:
                    results.append(timeLine[index])

        return results


class KMeansClustering:

    def __init__(self, clusterCount=None):
        self.clusterCount = clusterCount

    def process(self, timeLine):

        # Convert to the data frame
        data = {'time': []}
        for i in range(len(timeLine)):
            data['time'].append(timeLine[i]['time'])
        data = DataFrame(data)
        dataForClust = data.values

        # Pre-processing (scaling)
        scaler = preprocessing.StandardScaler()
        dataNorm = scaler.fit_transform(dataForClust)

        # Convert to the data frame
        dataNorm = DataFrame(dataNorm, columns=['time'])

        # Eucledian distance
        dataDist = pdist(dataNorm, 'euclidean')

        # Perform hierarchy clusterization
        dataLinkage = linkage(dataDist, method='average')

        # The "elbow" method to evaluate optimal segment count
        if self.clusterCount is None:

            start = 1
            before = 20

            samples = []
            for k in range(start, before):
                kmSamples = KMeans(n_clusters=k, n_init=before, random_state=1)
                kmSamples.fit(dataLinkage)
                samples.append(kmSamples.inertia_)

            x1, y1 = start, samples[0]
            x2, y2 = (before - 1), samples[len(samples) - 1]

            # Find the optimum cluster count
            distances = []
            for i in range(len(samples)):
                x0 = i + start
                y0 = samples[i]
                numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
                denominator = math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
                distances.append(numerator / denominator)

            self.clusterCount = distances.index(max(distances)) + start

        # Perform K-means clustering
        km = KMeans(n_clusters=self.clusterCount, n_init=10, random_state=1).fit(dataNorm)
        km = list(km.labels_ + 1)

        # Re-index cluster identifiers to make them sequential
        reindexedClusters = []
        value = 1
        for j in range(len(km)):
            if j != 0:
                cluster = km[j]
                previousCluster = km[j - 1]
                if cluster == previousCluster:
                    reindexedClusters.append(value)
                else:
                    value += 1
                    reindexedClusters.append(value)
            elif j == 0:
                reindexedClusters.append(value)

        results = []
        for i in range(len(data)):
            results.append({
                'time': data['time'][i],
                'value': reindexedClusters[i]
            })

        return results


class ClusterCentroid:

    def process(self, timeLine, timeLineClusters):

        # Extracting time-line values
        data = {'value': []}
        for i in range(len(timeLine)):
            data['value'].append(timeLine[i]['value'])

            # Look for cluster groups count from timeLineClusters
        # Find interval start and end indexes for each group
        clusters = []
        timeLineLength = len(timeLineClusters)
        for index in range(timeLineLength):
            cluster = timeLineClusters[index]['value']
            if index != 0:
                previouscluster = timeLineClusters[index - 1]['value']
                if cluster != previouscluster:
                    if len(clusters) == 0:
                        interval = [0, index]
                        clusters.append(interval)
                    else:
                        interval = [(clusters[-1][-1]) + 1, index]
                        clusters.append(interval)
                elif index == (timeLineLength - 1):
                    interval = [(clusters[-1][-1]) + 1, timeLineLength - 1]
                    clusters.append(interval)

        # A new list containing cluster groups united by similarity for a given time span.
        # Cluster groups contain sums of values of the cluster time span.
        result = []
        for i in range(len(clusters)):
            first = clusters[i][0]
            last = clusters[i][1]
            timeLineCenter = int((timeLineClusters[first]['time'] + timeLineClusters[last]['time']) / 2)
            total = sum(data['value'][first:last + 1])
            result.append({
                'time': timeLineCenter,
                'value': total
            })

        return result


class Lowercase:

    def process(self, timeLine):
        for j in range(len(timeLine)):
            segment = timeLine[j]['value']
            if isinstance(segment, int) or isinstance(segment, str):
                segment = segment.lower()
            else:
                for k in range(len(segment)):
                    segment[k] = segment[k].lower()
            timeLine[j]['value'] = segment
        return timeLine


class CharacterBlackList:

    def __init__(self, substrings):
        self.substrings = substrings

    def process(self, timeLine):
        for j in range(len(timeLine)):
            segment = timeLine[j]['value']
            if isinstance(segment, int) or isinstance(segment, str):
                for k in range(len(self.substrings)):
                    segment = segment.strip(self.substrings[k])
                    print(segment, self.substrings[k])
            else:
                for i in range(len(segment)):
                    for k in range(len(self.substrings)):
                        segment[i] = segment[i].strip(self.substrings[k])
            timeLine[j]['value'] = segment
        return timeLine


class LambdaProjection:

    def __init__(self, projection):
        self.projection = projection

    def process(self, timeLine):
        result = []
        for i in range(len(timeLine)):
            event = timeLine[i]
            projection = self.projection(event)
            if None != projection:
                result.append(projection)

        return result


class JSON:

    def process(self, timeLine):
        result = []
        for i in range(len(timeLine)):
            event = timeLine[i]
            event["value"] = json.loads(event["value"])
            result.append(event)

        return result


class Limit:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def process(self, timeLine):
        return timeLine[self.start:self.end]


class Count:
    def process(self, timeLine):
        return [len(timeLine)]


class Empty():
    def process(self, timeLine):
        return


class LastTimeFrame:
    def process(self, timeLine):
        newTimeLine = []
        for i in range(len(timeLine)):
            value = timeLine[i]
            if self.start <= value['time']:
                newTimeLine.append(value)
        return newTimeLine

    def startTime(self, delta):
        currentDate = datetime.today()
        currentDate = datetime(currentDate.year, currentDate.month, currentDate.day)
        currentDate = currentDate - delta
        self.start = time.mktime(currentDate.timetuple()) * 1000


class LastMinutes(LastTimeFrame):
    def __init__(self, count):
        self.startTime(timedelta(minutes=count))


class LastHours(LastTimeFrame):
    def __init__(self, count):
        self.startTime(timedelta(hours=count))


class LastDays(LastTimeFrame):
    def __init__(self, count):
        self.startTime(timedelta(days=count))


class LastWeeks(LastTimeFrame):
    def __init__(self, count):
        self.startTime(timedelta(weeks=count))


class LastMonths(LastTimeFrame):
    def __init__(self, count):
        self.startTime(timedelta(months=count))


class CopyAIAugmentation:

    def __init__(self, uri, augmented_culture):
        self.uri = uri
        self.augmented_culture = augmented_culture

    @staticmethod
    def headers():
        return {
            'content-type': "application/json",
            'user-agent': "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/96.0.4664.110 Safari/537.36"
        }

    @staticmethod
    def __build_augmented_text(api_response):
        for event in api_response:
            sentence = ""
            for atom in event:
                sentence = sentence + atom + "\n"
            return sentence

    def __build_augmented_event(self, original, augmented_text):
        augmented_event = {
            "kernelIdentifier": original["kernelIdentifier"],
            "keyIdentifier": original["keyIdentifier"],
            "hash": original["hash"],
            "uri": original["uri"],
            "date": original["date"],
            "text": augmented_text,
            "culture": self.augmented_culture,
            "augmenter": "CopyAI"
        }
        return augmented_event

    def process(self, time_line):
        results = []
        for event in time_line:
            event_time = event["time"]
            event_value = event["value"]
            text = event_value["text"]
            data = {
                "name": text,
                "description": text,
                # TODO: Take original language from the kernel key culture
                "input_language": self.augmented_culture,
                "output_language": self.augmented_culture
            }
            response = requests.post(self.uri, headers=CopyAIAugmentation.headers(), data=json.dumps(data))
            if response.status_code == 200:
                atoms = json.loads(response.text)
                augmented_text = CopyAIAugmentation.__build_augmented_text(atoms)
                augmented_event_value = self.__build_augmented_event(event_value, augmented_text)
                if "augmentations" not in event_value:
                    event_value["augmentations"] = []
                event_value["augmentations"].append(self.augmented_culture)
                results.append(event)
                results.append({
                    "time": event_time,
                    "value": augmented_event_value
                })

        return results


class GPT2Transformer:

    def __init__(self, length, sentences):
        self.length = length
        self.sentences = sentences

    def process(self, data):

        from transformers import pipeline
        generator = pipeline('text-generation', model='gpt2')

        results = []
        for item in data:

            sentences = []

            response = generator(
                item,
                do_sample=True,
                top_k=50,
                temperature=0.6,
                max_length=self.length,
                num_return_sequences=self.sentences
            )

            for sentence in response:
                sentence = sentence["generated_text"]
                last_fullstop = sentence.rfind(".")
                sentence = sentence[:last_fullstop + 1]
                sentences.append(sentence)

            results.append(sentences)

        return results
