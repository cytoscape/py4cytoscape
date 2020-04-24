# -*- coding: utf-8 -*-

import PyCy3
import os
import requests

def __init__(self):
    pass

def load_test_session(session_filename=None):
    PyCy3.open_session(session_filename)


def load_test_network(network_name, make_current=True):
    if make_current:
        imported = PyCy3.import_network_from_file(network_name)
        PyCy3.set_current_network(imported['networks'][0])
    else:
        try:
            cur_suid = PyCy3.get_network_suid()
        except:
            cur_suid = None
        imported = PyCy3.import_network_from_file(network_name)
        if cur_suid: PyCy3.set_current_network(cur_suid)
    return imported['networks'][0], imported['views'][0]

def test_select_nodes(node_list):
    if len(node_list) == 0:
        PyCy3.clear_selection(type='nodes')
    else:
        PyCy3.select_nodes(node_list, by_col='COMMON')

def clean_session_file(session_filename):
    if os.path.isfile(session_filename): os.remove(session_filename)
