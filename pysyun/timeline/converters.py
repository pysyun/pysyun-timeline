import time

class JSONArray:
    
    def __init__(self, dateField, textField):
        self.dateField = dateField
        self.textField = textField
    
    def process(self, timeLine):
        results = []
        for i in range(len(timeLine)):
            event = timeLine[i]
            dateValue = event[self.dateField]
            # TODO: There is an opinion that "ciso8601" library is much faster
            dateValue = time.mktime(time.strptime(dateValue, '%Y-%m-%dT%H:%M:%S.%fZ'))
            dateValue = int(dateValue) * 1000
            value = event[self.textField] 
            results.append ({
                'time': dateValue,
                'value': value
            })            
        return results
