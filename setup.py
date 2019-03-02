from setuptools import setup

setup (
   name = 'pysyun_timeline',
   version = '1.0',
   description = 'Syun\'s Python SDK for time series analysis. Python toolkit for analyzing time series data.',
   author = 'Py Syun',
   author_email = 'pysyun@vitche.com',
   py_modules = ['pysyun_timeline.algebra', 'pysyun_timeline.converters', 'pysyun_timeline.filters', 'pysyun_timeline.reducers', 'pysyun_timeline.segmenters', 'pysyun_timeline.sources'],
   install_requires = []
)