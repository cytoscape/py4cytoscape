# -*- coding: utf-8 -*-

"""Functions for retrieving current values for visual properties.

I. General functions for getting node, edge and network properties
II. Specific functions for getting particular node, edge and network properties

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
import sys

# Internal module imports
from . import networks
from . import network_views
from . import commands

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log


# ==============================================================================
# I. General Functions
# ------------------------------------------------------------------------------

def get_node_property(node_names=None, visual_property='', network=None, base_url=DEFAULT_BASE_URL):
    net_suid = networks.get_network_suid(network, base_url=base_url)
    view_suid = network_views.get_network_views(net_suid, base_url=base_url)[0]

    if node_names is None:
        res = commands.cyrest_get('networks/' + str(net_suid) + '/views/' + str(view_suid) + '/nodes',
                                  {'visualProperty': visual_property}, base_url=base_url)
        node_suids = [node['SUID'] for node in res]
        node_names = node_suid_to_node_name(node_suids, network=network, base_url=base_url)
        node_props = {name: node['view'][0]['value'] for node, name in zip(res, node_names)}
        return node_props
    else:
        node_suids = node_name_to_node_suid(node_names, network=network, base_url=base_url)
        node_props = {node_name: commands.cyrest_get(
            'networks/' + str(net_suid) + '/views/' + str(view_suid) + '/nodes/' + str(
                node_suid) + '/' + visual_property,
            base_url=base_url)['value']
                      for node_suid, node_name in zip(node_suids, node_names)}
        return node_props
