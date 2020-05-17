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
import pandas as df

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

@cy_log
def get_node_property(node_names=None, visual_property=None, network=None, base_url=DEFAULT_BASE_URL):
    """Get values for any node property of the specified nodes.

    Args:
        node_names (list): List of node names or node SUIDs. Default is None for all nodes.
        visual_property (str): Name of a visual property. See ``get_visual_property_names``
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: as a collection of {node-name: prop_value} for each node in node_names parameter

    Raises:
        CyError: if network name, node name or property name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_node_property(visual_property='NODE_LABEL')
        >>> {'YIL070C': 'MAM33', 'YHR198C': 'YHR198C', ...}
        >>> get_node_property(visual_property='NODE_LABEL', node_names=['YIL070C', 'YHR198C'])
        >>> {'YIL070C': 'MAM33', 'YHR198C': 'YHR198C'}
        >>> get_node_property(visual_property='NODE_LABEL', node_names=[391173, 391172, 391175])
        >>> {391173: 'RPL11B', 391172: 'SXM1', 391175: 'MPT1'}
        >>> get_node_property(visual_property='NODE_LABEL', node_names='YER112W', network='galFiltered.sif')
        >>> {'YER112W': 'LSM4'}
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    view_suid = network_views.get_network_views(net_suid, base_url=base_url)[0]

    if visual_property is None:
        raise CyError('Invalid visual property')

    if node_names is None:
        res = commands.cyrest_get('networks/' + str(net_suid) + '/views/' + str(view_suid) + '/nodes',
                                  {'visualProperty': visual_property}, base_url=base_url)
        node_suids = [node['SUID'] for node in res]
        node_names = node_suid_to_node_name(node_suids, network=network, base_url=base_url)
        node_props = {name: node['view'][0]['value'] for node, name in zip(res, node_names)}
        return node_props
    else:
        if isinstance(node_names, str): node_names = [node_names]
        # TODO: Should this be a split(',')
        node_suids = node_name_to_node_suid(node_names, network=network, base_url=base_url)
        node_props = {node_name: commands.cyrest_get(
            'networks/' + str(net_suid) + '/views/' + str(view_suid) + '/nodes/' + str(
                node_suid) + '/' + visual_property,
            base_url=base_url)['value']
                      for node_suid, node_name in zip(node_suids, node_names)}
        return node_props

@cy_log
def get_edge_property(edge_names=None, visual_property=None, network=None, base_url=DEFAULT_BASE_URL):
    """Get values for any edge property of the specified edges.

    This method retrieves the actual property of the node, given the current visual style, factoring together
    any default, mapping and bypass setting.

    Args:
        edge_names (list): List of edge names or node SUIDs. Default is None for all edges.
        visual_property (str): Name of a visual property. See ``get_visual_property_names``
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: as a collection of {edge-name: prop_value} for each edge in edge_names parameter

    Raises:
        CyError: if network name, edge name or property name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_edge_property(visual_property='EDGE_LABEL')
        >>> {'YJR022W (pp) YNL050C': 'pp', 'YKR026C (pp) YGL122C': 'pp', ...}
        >>> get_edge_property(visual_property='EDGE_LABEL', edge_names=['YCL067C (pd) YIL015W', 'YCR084C (pp) YCL067C'])
        >>> {'YCL067C (pd) YIL015W': 'pd', 'YCR084C (pp) YCL067C': 'pp'}
        >>> get_edge_property(visual_property='EDGE_LABEL', edge_names=[393222, 393223])
        >>> {393222: 'pd', 393223: 'pp'}
        >>> get_edge_property(visual_property='EDGE_LABEL', edge_names='YDR277C (pp) YJR022W', network='galFiltered.sif')
        >>> {'YDR277C (pp) YJR022W': 'pp'}
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    view_suid = network_views.get_network_views(net_suid, base_url=base_url)[0]

    if visual_property is None:
        raise CyError('Invalid visual property')

    if edge_names is None:
        res = commands.cyrest_get('networks/' + str(net_suid) + '/views/' + str(view_suid) + '/edges',
                                  {'visualProperty': visual_property}, base_url=base_url)
        edge_suids = [edge['SUID'] for edge in res]
        edge_names = edge_suid_to_edge_name(edge_suids, network=network, base_url=base_url)
        edge_props = {name: edge['view'][0]['value'] for edge, name in zip(res, edge_names)}
        return edge_props
    else:
        if isinstance(edge_names, str): edge_names = [edge_names]
        # TODO: Should this be a split(',')
        edge_suids = edge_name_to_edge_suid(edge_names, network=network, base_url=base_url)
        edge_props = {edge_name: commands.cyrest_get(
            'networks/' + str(net_suid) + '/views/' + str(view_suid) + '/edges/' + str(
                edge_suid) + '/' + visual_property,
            base_url=base_url)['value']
                      for edge_suid, edge_name in zip(edge_suids, edge_names)}
        return edge_props

@cy_log
def get_network_property(visual_property, network=None, base_url=DEFAULT_BASE_URL):
    """Get values for any network property.

    This method retrieves the actual property of the network, given the current visual style, factoring together any
    default, mapping and bypass setting.

    Args:
        visual_property (str): Name of a visual property. See ``get_visual_property_names``
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: as {property-name: property_value}

    Raises:
        CyError: if network name or property name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_network_property('NETWORK_SCALE_FACTOR')
        >>> {'NETWORK_SCALE_FACTOR': 0.6299925248514752}
        >>> get_network_property(visual_property='NETWORK_SCALE_FACTOR', network='galFiltered.sif')
        >>> {'NETWORK_SCALE_FACTOR': 0.6299925248514752}
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    view_suid = network_views.get_network_views(net_suid, base_url=base_url)[0]

    if visual_property is None:
        raise CyError('Invalid visual property')

    res = commands.cyrest_get('networks/' + str(net_suid) + '/views/' + str(view_suid) + '/network/' + visual_property, base_url=base_url)
    return res

# ==============================================================================
# II. Specific Functions
# ==============================================================================
# II.a. Node Properties
# Pattern: call getNodeProperty()
# ------------------------------------------------------------------------------

def get_node_color(node_names=None, network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the actual fill color of specified nodes.

    Args:
        node_names (list): List of node names or node SUIDs. Default is None for all nodes.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: as a collection of {node-name: fill-color} for each node in node_names parameter

    Raises:
        CyError: if network name or node doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_node_color()
        >>> {'YOR215C': '#FFFFEC', 'YBL026W': '#FCFDFE', 'YOL149W': '#FFFFE3', ...}
        >>> get_node_color(['YOR215C', 'YBL026W', 'YOL149W'])
        >>> {'YOR215C': '#FFFFEC', 'YBL026W': '#FCFDFE', 'YOL149W': '#FFFFE3'}
        >>> get_node_color([395406, 395407, 395404])
        >>> {395406: '#FFFFEC', 395407: '#FCFDFE', 395404: '#FFFFE3'}
        >>> get_node_color(node_names='YOR215C', network='galFiltered.sif')
        >>> {'YYOR215C': '#FFFFEC'}
    """
    res = get_node_property(node_names, "NODE_FILL_COLOR", network=network, base_url=base_url)
    return res

def get_node_size(node_names=None, network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the actual size of specified nodes.

    Args:
        node_names (list): List of node names or node SUIDs. Default is None for all nodes.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: as a collection of {node-name: size} for each node in node_names parameter

    Raises:
        CyError: if network name or node doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_node_size()
        >>> {'YOR215C': 50.0, 'YBL026W': 50.0, 'YOL149W': 50.0, ...}
        >>> get_node_size(['YOR215C', 'YBL026W', 'YOL149W'])
        >>> {'YOR215C': 50.0, 'YBL026W': 50.0, 'YOL149W': 50.0}
        >>> get_node_size([395406, 395407, 395404])
        >>> {395406: 50.0, 395407: 50.0, 395404: 50.0}
        >>> get_node_size(node_names='YOR215C', network='galFiltered.sif')
        >>> {'YYOR215C': 50.0}
    """
    res = get_node_property(node_names, "NODE_SIZE", network=network, base_url=base_url)
    return res

def get_node_width(node_names=None, network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the actual width of specified nodes.

    Args:
        node_names (list): List of node names or node SUIDs. Default is None for all nodes.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: as a collection of {node-name: width} for each node in node_names parameter

    Raises:
        CyError: if network name or node doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_node_width()
        >>> {'YOR215C': 50.0, 'YBL026W': 50.0, 'YOL149W': 50.0, ...}
        >>> get_node_width(['YOR215C', 'YBL026W', 'YOL149W'])
        >>> {'YOR215C': 50.0, 'YBL026W': 50.0, 'YOL149W': 50.0}
        >>> get_node_width([395406, 395407, 395404])
        >>> {395406: 50.0, 395407: 50.0, 395404: 50.0}
        >>> get_node_width(node_names='YOR215C', network='galFiltered.sif')
        >>> {'YYOR215C': 50.0}
    """
    res = get_node_property(node_names, "NODE_WIDTH", network=network, base_url=base_url)
    return res

def get_node_height(node_names=None, network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the actual height of specified nodes.

    Args:
        node_names (list): List of node names or node SUIDs. Default is None for all nodes.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: as a collection of {node-name: height} for each node in node_names parameter

    Raises:
        CyError: if network name or node doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_node_height()
        >>> {'YOR215C': 50.0, 'YBL026W': 50.0, 'YOL149W': 50.0, ...}
        >>> get_node_height(['YOR215C', 'YBL026W', 'YOL149W'])
        >>> {'YOR215C': 50.0, 'YBL026W': 50.0, 'YOL149W': 50.0}
        >>> get_node_height([395406, 395407, 395404])
        >>> {395406: 50.0, 395407: 50.0, 395404: 50.0}
        >>> get_node_height(node_names='YOR215C', network='galFiltered.sif')
        >>> {'YYOR215C': 50.0}
    """
    res = get_node_property(node_names, "NODE_HEIGHT", network=network, base_url=base_url)
    return res

def get_node_position(node_names=None, network=None, base_url=DEFAULT_BASE_URL):
    x_location = get_node_property(node_names, "NODE_X_LOCATION", network=network, base_url=base_url)
    x_values = [node['value']    for node in x_location]
    x_names = [node['name']  for node in x_location]

    y_location = get_node_property(node_names, "NODE_Y_LOCATION", network=network, base_url=base_url)
    y_values = [node['value']    for node in y_location]
    y_names = [node['name']  for node in y_location]

    data = df.DataFrame(index=y_names, data={'x': x_values, 'y': y_values})

    return data

