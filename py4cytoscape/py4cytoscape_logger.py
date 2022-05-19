# -*- coding: utf-8 -*-

"""Centralized logging definitions.

Any module needing logging facilities can access the ``logger`` class instance by simply importing this module, then
calling ``summary_logger.<method>`` or ``detail_logger.<method>``. The ``summary_logger`` sends only short information
and is suitable for a console. The ``debug_logger`` sends complete information and is suitable for a disk log.
Also the ``@cy_log`` decorator can be used before any function to cause logging of inbound parameters and outbound
return/exception values.
"""

"""Copyright 2020-2022 The Cytoscape Consortium

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

# External library imports
import logging
from logging.handlers import RotatingFileHandler
import functools
import os
import sys

from .py4cytoscape_logger_settings import _DETAIL_LOG_DIR, _DETAIL_LOG_LEVEL, _DETAIL_LOG_NAME, _DETAIL_ENABLE_HTTP_CALLS, _SUMMARY_LOG_LEVEL, _SUMMARY_ENABLE_HTTP_CALLS, _DETAIL_ENABLE_HTTP_CONTENT, _SUMMARY_ENABLE_HTTP_CONTENT

# print(f'Starting {__name__} module')


_detail_log_base = os.path.join(_DETAIL_LOG_DIR, _DETAIL_LOG_NAME)
if not os.path.exists(_DETAIL_LOG_DIR): os.makedirs(_DETAIL_LOG_DIR)

# Set up detail logger
detail_logger = logging.getLogger('py4...')
detail_handler = RotatingFileHandler(_detail_log_base, maxBytes=10485760, backupCount=10, encoding='utf8')
detail_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
detail_logger.setLevel(_DETAIL_LOG_LEVEL)
detail_logger.addHandler(detail_handler)

# Set up summary logger
summary_logger = logging.getLogger('py4...S')
summary_handler = logging.StreamHandler()
summary_handler.setFormatter(logging.Formatter('[%(levelname)s] %(name)s: %(message)s'))
summary_logger.setLevel(_SUMMARY_LOG_LEVEL)
summary_logger.addHandler(summary_handler)

_summary_logger_enable = (os.environ.get('PY4CYTOSCAPE_SUMMARY_LOGGER', 'FALSE').upper() == 'TRUE')
def set_summary_logger(enable):
    global _summary_logger_enable
    orig_enable = _summary_logger_enable
    _summary_logger_enable = enable
    return orig_enable

_NESTING_SPACER = '\u01c0' # Use latin dental click character to represent spacing = nesting
_FUNCTION_SPACER = '-' * 20

# Decorator so functions can get automatic logging
_logger_nesting = -1
_logger_nesting_spacer = ''

_SPHINX_BUILD = (os.environ.get('SPHINX_BUILD', 'FALSE').upper() == 'TRUE')
def cy_log(func):
    """Log function call parameters and results"""

    def log_incoming(func, *args, **kwargs):
        global _logger_nesting
        global _logger_nesting_spacer
        global _summary_logger_enable

        _logger_nesting += 1
        _logger_nesting_spacer = _NESTING_SPACER * _logger_nesting

        if detail_logger.isEnabledFor(logging.DEBUG):
            # Show function name and all positional and named arguments
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            detail_logger.debug(f"{_logger_nesting_spacer}Calling {func.__name__}({signature})")

        if _summary_logger_enable:
            summary_logger.debug(f"{_logger_nesting_spacer}Into {func.__name__}()")

    def log_return(func, value):
        global _logger_nesting
        global _logger_nesting_spacer
        global _summary_logger_enable

        if _summary_logger_enable:
            summary_logger.debug(f"{_logger_nesting_spacer}Out of {func.__name__!r}")
        if detail_logger.isEnabledFor(logging.DEBUG): detail_logger.debug(
            f"{_logger_nesting_spacer}Returning {func.__name__!r}: {value!r}")
        return value

    def log_exception(func, e):
        global _logger_nesting
        global _logger_nesting_spacer
        global _summary_logger_enable

        if _summary_logger_enable:
            summary_logger.debug(f"{_logger_nesting_spacer}Exception from {func.__name__!r}")
        if detail_logger.isEnabledFor(logging.DEBUG): detail_logger.debug(
            f"{_logger_nesting_spacer}{func.__name__!r} exception {e!r}")
        raise

    def log_finally():
        global _logger_nesting
        global _logger_nesting_spacer
        global _summary_logger_enable

        _logger_nesting -= 1
        _logger_nesting_spacer = _NESTING_SPACER * _logger_nesting
        if _logger_nesting == -1:
            if detail_logger.isEnabledFor(logging.DEBUG): detail_logger.debug(_FUNCTION_SPACER)
            if _summary_logger_enable: summary_logger.debug(_FUNCTION_SPACER)

    @functools.wraps(func)
    def wrapper_log(*args, **kwargs):
        log_incoming(func, *args, **kwargs)
        try:
            value = func(*args, **kwargs) # Call function being logged
            return log_return(func, value)
        except Exception as e:
            log_exception(func, e)
        finally:
            log_finally()

    return func if _SPHINX_BUILD else wrapper_log

# HTTP loggers that take advantage of logging setup
def log_http_request(method, url, **kwargs):
    if (_DETAIL_ENABLE_HTTP_CALLS and detail_logger.isEnabledFor(logging.DEBUG)) or \
        (_SUMMARY_ENABLE_HTTP_CALLS and summary_logger.isEnabledFor(logging.DEBUG)):
        if url is None: url=''
        params = kwargs.get('params')
        params = '' if params is None else ', params: ' + str(params)
        json = kwargs.get('json')
        json = '' if json is None else ', json: ' + str(json)
        data = kwargs.get('data')
        data = '' if data is None else ', data: ' + str(data)

        if _DETAIL_ENABLE_HTTP_CALLS and detail_logger.isEnabledFor(logging.DEBUG):
            detail_logger.debug(_logger_nesting_spacer + 'HTTP ' + method + '(' + url + ')' + params + json + data)
        if _SUMMARY_ENABLE_HTTP_CALLS and summary_logger.isEnabledFor(logging.INFO) and _summary_logger_enable:
            summary_logger.info(' ' + _logger_nesting_spacer + 'HTTP ' + method + '(' + url + ')' + params + json + data)

def log_http_result(r):
    if (_DETAIL_ENABLE_HTTP_CALLS and detail_logger.isEnabledFor(logging.DEBUG)) or \
        (_SUMMARY_ENABLE_HTTP_CALLS and summary_logger.isEnabledFor(logging.DEBUG)):
        if _DETAIL_ENABLE_HTTP_CALLS and detail_logger.isEnabledFor(logging.DEBUG):
            content = ', content: ' + r.text if _DETAIL_ENABLE_HTTP_CONTENT else ''
            detail_logger.debug(_logger_nesting_spacer + r.reason + '[' + str(r.status_code) + ']' + content)
        if _SUMMARY_ENABLE_HTTP_CALLS and summary_logger.isEnabledFor(logging.INFO) and _summary_logger_enable:
            content = ', content: ' + r.text if _SUMMARY_ENABLE_HTTP_CONTENT else ''
            summary_logger.info(' ' + _logger_nesting_spacer + r.reason + '[' + str(r.status_code) + ']' + content)

def narrate(progress):
    from .py4cytoscape_notebook import get_notebook_is_running
    if get_notebook_is_running():
        print(progress)
    return progress

def show_error(error_text):
    print(error_text, file=sys.stderr)
