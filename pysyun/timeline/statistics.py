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
