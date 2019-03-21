from datetime import datetime
import matplotlib.pyplot as plot
from pysyun.timeline.statistics import MedianAggregateIndexes

class DownsampledTimeLineChart:

    def __init__(self, intervalCount):
        self.intervalCount = intervalCount
    
    def process(self, timeLine):

        # Sort the time-line by time-stamps
        timeLine.sort(key=lambda value: value['time'])

        # Extract values
        values = []
        for i in range(len(timeLine)):
            values.append(timeLine[i]['value'])

        # Extract dates and time-stamps
        timeValues = []
        dateValues = []
        for i in range(len(timeLine)):
            seconds = timeLine[i]['time'] / 1000
            timeValues.append(seconds)
            dateValues.append(datetime.utcfromtimestamp(seconds).strftime('%Y-%m-%d %H:%M'))

        # Group the time-line into intervals by median
        indexes = MedianAggregateIndexes(self.intervalCount).process(timeValues)

        # Projecting median indexes into dates and values
        filteredValues = []
        filteredDates = []
        for i in indexes:
            filteredValues.append(values[i])
            filteredDates.append(dateValues[i])

        # Render the chart
        fig, ax = plot.subplots(figsize=(20, 10))
        # Configure axes
        fig.autofmt_xdate()
        # Display the grid
        ax.grid(True)
        # Data to display
        ax.plot(filteredDates, filteredValues)
