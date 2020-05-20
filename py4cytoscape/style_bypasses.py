# -*- coding: utf-8 -*-

"""Functions for getting and setting BYPASS values for visual properties, organized into sections:

I. General functions for setting/clearing node, edge and network properties
II. Specific functions for setting particular node, edge and network properties

NOTE: The CyREST 'bypass' endpoint is essential to properly set values that
will persist for a given network independent of applied style and style
changes, and from session to session if saved.

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
import time
import re
import json

# Internal module imports
from . import commands
from . import networks
from . import network_views

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log
from .py4cytoscape_tuning import MODEL_PROPAGATION_SECS


# ==============================================================================
# I. General Functions
# ==============================================================================
# I.a. Node Properties
# ------------------------------------------------------------------------------

def set_node_property_bypass(node_names, new_values, visual_property, bypass=True, network=None,
                             base_url=DEFAULT_BASE_URL):
    """Set Node Property Bypass.

    Set bypass values for any node property of the specified nodes, overriding default values and mappings defined by
    any visual style.

    This method permanently overrides any default values or mappings defined for the visual properties of the node
    or nodes specified. To restore defaults and mappings, use ``clear_node_property_bypass()``.

    Args:
        node_names (list): List of node names
        new_values (list): List of values to set, or single value
        visual_property (str): Name of a visual property. See ``get_visual_property_names``.
        bypass (bool): Whether to set permanent bypass value. Default is True
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if node, visual property or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> node_names = list(get_table_columns(columns='name')['name'])
        >>> set_node_property_bypass(node_names, '#FF00FF', 'NODE_FILL_COLOR')
        >>> ''
        >>> node_suids = list(get_table_columns(columns='name').index)
        >>> set_node_property_bypass(node_suids, ['#FF00FF'], 'NODE_FILL_COLOR', network='galFiltered.sif')
        >>> ''

    See Also:
        :meth:`clear_node_property_bypass`
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    view_suid = network_views.get_network_views(net_suid, base_url=base_url)[0]
    node_suids = node_name_to_node_suid(node_names, network=network, base_url=base_url)

    # TODO: Shouldn't we allow node_names=None to mean all nodes? ... as is, this causes an error below and is inconsistent with other functions
    # TODO: Find out how to test for bypass=True effects

    # there can be more than one node.SUID per node.name!
    # 'node.SUIDs' and 'new.values' must have the same length
    # TODO: Should we allow a scalar for a new_value, or do we assume a list?
    if not isinstance(new_values, list): new_values = [new_values]
    if len(new_values) == 1: new_values = new_values * len(node_suids)

    if visual_property is None: # TODO: Added this ... but what about an invalid property?
        raise CyError('Invalid visual property')

    if len(new_values) != len(node_suids):
        error = 'ERROR in set_node_property_bypass():\n   the number of nodes ' + str(
            len(node_suids)) + ' and new values ' + str(len(
            new_values)) + ' are not the same >> node(s) attribute couldn\'t be set. Note that having multiple nodes with the same name in the network can cause this error. Use node SUIDs or pass in duplicated names on their own.'
        sys.stderr.write(error)
        return None  # TODO: Is this what we want to return here?

    body_list = [{'SUID': str(suid), 'view': [{'visualProperty': visual_property, 'value': val}]}   for suid, val in zip(node_suids, new_values)]

    res = commands.cyrest_put('networks/' + str(net_suid) + '/views/' + str(view_suid) + '/nodes',
                              parameters={'bypass': bypass}, body=body_list, base_url=base_url, require_json=False)
    return res

def clear_node_property_bypass(node_names, visual_property, network=None, base_url=DEFAULT_BASE_URL):
    """Clear Node Property Bypass.

    Clear bypass values for any node property of the specified nodes, effectively restoring any previously defined
    style defaults or mappings.

    Args:
        node_names (list): List of node names
        visual_property (str): Name of a visual property. See ``get_visual_property_names``.
        bypass (bool): Whether to set permanent bypass value. Default is True
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'data': {}, 'errors': []}

    Raises:
        CyError: if node, visual property or network name doesn't exist
        TypeError: if node list is None
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> node_names = list(get_table_columns(columns='name')['name'])
        >>> clear_node_property_bypass(node_names, 'NODE_FILL_COLOR')
        >>> ''
        >>> node_suids = list(get_table_columns(columns='name').index)
        >>> clear_node_property_bypass(node_suids, 'NODE_FILL_COLOR', network='galFiltered.sif')
        >>> ''

    See Also:
        :meth:`set_node_property_bypass`
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    view_suid = network_views.get_network_views(net_suid, base_url=base_url)[0]

    if visual_property is None:  # TODO: Added this ... but what about an invalid property?
        raise CyError('Invalid visual property')

    if node_names == 'all':
        raise CyError('This is not yet supported by CyREST. Please provide a valid node list.')

    # TODO: Do we need to pass in net_suid ... other calls just let the function figure it out
    node_suids = node_name_to_node_suid(node_names, network=net_suid, base_url=base_url)

    for suid in node_suids:
        res = commands.cyrest_delete('networks/' + str(net_suid) + '/views/' + str(view_suid) + '/nodes/' + str(suid) + '/' + visual_property + '/bypass', base_url=base_url)

    return res
    # TODO: OK to miss res values during the loop?

# ==============================================================================
# I.b. Edge Properties
# ------------------------------------------------------------------------------

def set_edge_property_bypass(edge_names, new_values, visual_property, bypass=True, network=None,
                             base_url=DEFAULT_BASE_URL):
    """Set Edge Property Bypass.

    Set bypass values for any edge property of the specified nodes, overriding default values and mappings defined by
    any visual style.

    This method permanently overrides any default values or mappings defined for the visual properties of the edge
    or edges specified. To restore defaults and mappings, use ``clear_edge_property_bypass()``.

    Args:
        edge_names (list): List of edgenames
        new_values (list): List of values to set, or single value
        visual_property (str): Name of a visual property. See ``get_visual_property_names``.
        bypass (bool): Whether to set permanent bypass value. Default is True
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if edge, visual property or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> edge_names = list(get_table_columns(table='edge', columns='name')['name'])
        >>> set_edge_property_bypass(edge_names, '#FF00FF', 'EDGE_UNSELECTED_PAINT')
        >>> {'data': {}, 'errors': []}
        >>> edge_suids = list(get_table_columns(table='edge', columns='name').index)
        >>> set_edge_property_bypass(edge_suids, ['#FF00FF'], 'EDGE_UNSELECTED_PAINT', network='galFiltered.sif')
        >>> {'data': {}, 'errors': []}

    See Also:
        :meth:`clear_edge_property_bypass`
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    view_suid = network_views.get_network_views(net_suid, base_url=base_url)[0]
    edge_suids = edge_name_to_edge_suid(edge_names, network=network, base_url=base_url)

    # TODO: Shouldn't we allow node_names=None to mean all nodes? ... as is, this causes an error below and is inconsistent with other functions
    # TODO: Find out how to test for bypass=True effects

    # there can be more than one edge.SUID per edge.name!
    # 'edge.SUIDs' and 'new.values' must have the same length
    # TODO: Should we allow a scalar for a new_value, or do we assume a list?
    if not isinstance(new_values, list): new_values = [new_values]
    if len(new_values) == 1: new_values = new_values * len(edge_suids)

    if visual_property is None: # TODO: Added this ... but what about an invalid property?
        raise CyError('Invalid visual property')

    if len(new_values) != len(edge_suids):
        error = 'ERROR in set_node_property_bypass():\n   the number of nodes ' + str(
            len(edge_suids)) + ' and new values ' + str(len(
            new_values)) + ' are not the same >> node(s) attribute couldn\'t be set. Note that having multiple nodes with the same name in the network can cause this error. Use node SUIDs or pass in duplicated names on their own.'
        sys.stderr.write(error)
        return None  # TODO: Is this what we want to return here?

    body_list = [{'SUID': str(suid), 'view': [{'visualProperty': visual_property, 'value': val}]}   for suid, val in zip(edge_suids, new_values)]

    res = commands.cyrest_put('networks/' + str(net_suid) + '/views/' + str(view_suid) + '/edges',
                              parameters={'bypass': bypass}, body=body_list, base_url=base_url, require_json=False)
    return res

def clear_edge_property_bypass(edge_names, visual_property, network=None, base_url=DEFAULT_BASE_URL):
    """Clear Edge Property Bypass.

    Clear bypass values for any edge property of the specified nodes, effectively restoring any previously defined
    style defaults or mappings.

    Args:
        edge_names (list): List of edge names
        visual_property (str): Name of a visual property. See ``get_visual_property_names``.
        bypass (bool): Whether to set permanent bypass value. Default is True
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'data': {}, 'errors': []}

    Raises:
        CyError: if node, visual property or network name doesn't exist
        TypeError: if node list is None
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> edge_names = list(get_table_columns(table='edge', columns='name')['name'])
        >>> clear_edge_property_bypass(edge_names, 'EDGE_UNSELECTED_PAINT')
        >>> {'data': {}, 'errors': []}
        >>> edge_suids = list(get_table_columns(table='edge', columns='name').index)
        >>> clear_edge_property_bypass(edge_suids, 'EDGE_UNSELECTED_PAINT', network='galFiltered.sif')
        >>> {'data': {}, 'errors': []}

    See Also:
        :meth:`set_edge_property_bypass`
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    view_suid = network_views.get_network_views(net_suid, base_url=base_url)[0]

    if visual_property is None:  # TODO: Added this ... but what about an invalid property?
        raise CyError('Invalid visual property')

    if edge_names == 'all':
        raise CyError('This is not yet supported by CyREST. Please provide a valid edge list.')

    # TODO: Do we need to pass in net_suid ... other calls just let the function figure it out
    edge_suids = edge_name_to_edge_suid(edge_names, network=net_suid, base_url=base_url)

    for suid in edge_suids:
        res = commands.cyrest_delete('networks/' + str(net_suid) + '/views/' + str(view_suid) + '/edges/' + str(suid) + '/' + visual_property + '/bypass', base_url=base_url)

    return res
    # TODO: OK to miss res values during the loop?
