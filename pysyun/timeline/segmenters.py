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
