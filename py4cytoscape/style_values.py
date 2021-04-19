# -*- coding: utf-8 -*-

"""Functions for retrieving current values for visual properties.

I. General functions for getting node, edge and network properties
II. Specific functions for getting particular node, edge and network properties
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
        nodes_names (str or list or int or None): List of nodes or None. If node list:
            ``list`` of node names or SUIDs, comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``node table``. If list is None,
            default is all nodes.
        visual_property (str): Name of a visual property. See ``get_visual_property_names``
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: as a collection of {node-name: prop_value} for each node in node_names parameter

    Raises:
        CyError: if network name, node name or property name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_node_property(visual_property='NODE_LABEL')
        {'YIL070C': 'MAM33', 'YHR198C': 'YHR198C', ...}
        >>> get_node_property(visual_property='NODE_LABEL', node_names=['YIL070C', 'YHR198C'])
        {'YIL070C': 'MAM33', 'YHR198C': 'YHR198C'}
        >>> get_node_property(visual_property='NODE_LABEL', node_names='YIL070C, YHR198C')
        {'YIL070C': 'MAM33', 'YHR198C': 'YHR198C'}
        >>> get_node_property(visual_property='NODE_LABEL', node_names=[391173, 391172, 391175])
        {391173: 'RPL11B', 391172: 'SXM1', 391175: 'MPT1'}
        >>> get_node_property(visual_property='NODE_LABEL', node_names='391173, 391172, 391175')
        {391173: 'RPL11B', 391172: 'SXM1', 391175: 'MPT1'}
        >>> get_node_property(visual_property='NODE_LABEL', node_names='YER112W', network='galFiltered.sif')
        {'YER112W': 'LSM4'}
        >>> get_node_property(visual_property='NODE_LABEL', node_names=391173, network='galFiltered.sif')
        {391173: 'RPL11B'}
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    view_suid = network_views.get_network_views(net_suid, base_url=base_url)[0]

    if visual_property is None:
        raise CyError('Invalid visual property ... visual property must be non-null')

    if node_names is None:
        res = commands.cyrest_get('networks/' + str(net_suid) + '/views/' + str(view_suid) + '/nodes',
                                  {'visualProperty': visual_property}, base_url=base_url)
        node_suids = [node['SUID'] for node in res]
        node_names = node_suid_to_node_name(node_suids, network=network, base_url=base_url)
        node_props = {name: node['view'][0]['value'] for node, name in zip(res, node_names)}
        return node_props
    else:
        node_names = normalize_list(node_names)
        node_suids = node_name_to_node_suid(node_names, network=network, base_url=base_url, unique_list=True)
        node_props = {node_name: commands.cyrest_get(
            f'networks/{net_suid}/views/{view_suid}/nodes/{node_suid}/{visual_property}', base_url=base_url)['value']
                      for node_suid, node_name in zip(node_suids, node_names)}
        return node_props


@cy_log
def get_edge_property(edge_names=None, visual_property=None, network=None, base_url=DEFAULT_BASE_URL):
    """Get values for any edge property of the specified edges.

    This method retrieves the actual property of the node, given the current visual style, factoring together
    any default, mapping and bypass setting.

    Args:
        edge_names (str or list or int or None): List of edges or None. If node list:
            ``list`` of edge names or SUIDs, comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID. Edge names should be found in the ``name`` column of the ``edge table``. If list is None,
            default is all edges.
        visual_property (str): Name of a visual property. See ``get_visual_property_names``
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: as a collection of {edge-name: prop_value} for each edge in edge_names parameter

    Raises:
        CyError: if network name, edge name or property name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_edge_property(visual_property='EDGE_LABEL')
        {'YJR022W (pp) YNL050C': 'pp', 'YKR026C (pp) YGL122C': 'pp', ...}
        >>> get_edge_property(visual_property='EDGE_LABEL', edge_names=['YCL067C (pd) YIL015W', 'YCR084C (pp) YCL067C'])
        {'YCL067C (pd) YIL015W': 'pd', 'YCR084C (pp) YCL067C': 'pp'}
        >>> get_edge_property(visual_property='EDGE_LABEL', edge_names='YCL067C (pd) YIL015W, YCR084C (pp) YCL067C')
        {'YCL067C (pd) YIL015W': 'pd', 'YCR084C (pp) YCL067C': 'pp'}
        >>> get_edge_property(visual_property='EDGE_LABEL', edge_names=[393222, 393223])
        {393222: 'pd', 393223: 'pp'}
        >>> get_edge_property(visual_property='EDGE_LABEL', edge_names='393222, 393223')
        {393222: 'pd', 393223: 'pp'}
        >>> get_edge_property(visual_property='EDGE_LABEL', edge_names=393222)
        {393222: 'pd'}
        >>> get_edge_property(visual_property='EDGE_LABEL', edge_names='YDR277C (pp) YJR022W', network='galFiltered.sif')
        {'YDR277C (pp) YJR022W': 'pp'}
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    view_suid = network_views.get_network_views(net_suid, base_url=base_url)[0]

    if visual_property is None:
        raise CyError('Invalid visual property ... visual property must be non-null')

    if edge_names is None:
        res = commands.cyrest_get(f'networks/{net_suid}/views/{view_suid}/edges',
                                  {'visualProperty': visual_property}, base_url=base_url)
        edge_suids = [edge['SUID'] for edge in res]
        edge_names = edge_suid_to_edge_name(edge_suids, network=network, base_url=base_url)
        edge_props = {name: edge['view'][0]['value'] for edge, name in zip(res, edge_names)}
        return edge_props
    else:
        edge_names = normalize_list(edge_names)
        edge_suids = edge_name_to_edge_suid(edge_names, network=network, base_url=base_url, unique_list=True)
        edge_props = {edge_name: commands.cyrest_get(
            f'networks/{net_suid}/views/{view_suid}/edges/{edge_suid}/{visual_property}', base_url=base_url)['value']
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
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        float: value of visual property

    Raises:
        CyError: if network name or property name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_network_property('NETWORK_SCALE_FACTOR')
        0.6299925248514752
        >>> get_network_property(visual_property='NETWORK_SCALE_FACTOR', network='galFiltered.sif')
        0.6299925248514752
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    view_suid = network_views.get_network_views(net_suid, base_url=base_url)[0]

    if visual_property is None:
        raise CyError('Invalid visual property ... visual property must be non-null')

    res = commands.cyrest_get(f'networks/{net_suid}/views/{view_suid}/network/{visual_property}', base_url=base_url)
    return res['value']


# ==============================================================================
# II. Specific Functions
# ==============================================================================
# II.a. Node Properties
# Pattern: call getNodeProperty()
# ------------------------------------------------------------------------------

@cy_log
def get_node_color(node_names=None, network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the actual fill color of specified nodes.

    Args:
        nodes_names (str or list or int or None): List of nodes or None. If node list:
            ``list`` of node names or SUIDs, comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``node table``. If list is None,
            default is all nodes.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: as a collection of {node-name: fill-color} for each node in node_names parameter

    Raises:
        CyError: if network name or node doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_node_color()
        {'YOR215C': '#FFFFEC', 'YBL026W': '#FCFDFE', 'YOL149W': '#FFFFE3', ...}
        >>> get_node_color(['YOR215C', 'YBL026W', 'YOL149W'])
        {'YOR215C': '#FFFFEC', 'YBL026W': '#FCFDFE', 'YOL149W': '#FFFFE3'}
        >>> get_node_color('YOR215C, YBL026W, YOL149W')
        {'YOR215C': '#FFFFEC', 'YBL026W': '#FCFDFE', 'YOL149W': '#FFFFE3'}
        >>> get_node_color([395406, 395407, 395404])
        {395406: '#FFFFEC', 395407: '#FCFDFE', 395404: '#FFFFE3'}
        >>> get_node_color('395406, 395407, 395404')
        {395406: '#FFFFEC', 395407: '#FCFDFE', 395404: '#FFFFE3'}
        >>> get_node_color(395406)
        {395406: '#FFFFEC'}
        >>> get_node_color(node_names='YOR215C', network='galFiltered.sif')
        {'YYOR215C': '#FFFFEC'}
    """
    res = get_node_property(node_names, "NODE_FILL_COLOR", network=network, base_url=base_url)
    return res


@cy_log
def get_node_size(node_names=None, network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the actual size of specified nodes.

    Args:
        nodes_names (str or list or int or None): List of nodes or None. If node list:
            ``list`` of node names or SUIDs, comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``node table``. If list is None,
            default is all nodes.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: as a collection of {node-name: size} for each node in node_names parameter

    Raises:
        CyError: if network name or node doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_node_size()
        {'YOR215C': 50.0, 'YBL026W': 50.0, 'YOL149W': 50.0, ...}
        >>> get_node_size(['YOR215C', 'YBL026W', 'YOL149W'])
        {'YOR215C': 50.0, 'YBL026W': 50.0, 'YOL149W': 50.0}
        >>> get_node_size('YOR215C, YBL026W, YOL149W')
        {'YOR215C': 50.0, 'YBL026W': 50.0, 'YOL149W': 50.0}
        >>> get_node_size([395406, 395407, 395404])
        {395406: 50.0, 395407: 50.0, 395404: 50.0}
        >>> get_node_size('395406, 395407, 395404')
        {395406: 50.0, 395407: 50.0, 395404: 50.0}
        >>> get_node_size(395406)
        {395406: 50.0}
        >>> get_node_size(node_names='YOR215C', network='galFiltered.sif')
        {'YYOR215C': 50.0}
    """
    res = get_node_property(node_names, "NODE_SIZE", network=network, base_url=base_url)
    return res


@cy_log
def get_node_width(node_names=None, network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the actual width of specified nodes.

    Args:
        nodes_names (str or list or int or None): List of nodes or None. If node list:
            ``list`` of node names or SUIDs, comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``node table``. If list is None,
            default is all nodes.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: as a collection of {node-name: width} for each node in node_names parameter

    Raises:
        CyError: if network name or node doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_node_width()
        {'YOR215C': 50.0, 'YBL026W': 50.0, 'YOL149W': 50.0, ...}
        >>> get_node_width(['YOR215C', 'YBL026W', 'YOL149W'])
        {'YOR215C': 50.0, 'YBL026W': 50.0, 'YOL149W': 50.0}
        >>> get_node_width('YOR215C, YBL026W, YOL149W')
        {'YOR215C': 50.0, 'YBL026W': 50.0, 'YOL149W': 50.0}
        >>> get_node_width([395406, 395407, 395404])
        {395406: 50.0, 395407: 50.0, 395404: 50.0}
        >>> get_node_width('395406, 395407, 395404')
        {395406: 50.0, 395407: 50.0, 395404: 50.0}
        >>> get_node_width(395406)
        {395406: 50.0}
        >>> get_node_width(node_names='YOR215C', network='galFiltered.sif')
        {'YYOR215C': 46.470588235294116}
    """
    res = get_node_property(node_names, "NODE_WIDTH", network=network, base_url=base_url)
    return res


@cy_log
def get_node_height(node_names=None, network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the actual height of specified nodes.

    Args:
        nodes_names (str or list or int or None): List of nodes or None. If node list:
            ``list`` of node names or SUIDs, comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``node table``. If list is None,
            default is all nodes.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: as a collection of {node-name: height} for each node in node_names parameter

    Raises:
        CyError: if network name or node doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_node_height()
        {'YOR215C': 50.0, 'YBL026W': 50.0, 'YOL149W': 50.0, ...}
        >>> get_node_height(['YOR215C', 'YBL026W', 'YOL149W'])
        {'YOR215C': 50.0, 'YBL026W': 50.0, 'YOL149W': 50.0}
        >>> get_node_height('YOR215C, YBL026W, YOL149W')
        {'YOR215C': 50.0, 'YBL026W': 50.0, 'YOL149W': 50.0}
        >>> get_node_height([395406, 395407, 395404])
        {395406: 50.0, 395407: 50.0, 395404: 50.0}
        >>> get_node_height('395406, 395407, 395404')
        {395406: 50.0, 395407: 50.0, 395404: 50.0}
        >>> get_node_height(395406)
        {395406: 50.0}
        >>> get_node_height(node_names='YOR215C', network='galFiltered.sif')
        {'YYOR215C': 46.470588235294116}
    """
    res = get_node_property(node_names, "NODE_HEIGHT", network=network, base_url=base_url)
    return res


@cy_log
def get_node_position(node_names=None, network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the actual x,y position of specified nodes.

    Args:
        nodes_names (str or list or int or None): List of nodes or None. If node list:
            ``list`` of node names or SUIDs, comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``node table``. If list is None,
            default is all nodes.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dataframe: with index as node_names values and columns x and y containing coordinates

    Raises:
        CyError: if network name or node doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_node_position()
                        x                    y
        YIL052C 2628.866343678256  1180.9601936051579
        YDL215C 1723.7108261001308 2230.935871095392
        YLR432W 1660.9524948013027 2387.6488532731264
        ...
        >>> get_node_position(['YDR429C', 'YMR005W', 'YDR142C'])
                        x                    y
        YDR429C 2628.866343678256  1180.9601936051579
        YMR005W 1723.7108261001308 2230.935871095392
        YDR142C 1660.9524948013027 2387.6488532731264
        >>> get_node_position([432646, 432647, 432644])
                        x                    y
        432646  2628.866343678256  1180.9601936051579
        432647  1723.7108261001308 2230.935871095392
        432644  1660.9524948013027 2387.6488532731264
        >>> get_node_position(node_names='YER112W', network='galFiltered.sif')
                        x                    y
        YER112W  2151.8481399429043 2326.677814454767
    """
    x_location = get_node_property(node_names, "NODE_X_LOCATION", network=network, base_url=base_url)
    x_values = [x_location[node_name] for node_name in x_location]
    x_names = [node_name for node_name in x_location]

    y_location = get_node_property(node_names, "NODE_Y_LOCATION", network=network, base_url=base_url)
    y_values = [y_location[node_name] for node_name in y_location]
    y_names = [node_name for node_name in y_location]

    # Verify that both property calls return locations for the same set of nodes ... necessary because
    # two calls are not atomic. (This stands virtually no chance of failing, but non-atomic call must be checked.)
    name_skew = [[x_name, y_name] for x_name, y_name in zip(x_names, y_names) if x_name != y_name]
    if name_skew != []:
        raise CyError(f'Inconsistent node sets returned: "{name_skew}"')

    data = df.DataFrame(index=y_names, data={'x': x_values, 'y': y_values})
    # TODO: Verify that this is what R returns, too

    return data


# ==============================================================================
# II.b. Edge Properties
# Pattern: call getEdgeProperty()
# ------------------------------------------------------------------------------

@cy_log
def get_edge_line_width(edge_names=None, network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the actual line width of specified edge.

    Args:
        edge_names (str or list or int or None): List of edges or None. If edge list:
            ``list`` of edge names or SUIDs, comma-separated string of edge names or SUIDs, or scalar node edge
            or SUID. Edge names should be found in the ``name`` column of the ``edge table``. If list is None,
            default is all edges.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: as a collection of {edge-name: width} for each edge in edge_names parameter

    Raises:
        CyError: if network name or node doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_edge_line_width()
        {'YLR197W (pp) YOR310C': 2.0, 'YIL074C (pp) YNL311C': 2.0, ...}
        >>> get_edge_line_width(['YHR084W (pd) YFL026W', 'YHR084W (pd) YDR461W', 'YMR255W (pp) YGL122C'])
        {'YHR084W (pd) YFL026W': 2.0, 'YHR084W (pd) YDR461W': 2.0, 'YMR255W (pp) YGL122C': 2.0}
        >>> get_edge_line_width('YHR084W (pd) YFL026W, YHR084W (pd) YDR461W, YMR255W (pp) YGL122C')
        {'YHR084W (pd) YFL026W': 2.0, 'YHR084W (pd) YDR461W': 2.0, 'YMR255W (pp) YGL122C': 2.0}
        >>> get_edge_line_width([421382, 421383, 421380])
        {421382: 2.0, 421383: 2.0, 421380: 2.0}
        >>> get_edge_line_width('421382, 421383, 421380')
        {421382: 2.0, 421383: 2.0, 421380: 2.0}
        >>> get_edge_line_width(421382)
        {421382: 2.0}
        >>> get_edge_line_width(edge_names='YOR355W (pp) YNL091W', network='galFiltered.sif')
        {'YOR355W (pp) YNL091W': 2.0}
    """
    res = get_edge_property(edge_names, "EDGE_WIDTH", network=network, base_url=base_url)
    return res


@cy_log
def get_edge_color(edge_names=None, network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the actual line color of specified edges.

    Args:
        edge_names (str or list or int or None): List of edges or None. If edge list:
            ``list`` of edge names or SUIDs, comma-separated string of edge names or SUIDs, or scalar node edge
            or SUID. Edge names should be found in the ``name`` column of the ``edge table``. If list is None,
            default is all edges.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: as a collection of {edge-name: line-color} for each edge in edge_names parameter

    Raises:
        CyError: if network name or edge doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_edge_color()
        {'YMR117C (pp) YCL032W': '#808080', 'YMR255W (pp) YGL122C': '#808080', 'YNL214W (pp) YGL153W': '#808080', ...}
        >>> get_edge_color(['YHR084W (pd) YFL026W', 'YHR084W (pd) YDR461W', 'YMR255W (pp) YGL122C'])
        {'YHR084W (pd) YFL026W': '#808080', 'YHR084W (pd) YDR461W': '#808080', 'YMR255W (pp) YGL122C': '#808080'}
        >>> get_edge_color('YHR084W (pd) YFL026W, YHR084W (pd) YDR461W, YMR255W (pp) YGL122C')
        {'YHR084W (pd) YFL026W': '#808080', 'YHR084W (pd) YDR461W': '#808080', 'YMR255W (pp) YGL122C': '#808080'}
        >>> get_edge_color([421382, 421383, 421380])
        {421382: '#808080', 421383: '#808080', 421380: '#808080'}
        >>> get_edge_color('421382, 421383, 421380')
        {421382: '#808080', 421383: '#808080', 421380: '#808080'}
        >>> get_edge_color(421382)
        {421382: '#808080'}
        >>> get_edge_color(edge_names='YOR355W (pp) YNL091W', network='galFiltered.sif')
        {'YOR355W (pp) YNL091W': '#808080'}
    """
    res = get_edge_property(edge_names, "EDGE_PAINT", network=network, base_url=base_url)
    return res


@cy_log
def get_edge_line_style(edge_names=None, network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the actual line style of specified edges.

    Args:
        edge_names (str or list or int or None): List of edges or None. If edge list:
            ``list`` of edge names or SUIDs, comma-separated string of edge names or SUIDs, or scalar node edge
            or SUID. Edge names should be found in the ``name`` column of the ``edge table``. If list is None,
            default is all edges.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: as a collection of {edge-name: line-style} for each edge in edge_names parameter

    Raises:
        CyError: if network name or edge doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_edge_line_style()
        {'YMR117C (pp) YCL032W': 'SOLID', 'YMR255W (pp) YGL122C': 'SOLID', 'YNL214W (pp) YGL153W': 'SOLID', ...}
        >>> get_edge_line_style(['YHR084W (pd) YFL026W', 'YHR084W (pd) YDR461W', 'YMR255W (pp) YGL122C'])
        {'YHR084W (pd) YFL026W': 'SOLID', 'YHR084W (pd) YDR461W': 'SOLID', 'YMR255W (pp) YGL122C': 'SOLID'}
        >>> get_edge_line_style('YHR084W (pd) YFL026W, YHR084W (pd) YDR461W, YMR255W (pp) YGL122C')
        {'YHR084W (pd) YFL026W': 'SOLID', 'YHR084W (pd) YDR461W': 'SOLID', 'YMR255W (pp) YGL122C': 'SOLID'}
        >>> get_edge_line_style([421382, 421383, 421380])
        {421382: 'SOLID', 421383: 'SOLID', 421380: 'SOLID'}
        >>> get_edge_line_style('421382, 421383, 421380')
        {421382: 'SOLID', 421383: 'SOLID', 421380: 'SOLID'}
        >>> get_edge_line_style(421382)
        {421382: 'SOLID'}
        >>> get_edge_line_style(edge_names='YOR355W (pp) YNL091W', network='galFiltered.sif')
        {'YOR355W (pp) YNL091W': 'SOLID'}
    """
    res = get_edge_property(edge_names, "EDGE_LINE_TYPE", network=network, base_url=base_url)
    return res


@cy_log
def get_edge_target_arrow_shape(edge_names=None, network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the actual target arrow shape of specified edges.

    Args:
        edge_names (str or list or int or None): List of edges or None. If edge list:
            ``list`` of edge names or SUIDs, comma-separated string of edge names or SUIDs, or scalar node edge
            or SUID. Edge names should be found in the ``name`` column of the ``edge table``. If list is None,
            default is all edges.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: as a collection of {edge-name: arrow-shape} for each edge in edge_names parameter

    Raises:
        CyError: if network name or edge doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_edge_target_arrow_shape()
        {'YMR117C (pp) YCL032W': 'NONE', 'YMR255W (pp) YGL122C': 'NONE', 'YNL214W (pp) YGL153W': 'NONE', ...}
        >>> get_edge_target_arrow_shape(['YHR084W (pd) YFL026W', 'YHR084W (pd) YDR461W', 'YMR255W (pp) YGL122C'])
        {'YHR084W (pd) YFL026W': 'NONE', 'YHR084W (pd) YDR461W': 'NONE', 'YMR255W (pp) YGL122C': 'NONE'}
        >>> get_edge_target_arrow_shape('YHR084W (pd) YFL026W, YHR084W (pd) YDR461W, YMR255W (pp) YGL122C')
        {'YHR084W (pd) YFL026W': 'NONE', 'YHR084W (pd) YDR461W': 'NONE', 'YMR255W (pp) YGL122C': 'NONE'}
        >>> get_edge_target_arrow_shape([421382, 421383, 421380])
        {421382: 'NONE', 421383: 'NONE', 421380: 'NONE'}
        >>> get_edge_target_arrow_shape('421382, 421383, 421380')
        {421382: 'NONE', 421383: 'NONE', 421380: 'NONE'}
        >>> get_edge_target_arrow_shape(421382)
        {421382: 'NONE'}
        >>> get_edge_target_arrow_shape(edge_names='YOR355W (pp) YNL091W', network='galFiltered.sif')
        {'YOR355W (pp) YNL091W': 'NONE'}
    """
    res = get_edge_property(edge_names, "EDGE_TARGET_ARROW_SHAPE", network=network, base_url=base_url)
    return res


# ==============================================================================
# II.c. Network Properties
# Pattern: call getNetworkProperty()
# ------------------------------------------------------------------------------

@cy_log
def get_network_center(network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the center of specified network.

    Args:
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: as {x: x-coord, y: y-coord} for center of network

    Raises:
        CyError: if network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_network_center()
        {'x': 2628.866343678256, 'y': 1180.9601936051579}
        >>> get_network_center(network='galFiltered.sif')
        {'x': 2628.866343678256, 'y': 1180.9601936051579}
    """
    x_coordinate = get_network_property('NETWORK_CENTER_X_LOCATION', network=network, base_url=base_url)
    y_coordinate = get_network_property('NETWORK_CENTER_Y_LOCATION', network=network, base_url=base_url)

    return {'x': x_coordinate, 'y': y_coordinate}


@cy_log
def get_network_zoom(network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the scale factor of specified network.

    Args:
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        float: for zoom factor

    Raises:
        CyError: if network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_network_zoom()
        0.6299925248514752
        >>> get_network_zoom(network='galFiltered.sif')
        0.6299925248514752
    """
    res = get_network_property('NETWORK_SCALE_FACTOR', network=network, base_url=base_url)
    return res
