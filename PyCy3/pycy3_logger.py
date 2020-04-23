# -*- coding: utf-8 -*-

import logging
import logging.config
import functools
import os

from . import pycy3_logger_settings

_log_base = os.path.join(pycy3_logger_settings._FILE_LOG_DIR, pycy3_logger_settings._FILE_LOG_NAME)
if not os.path.exists(pycy3_logger_settings._FILE_LOG_DIR): os.makedirs(pycy3_logger_settings._FILE_LOG_DIR)

# Define the loggers for this library
_logging_config = {
    'version': 1,
    'disable_existing_loggers': pycy3_logger_settings._DISABLE_DEBUG_HTTP,
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
            'level': pycy3_logger_settings._FILE_LOG_LEVEL,
            'formatter': 'standard',
            'filename': _log_base,
            'encoding': 'utf8',
            'backupCount': 10,
            'maxBytes': 1048576, # 1MB
            'delay': True
        },
        'console_handler': {
            'class': 'logging.StreamHandler',
            'level': pycy3_logger_settings._CONSOLE_LOG_LEVEL,
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
_logger_debug = 'DEBUG' in [pycy3_logger_settings._FILE_LOG_LEVEL, pycy3_logger_settings._CONSOLE_LOG_LEVEL]

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