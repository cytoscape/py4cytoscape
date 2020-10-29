# -*- coding: utf-8 -*-

"""Logging configuration values that can be set by a user.
"""

"""Copyright 2020 The Cytoscape Consortium

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the 
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit 
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the 
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO 
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

# Log level choices are here: https://docs.python.org/3/howto/logging.html#logging-levels

# print(f'Starting {__name__} module')


_SUMMARY_LOG_LEVEL = 'INFO' # 'DEBUG' to turn on, 'NOTSET' to turn off, 'INFO' to turn on just HTTP calls
_SUMMARY_ENABLE_HTTP_CALLS = True
_SUMMARY_ENABLE_HTTP_CONTENT = False

_DETAIL_LOG_LEVEL = 'DEBUG' # 'DEBUG' to turn on, 'NOTSET' to turn off
_DETAIL_ENABLE_HTTP_CALLS = True
_DETAIL_ENABLE_HTTP_CONTENT = True
_DETAIL_LOG_DIR = 'logs'
_DETAIL_LOG_NAME = 'py4cytoscape.log'

