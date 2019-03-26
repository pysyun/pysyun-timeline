from statistics import median_low

class MedianAggregateIndexes:

    def __init__(self, intervalCount):
        self.intervalCount = intervalCount

    def process(self, coordinates):
        indexes = []
        length = len(coordinates)
        step = int(length / self.intervalCount)
        i = 0
        while i < length:
            section = coordinates[i:i+step]
            median = median_low(section)
            indexes.append(i + section.index(median))
            i = i + step
        return indexes

class EventCountAggregate:

    def __init__(self, intervalCount):
        self.intervalCount = intervalCount

    def process(self, timeLine):

        if 0 == len(timeLine):
            return []        

        newTimeLine = []
        
        timeLine.sort(key=lambda value: value['time'])

        # Minimum and maximum time stamps
        i = 0
        minimum = timeLine[0]['time']
        maximum = minimum
        while i < len(timeLine):
            currentEventTime = timeLine[i]['time']
            if currentEventTime < minimum:
                minimum = currentEventTime
            if maximum < currentEventTime:
                maximum = currentEventTime
            i = i + 1
        
        # Desired interval length
        step = int((maximum - minimum) / self.intervalCount)
        
        # Process each interval
        i = 0
        length = len(timeLine)
        currentIntervalStart = minimum
        currentIntervalEnd = currentIntervalStart + step
        currentEventCount = 0
        while i < length:
            currentEventTime = timeLine[i]['time']
            currentEventCount = currentEventCount + 1
            if currentIntervalEnd <= currentEventTime or i == length - 1:
                newTimeLine.append({
                    'time': currentEventTime,
                    'value': currentEventCount
                })
                currentEventCount = 0
                currentIntervalStart = currentIntervalStart + step
                currentIntervalEnd = currentIntervalEnd + step
            i = i + 1

        return newTimeLine
