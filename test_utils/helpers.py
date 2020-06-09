# -*- coding: utf-8 -*-

"""Functions common to test suites.
"""

"""License:
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

from py4cytoscape import *
import os
import functools


def __init__(self):
    pass


def load_test_session(session_filename=None):
    open_session(session_filename)


def load_test_network(network_name, make_current=True):
    if make_current:
        imported = import_network_from_file(network_name)
        set_current_network(imported['networks'][0])
    else:
        try:
            cur_suid = get_network_suid()
        except:
            cur_suid = None
        imported = import_network_from_file(network_name)
        if cur_suid: set_current_network(cur_suid)
    return imported['networks'][0], imported['views'][0]


def test_select_nodes(node_list):
    if len(node_list) == 0:
        clear_selection(type='nodes')
    else:
        select_nodes(node_list, by_col='COMMON')


def clean_session_file(session_filename):
    if os.path.isfile(session_filename): os.remove(session_filename)

def skip_for_ui():
    return os.environ.get('PY4CYTOSCAPE_SKIP_UI_TESTS', 'FALSE').upper() == 'TRUE'

def show_test_progress():
    return os.environ.get('PY4CYTOSCAPE_SHOW_TEST_PROGRESS', 'TRUE').upper() == 'TRUE'


# Decorators inspired by https://realpython.com/primer-on-python-decorators/
def print_entry_exit(func):
    """Print the function signature and return value"""

    @functools.wraps(func)
    def wrapper_entry_exit(*args, **kwargs):
        if show_test_progress():
            print(f"Into {func.__name__}()")
            try:
                value = func(*args, **kwargs)
                print(f"Out of {func.__name__!r}")
                return value
            except Exception as e:
                print(f"{func.__name__!r} exception {e!r}")
                raise
        else:
            return func(*args, **kwargs)

    return wrapper_entry_exit
