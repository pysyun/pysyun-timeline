class ChartNode(Node):

    __arguments = []
    __chart = None
    __projection = None
    
    def __init__(self, title, xTitle, yTitle):
        self.__chart = InteractiveTimeLineChart(title, xTitle, yTitle)
        super().__init__()
        
    def read(self):
        return self.__arguments
        
    def write(self, data):
        if [] == data:
            self.__arguments = []
        elif None != data:
            if 0 < len(data):
                first = data[0]
                if isinstance(first, str):
                    self.__projection = first 
                else:
                    self.__arguments += data

    def process(self):
        data = self.read()
        filteredResult = WhiteList([self.__projection]).process(data)
        filteredResult = EventCountAggregate(52).process(filteredResult)
        if 0 < len(filteredResult) or '' == self.__projection:
            self.__chart.process(self.__projection, filteredResult)
