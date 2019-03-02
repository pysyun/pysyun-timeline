# Builds a time-line which gathers zero or more time-lines 
# having all values sorted in the time ascending order
class Add:
    
    def __init__(self):
        self.result = []
    
    def process(self, secondTimeLine):
        self.result.extend(secondTimeLine)
        self.result.sort(key=lambda value: value['time'], reverse=True)
        return self.result
