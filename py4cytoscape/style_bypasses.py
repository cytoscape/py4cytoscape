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
from . import style_dependencies
from . import styles

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

    if visual_property is None:  # TODO: Added this ... but what about an invalid property?
        raise CyError('Invalid visual property')

    if len(new_values) != len(node_suids):
        error = 'ERROR in set_node_property_bypass():\n   the number of nodes ' + str(
            len(node_suids)) + ' and new values ' + str(len(
            new_values)) + ' are not the same >> node(s) attribute couldn\'t be set. Note that having multiple nodes with the same name in the network can cause this error. Use node SUIDs or pass in duplicated names on their own.'
        sys.stderr.write(error)
        return None  # TODO: Is this what we want to return here?

    body_list = [{'SUID': str(suid), 'view': [{'visualProperty': visual_property, 'value': val}]} for suid, val in
                 zip(node_suids, new_values)]

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
        res = commands.cyrest_delete('networks/' + str(net_suid) + '/views/' + str(view_suid) + '/nodes/' + str(
            suid) + '/' + visual_property + '/bypass', base_url=base_url)

    return res
    # TODO: OK to miss res values during the loop?


# ==============================================================================
# I.b. Edge Properties
# ------------------------------------------------------------------------------

def set_edge_property_bypass(edge_names, new_values, visual_property, bypass=True, network=None,
                             base_url=DEFAULT_BASE_URL):
    """Set Edge Property Bypass.

    Set bypass values for any edge property of the specified edges, overriding default values and mappings defined by
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

    if visual_property is None:  # TODO: Added this ... but what about an invalid property?
        raise CyError('Invalid visual property')

    if len(new_values) != len(edge_suids):
        error = 'ERROR in set_node_property_bypass():\n   the number of nodes ' + str(
            len(edge_suids)) + ' and new values ' + str(len(
            new_values)) + ' are not the same >> node(s) attribute couldn\'t be set. Note that having multiple nodes with the same name in the network can cause this error. Use node SUIDs or pass in duplicated names on their own.'
        sys.stderr.write(error)
        return None  # TODO: Is this what we want to return here?

    body_list = [{'SUID': str(suid), 'view': [{'visualProperty': visual_property, 'value': val}]} for suid, val in
                 zip(edge_suids, new_values)]

    res = commands.cyrest_put('networks/' + str(net_suid) + '/views/' + str(view_suid) + '/edges',
                              parameters={'bypass': bypass}, body=body_list, base_url=base_url, require_json=False)
    return res


def clear_edge_property_bypass(edge_names, visual_property, network=None, base_url=DEFAULT_BASE_URL):
    """Clear Edge Property Bypass.

    Clear bypass values for any edge property of the specified edges, effectively restoring any previously defined
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
        res = commands.cyrest_delete('networks/' + str(net_suid) + '/views/' + str(view_suid) + '/edges/' + str(
            suid) + '/' + visual_property + '/bypass', base_url=base_url)

    return res
    # TODO: OK to miss res values during the loop?


def set_network_property_bypass(new_value, visual_property, bypass=True, network=None, base_url=DEFAULT_BASE_URL):
    """Set Network Property Bypass.

    Set bypass values for any network property, overriding default values defined by any visual style.

    This method permanently overrides any default values or mappings defined for the visual properties of the network
    specified. To restore defaults and mappings, use ``clear_network_property_bypass()``.

    Args:
        new_value (any): Value to set
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
        CyError: if visual property or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_network_property_bypass(0.5, 'NETWORK_SCALE_FACTOR')
        >>> ''
        >>> set_network_property_bypass(0.5, 'NETWORK_SCALE_FACTOR', network='galFiltered.sif')
        >>> ''

    See Also:
        :meth:`clear_network_property_bypass`
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    view_suid = network_views.get_network_views(net_suid, base_url=base_url)[0]

    res = commands.cyrest_put('networks/' + str(net_suid) + '/views/' + str(view_suid) + '/network',
                              parameters={'bypass': bypass},
                              body=[{'visualProperty': visual_property, 'value': new_value}], base_url=base_url,
                              require_json=False)
    return res


def clear_network_property_bypass(visual_property, network=None, base_url=DEFAULT_BASE_URL):
    """Clear Network Property Bypass.

    Clear bypass values for any network property, effectively restoring any previously defined style defaults
    or mappings.

    Args:
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
        CyError: if visual property or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> clear_network_property_bypass('NETWORK_SCALE_FACTOR')
        >>> ''
        >>> clear_network_property_bypass('NETWORK_SCALE_FACTOR', network='galFiltered.sif')
        >>> ''

    See Also:
        :meth:`set_network_property_bypass`
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    view_suid = network_views.get_network_views(net_suid, base_url=base_url)[0]

    if visual_property is None:  # TODO: Added this ... but what about an invalid property?
        raise CyError('Invalid visual property')

    res = commands.cyrest_delete(
        'networks/' + str(net_suid) + '/views/' + str(view_suid) + '/network/' + visual_property + '/bypass',
        base_url=base_url)
    return res


# ==============================================================================
# II. Specific Functions
# ------------------------------------------------------------------------------

def unhide_all(network=None, base_url=DEFAULT_BASE_URL):
    """Unhide all previously hidden nodes and edges, by clearing the Visible property bypass value.

    Args:
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> unhide_all()
        >>> ''
        >>> unhide_all(network='galFiltered.sif')
        >>> ''

    See Also:
        :meth:`clear_edge_property_bypass`, :meth:`unhide_nodes`, :meth:`unhide_edges`
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    res = None

    node_names = networks.get_all_nodes(net_suid, base_url=base_url)
    if len(node_names) > 0:
        res = set_node_property_bypass(node_names, new_values='true', visual_property='NODE_VISIBLE', network=network,
                                       base_url=base_url)

    edge_names = networks.get_all_edges(net_suid, base_url=base_url)
    if len(edge_names) > 0:
        res = set_edge_property_bypass(edge_names, new_values='true', visual_property='EDGE_VISIBLE', network=network,
                                       base_url=base_url)

    return res
    # TODO: res is ambiguous ... unclear what it really should be


# ==============================================================================
# II.a. Node Properties
# Pattern: (1) validate input value, (2) call setNodePropertyBypass()
# ------------------------------------------------------------------------------

def set_node_color_bypass(node_names, new_colors, network=None, base_url=DEFAULT_BASE_URL):
    """Set the bypass value for fill color for the specified node or nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (list): list of node names
        new_colors (str or list): list of hex colors or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: '' (None if invalid color is found in new_colors)

    Raises:
        CyError: if node or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_color_bypass(get_node_names(), '#FF00FF')
        >>> ''
        >>> set_node_color_bypass(['YDL194W', 'YBR043C'], ['#FF00FF', '#CCCCCC'], network='galFiltered.sif')
        >>> ''

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    if isinstance(new_colors, str): new_colors = [
        new_colors]  # TODO: It looks like this should be happening everywhere?
    for color in new_colors:
        if is_not_hex_color(color):
            return None  # TODO: Shouldn't this be an exception?

    res = set_node_property_bypass(node_names, new_colors, 'NODE_FILL_COLOR', network=network, base_url=base_url)
    return res


def set_node_size_bypass(node_names, new_sizes, network=None, base_url=DEFAULT_BASE_URL):
    """Set Node Size Bypass.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (list): list of node names
        new_sizes (int or float or list): list of size values or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: '' (None if invalid size is found in new_sizes)

    Raises:
        CyError: if node or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_size_bypass(get_node_names(), 50)
        >>> ''
        >>> set_node_size_bypass(['YDL194W', 'YBR043C'], [150.5, 90.5], network='galFiltered.sif')
        >>> ''

    Note:
        Sets the bypass value of node size for one or more nodes. Only applicable if node dimensions are locked.
        See ``lockNodeDimensions()``.

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    if not isinstance(new_sizes, list): new_sizes = [new_sizes]  # TODO: It looks like this should be happening everywhere?
    for size in new_sizes:
        if not isinstance(size, float) and not isinstance(size, int):
            error = 'illegal size string ' + str(size) + ' in set_node_size_bypass(). It needs to be a number.'
            sys.stderr.write(error)
            return None  # TODO: Is this what we want to return here?

    res = set_node_property_bypass(node_names, new_sizes, 'NODE_SIZE', network=network, base_url=base_url)
    return res

def set_node_tooltip_bypass(node_names, new_tooltip, network=None, base_url=DEFAULT_BASE_URL):
    """Sets a bypass tooltip for one or more nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (list): list of node names
        new_tooltip (str or list): list of size values or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if node or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_tooltip_bypass(get_node_names(), 'Some Tooltip')
        >>> ''
        >>> set_node_tooltip_bypass(['YDL194W', 'YBR043C'], ['One Tooltip', 'Other Tooltip'], network='galFiltered.sif')
        >>> ''

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    res = set_node_property_bypass(node_names, new_tooltip, 'NODE_TOOLTIP', network=network, base_url=base_url)
    return res

def set_node_width_bypass(node_names, new_widths, network=None, base_url=DEFAULT_BASE_URL):
    """Override the width for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (list): list of node names
        new_widths (int or float or list): list of width values or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: '' (None if width is invalid)

    Raises:
        CyError: if node or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_width_bypass(get_node_names(), 80)
        >>> ''
        >>> set_node_width_bypass(['YDL194W', 'YBR043C'], [80, 100.5], network='galFiltered.sif')
        >>> ''

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    style_dependencies.lock_node_dimensions(False)

    if not isinstance(new_widths, list): new_widths = [new_widths]  # TODO: It looks like this should be happening everywhere?
    for width in new_widths:
        if not isinstance(width, float) and not isinstance(width, int):
            error = 'illegal node width ' + str(width) + ' in set_node_width_bypass(). It needs to be a number.'
            sys.stderr.write(error)
            return None  # TODO: Is this what we want to return here?

    res = set_node_property_bypass(node_names, new_widths, 'NODE_WIDTH', network=network, base_url=base_url)
    return res

def set_node_height_bypass(node_names, new_heights, network=None, base_url=DEFAULT_BASE_URL):
    """Override the height for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (list): list of node names
        new_heights (int or float or list): list of height values or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: '' (None if height is invalid)

    Raises:
        CyError: if node or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_height_bypass(get_node_names(), 80)
        >>> ''
        >>> set_node_height_bypass(['YDL194W', 'YBR043C'], [80, 100.5], network='galFiltered.sif')
        >>> ''

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    style_dependencies.lock_node_dimensions(False)

    if not isinstance(new_heights, list): new_heights = [new_heights]  # TODO: It looks like this should be happening everywhere?
    for height in new_heights:
        if not isinstance(height, float) and not isinstance(height, int):
            error = 'illegal node height ' + str(height) + ' in set_node_height_bypass(). It needs to be a number.'
            sys.stderr.write(error)
            return None  # TODO: Is this what we want to return here?

    res = set_node_property_bypass(node_names, new_heights, 'NODE_HEIGHT', network=network, base_url=base_url)
    return res

def set_node_label_bypass(node_names, new_labels, network=None, base_url=DEFAULT_BASE_URL):
    """Override the label for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (list): list of node names
        new_labels (str or list): list of label values or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if node or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_label_bypass(get_node_names(), 'test label')
        >>> ''
        >>> set_node_label_bypass(['YDL194W', 'YBR043C'], ['A', 'B'], network='galFiltered.sif')
        >>> ''

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    res = set_node_property_bypass(node_names, new_labels, 'NODE_LABEL', network=network, base_url=base_url)
    return res

def set_node_font_face_bypass(node_names, new_fonts, network=None, base_url=DEFAULT_BASE_URL):
    """Override the font face for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (list): list of node names
        new_fonts (str or list): list of font values or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if node or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_font_face_bypass(get_node_names(), 'Dialog.italic,plain,20')
        >>> ''
        >>> set_node_font_face_bypass(['YDL194W', 'YBR043C'], ['Dialog.italic,plain,20', 'Dialog.bold,plain,10'], network='galFiltered.sif')
        >>> ''

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    res = set_node_property_bypass(node_names, new_fonts, 'NODE_LABEL_FONT_FACE', network=network, base_url=base_url)
    return res

def set_node_font_size_bypass(node_names, new_sizes, network=None, base_url=DEFAULT_BASE_URL):
    """Override the font size for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (list): list of node names
        new_sizes (int or float or list): list of font sizes or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if node or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_font_size_bypass(get_node_names(), 20)
        >>> ''
        >>> set_node_font_size_bypass(['YDL194W', 'YBR043C'], [50, 100], network='galFiltered.sif')
        >>> ''

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    if not isinstance(new_sizes, list): new_sizes = [new_sizes]  # TODO: It looks like this should be happening everywhere?
    size_type_errors = 0
    for size in new_sizes:
        if not isinstance(size, float) and not isinstance(size, int):
            error = 'illegal font size ' + str(size) + ' in set_node_font size_bypass(). It needs to be a number.'
            sys.stderr.write(error)
            size_type_errors += 1  # TODO: Why are we doing this when no other function does it? ... return None OK??

    if size_type_errors == 0:
        res = set_node_property_bypass(node_names, new_sizes, 'NODE_LABEL_FONT_SIZE', network=network, base_url=base_url)
    else:
        res = None

    return res

def set_node_label_color_bypass(node_names, new_colors, network=None, base_url=DEFAULT_BASE_URL):
    """Override the label color for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (list): list of node names
        new_colors (str or list):  list of hex colors, or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: '' (None if invalid color)

    Raises:
        CyError: if node or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_label_color_bypass(get_node_names(), '#FF00FF')
        >>> ''
        >>> set_node_label_color_bypass(['YDL194W', 'YBR043C'], ['#FF00FF', '#FFFF00'], network='galFiltered.sif')
        >>> ''

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    if not isinstance(new_colors, list): new_colors = [new_colors]  # TODO: It looks like this should be happening everywhere?
    for color in new_colors:
        if is_not_hex_color(color):
            return None  # TODO: Shouldn't this be an exception?

    res = set_node_property_bypass(node_names, new_colors, 'NODE_LABEL_COLOR', network=network, base_url=base_url)

    return res

def set_node_shape_bypass(node_names, new_shapes, network=None, base_url=DEFAULT_BASE_URL):
    """Override the shape for particular nodes

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (list): list of node names
        new_shapes (str or list):  List of shapes, or single value. See ``get_node_shapes()``.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: '' (None if invalid shape)

    Raises:
        CyError: if node or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_shape_bypass(get_node_names(), 'ROUND_RECTANGLE')
        >>> ''
        >>> set_node_shape_bypass(['YDL194W', 'YBR043C'], ['ROUND_RECTANGLE', 'OCTAGON'], network='galFiltered.sif')
        >>> ''

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    if not isinstance(new_shapes, list): new_shapes = [new_shapes]  # TODO: It looks like this should be happening everywhere?

    if len(node_names) != len(new_shapes) and len(new_shapes) != 1:
        error = 'error in set_node_shape_bypass().  new_shapes count ' + str(len(new_shapes)) + ' is neither 1 nor same as node_names count ' + str(len(node_names))
        sys.stderr.write(error)
        return None # Should this be an exception?

    # convert old to new node shapes
    # TODO: Why isn't this done on other shape functions?
    new_shapes = ['ROUND_RECTANGLE' if shape == 'round_rect' else shape    for shape in new_shapes]
    new_shapes = ['RECTANGLE' if shape == 'rect' else shape.upper()    for shape in new_shapes]

    # ensure valid node shapes
    valid_shapes = styles.get_node_shapes(base_url=base_url)
    for shape in new_shapes:
        if not shape in valid_shapes:
            error = 'ERROR in set_node_shape_bypass(). ' + shape + ' is not a valid shape. Please note that some older shapes are no longer available. For valid ones check get_node_shapes().'
            sys.stderr.write(error)
            return None  # Should this be an exception?

    res = set_node_property_bypass(node_names, new_shapes, 'NODE_SHAPE', network=network, base_url=base_url)

    return res

def set_node_border_width_bypass(node_names, new_sizes, network=None, base_url=DEFAULT_BASE_URL):
    """Override the border width for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (list): list of node names
        new_sizes (int or float or list): list of size values or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: '' (None if size is invalid)

    Raises:
        CyError: if node or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_border_width_bypass(get_node_names(), 10)
        >>> ''
        >>> set_node_border_width_bypass(['YDL194W', 'YBR043C'], [10, 20.5], network='galFiltered.sif')
        >>> ''

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    if not isinstance(new_sizes, list): new_sizes = [new_sizes]  # TODO: It looks like this should be happening everywhere?
    for size in new_sizes:
        if not isinstance(size, float) and not isinstance(size, int):
            error = 'illegal width string ' + str(size) + ' in set_node_border_width_bypass(). It needs to be a number.'
            sys.stderr.write(error)
            return None  # TODO: Is this what we want to return here?

    res = set_node_property_bypass(node_names, new_sizes, 'NODE_BORDER_WIDTH', network=network, base_url=base_url)
    return res

def set_node_border_color_bypass(node_names, new_colors, network=None, base_url=DEFAULT_BASE_URL):
    """Override the border color for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (list): list of node names
        new_colors (str or list): list of hex colors or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: '' (None if invalid color is found in new_colors)

    Raises:
        CyError: if node or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_border_color_bypass(get_node_names(), '#FF00FF')
        >>> ''
        >>> set_node_border_color_bypass(['YDL194W', 'YBR043C'], ['#FF00FF', '#CCCCCC'], network='galFiltered.sif')
        >>> ''

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    if isinstance(new_colors, str): new_colors = [
        new_colors]  # TODO: It looks like this should be happening everywhere?
    for color in new_colors:
        if is_not_hex_color(color):
            return None  # TODO: Shouldn't this be an exception?

    res = set_node_property_bypass(node_names, new_colors, 'NODE_BORDER_PAINT', network=network, base_url=base_url)
    return res

def set_node_opacity_bypass(node_names, new_values, network=None, base_url=DEFAULT_BASE_URL):
    """Set the bypass value for node fill, label and border opacity for the specified node or nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (list): list of node names
        new_values (int or float or list): list of values to set, or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: '' (None if invalid opacity is found in new_values)

    Raises:
        CyError: if node or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_opacity_bypass(get_node_names(), '#FF00FF')
        >>> ''
        >>> set_node_opacity_bypass(['YDL194W', 'YBR043C'], [128, 192], network='galFiltered.sif')
        >>> ''

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    if not isinstance(new_values, list): new_values = [new_values]  # TODO: It looks like this should be happening everywhere?
    for value in new_values:
        if (not isinstance(value, float) and not isinstance(value, int)) or value < 0 or value > 255:
            error = 'illegal opacity ' + str(value) + ' in set_node_opacity_bypass(). It needs to be a number.'
            sys.stderr.write(error)
            return None  # TODO: Is this what we want to return here?

    # TODO: Concerned about losing intermediate res results
    res = set_node_property_bypass(node_names, new_values, 'NODE_TRANSPARENCY', network=network, base_url=base_url)
    res = set_node_property_bypass(node_names, new_values, 'NODE_BORDER_TRANSPARENCY', network=network, base_url=base_url)
    res = set_node_property_bypass(node_names, new_values, 'NODE_LABEL_TRANSPARENCY', network=network, base_url=base_url)
    return res

def clear_node_opacity_bypass(node_names, network=None, base_url=DEFAULT_BASE_URL):
    """Clear Node Opacity Bypass.

    Clear the bypass value for node fill, label and border opacity for the specified node or nodes, effectively
    restoring any previously defined style defaults or mappings.

    Args:
        node_names (list): list of node names
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'data': {}, 'errors': []}

    Raises:
        CyError: if node or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> clear_node_opacity_bypass(get_node_names())
        >>> ''
        >>> clear_node_opacity_bypass(['YDL194W', 'YBR043C'], network='galFiltered.sif')
        >>> ''

    See Also:
        :meth:`set_node_opacity_bypass`
    """
    res = clear_node_property_bypass(node_names, 'NODE_TRANSPARENCY', network=network, base_url=base_url)
    res = clear_node_property_bypass(node_names, 'NODE_BORDER_TRANSPARENCY', network=network, base_url=base_url)
    res = clear_node_property_bypass(node_names, 'NODE_LABEL_TRANSPARENCY', network=network, base_url=base_url)
    return res
    # TODO: What kind of return result should there be, and what about losing intermediate return results?

def set_node_fill_opacity_bypass(node_names, new_values, network=None, base_url=DEFAULT_BASE_URL):
    """Override the fill opacity for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (list): list of node names
        new_values (int or float or list): list of values to set, or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: '' (None if invalid opacity is found in new_values)

    Raises:
        CyError: if node or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_fill_opacity_bypass(get_node_names(), '#FF00FF')
        >>> ''
        >>> set_node_fill_opacity_bypass(['YDL194W', 'YBR043C'], [128, 192], network='galFiltered.sif')
        >>> ''

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    if not isinstance(new_values, list): new_values = [new_values]  # TODO: It looks like this should be happening everywhere?
    for value in new_values:
        if (not isinstance(value, float) and not isinstance(value, int)) or value < 0 or value > 255:
            error = 'illegal opacity ' + str(value) + ' in set_node_fill_opacity_bypass(). It needs to be a number.'
            sys.stderr.write(error)
            return None  # TODO: Is this what we want to return here?

    res = set_node_property_bypass(node_names, new_values, 'NODE_TRANSPARENCY', network=network, base_url=base_url)
    return res

def set_node_border_opacity_bypass(node_names, new_values, network=None, base_url=DEFAULT_BASE_URL):
    """Override the border opacity for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (list): list of node names
        new_values (int or float or list): list of values to set, or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: '' (None if invalid opacity is found in new_values)

    Raises:
        CyError: if node or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_border_opacity_bypass(get_node_names(), '#FF00FF')
        >>> ''
        >>> set_node_border_opacity_bypass(['YDL194W', 'YBR043C'], [128, 192], network='galFiltered.sif')
        >>> ''

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    if not isinstance(new_values, list): new_values = [new_values]  # TODO: It looks like this should be happening everywhere?
    for value in new_values:
        if (not isinstance(value, float) and not isinstance(value, int)) or value < 0 or value > 255:
            error = 'illegal opacity ' + str(value) + ' in set_node_border_opacity_bypass(). It needs to be a number.'
            sys.stderr.write(error)
            return None  # TODO: Is this what we want to return here?

    res = set_node_property_bypass(node_names, new_values, 'NODE_BORDER_TRANSPARENCY', network=network, base_url=base_url)
    return res

def set_node_label_opacity_bypass(node_names, new_values, network=None, base_url=DEFAULT_BASE_URL):
    """Override the label opacity for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (list): list of node names
        new_values (int or float or list): list of values to set, or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: '' (None if invalid opacity is found in new_values)

    Raises:
        CyError: if node or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_label_opacity_bypass(get_node_names(), '#FF00FF')
        >>> ''
        >>> set_node_label_opacity_bypass(['YDL194W', 'YBR043C'], [128, 192], network='galFiltered.sif')
        >>> ''

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    if not isinstance(new_values, list): new_values = [new_values]  # TODO: It looks like this should be happening everywhere?
    for value in new_values:
        if (not isinstance(value, float) and not isinstance(value, int)) or value < 0 or value > 255:
            error = 'illegal opacity ' + str(value) + ' in set_node_label_opacity_bypass(). It needs to be a number.'
            sys.stderr.write(error)
            return None  # TODO: Is this what we want to return here?

    res = set_node_property_bypass(node_names, new_values, 'NODE_LABEL_TRANSPARENCY', network=network, base_url=base_url)
    return res
