# -*- coding: utf-8 -*-

"""Utility functions useful across multiple modules.
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

DEFAULT_BASE_URL: str = 'http://127.0.0.1:1234/v1'

# External library imports
import urllib.parse
import re
import sys

# Internal module imports
from . import tables
from . import cytoscape_system

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_logger import narrate

# ==============================================================================
# I. Package Utility Functions
# ------------------------------------------------------------------------------
# Supply a set of colors from Brewer palettes (without requiring rColorBrewer)
def cyPalette(name='set1'):
    PALETTES = {
        'set1': ['#E41A1C', '#377EB8', '#4DAF4A', '#984EA3', '#FF7F00', '#FFFF33', '#A65628', '#F781BF', '#999999'],
        'set2': ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854', '#FFD92F', '#E5C494', '#B3B3B3'],
        'set3': ['#8DD3C7', '#FFFFB3', '#BEBADA', '#FB8072', '#80B1D3', '#FDB462', '#B3DE69', '#FCCDE5', '#D9D9D9',
                 '#BC80BD', '#CCEBC5', '#FFED6F'],
        'reds': ['#FFF5F0', '#FEE0D2', '#FCBBA1', '#FC9272', '#FB6A4A', '#EF3B2C', '#CB181D', '#A50F15', '#67000D'],
        'rdbu': ['#67001F', '#B2182B', '#D6604D', '#F4A582', '#FDDBC7', '#F7F7F7', '#D1E5F0', '#92C5DE', '#4393C3',
                 '#2166AC', '#053061'],
        'burd': ['#053061', '#2166AC', '#4393C3', '#92C5DE', '#D1E5F0', '#F7F7F7', '#FDDBC7', '#F4A582', '#D6604D',
                 '#B2182B', '#67001F']
    }
    return PALETTES[name]

# ------------------------------------------------------------------------------
# Validate and provide user feedback when hex color codes are required input.
def verify_hex_colors(colors):
    if colors is None: return
    if not isinstance(colors, list): colors = [colors]

    for color in colors:
        if not color.startswith('#') or len(color) != 7:
            raise CyError(f'"{color}" is not a valid hexadecimal color (has to begin with # and be 7 characters long, for example: #FF00FF).', caller=sys._getframe(1).f_code.co_name)

# Validate and provide user feedback when opacity is required input.
def verify_opacities(opacities):
    if opacities is None: return
    if not isinstance(opacities, list):  opacities = [opacities]

    for opacity in opacities:
        if not (isinstance(opacity, float) or isinstance(opacity, int)) or opacity < 0 or opacity > 255:
            raise CyError(f'"{opacity}" is not a valid opacity (has to be an integer between 0 and 255).', caller=sys._getframe(1).f_code.co_name)

def verify_dimensions(dimension, sizes):
    if sizes is None: return
    if not isinstance(sizes, list): sizes = [sizes]

    for size in sizes:
        if not isinstance(size, float) and not isinstance(size, int):
            raise CyError(f'Illegal {dimension} "{size}". It needs to be a number.', caller=sys._getframe(1).f_code.co_name)

def verify_slot(slot):
    if not (isinstance(slot, float) or isinstance(slot, int)) or slot < 1 or slot > 9:
        raise CyError(f'slot must be an integer between 1 and 9', caller=sys._getframe(1).f_code.co_name)

def node_name_to_node_suid(node_names, network=None, base_url=DEFAULT_BASE_URL):
    if node_names is None: return None
    # TODO: Should this be a simple conversion, or a split(',')??
    if isinstance(node_names, str): node_names = [node_names]
    df = tables.get_table_columns('node', ['name'], 'default', network=network, base_url=base_url)

    all_suids = df.index
    test_present = [x in all_suids for x in node_names]
    if not False in test_present:
        return node_names

    # map all node names into SUIDs ... all names *must* be actual names ... for names mapping to multiple SUIDs, return a SUID list
    node_suids = [list(df[df.name.eq(node_name)].index.values) for node_name in node_names]
    if True in [True if len(x) == 0 else False for x in node_suids]:
        raise CyError(f'Invalid name in node name list: {node_names}')
    node_suids = [x[0] if len(x) == 1 else x for x in node_suids]

    return node_suids

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
        node_names = [all_names[all_suids_list.index(node_suid)] for node_suid in node_suids]
        return node_names
    except Exception as e:
        raise CyError(f'Invalid node SUID in list: {node_suids}')


def edge_name_to_edge_suid(edge_names, network=None, base_url=DEFAULT_BASE_URL):
    if edge_names is None: return None
    if isinstance(edge_names, str): edge_names = [edge_names]
    df = tables.get_table_columns('edge', ['name'], 'default', network, base_url=base_url)

    all_suids = df.index
    test_present = [x in all_suids for x in edge_names]
    if not False in test_present:
        return edge_names

    # map all edge names into SUIDs ... all names *must* be actual names ... for names mapping to multiple SUIDs, return a SUID list
    edge_suids = [list(df[df.name.eq(edge_name)].index.values) for edge_name in edge_names]
    if True in [True if len(x) == 0 else False for x in edge_suids]:
        raise CyError(f'Invalid edge name in list: {edge_names}')
    edge_suids = [x[0] if len(x) == 1 else x for x in edge_suids]

    return edge_suids


def edge_suid_to_edge_name(edge_suids, network=None, base_url=DEFAULT_BASE_URL):
    if edge_suids is None: return None
    if isinstance(edge_suids, str): edge_suids = [edge_suids]

    df = tables.get_table_columns('edge', ['name'], 'default', network, base_url=base_url)
    all_names = df['name'].values

    test = [edge_suid in all_names for edge_suid in edge_suids]
    if not False in test: return edge_suids  # the list already had valid names

    all_suids_list = df.index.tolist()
    try:
        # map all SUIDS into column names ... all SUIDS *must* be actual SUIDS
        edge_names = [all_names[all_suids_list.index(edge_suid)] for edge_suid in edge_suids]
        return edge_names
    except Exception as e:
        raise CyError(f'Invalid edge SUID in list: {edge_suids}')

# ------------------------------------------------------------------------------
# Checks to see if a particular column name exists in the specific table. Returns
# TRUE or FALSE.
# TODO: R had netowrk=network, which looks like a typo
def table_column_exists(table_column, table, network=None, base_url=DEFAULT_BASE_URL):
    if table_column not in tables.get_table_column_names(table, network=network, base_url=base_url):
        narrate('Column ' + table_column + ' does not exist in the ' + table + ' table.')
        return False
    return True

# ------------------------------------------------------------------------------
# Checks to see if min supported versions of api and cytoscape are running.
# Extracts numerics from api and major cytoscape versions before making comparison.
def verify_supported_versions(cyrest=1, cytoscape=3.6, base_url=DEFAULT_BASE_URL):
    v = cytoscape_system.cytoscape_version_info(base_url=base_url)
    v_api_str = v['apiVersion']
    v_cy_str = v['cytoscapeVersion']
    v_api_num = int(re.match('v([0-9]+)$', v_api_str).group(1))
    v_cy_num = float(re.match('([0-9]+\\.[0-9]+)\\..*$', v_cy_str).group(1))
    nogo = None

    if cyrest > v_api_num:
        nogo = 'CyREST API version %d or greater is required. You are currently working with version %d.' % (cyrest, v_api_num)

    if cytoscape > v_cy_num:
        nogo = 'Cytoscape version %0.2g or greater is required. You are currently working with version %0.2g.' % (cytoscape, v_cy_num)

    if nogo: raise CyError(f'Function not run due to unsupported version: {nogo}')

def build_url(base_url=DEFAULT_BASE_URL, command=None):
    """ Append a command (if it exists) to a base URL """
    if command is not None:
        return base_url + "/" + urllib.parse.quote(command)
    else:
        return base_url












