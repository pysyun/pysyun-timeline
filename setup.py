from setuptools import setup

setup (
   name = 'pysyun_timeline',
   version = '1.0',
   description = 'Syun\'s Python SDK for time series analysis. Python toolkit for analyzing time series data.',
   author = 'Py Syun',
   author_email = 'pysyun@vitche.com',
   py_modules = ['pysyun.timeline.algebra', 'pysyun.timeline.converters', 'pysyun.timeline.filters', 'pysyun.timeline.reducers', 'pysyun.timeline.segmenters', 'pysyun.timeline.sources'],
   install_requires = []
)