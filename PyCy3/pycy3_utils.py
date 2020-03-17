# -*- coding: utf-8 -*-


DEFAULT_BASE_URL: str = 'http://localhost:1234/v1'

import urllib.parse
from PyCy3 import tables
from PyCy3.decorators import debug
from .exceptions import CyError

def __init__(self):
    pass


def build_url(base_url=DEFAULT_BASE_URL, command=None):
    """ Append a command (if it exists) to a base URL """
    if command:
        return base_url + "/" + urllib.parse.quote(command)
    else:
        return base_url

def node_suid_to_node_name(node_suids, network=None, base_url=DEFAULT_BASE_URL):
    if node_suids is None: return None
    if isinstance(node_suids, str): node_suids = [node_suids]

    df = tables.get_table_columns('node', ['name'], 'default', network, base_url=base_url)
    all_names = df['name'].values

    test_present = [x in all_names for x in node_suids]
    if not False in test_present:
        return node_suids

    all_suids_list = df.index.tolist()
    try:
        # map all SUIDS into column names ... all SUIDS *must* be actual SUIDS
        node_names = [all_names[all_suids_list.index(node_suid)]    for node_suid in node_suids]
        return node_names
    except Exception as e:
        print("Invalid SUID in list: " + str(node_suids))
        raise CyError('Invalid SUID in list')

def node_name_to_node_suid(node_names, network=None, base_url=DEFAULT_BASE_URL):
    if node_names is None: return None
    if isinstance(node_names, str): node_names = [node_names]
    df = tables.get_table_columns('node', ['name'], 'default', network, base_url=base_url)

    all_suids = df.index
    test_present = [x in all_suids   for x in node_names]
    if not False in test_present:
        return node_names

    # map all node names into SUIDs ... all names *must* be actual names ... for names mapping to multiple SUIDs, return a SUID list
    node_suids = [list(df[df.name.eq(node_name)].index.values)   for node_name in node_names]
    if True in [True if len(x) == 0 else False   for x in node_suids]:
        print("Invalid name in list: " + str(node_names))
        raise CyError('Invalid name in list')
    node_suids = [x[0] if len(x) == 1 else x    for x in node_suids]

    return node_suids

def edge_name_to_edge_suid(edge_names, network=None, base_url=DEFAULT_BASE_URL):
    if edge_names is None: return None
    if isinstance(edge_names, str): edge_names = [edge_names]
    df = tables.get_table_columns('edge', ['name'], 'default', network, base_url=base_url)

    all_suids = df.index
    test_present = [x in all_suids   for x in edge_names]
    if not False in test_present:
        return edge_names

    # map all edge names into SUIDs ... all names *must* be actual names ... for names mapping to multiple SUIDs, return a SUID list
    edge_suids = [list(df[df.name.eq(edge_name)].index.values)    for edge_name in edge_names]
    if True in [True if len(x) == 0 else False   for x in edge_suids]:
        print("Invalid name in list: " + str(edge_names))
        raise CyError('Invalid name in list')
    edge_suids = [x[0] if len(x) == 1 else x    for x in edge_suids]

    return edge_suids

def edge_suid_to_edge_name(edge_suids, network=None, base_url=DEFAULT_BASE_URL):
    if edge_suids is None: return None
    if isinstance(edge_suids, str): edge_suids = [edge_suids]

    df = tables.get_table_columns('edge', ['name'], 'default', network, base_url=base_url)
    all_names = df['name'].values

    test = [edge_suid in all_names    for edge_suid in edge_suids]
    if not False in test: return edge_suids # the list already had valid names

    all_suids_list = df.index.tolist()
    try:
        # map all SUIDS into column names ... all SUIDS *must* be actual SUIDS
        edge_names = [all_names[all_suids_list.index(edge_suid)]    for edge_suid in edge_suids]
        return edge_names
    except Exception as e:
        print("Invalid SUID in list: " + str(edge_suids))
        raise CyError('Invalid SUID in list')

