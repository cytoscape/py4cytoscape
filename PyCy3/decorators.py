# -*- coding: utf-8 -*-

# External library imports
import functools
import time


# Inspired by https://realpython.com/primer-on-python-decorators/

def debug(func):
    """Print the function signature and return value"""

    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]  # 1
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  # 2
        signature = ", ".join(args_repr + kwargs_repr)  # 3
        print(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"Returning {func.__name__!r}: {value!r}")  # 4
        return value

    return wrapper_debug


def print_entry_exit(func):
    """Print the function signature and return value"""

    @functools.wraps(func)
    def wrapper_entry_exit(*args, **kwargs):
        print(f"Into {func.__name__}()")
        try:
            value = func(*args, **kwargs)
            print(f"Out of {func.__name__!r}")
            return value
        except Exception as e:
            print(f"{func.__name__!r} exception {e!r}")
            raise

    return wrapper_entry_exit


def timer(func):
    """Print the runtime of the decorated function"""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()  # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()  # 2
        run_time = end_time - start_time  # 3
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value

    return wrapper_timer


def skip(func):
    """Skip execution of this function completely"""
    return
