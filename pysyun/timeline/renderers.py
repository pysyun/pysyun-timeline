from datetime import datetime

# Matplotlib for simple charts
import matplotlib.pyplot as plot
from pysyun.timeline.statistics import MedianAggregateIndexes

# Plotly for interactive charts
import plotly.graph_objs as go
# Switch Plotly to offline mode
from plotly.offline import init_notebook_mode, iplot
init_notebook_mode(connected=True)

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

class InteractiveTimeLineChart:

    def __init__(self, title, xTitle, yTitle):
        self.traces = []
        self.title = title
        self.xTitle = xTitle
        self.yTitle = yTitle
    
    # Renders one more time-line each time
    def process(self, timeLine):
        
        # Extract values
        values = []
        for i in range(len(timeLine)):
            values.append(timeLine[i]['value'])

        # Extract dates and time-stamps
        dateValues = []
        for i in range(len(timeLine)):
            seconds = timeLine[i]['time'] / 1000
            dateValues.append(datetime.utcfromtimestamp(seconds).strftime('%Y-%m-%d %H:%M'))
            
        # Add the current time-line to the chart traces
        trace = go.Scatter(
            x=dateValues,
            y=values
        )
        self.traces.append(trace)
        
        # Render the chart
        layout = go.Layout(
            title=self.title, 
            xaxis=dict(title=self.xTitle),
            yaxis=dict(title=self.yTitle)
        )
        data = go.Figure(self.traces, layout=layout)
        iplot(data)  
