import os
import json
import os.path
import time
import psutil

from datetime import datetime

# Matplotlib for simple charts
import matplotlib.pyplot as plot
from pysyun.timeline.statistics import MedianAggregateIndexes

# Plotly for interactive charts
import plotly.graph_objs as go
# Switch Plotly to offline mode
from plotly.offline import init_notebook_mode
try:
    init_notebook_mode(connected=True)
except Exception:
    pass


class DownsampledTimeLineChart:

    def __init__(self, interval_count):
        self.intervalCount = interval_count

    def process(self, time_line):

        # Sort the time-line by time-stamps
        time_line.sort(key=lambda value: value['time'])

        # Extract values
        values = []
        for i in range(len(time_line)):
            values.append(time_line[i]['value'])

        # Extract dates and time-stamps
        time_values = []
        date_values = []
        for i in range(len(time_line)):
            seconds = time_line[i]['time'] / 1000
            time_values.append(seconds)
            date_values.append(datetime.utcfromtimestamp(seconds).strftime('%Y-%m-%d %H:%M'))

        # Group the time-line into intervals by median
        indexes = MedianAggregateIndexes(self.intervalCount).process(time_values)

        # Projecting median indexes into dates and values
        filtered_values = []
        filtered_dates = []
        for i in indexes:
            filtered_values.append(values[i])
            filtered_dates.append(date_values[i])

        # Render the chart
        fig, ax = plot.subplots(figsize=(20, 10))
        # Configure axes
        fig.autofmt_xdate()
        # Display the grid
        ax.grid(True)
        # Data to display
        ax.plot(filtered_dates, filtered_values)


class InteractiveTimeLineChart:

    def __init__(self, title, x_title, y_title):
        self.traces = []
        self.title = title
        self.xTitle = x_title
        self.yTitle = y_title

    # Renders one more time-line each time
    def process(self, time_line_name, time_line):

        # Extract values
        values = []
        for i in range(len(time_line)):
            values.append(time_line[i]['value'])

        # Extract dates and time-stamps
        date_values = []
        for i in range(len(time_line)):
            seconds = time_line[i]['time'] / 1000
            date_values.append(datetime.utcfromtimestamp(seconds).strftime('%Y-%m-%d %H:%M'))

        # Add the current time-line to the chart traces
        trace = go.Scatter(
            x=date_values,
            y=values,
            name=time_line_name
        )
        self.traces.append(trace)

        if not time_line:
            # Render the chart
            layout = go.Layout(
                title=self.title,
                xaxis=dict(title=self.xTitle),
                yaxis=dict(title=self.yTitle)
            )
            data = go.Figure(self.traces, layout=layout)
            data.show(renderer="colab")


class InteractiveScatterTimeLineChart:

    def __init__(self, title, x_title, y_title):
        self.traces = []
        self.title = title
        self.xTitle = x_title
        self.yTitle = y_title

    # Renders one more time-line each time
    def process(self, time_line_name, time_line):

        # Extract values
        values = []
        for i in range(len(time_line)):
            values.append(time_line[i]['value'])

        # Extract dates and time-stamps
        date_values = []
        for i in range(len(time_line)):
            seconds = time_line[i]['time'] / 1000
            date_values.append(datetime.utcfromtimestamp(seconds).strftime('%Y-%m-%d %H:%M'))

        # Add the current time-line to the chart traces
        trace = go.Scatter(
            x=date_values,
            y=values,
            name=time_line_name,
            # Display only markers not to fill empty intervals with lines
            mode='markers'
        )
        self.traces.append(trace)

        if not time_line:
            # Render the chart
            layout = go.Layout(
                title=self.title,
                xaxis=dict(title=self.xTitle),
                yaxis=dict(title=self.yTitle)
            )
            data = go.Figure(self.traces, layout=layout)
            data.show(renderer="colab")


class Console:
    def process(self, time_line):
        print(time_line)


class ResourceLimitAction:

    @staticmethod
    def exit():
        pid = os.getpid()
        process = psutil.Process(pid)
        process.terminate()


class ResourceLimit:

    def __init__(self, state_file_name, condition, action=ResourceLimitAction.exit):

        self.state_file_name = state_file_name
        self.condition = condition
        self.action = action

        # Try to load prior state
        if os.path.exists(state_file_name):
            file = open(state_file_name)
            self.state = json.load(file)
            file.close()
        else:
            if callable(self.condition):
                pass
            elif "last" in condition:
                self.state = {
                    "last": 0
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
                if callable(self.condition):
                    if self.condition():
                        self.action()
                elif "last" in condition:
                    condition = condition["last"]
                    if "lessThan" in condition:

                        # "Less than given number" condition
                        if condition["lessThan"] > ResourceLimit.__now() - self.state["last"]:
                            self.action()

                elif "single" in condition:
                    if os.path.exists(self.state_file_name):
                        self.action()
                    else:
                        self.__save()

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

    @staticmethod
    def __now():
        return int(round(time.time() * 1000))
