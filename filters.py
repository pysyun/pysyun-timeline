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
