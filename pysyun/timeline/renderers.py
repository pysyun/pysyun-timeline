import os
import json 
import os.path
import time

from sys import exit

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
    def process(self, timeLineName, timeLine):
        
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
            y=values,
            name=timeLineName
        )
        self.traces.append(trace)
        
        if [] == timeLine:

            # Render the chart
            layout = go.Layout(
                title=self.title, 
                xaxis=dict(title=self.xTitle),
                yaxis=dict(title=self.yTitle)
            )
            data = go.Figure(self.traces, layout=layout)
            iplot(data)

class InteractiveScatterTimeLineChart:

    def __init__(self, title, xTitle, yTitle):
        self.traces = []
        self.title = title
        self.xTitle = xTitle
        self.yTitle = yTitle
    
    # Renders one more time-line each time
    def process(self, timeLineName, timeLine):
        
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
            y=values,
            name=timeLineName,
            # Display only markers not to fill empty intervals with lines
            mode='markers'
        )
        self.traces.append(trace)
        
        if [] == timeLine:

            # Render the chart
            layout = go.Layout(
                title=self.title, 
                xaxis=dict(title=self.xTitle),
                yaxis=dict(title=self.yTitle)
            )
            data = go.Figure(self.traces, layout=layout)
            iplot(data)

class Console:
    def process(self, timeLine):
        print(timeLine)


class ResourceLimit:

  def __init__(self, state_file_name, condition):

    self.state_file_name = state_file_name
    self.condition = condition

    # Try to load prior state
    if os.path.exists(state_file_name):
      file = open(state_file_name)
      self.state = json.load(file)
      file.close()
    else:
      if "last" in condition:
        self.state = {
            "last": ResourceLimit.__now()
        }
      elif "single" in condition:
        self.state = {
            "single": True
        }

  def process(self, data):

      if 0 < len(data):
        atom = data[0]
        if "enter" in atom:

          # Try to process available conditions
          condition = self.condition
          if "last" in condition:
            condition = condition["last"]
            if "lessThan" in condition:

              # "Less than given number" condition
              if condition["lessThan"] < ResourceLimit.__now() - self.state["last"]:
                os.remove(self.state_file_name)
                exit()

          elif "single" in condition:
            if os.path.exists(self.state_file_name):
              exit()

        elif "release" in atom:

          # State update and saving
          if "last" in self.state:
            self.state["last"] = ResourceLimit.__now()
            self.__save()
          elif "single" in self.state:
            if os.path.exists(self.state_file_name):
              os.remove(self.state_file_name)

  def __save(self):
      with open(self.state_file_name, 'w') as file:
        json.dump(self.state, file)

  def __now():
    return int(round(time.time() * 1000))
