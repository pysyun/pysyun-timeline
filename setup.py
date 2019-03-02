from setuptools import setup

setup (
   name = 'pysyun_timeline',
   version = '1.0',
   description = 'Syun\'s Python SDK for time series analysis. Python toolkit for analyzing time series data.',
   author = 'Py Syun',
   author_email = 'pysyun@vitche.com',
   py_modules = ['algebra', 'converters', 'filters', 'reducers', 'segmenters', 'sources'],
   install_requires = []
)