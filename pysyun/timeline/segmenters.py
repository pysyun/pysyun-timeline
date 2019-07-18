import re

# Builds a time-line containing currency abbreviations
class CurrencyAbbreviations:
    
    def process(self, timeLine):
        newTimeLine = []
        for i in range(len(timeLine)):
            regularExpression = r'[A-Z]{3,}'
            segment = timeLine[i]['value']
            results = re.findall(regularExpression, segment)
            if len(results) != 0:
                results = set(results)
                results = list(results)
                # TODO: Пока не скажу, что здесь не так - потом скажу, но тут очень интересно
                newTimeLine.append({
                    'time': timeLine[i]['time'],
                    'value': results
                })
        return newTimeLine

# Builds a time-line containing hyper-links
class Hyperlinks:
    
    def process(self, timeLine):
        newTimeLine = []
        for i in range(len(timeLine)):
            regularExpression = r'[\w]+:\/\/[a-zA-Z0-9u00a1-\uffff0-]+\.[a-zA-Z0-9u00a1-\uffff0-]+\S*'
            segment = timeLine[i]['value']
            results = re.findall(regularExpression, segment)
            if len(results) != 0:
                newTimeLine.append({
                    'time': timeLine[i]['time'],
                    'value': results
                })
        return newTimeLine

class Words:

    def process(self, timeLine):
        newTimeLine = []
        for i in range(len(timeLine)):

            segment = timeLine[i]['value']
            results = segment.split()

            if 0 != len(results):

                results = set(results)
                results = list(results)
                newTimeLine.append({
                    'time': timeLine[i]['time'],
                    'value': results
                })

        return newTimeLine

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
