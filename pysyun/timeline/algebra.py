# Builds a time-line which gathers zero or more time-lines 
# having all values sorted in the time ascending order
class Add:
    
    def __init__(self):
        self.result = []
    
    def process(self, secondTimeLine):
        self.result.extend(secondTimeLine)
        self.result.sort(key=lambda value: value['time'], reverse=True)
        return self.result

class SubtractProcessor:
    def process(self, data):
        data1 = data[0]
        data2 = data[1]
        return [{'time': data1[i]['time'], 'value': data1[i]['value'] - data2[i]['value']}
                for i in range(len(data1))]


class AbsoluteProcessor:
    def process(self, data):
        return [{'time': item['time'], 'value': abs(item['value'])} for item in data]
