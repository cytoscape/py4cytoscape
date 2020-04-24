# -*- coding: utf-8 -*-

"""Centralized logging definitions.

Any module needing logging facilities can access the ``logger`` class instance by simply importing this module, then
calling ``logger.<method>``. Also the ``@cy_log`` decorator can be used before any function to cause logging of
inbound parameters and outbound return/exception values.

License:
    Copyright 2020 The Cytoscape Consortium

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
    documentation files (the "Software"), to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
    and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions
    of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
    WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
    OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
    OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


# External library imports
import logging
import logging.config
import functools
import os

from .pycy3_logger_settings import _FILE_LOG_DIR, _FILE_LOG_LEVEL, _FILE_LOG_NAME, _DISABLE_DEBUG_HTTP, \
    _CONSOLE_LOG_LEVEL

_log_base = os.path.join(_FILE_LOG_DIR, _FILE_LOG_NAME)
if not os.path.exists(_FILE_LOG_DIR): os.makedirs(_FILE_LOG_DIR)

# Define the loggers for this library
_logging_config = {
    'version': 1,
    'disable_existing_loggers': _DISABLE_DEBUG_HTTP,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'console': {
            'format': '[%(levelname)s] %(name)s: %(message)s',
        },
    },
    'handlers': {
        'default_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': _FILE_LOG_LEVEL,
            'formatter': 'standard',
            'filename': _log_base,
            'encoding': 'utf8',
            'backupCount': 10,
            'maxBytes': 1048576,  # 1MB
            'delay': True
        },
        'console_handler': {
            'class': 'logging.StreamHandler',
            'level': _CONSOLE_LOG_LEVEL,
            'formatter': 'console',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default_handler', 'console_handler'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

# Register the loggers with the logging system
logging.config.dictConfig(_logging_config)

# Create the logger this library will use
logger = logging.getLogger('PyCy3')
_logger_debug = 'DEBUG' in [_FILE_LOG_LEVEL, _CONSOLE_LOG_LEVEL]


# Decorator so functions can get automatic logging

# TODO: Consider indenting entries to indicate nesting
def cy_log(func):
    """Log function call parameters and results"""

    @functools.wraps(func)
    def wrapper_log(*args, **kwargs):
        if _logger_debug:
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            logger.debug(f"Calling {func.__name__}({signature})")
        logger.info(f"Into {func.__name__}()")
        try:
            value = func(*args, **kwargs)
            logger.info(f"Out of {func.__name__!r}")
            if _logger_debug: logger.debug(f"Returning {func.__name__!r}: {value!r}")
            return value
        except Exception as e:
            logger.info(f"Exception from {func.__name__!r}")
            if _logger_debug: logger.debug(f"{func.__name__!r} exception {e!r}")
            raise

    return wrapper_log
