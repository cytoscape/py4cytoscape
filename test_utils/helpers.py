# -*- coding: utf-8 -*-

from PyCy3 import *

def __init__(self):
    pass

def load_test_session(session_filename=None):
    open_session(session_filename)


def load_test_network(network_name, make_current=True):
    if make_current:
        new_suid = import_network_from_file(network_name)
        set_current_network(new_suid)
    else:
        try:
            cur_suid = get_network_suid()
        except:
            cur_suid = None
        import_network_from_file(network_name)
        if cur_suid: set_current_network(cur_suid)

def test_select_nodes(node_list):
    if len(node_list) == 0:
        clear_selection(type='nodes')
    else:
        select_nodes(node_list, by_col='COMMON')

def clean_session_file(session_filename):
    if os.path.isfile(session_filename): os.remove(session_filename)
