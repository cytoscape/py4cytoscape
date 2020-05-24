# -*- coding: utf-8 -*-

"""Logging configuration values that can be set by a user.
"""

# Log level choices are here: https://docs.python.org/3/howto/logging.html#logging-levels

_SUMMARY_LOG_LEVEL = 'INFO' # 'DEBUG' to turn on, 'NOTSET' to turn off, 'INFO' to turn on just HTTP calls
_SUMMARY_ENABLE_HTTP_CALLS = True
_SUMMARY_ENABLE_HTTP_CONTENT = False

_DETAIL_LOG_LEVEL = 'DEBUG' # 'DEBUG' to turn on, 'NOTSET' to turn off
_DETAIL_ENABLE_HTTP_CALLS = True
_DETAIL_ENABLE_HTTP_CONTENT = True
_DETAIL_LOG_DIR = 'logs'
_DETAIL_LOG_NAME = 'py4cytoscape.log'

