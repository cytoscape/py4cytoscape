# -*- coding: utf-8 -*-

"""Functions for getting and setting BYPASS values for visual properties, organized into sections:

I. General functions for setting/clearing node, edge and network properties
II. Specific functions for setting particular node, edge and network properties

NOTE: The CyREST 'bypass' endpoint is essential to properly set values that
will persist for a given network independent of applied style and style
changes, and from session to session if saved.
"""

"""Copyright 2020-2022 The Cytoscape Consortium

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
import time
import re
import json

# Internal module imports
from . import commands
from . import networks
from . import network_selection
from . import network_views
from . import style_dependencies
from . import styles


# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log, show_error
from .py4cytoscape_tuning import MODEL_PROPAGATION_SECS
from .style_visual_props import *

# ==============================================================================
# I. General Functions
# ==============================================================================
# I.a. Node Properties
# ------------------------------------------------------------------------------

@cy_log
def set_node_property_bypass(node_names, new_values, visual_property, bypass=True, network=None,
                             base_url=DEFAULT_BASE_URL):
    """Set Node Property Bypass.

    Set bypass values for any node property of the specified nodes, overriding default values and mappings defined by
    any visual style.

    This method permanently overrides any default values or mappings defined for the visual properties of the node
    or nodes specified. To restore defaults and mappings, use ``clear_node_property_bypass()``.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
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
        ''
        >>> set_node_property_bypass(node_names, 'red', 'NODE_FILL_COLOR')
        ''
        >>> set_node_property_bypass('YDL194W, YDR277C', '#FF00FF', 'NODE_FILL_COLOR')
        ''
        >>> node_suids = list(get_table_columns(columns='name').index)
        >>> set_node_property_bypass(node_suids, ['#FF00FF'], 'NODE_FILL_COLOR', network='galFiltered.sif')
        ''
        >>> set_node_property_bypass('12755, 13877', '#FF00FF', 'NODE_FILL_COLOR')
        ''
        >>> set_node_property_bypass(12755, ['#FF00FF'], 'NODE_FILL_COLOR', network='galFiltered.sif')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`clear_node_property_bypass`
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    view_suid = network_views.get_network_views(net_suid, base_url=base_url)[0]
    node_suids = node_name_to_node_suid(node_names, network=network, base_url=base_url, unique_list=True)
    if node_suids is None: return ''

    # TODO: Shouldn't we allow node_names=None to mean all nodes? ... as is, this causes an error below and is inconsistent with other functions
    # TODO: Find out how to test for bypass=True effects

    visual_property = normalize_prop_name(visual_property)

    if not isinstance(new_values, list): new_values = [new_values]

    # If the property is verifiable, verify the values and adjust as appropriate
    if visual_property in NODE_COLOR_PROPERTIES:
        new_values = verify_hex_colors(new_values)
    elif visual_property in NODE_DIMENSION_PROPERTIES.keys():
        new_values = verify_dimensions(NODE_DIMENSION_PROPERTIES[visual_property], new_values)
    elif visual_property in NODE_OPACITY_PROPERTIES:
        new_values = verify_opacities(new_values)
    elif visual_property in NODE_SHAPE_PROPERTIES:
        new_values = verify_node_shapes(new_values, styles.get_node_shapes(base_url=base_url))
    elif visual_property in NODE_VISIBLE_PROPERTIES:
        new_values = verify_bools(new_values)
    elif visual_property in NODE_LABEL_PROPERTIES | NODE_TOOLTIP_PROPERTIES | NODE_FONT_FACE_PROPERTIES:
        new_values = verify_strs(new_values)
    else:
        # There are a bunch of properties that we can validate when we're next in a major development.
        # It takes a lot to test these validations, so we don't take this lightly. The NODE properties
        # we're not validating are: NODE, NODE_BORDER_STROKE, NODE_CUSTOMGRAPHICS_SIZE_1..9, NODE_CUSTOMPAINT_1..9,
        # NODE_DEPTH, NODE_LABEL_BACKGROUND_COLOR, NODE_LABEL_BACKGROUND_SHAPE, NODE_LABEL_BACKGROUND_TRANSPARENCY,
        # NODE_LABEL_FONT_FACE, NODE_LABEL_POSITION, NODE_LABEL_ROTATION, NODE_LABEL_WIDTH,
        # NODE_NESTED_NETWORK_IMAGE_VISIBLE, NODE_PAINT, NODE_SELECTED_PAINT, NODE_X_LOCATION, NODE_Y_LOCATION,
        # NODE_Z_LOCATION
        # So, the validation we *do* do should be considered an early convenience, as it's incomplete. Of course, if
        # a value isn't acceptable to CyREST, an error will be generated by CyREST. So, the above validation is
        # somewhat redundant. The major exception is with color properties, which should be passed to CyREST as
        # hex values (e.g., 0x123456). Color validation converts color words (e.g., RED) to hex values, so
        # the caller must pass unvalidated color properties (e.g., NODE_LABEL_BACKGROUND_COLOR) as only hex values.
        # Given this, we're removing the warning we were giving for unvalidated properties, as it's more of a
        # worry for users than it's worth:
        # show_error(f'Warning: setting unknown node bypass property "{visual_property}"')
        pass

    # there can be more than one node.SUID per node.name!
    # 'node.SUIDs' and 'new.values' must have the same length
    # TODO: Should we allow a scalar for a new_value, or do we assume a list?
    if len(new_values) == 1: new_values = new_values * len(node_suids)

    if len(new_values) != len(node_suids):
        error = 'The number of nodes ' + str(len(node_suids)) + ' and new values ' + str(len(new_values)) \
                + ' are not the same >> node(s) attribute couldn\'t be set. Note that having multiple nodes with the same name in the network can cause this error. Use node SUIDs or pass in duplicated names on their own.'
        raise CyError(error)

    body_list = [{'SUID': str(suid), 'view': [{'visualProperty': visual_property, 'value': val}]} for suid, val in
                 zip(node_suids, new_values)]

    res = commands.cyrest_put(f'networks/{net_suid}/views/{view_suid}/nodes',
                              parameters={'bypass': bypass}, body=body_list, base_url=base_url, require_json=False)
    return res


@cy_log
def clear_node_property_bypass(node_names, visual_property, network=None, base_url=DEFAULT_BASE_URL):
    """Clear Node Property Bypass.

    Clear bypass values for any node property of the specified nodes, effectively restoring any previously defined
    style defaults or mappings.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
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
        ''
        >>> clear_node_property_bypass('YDL194W, YDR277C', 'NODE_FILL_COLOR')
        ''
        >>> node_suids = list(get_table_columns(columns='name').index)
        >>> clear_node_property_bypass(node_suids, 'NODE_FILL_COLOR', network='galFiltered.sif')
        ''
        >>> clear_node_property_bypass('12755, 13877', 'NODE_FILL_COLOR')
        ''
        >>> clear_node_property_bypass(12755, 'NODE_FILL_COLOR', network='galFiltered.sif')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`set_node_property_bypass`
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    view_suid = network_views.get_network_views(net_suid, base_url=base_url)[0]

    visual_property = normalize_prop_name(visual_property)

    if node_names == 'all':
        raise CyError('"all" node_names is not yet supported by CyREST. Please provide a valid node list.')

    # TODO: Do we need to pass in net_suid ... other calls just let the function figure it out
    node_suids = node_name_to_node_suid(node_names, network=net_suid, base_url=base_url, unique_list=True)

    if node_suids == []:
        res = {'data': {}, 'errors': []}
    else:
        for suid in node_suids:
            res = commands.cyrest_delete(f'networks/{net_suid}/views/{view_suid}/nodes/{suid}/{visual_property}/bypass',
                                         base_url=base_url)

    return res
    # TODO: OK to miss res values during the loop?


# ==============================================================================
# I.b. Edge Properties
# ------------------------------------------------------------------------------

@cy_log
def set_edge_property_bypass(edge_names, new_values, visual_property, bypass=True, network=None,
                             base_url=DEFAULT_BASE_URL):
    """Set Edge Property Bypass.

    Set bypass values for any edge property of the specified edges, overriding default values and mappings defined by
    any visual style.

    This method permanently overrides any default values or mappings defined for the visual properties of the edge
    or edges specified. To restore defaults and mappings, use ``clear_edge_property_bypass()``.

    Args:
        edge_names (str or list or int or None): List of edges as ``list`` of edge names or SUIDs,
            comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID. Edge names should be found in the ``name`` column of the ``edges table``.
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
        {'data': {}, 'errors': []}
        >>> set_edge_property_bypass('YDR277C (pp) YDL194W, YDR277C (pp) YJR022W', ['#FF00FF'], 'EDGE_UNSELECTED_PAINT')
        {'data': {}, 'errors': []}
        >>> set_edge_property_bypass('YDR277C (pp) YDL194W, YDR277C (pp) YJR022W', ['red'], 'EDGE_UNSELECTED_PAINT')
        {'data': {}, 'errors': []}
        >>> edge_suids = list(get_table_columns(table='edge', columns='name').index)
        >>> set_edge_property_bypass(edge_suids, ['#FF00FF'], 'EDGE_UNSELECTED_PAINT', network='galFiltered.sif')
        {'data': {}, 'errors': []}
        >>> set_edge_property_bypass('12755, 13877', ['#FF00FF'], 'EDGE_UNSELECTED_PAINT')
        {'data': {}, 'errors': []}
        >>> set_edge_property_bypass(12755, '#FF00FF', 'EDGE_UNSELECTED_PAINT')
        {'data': {}, 'errors': []}

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1 (pd) node\\\\,2' identifies 'node1 (pd) node,2'.

    See Also:
        :meth:`clear_edge_property_bypass`
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    view_suid = network_views.get_network_views(net_suid, base_url=base_url)[0]
    edge_suids = edge_name_to_edge_suid(edge_names, network=network, base_url=base_url, unique_list=True)
    if edge_suids is None: return ''

    # TODO: Shouldn't we allow node_names=None to mean all nodes? ... as is, this causes an error below and is inconsistent with other functions
    # TODO: Find out how to test for bypass=True effects

    visual_property = normalize_prop_name(visual_property)

    if not isinstance(new_values, list): new_values = [new_values]

    # If the property is verifiable, verify the values and adjust as appropriate
    if visual_property in EDGE_COLOR_PROPERTIES:
        new_values = verify_hex_colors(new_values)
    elif visual_property in EDGE_DIMENSION_PROPERTIES.keys():
        new_values = verify_dimensions(EDGE_DIMENSION_PROPERTIES[visual_property], new_values)
    elif visual_property in EDGE_OPACITY_PROPERTIES:
        new_values = verify_opacities(new_values)
    elif visual_property in EDGE_LINE_STYLE_PROPERTIES:
        new_values = verify_edge_shapes(new_values, styles.get_line_styles(base_url=base_url), 'line style', 'get_line_styles')
    elif visual_property in EDGE_ARROW_STYLE_PROPERTIES:
        new_values = verify_edge_shapes(new_values, styles.get_arrow_shapes(base_url=base_url), 'arrow shape', 'get_arrow_shapes')
    elif visual_property in EDGE_VISIBLE_PROPERTIES:
        new_values = verify_bools(new_values)
    elif visual_property in EDGE_LABEL_PROPERTIES | EDGE_TOOLTIP_PROPERTIES | EDGE_FONT_FACE_PROPERTIES:
        new_values = verify_strs(new_values)
    else:
        # There are a bunch of properties that we can validate when we're next in a major development.
        # It takes a lot to test these validations, so we don't take this lightly. The EDGE properties
        # we're not validating are: EDGE, EDGE_BEND, EDGE_CURVED, EDGE_LABEL_AUTOROTATE, EDGE_LABEL_BACKGROUND_COLOR,
        # EDGE_LABEL_BACKGROUND_SHAPE, EDGE_LABEL_BACKGROUND_TRANSPARENCY, EDGE_LABEL_FONT_SIZE, EDGE_LABEL_POSITION,
        # EDGE_LABEL_ROTATION, EDGE_LABEL_WIDTH, EDGE_PAINT, EDGE_SELECTED, EDGE_SOURCE_ARROW_SIZE, EDGE_STACKING,
        # EDGE_STACKING_DENSITY, EDGE_TARGET_ARROW_SELECTED_PAINT, EDGE_TARGET_ARROW_SIZE, EDGE_WIDTH, EDGE_Z_ORDER
        # So, the validation we *do* do should be considered an early convenience, as it's incomplete. Of course, if
        # a value isn't acceptable to CyREST, an error will be generated by CyREST. So, the above validation is
        # somewhat redundant. The major exception is with color properties, which should be passed to CyREST as
        # hex values (e.g., 0x123456). Color validation converts color words (e.g., RED) to hex values, so
        # the caller must pass unvalidated color properties (e.g., EDGE_LABEL_BACKGROUND_COLOR) as only hex values.
        # Given this, we're removing the warning we were giving for unvalidated properties, as it's more of a
        # worry for users than it's worth:
        # show_error(f'Warning: setting unknown edge bypass property "{visual_property}"')
        pass

    # there can be more than one edge.SUID per edge.name!
    # 'edge.SUIDs' and 'new.values' must have the same length
    # TODO: Should we allow a scalar for a new_value, or do we assume a list?
    if len(new_values) == 1: new_values = new_values * len(edge_suids)

    if len(new_values) != len(edge_suids):
        error = 'The number of nodes ' + str(len(edge_suids)) + ' and new values ' + str(len(new_values)) \
                + ' are not the same >> node(s) attribute couldn\'t be set. Note that having multiple nodes with the same name in the network can cause this error. Use node SUIDs or pass in duplicated names on their own.'
        raise CyError(error)

    body_list = [{'SUID': str(suid), 'view': [{'visualProperty': visual_property, 'value': val}]} for suid, val in
                 zip(edge_suids, new_values)]

    res = commands.cyrest_put(f'networks/{net_suid}/views/{view_suid}/edges',
                              parameters={'bypass': bypass}, body=body_list, base_url=base_url, require_json=False)
    return res


@cy_log
def clear_edge_property_bypass(edge_names, visual_property, network=None, base_url=DEFAULT_BASE_URL):
    """Clear Edge Property Bypass.

    Clear bypass values for any edge property of the specified edges, effectively restoring any previously defined
    style defaults or mappings.

    Args:
        edge_names (str or list or int or None): List of edges as ``list`` of edge names or SUIDs,
            comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID. Edge names should be found in the ``name`` column of the ``edges table``.
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
        {'data': {}, 'errors': []}
        >>> clear_edge_property_bypass('YDR277C (pp) YDL194W, YDR277C (pp) YJR022W', 'EDGE_UNSELECTED_PAINT')
        {'data': {}, 'errors': []}
        >>> edge_suids = list(get_table_columns(table='edge', columns='name').index)
        >>> clear_edge_property_bypass(edge_suids, 'EDGE_UNSELECTED_PAINT', network='galFiltered.sif')
        {'data': {}, 'errors': []}
        >>> clear_edge_property_bypass('12755, 13877', 'EDGE_UNSELECTED_PAINT')
        {'data': {}, 'errors': []}
        >>> clear_edge_property_bypass(12755, 'EDGE_UNSELECTED_PAINT', network='galFiltered.sif')
        {'data': {}, 'errors': []}

    See Also:
        :meth:`set_edge_property_bypass`
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    view_suid = network_views.get_network_views(net_suid, base_url=base_url)[0]

    visual_property = normalize_prop_name(visual_property)

    if edge_names == 'all':
        raise CyError('"all" edge_names is not yet supported by CyREST. Please provide a valid edge list.')

    # TODO: Do we need to pass in net_suid ... other calls just let the function figure it out
    edge_suids = edge_name_to_edge_suid(edge_names, network=net_suid, base_url=base_url, unique_list=True)

    if edge_suids == []:
        res = {'data': {}, 'errors': []}
    else:
        for suid in edge_suids:
            res = commands.cyrest_delete(f'networks/{net_suid}/views/{view_suid}/edges/{suid}/{visual_property}/bypass',
                                         base_url=base_url)

    return res
    # TODO: OK to miss res values during the loop?


@cy_log
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
        ''
        >>> set_network_property_bypass(0.5, 'NETWORK_SCALE_FACTOR', network='galFiltered.sif')
        ''

    See Also:
        :meth:`clear_network_property_bypass`
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    view_suid = network_views.get_network_views(net_suid, base_url=base_url)[0]

    visual_property = normalize_prop_name(visual_property)

    # If the property is a color property, verify that all of the colors are valid, and translate named colors
    if visual_property in NETWORK_COLOR_PROPERTIES:
        new_value = verify_hex_colors(new_value)

    res = commands.cyrest_put(f'networks/{net_suid}/views/{view_suid}/network',
                              parameters={'bypass': bypass},
                              body=[{'visualProperty': visual_property, 'value': new_value}], base_url=base_url,
                              require_json=False)
    return res


@cy_log
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
        ''
        >>> clear_network_property_bypass('NETWORK_SCALE_FACTOR', network='galFiltered.sif')
        ''

    See Also:
        :meth:`set_network_property_bypass`
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    view_suid = network_views.get_network_views(net_suid, base_url=base_url)[0]

    visual_property = normalize_prop_name(visual_property)

    res = commands.cyrest_delete(f'networks/{net_suid}/views/{view_suid}/network/{visual_property}/bypass',
                                 base_url=base_url)
    return res


# ==============================================================================
# II. Specific Functions
# ------------------------------------------------------------------------------

@cy_log
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
        ''
        >>> unhide_all(network='galFiltered.sif')
        ''

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

@cy_log
def set_node_color_bypass(node_names, new_colors, network=None, base_url=DEFAULT_BASE_URL):
    """Set the bypass value for fill color for the specified node or nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
        new_colors (str or list): list of hex colors or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if invalid color, or if node or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_color_bypass(get_node_names(), '#FF00FF')
        ''
        >>> set_node_color_bypass(get_node_names(), 'red')
        ''
        >>> set_node_color_bypass(['YDL194W', 'YBR043C'], ['#FF00FF', '#CCCCCC'], network='galFiltered.sif')
        ''
        >>> set_node_color_bypass('YDL194W, YBR043C', ['#FF00FF', '#CCCCCC'], network='galFiltered.sif')
        ''
        >>> set_node_color_bypass([1255, 1988], ['#FF00FF', '#CCCCCC'], network='galFiltered.sif')
        ''
        >>> set_node_color_bypass('1255, 1988', ['#FF00FF', 'blue'], network='galFiltered.sif')
        ''
        >>> set_node_color_bypass(1255, '#FF00FF', network='galFiltered.sif')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    res = set_node_property_bypass(node_names, new_colors, 'NODE_FILL_COLOR', network=network, base_url=base_url)
    return res


@cy_log
def set_node_size_bypass(node_names, new_sizes, network=None, base_url=DEFAULT_BASE_URL):
    """Set Node Size Bypass.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
        new_sizes (int or float or list): list of size values or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if node or network name doesn't exist or if size isn't valid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_size_bypass(get_node_names(), 50)
        ''
        >>> set_node_size_bypass('YDL194W, YBR043C', [150.5, 90.5], network='galFiltered.sif')
        ''
        >>> set_node_size_bypass(['YDL194W', 'YBR043C'], [150.5, 90.5], network='galFiltered.sif')
        ''
        >>> set_node_size_bypass([1255, 1988], [150.5, 90.5], network='galFiltered.sif')
        ''
        >>> set_node_size_bypass('1255, 1988', [150.5, 90.5], network='galFiltered.sif')
        ''
        >>> set_node_size_bypass(1255, 150.5, network='galFiltered.sif')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    Note:
        Sets the bypass value of node size for one or more nodes. Only applicable if node dimensions are locked.
        See ``lockNodeDimensions()``.

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    res = set_node_property_bypass(node_names, new_sizes, 'NODE_SIZE', network=network, base_url=base_url)
    return res

@cy_log
def set_node_position_bypass(node_names, new_x_locations=None, new_y_locations=None, network=None, base_url=DEFAULT_BASE_URL):
    """Sets the bypass value of node position for one or more nodes. Only applicable if node dimensions are locked. See ``lock_node_dimensions()``.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (str or list or int): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
        new_x_locations (list, int or float): List of x position values, or single value, default is current x position
        new_y_locations (list, int or float): List of y position values, or single value, default is current y position
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
        >>> set_node_position_bypass(get_node_names(), new_x_locations, new_y_locations)
        ''
        >>> set_node_position_bypass(['YDL194W', 'YBR043C'], [100, 200], [300, 400], network='galFiltered.sif')
        ''
        >>> set_node_position_bypass('YDL194W, YBR043C', [100, 200], [300, 400], network='galFiltered.sif')
        ''
        >>> set_node_position_bypass([1255, 1988], [100, 200], [300, 400], network='galFiltered.sif')
        ''
        >>> set_node_position_bypass('1255, 1988', [100, 200], [300, 400], network='galFiltered.sif')
        ''
        >>> set_node_position_bypass(1255, 100, 300, network='galFiltered.sif')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`, :meth:`lock_node_dimensions`
    """
    def check_locations(locations, location_name) :
        if locations is not None:
            if not isinstance(locations, list):
                locations = [locations]
            for loc in locations:
                if not isinstance(loc, float) and not isinstance(loc, int):
                    raise CyError(f'Illegal {location_name} position "{loc}" -- it must be a number.')
        return locations

    # Check and normalize location parameters
    new_x_locations = check_locations(new_x_locations, 'x')
    new_y_locations = check_locations(new_y_locations, 'y')

    # Just validate network if it looks like no locations were passed in
    if new_x_locations is None and new_y_locations is None:
        networks.get_network_suid(network, base_url=base_url)
    else:
        # Set the node properties bypass
        if new_x_locations is not None:
            set_node_property_bypass(node_names, new_x_locations, 'NODE_X_LOCATION', network=network, base_url=base_url)
        if new_y_locations is not None:
            set_node_property_bypass(node_names, new_y_locations, 'NODE_Y_LOCATION', network=network, base_url=base_url)
    return ""


@cy_log
def set_node_tooltip_bypass(node_names, new_tooltip, network=None, base_url=DEFAULT_BASE_URL):
    """Sets a bypass tooltip for one or more nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
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
        ''
        >>> set_node_tooltip_bypass(['YDL194W', 'YBR043C'], ['One Tooltip', 'Other Tooltip'], network='galFiltered.sif')
        ''
        >>> set_node_tooltip_bypass('YDL194W, YBR043C', ['One Tooltip', 'Other Tooltip'], network='galFiltered.sif')
        ''
        >>> set_node_tooltip_bypass([1255, 1988], ['One Tooltip', 'Other Tooltip'], network='galFiltered.sif')
        ''
        >>> set_node_tooltip_bypass('1255, 1988', ['One Tooltip', 'Other Tooltip'], network='galFiltered.sif')
        ''
        >>> set_node_tooltip_bypass(1255, 'One Tooltip', network='galFiltered.sif')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    res = set_node_property_bypass(node_names, new_tooltip, 'NODE_TOOLTIP', network=network, base_url=base_url)
    return res


@cy_log
def set_node_width_bypass(node_names, new_widths, network=None, base_url=DEFAULT_BASE_URL):
    """Override the width for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
        new_widths (int or float or list): list of width values or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if node or network name doesn't exist, or if width is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_width_bypass(get_node_names(), 80)
        ''
        >>> set_node_width_bypass(['YDL194W', 'YBR043C'], [80, 100.5], network='galFiltered.sif')
        ''
        >>> set_node_width_bypass('YDL194W, YBR043C', [80, 100.5], network='galFiltered.sif')
        ''
        >>> set_node_width_bypass([1255, 1988], [80, 100.5], network='galFiltered.sif')
        ''
        >>> set_node_width_bypass('1255, 1988', [80, 100.5], network='galFiltered.sif')
        ''
        >>> set_node_width_bypass(1255, 80)
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    current_style = styles.get_current_style(network=network, base_url=base_url)
    style_dependencies.lock_node_dimensions(False, style_name=current_style, base_url=base_url)

    res = set_node_property_bypass(node_names, new_widths, 'NODE_WIDTH', network=network, base_url=base_url)
    return res


@cy_log
def set_node_height_bypass(node_names, new_heights, network=None, base_url=DEFAULT_BASE_URL):
    """Override the height for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
        new_heights (int or float or list): list of height values or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if node or network name doesn't exist, or if height is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_height_bypass(get_node_names(), 80)
        ''
        >>> set_node_height_bypass(['YDL194W', 'YBR043C'], [80, 100.5], network='galFiltered.sif')
        ''
        >>> set_node_height_bypass('YDL194W, YBR043C', [80, 100.5], network='galFiltered.sif')
        ''
        >>> set_node_height_bypass([1255, 1988], [80, 100.5], network='galFiltered.sif')
        ''
        >>> set_node_height_bypass('1255, 1988', [80, 100.5], network='galFiltered.sif')
        ''
        >>> set_node_height_bypass(1255, 80)
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    current_style = styles.get_current_style(network=network, base_url=base_url)
    style_dependencies.lock_node_dimensions(False, style_name=current_style, base_url=base_url)

    res = set_node_property_bypass(node_names, new_heights, 'NODE_HEIGHT', network=network, base_url=base_url)
    return res


@cy_log
def set_node_label_bypass(node_names, new_labels, network=None, base_url=DEFAULT_BASE_URL):
    """Override the label for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
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
        ''
        >>> set_node_label_bypass(['YDL194W', 'YBR043C'], ['A', 'B'], network='galFiltered.sif')
        ''
        >>> set_node_label_bypass('YDL194W, YBR043C', ['A', 'B'], network='galFiltered.sif')
        ''
        >>> set_node_label_bypass([1255, 1988], ['A', 'B'], network='galFiltered.sif')
        ''
        >>> set_node_label_bypass('1255, 1988', ['A', 'B'], network='galFiltered.sif')
        ''
        >>> set_node_label_bypass(1255, 'test label')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    res = set_node_property_bypass(node_names, new_labels, 'NODE_LABEL', network=network, base_url=base_url)
    return res


@cy_log
def set_node_label_position_bypass(node_names, new_positions, network=None, base_url=DEFAULT_BASE_URL):
    """Override the label position for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
        new_positions (str or list): list of position values or single value. A position value has 5 comma-separated
            elements: node_anchor, graphic_anchor, justification, x_offset, y_offset. For example: N,C,c,0.00,0.00. For
            details, see ``set_node_label_position_default()``
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
        >>> set_node_label_position_bypass(get_node_names(), 'N,E,l,100.00,-200.00')
        ''
        >>> set_node_label_position_bypass(['YDL194W', 'YBR043C'], ['N,E,l,100.00,-200.00', 'W,N,r,-100.00,200.00'], network='galFiltered.sif')
        ''
        >>> set_node_label_position_bypass('YDL194W, YBR043C', ['N,E,l,100.00,-200.00', 'W,N,r,-100.00,200.00'], network='galFiltered.sif')
        ''
        >>> set_node_label_position_bypass([1255, 1988], ['N,E,l,100.00,-200.00', 'W,N,r,-100.00,200.00'], network='galFiltered.sif')
        ''
        >>> set_node_label_position_bypass('1255, 1988', ['N,E,l,100.00,-200.00', 'W,N,r,-100.00,200.00'], network='galFiltered.sif')
        ''
        >>> set_node_label_position_bypass(1255, 'N,E,l,100.00,-200.00', network='galFiltered.sif')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`, :meth:`set_node_label_position_default`
    """
    res = set_node_property_bypass(node_names, new_positions, 'NODE_LABEL_POSITION', network=network, base_url=base_url)
    return res


@cy_log
def set_node_font_face_bypass(node_names, new_fonts, network=None, base_url=DEFAULT_BASE_URL):
    """Override the font face for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
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
        ''
        >>> set_node_font_face_bypass(['YDL194W', 'YBR043C'], ['Dialog.italic,plain,20', 'Dialog.bold,plain,10'], network='galFiltered.sif')
        ''
        >>> set_node_font_face_bypass('YDL194W, YBR043C', ['Dialog.italic,plain,20', 'Dialog.bold,plain,10'], network='galFiltered.sif')
        ''
        >>> set_node_font_face_bypass([1255, 1988], ['Dialog.italic,plain,20', 'Dialog.bold,plain,10'], network='galFiltered.sif')
        ''
        >>> set_node_font_face_bypass('1255, 1988', ['Dialog.italic,plain,20', 'Dialog.bold,plain,10'], network='galFiltered.sif')
        ''
        >>> set_node_font_face_bypass(1255, 'Dialog.italic,plain,20')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    res = set_node_property_bypass(node_names, new_fonts, 'NODE_LABEL_FONT_FACE', network=network, base_url=base_url)
    return res


@cy_log
def set_node_font_size_bypass(node_names, new_sizes, network=None, base_url=DEFAULT_BASE_URL):
    """Override the font size for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
        new_sizes (int or float or list): list of font sizes or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if node or network name doesn't exist, or if size is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_font_size_bypass(get_node_names(), 20)
        ''
        >>> set_node_font_size_bypass(['YDL194W', 'YBR043C'], [50, 100], network='galFiltered.sif')
        ''
        >>> set_node_font_size_bypass('YDL194W, YBR043C', [50, 100], network='galFiltered.sif')
        ''
        >>> set_node_font_size_bypass([1255, 1988], [50, 100], network='galFiltered.sif')
        ''
        >>> set_node_font_size_bypass('1255, 1988', [50, 100], network='galFiltered.sif')
        ''
        >>> set_node_font_size_bypass(1255, 20)
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    res = set_node_property_bypass(node_names, new_sizes, 'NODE_LABEL_FONT_SIZE', network=network,
                                   base_url=base_url)
    return res


@cy_log
def set_node_label_color_bypass(node_names, new_colors, network=None, base_url=DEFAULT_BASE_URL):
    """Override the label color for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
        new_colors (str or list):  list of hex colors, or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if invalid color, or if node or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_label_color_bypass(get_node_names(), '#FF00FF')
        ''
        >>> set_node_label_color_bypass(get_node_names(), 'red')
        ''
        >>> set_node_label_color_bypass(['YDL194W', 'YBR043C'], ['#FF00FF', '#FFFF00'], network='galFiltered.sif')
        ''
        >>> set_node_label_color_bypass('YDL194W, YBR043C', ['#FF00FF', '#FFFF00'], network='galFiltered.sif')
        ''
        >>> set_node_label_color_bypass([1255, 1988], ['#FF00FF', '#FFFF00'], network='galFiltered.sif')
        ''
        >>> set_node_label_color_bypass('1255, 1988', ['#FF00FF', 'blue'], network='galFiltered.sif')
        ''
        >>> set_node_label_color_bypass(1255, '#FF00FF')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    res = set_node_property_bypass(node_names, new_colors, 'NODE_LABEL_COLOR', network=network, base_url=base_url)

    return res


@cy_log
def set_node_shape_bypass(node_names, new_shapes, network=None, base_url=DEFAULT_BASE_URL):
    """Override the shape for particular nodes

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
        new_shapes (str or list):  List of shapes, or single value. See ``get_node_shapes()``.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if node or network name doesn't exist, or if shape list is invalid or doesn't match nodes
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_shape_bypass(get_node_names(), 'ROUND_RECTANGLE')
        ''
        >>> set_node_shape_bypass(['YDL194W', 'YBR043C'], ['ROUND_RECTANGLE', 'OCTAGON'], network='galFiltered.sif')
        ''
        >>> set_node_shape_bypass('YDL194W, YBR043C', ['ROUND_RECTANGLE', 'OCTAGON'], network='galFiltered.sif')
        ''
        >>> set_node_shape_bypass([1255, 1988], ['ROUND_RECTANGLE', 'OCTAGON'], network='galFiltered.sif')
        ''
        >>> set_node_shape_bypass('1255, 1988', ['ROUND_RECTANGLE', 'OCTAGON'], network='galFiltered.sif')
        ''
        >>> set_node_shape_bypass(1255, 'ROUND_RECTANGLE')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    res = set_node_property_bypass(node_names, new_shapes, 'NODE_SHAPE', network=network, base_url=base_url)

    return res


@cy_log
def set_node_border_width_bypass(node_names, new_sizes, network=None, base_url=DEFAULT_BASE_URL):
    """Override the border width for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
        new_sizes (int or float or list): list of size values or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if node or network name doesn't exist, or if width is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_border_width_bypass(get_node_names(), 10)
        ''
        >>> set_node_border_width_bypass(['YDL194W', 'YBR043C'], [10, 20.5], network='galFiltered.sif')
        ''
        >>> set_node_border_width_bypass('YDL194W, YBR043C', [10, 20.5], network='galFiltered.sif')
        ''
        >>> set_node_border_width_bypass([1255, 1988], [10, 20.5], network='galFiltered.sif')
        ''
        >>> set_node_border_width_bypass('1255, 1988', [10, 20.5], network='galFiltered.sif')
        ''
        >>> set_node_border_width_bypass(1255, 10)
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    res = set_node_property_bypass(node_names, new_sizes, 'NODE_BORDER_WIDTH', network=network, base_url=base_url)
    return res


@cy_log
def set_node_border_color_bypass(node_names, new_colors, network=None, base_url=DEFAULT_BASE_URL):
    """Override the border color for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
        new_colors (str or list): list of hex colors or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if invalid color, or if node or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_border_color_bypass(get_node_names(), '#FF00FF')
        ''
        >>> set_node_border_color_bypass(get_node_names(), 'red')
        ''
        >>> set_node_border_color_bypass(['YDL194W', 'YBR043C'], ['#FF00FF', '#CCCCCC'], network='galFiltered.sif')
        ''
        >>> set_node_border_color_bypass('YDL194W, YBR043C', ['#FF00FF', '#CCCCCC'], network='galFiltered.sif')
        ''
        >>> set_node_border_color_bypass([1255, 1988], ['#FF00FF', '#CCCCCC'], network='galFiltered.sif')
        ''
        >>> set_node_border_color_bypass('1255, 1988', ['#FF00FF', 'blue'], network='galFiltered.sif')
        ''
        >>> set_node_border_color_bypass(1255, '#FF00FF')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    res = set_node_property_bypass(node_names, new_colors, 'NODE_BORDER_PAINT', network=network, base_url=base_url)
    return res


@cy_log
def set_node_opacity_bypass(node_names, new_values, network=None, base_url=DEFAULT_BASE_URL):
    """Set the bypass value for node fill, label and border opacity for the specified node or nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
        new_values (int or float or list): list of values to set, or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if node or network name doesn't exist, or if opacity values are invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_opacity_bypass(get_node_names(), 128)
        ''
        >>> set_node_opacity_bypass(['YDL194W', 'YBR043C'], [128, 192], network='galFiltered.sif')
        ''
        >>> set_node_opacity_bypass('YDL194W, YBR043C', [128, 192], network='galFiltered.sif')
        ''
        >>> set_node_opacity_bypass([1255, 1988], [128, 192], network='galFiltered.sif')
        ''
        >>> set_node_opacity_bypass('1255, 1988', [128, 192], network='galFiltered.sif')
        ''
        >>> set_node_opacity_bypass(1255, 128)
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    # TODO: Concerned about losing intermediate res results
    res = set_node_property_bypass(node_names, new_values, 'NODE_TRANSPARENCY', network=network, base_url=base_url)
    res = set_node_property_bypass(node_names, new_values, 'NODE_BORDER_TRANSPARENCY', network=network,
                                   base_url=base_url)
    res = set_node_property_bypass(node_names, new_values, 'NODE_LABEL_TRANSPARENCY', network=network,
                                   base_url=base_url)
    return res


@cy_log
def clear_node_opacity_bypass(node_names, network=None, base_url=DEFAULT_BASE_URL):
    """Clear Node Opacity Bypass.

    Clear the bypass value for node fill, label and border opacity for the specified node or nodes, effectively
    restoring any previously defined style defaults or mappings.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
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
        ''
        >>> clear_node_opacity_bypass(['YDL194W', 'YBR043C'], network='galFiltered.sif')
        ''
        >>> clear_node_opacity_bypass('YDL194W, YBR043C', network='galFiltered.sif')
        ''
        >>> clear_node_opacity_bypass([1255, 1988], network='galFiltered.sif')
        ''
        >>> clear_node_opacity_bypass('1255, 1988', network='galFiltered.sif')
        ''
        >>> clear_node_opacity_bypass(1255)
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`set_node_opacity_bypass`
    """
    res = clear_node_property_bypass(node_names, 'NODE_TRANSPARENCY', network=network, base_url=base_url)
    res = clear_node_property_bypass(node_names, 'NODE_BORDER_TRANSPARENCY', network=network, base_url=base_url)
    res = clear_node_property_bypass(node_names, 'NODE_LABEL_TRANSPARENCY', network=network, base_url=base_url)
    return res
    # TODO: What kind of return result should there be, and what about losing intermediate return results?


@cy_log
def set_node_fill_opacity_bypass(node_names, new_values, network=None, base_url=DEFAULT_BASE_URL):
    """Override the fill opacity for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
        new_values (int or float or list): list of values to set, or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if node or network name doesn't exist, or if opacity is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_fill_opacity_bypass(get_node_names(), 128)
        ''
        >>> set_node_fill_opacity_bypass(['YDL194W', 'YBR043C'], [128, 192], network='galFiltered.sif')
        ''
        >>> set_node_fill_opacity_bypass('YDL194W, YBR043C', [128, 192], network='galFiltered.sif')
        ''
        >>> set_node_fill_opacity_bypass([1255, 1988], [128, 192], network='galFiltered.sif')
        ''
        >>> set_node_fill_opacity_bypass('1255, 1988', [128, 192], network='galFiltered.sif')
        ''
        >>> set_node_fill_opacity_bypass(1255, 128)
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    res = set_node_property_bypass(node_names, new_values, 'NODE_TRANSPARENCY', network=network, base_url=base_url)
    return res


@cy_log
def set_node_border_opacity_bypass(node_names, new_values, network=None, base_url=DEFAULT_BASE_URL):
    """Override the border opacity for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
        new_values (int or float or list): list of values to set, or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if node or network name doesn't exist, or if opacity is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_border_opacity_bypass(get_node_names(), 128)
        ''
        >>> set_node_border_opacity_bypass(['YDL194W', 'YBR043C'], [128, 192], network='galFiltered.sif')
        ''
        >>> set_node_border_opacity_bypass('YDL194W, YBR043C', [128, 192], network='galFiltered.sif')
        ''
        >>> set_node_border_opacity_bypass([1255, 1988], [128, 192], network='galFiltered.sif')
        ''
        >>> set_node_border_opacity_bypass('1255, 1988', [128, 192], network='galFiltered.sif')
        ''
        >>> set_node_border_opacity_bypass(1255, 128)
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    res = set_node_property_bypass(node_names, new_values, 'NODE_BORDER_TRANSPARENCY', network=network,
                                   base_url=base_url)
    return res


@cy_log
def set_node_label_opacity_bypass(node_names, new_values, network=None, base_url=DEFAULT_BASE_URL):
    """Override the label opacity for particular nodes.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_node_property_bypass()``, see examples.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
        new_values (int or float or list): list of values to set, or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if node or network name doesn't exist, or if opacity is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_label_opacity_bypass(get_node_names(), 128)
        ''
        >>> set_node_label_opacity_bypass(['YDL194W', 'YBR043C'], [128, 192], network='galFiltered.sif')
        ''
        >>> set_node_label_opacity_bypass('YDL194W, YBR043C', [128, 192], network='galFiltered.sif')
        ''
        >>> set_node_label_opacity_bypass([1255, 1988], [128, 192], network='galFiltered.sif')
        ''
        >>> set_node_label_opacity_bypass('1255, 1988', [128, 192], network='galFiltered.sif')
        ''
        >>> set_node_label_opacity_bypass(1255, 128)
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    res = set_node_property_bypass(node_names, new_values, 'NODE_LABEL_TRANSPARENCY', network=network,
                                   base_url=base_url)
    return res


@cy_log
def hide_selected_nodes(network=None, base_url=DEFAULT_BASE_URL):
    """Hide Selected Nodes.

    Hide (but do not delete) the currently selected nodes, by setting the Visible property bypass value to false.

    This method permanently overrides any default values or mappings defined for this visual property of the node
    or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``, which
    can be used to set any visual property. To restore defaults and mappings, use ``unhide_nodes()`` or ``unhide_all()``.

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
        >>> hide_selected_nodes()
        ''
        >>> hide_selected_nodes(network='galFiltered.sif')
        ''

    See Also:
        :meth:`set_node_property_bypass`, :meth:`hide_nodes`, :meth:`unhide_nodes`, :meth:`unhide_all`
    """
    node_names = network_selection.get_selected_nodes(network=network, base_url=base_url)
    res = set_node_property_bypass(node_names, False, 'NODE_VISIBLE', network=network, base_url=base_url)
    return res


@cy_log
def hide_nodes(node_names, network=None, base_url=DEFAULT_BASE_URL):
    """Hide Nodes.

    Hide (but do not delete) the specified node or nodes, by setting the Visible property bypass value to false.

    This method permanently overrides any default values or mappings defined for this visual property of the node
    or nodes specified. This method ultimately calls the generic function, ``set_node_property_bypass()``, which
    can be used to set any visual property. To restore defaults and mappings, use ``unhide_nodes()`` or ``unhide_all()``.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
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
        >>> hide_nodes(get_node_names())
        ''
        >>> hide_nodes(['YDL194W', 'YBR043C'], network='galFiltered.sif')
        ''
        >>> hide_nodes('YDL194W, YBR043C', network='galFiltered.sif')
        ''
        >>> hide_nodes([1255, 1988], network='galFiltered.sif')
        ''
        >>> hide_nodes('1255, 1988', network='galFiltered.sif')
        ''
        >>> hide_nodes(1255, network='galFiltered.sif')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`set_node_property_bypass`, :meth:`hide_nodes`, :meth:`unhide_nodes`, :meth:`unhide_all`
    """
    res = set_node_property_bypass(node_names, False, 'NODE_VISIBLE', network=network, base_url=base_url)
    return res


@cy_log
def unhide_nodes(node_names, network=None, base_url=DEFAULT_BASE_URL):
    """Unhide Nodes.

    Unhide specified nodes that were previously hidden, by clearing the Node Visible property bypass value.

    This method ultimately calls the generic function, ``clear_node_property_bypass()``, which can be used to
    clear any visual property.

    Args:
        node_names (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``name`` column of the ``nodes table``.
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
        >>> hide_nodes(get_node_names())
        ''
        >>> hide_nodes(['YDL194W', 'YBR043C'], network='galFiltered.sif')
        ''
        >>> hide_nodes('YDL194W, YBR043C', network='galFiltered.sif')
        ''
        >>> hide_nodes([1255, 1988], network='galFiltered.sif')
        ''
        >>> hide_nodes('1255, 1988', network='galFiltered.sif')
        ''
        >>> hide_nodes(1255)
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.

    See Also:
        :meth:`clear_node_property_bypass`, :meth:`unhide_all`
    """
    res = clear_node_property_bypass(node_names, 'NODE_VISIBLE', network=network, base_url=base_url)
    return res


# ==============================================================================
# II.b. Edge Properties
# Pattern: (1) validate input value, (2) call setEdgePropertyBypass()
# ------------------------------------------------------------------------------

@cy_log
def set_edge_opacity_bypass(edge_names, new_values, network=None, base_url=DEFAULT_BASE_URL):
    """Override the opacity for particular edges.

    This method permanently overrides any default values or mappings defined for this visual property
    of the node or nodes specified. This method ultimately calls the generic function, ``set_edge_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_edge_property_bypass()``, see examples.

    Args:
        edge_names (str or list or int or None): List of edges as ``list`` of edge names or SUIDs,
            comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID. Edge names should be found in the ``name`` column of the ``edges table``.
        new_values (int or float or list): list of values to set, or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if edge or network name doesn't exist, or if opacity is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_opacity_bypass(get_edge_names(), 128)
        ''
        >>> set_edge_opacity_bypass(['YJR022W (pp) YNL050C', 'YJR022W (pp) YNR050C'], [128, 192], network='galFiltered.sif')
        ''
        >>> set_edge_opacity_bypass('YJR022W (pp) YNL050C, YJR022W (pp) YNR050C', [128, 192], network='galFiltered.sif')
        ''
        >>> set_edge_opacity_bypass([10288, 16300], [128, 192], network='galFiltered.sif')
        ''
        >>> set_edge_opacity_bypass('10288, 16300', [128, 192], network='galFiltered.sif')
        ''
        >>> set_edge_opacity_bypass(10288, 128)
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1 (pd) node\\\\,2' identifies 'node1 (pd) node,2'.

    See Also:
        :meth:`set_node_property_bypass`, :meth:`clear_node_property_bypass`
    """
    # TODO: Concerned about losing intermediate res results
    res = set_edge_property_bypass(edge_names, new_values, 'EDGE_LABEL_TRANSPARENCY', network=network,
                                   base_url=base_url)
    res = set_edge_property_bypass(edge_names, new_values, 'EDGE_TRANSPARENCY', network=network, base_url=base_url)
    return res


@cy_log
def set_edge_color_bypass(edge_names, new_colors, network=None, base_url=DEFAULT_BASE_URL):
    """Set the bypass value for fill color for the specified edge or edges.

    This method permanently overrides any default values or mappings defined for this visual property
    of the edge or edges specified. This method ultimately calls the generic function, ``set_edge_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_edge_property_bypass()``, see examples.

    Args:
        edge_names (str or list or int or None): List of edges as ``list`` of edge names or SUIDs,
            comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID. Edge names should be found in the ``name`` column of the ``edges table``.
        new_colors (str or list): list of hex colors or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: '' (None if invalid color is found in new_colors)

    Raises:
        CyError: if invalid color, or if edge or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_color_bypass(get_edge_names(), '#FF00FF')
        ''
        >>> set_edge_color_bypass(get_edge_names(), 'red')
        ''
        >>> set_edge_color_bypass(['YJR022W (pp) YNL050C', 'YJR022W (pp) YNR050C'], ['#FF00FF', '#CCCCCC'], network='galFiltered.sif')
        ''
        >>> set_edge_color_bypass('YJR022W (pp) YNL050C, YJR022W (pp) YNR050C', ['#FF00FF', '#CCCCCC'], network='galFiltered.sif')
        ''
        >>> set_edge_color_bypass([10288, 16300], ['#FF00FF', '#CCCCCC'], network='galFiltered.sif')
        ''
        >>> set_edge_color_bypass('10288, 16300', ['#FF00FF', 'blue'], network='galFiltered.sif')
        ''
        >>> set_edge_color_bypass(10288, '#FF00FF')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1 (pd) node\\\\,2' identifies 'node1 (pd) node,2'.

    See Also:
        :meth:`set_edge_property_bypass`, :meth:`clear_edge_property_bypass`
    """
    # TODO: What to do about lost res?
    res = set_edge_property_bypass(edge_names, new_colors, 'EDGE_STROKE_UNSELECTED_PAINT', network=network,
                                   base_url=base_url)
    res = set_edge_property_bypass(edge_names, new_colors, 'EDGE_UNSELECTED_PAINT', network=network, base_url=base_url)
    return res


@cy_log
def set_edge_label_bypass(edge_names, new_labels, network=None, base_url=DEFAULT_BASE_URL):
    """Override the label for particular edges.

    This method permanently overrides any default values or mappings defined for this visual property
    of the edge or edges specified. This method ultimately calls the generic function, ``set_edge_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_edge_property_bypass()``, see examples.

    Args:
        edge_names (str or list or int or None): List of edges as ``list`` of edge names or SUIDs,
            comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID. Edge names should be found in the ``name`` column of the ``edges table``.
        new_labels (str or list): list of label values or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if edge or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_label_bypass(get_edge_names(), 'test label')
        ''
        >>> set_edge_label_bypass(['YJR022W (pp) YNL050C', 'YJR022W (pp) YNR050C'], ['A', 'B'], network='galFiltered.sif')
        ''
        >>> set_edge_label_bypass('YJR022W (pp) YNL050C, YJR022W (pp) YNR050C', ['A', 'B'], network='galFiltered.sif')
        ''
        >>> set_edge_label_bypass([10288, 16300], ['A', 'B'], network='galFiltered.sif')
        ''
        >>> set_edge_label_bypass('10288, 16300', ['A', 'B'], network='galFiltered.sif')
        ''
        >>> set_edge_label_bypass(10288, 'test label')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1 (pd) node\\\\,2' identifies 'node1 (pd) node,2'.

    See Also:
        :meth:`set_edge_property_bypass`, :meth:`clear_edge_property_bypass`
    """
    res = set_edge_property_bypass(edge_names, new_labels, 'EDGE_LABEL', network=network, base_url=base_url)
    return res


@cy_log
def set_edge_font_face_bypass(edge_names, new_fonts, network=None, base_url=DEFAULT_BASE_URL):
    """Override the font face for particular edges.

    This method permanently overrides any default values or mappings defined for this visual property
    of the edge or edges specified. This method ultimately calls the generic function, ``set_edge_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_edge_property_bypass()``, see examples.

    Args:
        edge_names (str or list or int or None): List of edges as ``list`` of edge names or SUIDs,
            comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID. Edge names should be found in the ``name`` column of the ``edges table``.
        new_fonts (str or list): list of font values or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if edge or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_font_face_bypass(get_edge_names(), 'Dialog.italic,plain,20')
        ''
        >>> set_edge_font_face_bypass(['YJR022W (pp) YNL050C', 'YJR022W (pp) YNR050C'], ['Dialog.italic,plain,20', 'Dialog.bold,plain,10'], network='galFiltered.sif')
        ''
        >>> set_edge_font_face_bypass('YJR022W (pp) YNL050C, YJR022W (pp) YNR050C', ['Dialog.italic,plain,20', 'Dialog.bold,plain,10'], network='galFiltered.sif')
        ''
        >>> set_edge_font_face_bypass([10288, 16300], ['Dialog.italic,plain,20', 'Dialog.bold,plain,10'], network='galFiltered.sif')
        ''
        >>> set_edge_font_face_bypass('10288, 16300', ['Dialog.italic,plain,20', 'Dialog.bold,plain,10'], network='galFiltered.sif')
        ''
        >>> set_edge_font_face_bypass(10288, 'Dialog.italic,plain,20')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1 (pd) node\\\\,2' identifies 'node1 (pd) node,2'.

    See Also:
        :meth:`set_edge_property_bypass`, :meth:`clear_edge_property_bypass`
    """
    res = set_edge_property_bypass(edge_names, new_fonts, 'EDGE_LABEL_FONT_FACE', network=network, base_url=base_url)
    return res


@cy_log
def set_edge_font_size_bypass(edge_names, new_sizes, network=None, base_url=DEFAULT_BASE_URL):
    """Override the font size for particular edges.

    This method permanently overrides any default values or mappings defined for this visual property
    of the edge or edges specified. This method ultimately calls the generic function, ``set_edge_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_edge_property_bypass()``, see examples.

    Args:
        edge_names (str or list or int or None): List of edges as ``list`` of edge names or SUIDs,
            comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID. Edge names should be found in the ``name`` column of the ``edges table``.
        new_sizes (int or float or list): list of font sizes or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if edge or network name doesn't exist, or if size is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_font_size_bypass(get_edge_names(), 20)
        ''
        >>> set_edge_font_size_bypass(['YJR022W (pp) YNL050C', 'YJR022W (pp) YNR050C'], [50, 100], network='galFiltered.sif')
        ''
        >>> set_edge_font_size_bypass('YJR022W (pp) YNL050C, YJR022W (pp) YNR050C', [50, 100], network='galFiltered.sif')
        ''
        >>> set_edge_font_size_bypass([10288, 16300], [50, 100], network='galFiltered.sif')
        ''
        >>> set_edge_font_size_bypass('10288, 16300', [50, 100], network='galFiltered.sif')
        ''
        >>> set_edge_font_size_bypass(10288, 20)
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1 (pd) node\\\\,2' identifies 'node1 (pd) node,2'.

    See Also:
        :meth:`set_edge_property_bypass`, :meth:`clear_edge_property_bypass`
    """
    res = set_edge_property_bypass(edge_names, new_sizes, 'EDGE_LABEL_FONT_SIZE', network=network,
                                   base_url=base_url)
    return res


@cy_log
def set_edge_label_color_bypass(edge_names, new_colors, network=None, base_url=DEFAULT_BASE_URL):
    """Override the label color for particular edges.

    This method permanently overrides any default values or mappings defined for this visual property
    of the edge or edges specified. This method ultimately calls the generic function, ``set_edge_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_edge_property_bypass()``, see examples.

    Args:
        edge_names (str or list or int or None): List of edges as ``list`` of edge names or SUIDs,
            comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID. Edge names should be found in the ``name`` column of the ``edges table``.
        new_colors (str or list):  list of hex colors, or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if invalid color, or if edge or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_label_color_bypass(get_edge_names(), '#FF00FF')
        ''
        >>> set_edge_label_color_bypass(get_edge_names(), 'red')
        ''
        >>> set_edge_label_color_bypass(['YJR022W (pp) YNL050C', 'YJR022W (pp) YNR050C'], ['#FF00FF', '#FFFF00'], network='galFiltered.sif')
        ''
        >>> set_edge_label_color_bypass('YJR022W (pp) YNL050C, YJR022W (pp) YNR050C', ['#FF00FF', '#FFFF00'], network='galFiltered.sif')
        ''
        >>> set_edge_label_color_bypass([10288, 16300], ['#FF00FF', '#FFFF00'], network='galFiltered.sif')
        ''
        >>> set_edge_label_color_bypass('10288, 16300', ['#FF00FF', 'blue'], network='galFiltered.sif')
        ''
        >>> set_edge_label_color_bypass(10288, '#FF00FF')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1 (pd) node\\\\,2' identifies 'node1 (pd) node,2'.

    See Also:
        :meth:`set_edge_property_bypass`, :meth:`clear_edge_property_bypass`
    """
    res = set_edge_property_bypass(edge_names, new_colors, 'EDGE_LABEL_COLOR', network=network, base_url=base_url)

    return res


@cy_log
def set_edge_tooltip_bypass(edge_names, new_tooltip, network=None, base_url=DEFAULT_BASE_URL):
    """Sets a bypass tooltip for one or more edges.

    This method permanently overrides any default values or mappings defined for this visual property
    of the edge or edges specified. This method ultimately calls the generic function, ``set_edge_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_edge_property_bypass()``, see examples.

    Args:
        edge_names (str or list or int or None): List of edges as ``list`` of edge names or SUIDs,
            comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID. Edge names should be found in the ``name`` column of the ``edges table``.
        new_tooltip (str or list): list of size values or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if edge or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_tooltip_bypass(get_edge_names(), 'Some Tooltip')
        ''
        >>> set_edge_tooltip_bypass(['YJR022W (pp) YNL050C', 'YJR022W (pp) YNR050C'], ['One Tooltip', 'Other Tooltip'], network='galFiltered.sif')
        ''
        >>> set_edge_tooltip_bypass('YJR022W (pp) YNL050C, YJR022W (pp) YNR050C', ['One Tooltip', 'Other Tooltip'], network='galFiltered.sif')
        ''
        >>> set_edge_tooltip_bypass([10288, 16300], ['One Tooltip', 'Other Tooltip'], network='galFiltered.sif')
        ''
        >>> set_edge_tooltip_bypass('10288, 16300', ['One Tooltip', 'Other Tooltip'], network='galFiltered.sif')
        ''
        >>> set_edge_tooltip_bypass(10288, 'Some Tooltip')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1 (pd) node\\\\,2' identifies 'node1 (pd) node,2'.

    See Also:
        :meth:`set_edge_property_bypass`, :meth:`clear_edge_property_bypass`
    """
    res = set_edge_property_bypass(edge_names, new_tooltip, 'EDGE_TOOLTIP', network=network, base_url=base_url)
    return res


@cy_log
def set_edge_line_width_bypass(edge_names, new_widths, network=None, base_url=DEFAULT_BASE_URL):
    """Override the width for particular edges.

    This method permanently overrides any default values or mappings defined for this visual property
    of the edge or edges specified. This method ultimately calls the generic function, ``set_edge_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_edge_property_bypass()``, see examples.

    Args:
        edge_names (str or list or int or None): List of edges as ``list`` of edge names or SUIDs,
            comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID. Edge names should be found in the ``name`` column of the ``edges table``.
        new_widths (int or float or list): list of width values or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if edge or network name doesn't exist, or if width is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_width_bypass(get_edge_names(), 80)
        ''
        >>> set_edge_width_bypass(['YJR022W (pp) YNL050C', 'YJR022W (pp) YNR050C'], [80, 100.5], network='galFiltered.sif')
        ''
        >>> set_edge_width_bypass('YJR022W (pp) YNL050C, YJR022W (pp) YNR050C', [80, 100.5], network='galFiltered.sif')
        ''
        >>> set_edge_width_bypass([10288, 16300], [80, 100.5], network='galFiltered.sif')
        ''
        >>> set_edge_width_bypass('10288, 16300', [80, 100.5], network='galFiltered.sif')
        ''
        >>> set_edge_width_bypass(10288, 80)
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1 (pd) node\\\\,2' identifies 'node1 (pd) node,2'.

    See Also:
        :meth:`set_edge_property_bypass`, :meth:`clear_edge_property_bypass`
    """
    res = set_edge_property_bypass(edge_names, new_widths, 'EDGE_WIDTH', network=network, base_url=base_url)
    return res


@cy_log
def set_edge_line_style_bypass(edge_names, new_styles, network=None, base_url=DEFAULT_BASE_URL):
    """Override the style for particular edges.

    This method permanently overrides any default values or mappings defined for this visual property
    of the edge or edges specified. This method ultimately calls the generic function, ``set_edge_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_edge_property_bypass()``, see examples.

    Args:
        edge_names (str or list or int or None): List of edges as ``list`` of edge names or SUIDs,
            comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID. Edge names should be found in the ``name`` column of the ``edges table``.
        new_styles (str or list):  List of styles, or single value.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if edge or network name doesn't exist, or if syle is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_shape_bypass(get_edge_names(), 'SOLID')
        ''
        >>> set_edge_shape_bypass(['YJR022W (pp) YNL050C', 'YJR022W (pp) YNR050C'], ['SOLID', 'ZIGZAG'], network='galFiltered.sif')
        ''
        >>> set_edge_shape_bypass('YJR022W (pp) YNL050C, YJR022W (pp) YNR050C', ['SOLID', 'ZIGZAG'], network='galFiltered.sif')
        ''
        >>> set_edge_shape_bypass([10288, 16300], ['SOLID', 'ZIGZAG'], network='galFiltered.sif')
        ''
        >>> set_edge_shape_bypass('10288, 16300', ['SOLID', 'ZIGZAG'], network='galFiltered.sif')
        ''
        >>> set_edge_shape_bypass(10288, 'SOLID')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1 (pd) node\\\\,2' identifies 'node1 (pd) node,2'.

    See Also:
        :meth:`set_edge_property_bypass`, :meth:`clear_edge_property_bypass`
    """
    res = set_edge_property_bypass(edge_names, new_styles, 'EDGE_LINE_TYPE', network=network, base_url=base_url)

    return res


@cy_log
def set_edge_source_arrow_shape_bypass(edge_names, new_shapes, network=None, base_url=DEFAULT_BASE_URL):
    """Override the source arrow shape for particular edges.

    This method permanently overrides any default values or mappings defined for this visual property
    of the edge or edges specified. This method ultimately calls the generic function, ``set_edge_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_edge_property_bypass()``, see examples.

    Args:
        edge_names (str or list or int or None): List of edges as ``list`` of edge names or SUIDs,
            comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID. Edge names should be found in the ``name`` column of the ``edges table``.
        new_shapes (str or list):  List of styles, or single value.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if edge or network name doesn't exist, or if shape is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_source_arrow_shape_bypass(get_edge_names(), 'ARROW')
        ''
        >>> set_edge_source_arrow_shape_bypass(['YJR022W (pp) YNL050C', 'YJR022W (pp) YNR050C'], ['DIAMOND', 'CIRCLE'], network='galFiltered.sif')
        ''
        >>> set_edge_source_arrow_shape_bypass('YJR022W (pp) YNL050C, YJR022W (pp) YNR050C', ['DIAMOND', 'CIRCLE'], network='galFiltered.sif')
        ''
        >>> set_edge_source_arrow_shape_bypass([10288, 16300], ['DIAMOND', 'CIRCLE'], network='galFiltered.sif')
        ''
        >>> set_edge_source_arrow_shape_bypass('10288, 16300', ['DIAMOND', 'CIRCLE'], network='galFiltered.sif')
        ''
        >>> set_edge_source_arrow_shape_bypass(10288, 'ARROW')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1 (pd) node\\\\,2' identifies 'node1 (pd) node,2'.

    See Also:
        :meth:`set_edge_property_bypass`, :meth:`clear_edge_property_bypass`
    """
    res = set_edge_property_bypass(edge_names, new_shapes, 'EDGE_SOURCE_ARROW_SHAPE', network=network,
                                   base_url=base_url)

    return res


@cy_log
def set_edge_target_arrow_shape_bypass(edge_names, new_shapes, network=None, base_url=DEFAULT_BASE_URL):
    """Override the target arrow shape for particular edges.

    This method permanently overrides any default values or mappings defined for this visual property
    of the edge or edges specified. This method ultimately calls the generic function, ``set_edge_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_edge_property_bypass()``, see examples.

    Args:
        edge_names (str or list or int or None): List of edges as ``list`` of edge names or SUIDs,
            comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID. Edge names should be found in the ``name`` column of the ``edges table``.
        new_shapes (str or list):  List of styles, or single value.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if edge or network name doesn't exist, or if shape is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_target_arrow_shape_bypass(get_edge_names(), 'ARROW')
        ''
        >>> set_edge_target_arrow_shape_bypass(['YJR022W (pp) YNL050C', 'YJR022W (pp) YNR050C'], ['DIAMOND', 'CIRCLE'], network='galFiltered.sif')
        ''
        >>> set_edge_target_arrow_shape_bypass('YJR022W (pp) YNL050C, YJR022W (pp) YNR050C', ['DIAMOND', 'CIRCLE'], network='galFiltered.sif')
        ''
        >>> set_edge_target_arrow_shape_bypass([10288, 16300], ['DIAMOND', 'CIRCLE'], network='galFiltered.sif')
        ''
        >>> set_edge_target_arrow_shape_bypass('10288, 16300', ['DIAMOND', 'CIRCLE'], network='galFiltered.sif')
        ''
        >>> set_edge_target_arrow_shape_bypass(10288, 'ARROW')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1 (pd) node\\\\,2' identifies 'node1 (pd) node,2'.

    See Also:
        :meth:`set_edge_property_bypass`, :meth:`clear_edge_property_bypass`
    """
    res = set_edge_property_bypass(edge_names, new_shapes, 'EDGE_TARGET_ARROW_SHAPE', network=network,
                                   base_url=base_url)

    return res


@cy_log
def set_edge_source_arrow_color_bypass(edge_names, new_colors, network=None, base_url=DEFAULT_BASE_URL):
    """Override the target arrow color for particular edges.

    This method permanently overrides any default values or mappings defined for this visual property
    of the edge or edges specified. This method ultimately calls the generic function, ``set_edge_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_edge_property_bypass()``, see examples.

    Args:
        edge_names (str or list or int or None): List of edges as ``list`` of edge names or SUIDs,
            comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID. Edge names should be found in the ``name`` column of the ``edges table``.
        new_colors (str or list):  list of hex colors, or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if invalid color, or if edge or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1 (pd) node\\\\,2' identifies 'node1 (pd) node,2'.

    Examples:
        >>> set_edge_label_color_bypass(get_edge_names(), '#FF00FF')
        ''
        >>> set_edge_label_color_bypass(get_edge_names(), 'red')
        ''
        >>> set_edge_label_color_bypass(['YJR022W (pp) YNL050C', 'YJR022W (pp) YNR050C'], ['#FF00FF', '#FFFF00'], network='galFiltered.sif')
        ''
        >>> set_edge_label_color_bypass('YJR022W (pp) YNL050C, YJR022W (pp) YNR050C', ['#FF00FF', '#FFFF00'], network='galFiltered.sif')
        ''
        >>> set_edge_label_color_bypass([10288, 16300], ['#FF00FF', '#FFFF00'], network='galFiltered.sif')
        ''
        >>> set_edge_label_color_bypass('10288, 16300', ['#FF00FF', 'blue'], network='galFiltered.sif')
        ''
        >>> set_edge_label_color_bypass(10288, '#FF00FF')
        ''

    See Also:
        :meth:`set_edge_property_bypass`, :meth:`clear_edge_property_bypass`
    """
    res = set_edge_property_bypass(edge_names, new_colors, 'EDGE_SOURCE_ARROW_UNSELECTED_PAINT', network=network,
                                   base_url=base_url)

    return res


@cy_log
def set_edge_target_arrow_color_bypass(edge_names, new_colors, network=None, base_url=DEFAULT_BASE_URL):
    """Override the target arrow color for particular edges.

    This method permanently overrides any default values or mappings defined for this visual property
    of the edge or edges specified. This method ultimately calls the generic function, ``set_edge_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_edge_property_bypass()``, see examples.

    Args:
        edge_names (str or list or int or None): List of edges as ``list`` of edge names or SUIDs,
            comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID. Edge names should be found in the ``name`` column of the ``edges table``.
        new_colors (str or list):  list of hex colors, or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if invalid color, or if edge or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_label_color_bypass(get_edge_names(), '#FF00FF')
        ''
        >>> set_edge_label_color_bypass(get_edge_names(), 'red')
        ''
        >>> set_edge_label_color_bypass(['YJR022W (pp) YNL050C', 'YJR022W (pp) YNR050C'], ['#FF00FF', '#FFFF00'], network='galFiltered.sif')
        ''
        >>> set_edge_label_color_bypass('YJR022W (pp) YNL050C, YJR022W (pp) YNR050C', ['#FF00FF', '#FFFF00'], network='galFiltered.sif')
        ''
        >>> set_edge_label_color_bypass([10288, 16300], ['#FF00FF', '#FFFF00'], network='galFiltered.sif')
        ''
        >>> set_edge_label_color_bypass('10288, 16300', ['#FF00FF', 'blue'], network='galFiltered.sif')
        ''
        >>> set_edge_label_color_bypass(10288, '#FF00FF')
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1 (pd) node\\\\,2' identifies 'node1 (pd) node,2'.

    See Also:
        :meth:`set_edge_property_bypass`, :meth:`clear_edge_property_bypass`
    """
    res = set_edge_property_bypass(edge_names, new_colors, 'EDGE_TARGET_ARROW_UNSELECTED_PAINT', network=network,
                                   base_url=base_url)

    return res


@cy_log
def set_edge_label_opacity_bypass(edge_names, new_values, network=None, base_url=DEFAULT_BASE_URL):
    """Override the label opacity for particular edges.

    This method permanently overrides any default values or mappings defined for this visual property
    of the edge or edges specified. This method ultimately calls the generic function, ``set_edge_property_bypass()``
    which can be used to set any visual property. To restore defaults and mappings, use
    ``clear_edge_property_bypass()``, see examples.

    Args:
        edge_names (str or list or int or None): List of edges as ``list`` of edge names or SUIDs,
            comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID. Edge names should be found in the ``name`` column of the ``edges table``.
        new_values (int or float or list): list of values to set, or single value
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: '' (None if invalid opacity is found in new_values)

    Raises:
        CyError: if edge or network name doesn't exist, or if opacity is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_label_opacity_bypass(get_edge_names(), 128)
        ''
        >>> set_edge_label_opacity_bypass(['YJR022W (pp) YNL050C', 'YJR022W (pp) YNR050C'], [128, 192], network='galFiltered.sif')
        ''
        >>> set_edge_label_opacity_bypass('YJR022W (pp) YNL050C, YJR022W (pp) YNR050C', [128, 192], network='galFiltered.sif')
        ''
        >>> set_edge_label_opacity_bypass([10288, 16300], [128, 192], network='galFiltered.sif')
        ''
        >>> set_edge_label_opacity_bypass('10288, 16300', [128, 192], network='galFiltered.sif')
        ''
        >>> set_edge_label_opacity_bypass(10288, 128)
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1 (pd) node\\\\,2' identifies 'node1 (pd) node,2'.

    See Also:
        :meth:`set_edge_property_bypass`, :meth:`clear_edge_property_bypass`
    """
    res = set_edge_property_bypass(edge_names, new_values, 'EDGE_LABEL_TRANSPARENCY', network=network,
                                   base_url=base_url)
    return res


@cy_log
def hide_selected_edges(network=None, base_url=DEFAULT_BASE_URL):
    """Hide Selected Edges.

    Hide (but do not delete) the currently selected edges, by setting the Visible property bypass value to false.

    This method permanently overrides any default values or mappings defined for this visual property of the edge
    or edges specified. This method ultimately calls the generic function, ``set_edge_property_bypass()``, which
    can be used to set any visual property. To restore defaults and mappings, use ``unhide_edges()`` or ``unhide_all()``.

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
        >>> hide_selected_edges()
        ''
        >>> hide_selected_edges(network='galFiltered.sif')
        ''

    See Also:
        :meth:`set_edge_property_bypass`, :meth:`hide_edges`, :meth:`unhide_edges`, :meth:`unhide_all`
    """
    edge_names = network_selection.get_selected_edges(network=network, base_url=base_url)
    res = set_edge_property_bypass(edge_names, False, 'EDGE_VISIBLE', network=network, base_url=base_url)
    return res


@cy_log
def hide_edges(edge_names, network=None, base_url=DEFAULT_BASE_URL):
    """Hide Edges.

    Hide (but do not delete) the specified edge or edges, by setting the Visible property bypass value to false.

    This method permanently overrides any default values or mappings defined for this visual property of the edge
    or edges specified. This method ultimately calls the generic function, ``set_edge_property_bypass()``, which
    can be used to set any visual property. To restore defaults and mappings, use ``unhide_edges()`` or ``unhide_all()``.

    Args:
        edge_names (str or list or int or None): List of edges as ``list`` of edge names or SUIDs,
            comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID. Edge names should be found in the ``name`` column of the ``edges table``.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if edge or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> hide_edges(get_edge_names())
        ''
        >>> hide_edges(['YJR022W (pp) YNL050C', 'YJR022W (pp) YNR050C'], network='galFiltered.sif')
        ''
        >>> hide_edges('YJR022W (pp) YNL050C, YJR022W (pp) YNR050C', network='galFiltered.sif')
        ''
        >>> hide_edges([10288, 16300], network='galFiltered.sif')
        ''
        >>> hide_edges('10288, 16300', network='galFiltered.sif')
        ''
        >>> hide_edges(10288)
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1 (pd) node\\\\,2' identifies 'node1 (pd) node,2'.

    See Also:
        :meth:`set_edge_property_bypass`, :meth:`hide_edges`, :meth:`unhide_edges`, :meth:`unhide_all`
    """
    res = set_edge_property_bypass(edge_names, False, 'EDGE_VISIBLE', network=network, base_url=base_url)
    return res


@cy_log
def unhide_edges(edge_names, network=None, base_url=DEFAULT_BASE_URL):
    """Unhide Edges.

    Unhide specified edges that were previously hidden, by clearing the edge Visible property bypass value.

    This method ultimately calls the generic function, ``clear_edge_property_bypass()``, which can be used to
    clear any visual property.

    Args:
        edge_names (str or list or int or None): List of edges as ``list`` of edge names or SUIDs,
            comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID. Edge names should be found in the ``name`` column of the ``edges table``.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'data': {}, 'errors': []}

    Raises:
        CyError: if edge or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> unhide_edges(get_edge_names())
        ''
        >>> unhide_edges(['YJR022W (pp) YNL050C', 'YJR022W (pp) YNR050C'], network='galFiltered.sif')
        ''
        >>> unhide_edges('YJR022W (pp) YNL050C, YJR022W (pp) YNR050C', network='galFiltered.sif')
        ''
        >>> unhide_edges([10288, 16300], network='galFiltered.sif')
        ''
        >>> unhide_edges('10288, 16300', network='galFiltered.sif')
        ''
        >>> unhide_edges(10288)
        ''

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1 (pd) node\\\\,2' identifies 'node1 (pd) node,2'.

    See Also:
        :meth:`clear_edge_property_bypass`, :meth:`unhide_all`
    """
    res = clear_edge_property_bypass(edge_names, 'EDGE_VISIBLE', network=network, base_url=base_url)
    return res


# ==============================================================================
# II.c. Network Properties
# Pattern: (1) validate input value, (2) call setNetworkPropertyBypass()
# ------------------------------------------------------------------------------

# TODO: Find out why this bypass=False instead of True like the others ... it messes up clear_network_zoom_bypass()
@cy_log
def set_network_zoom_bypass(new_value, bypass=False, network=None, base_url=DEFAULT_BASE_URL):
    """Set the bypass value for scale factor for the network.

    This method permanently overrides any default values for this visual property. This method ultimately calls
    the generic function, ``set_network_property_bypass()``, which can be used to set any visual property.
    To restore defaults, use ``clear_network_property_bypass()``.

    Args:
        new_value (float): Zoom factor
        bypass (bool): Whether to set permanent bypass value. Default is ``False`` per common use of temporary zoom settings.
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
        >>> set_network_zoom_bypass(1.5, bypass=True)
        ''
        >>> set_network_zoom_bypass(0.25, bypass=True, network='galFiltered.sif')
        ''

    See Also:
        :meth:`set_network_property_bypass`, :meth:`clear_netowrk_property_bypass`
    """
    # TODO: Find out what bypass= is supposed to do
    res = set_network_property_bypass(new_value, 'NETWORK_SCALE_FACTOR', bypass=bypass, network=network,
                                      base_url=base_url)
    return res


@cy_log
def clear_network_zoom_bypass(network=None, base_url=DEFAULT_BASE_URL):
    """Clear the bypass value for the scale factor for the network, effectively restoring prior default values.

    Args:
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'data': {}, 'errors': []}

    Raises:
        CyError: if zoom property or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> clear_network_zoom_bypass()
        {'data': {}, 'errors': []}
        >>> clear_network_zoom_bypass(network='galFiltered.sif')
        {'data': {}, 'errors': []}

    Warning:
        Before clearing the zoom bypass, the zoom bypass must have been set via a call to either
        ``set_network_zoom_bypass()`` or ``set_network_property_bypass()`` with the bypass=True parameter set. Otherwise,
        clearing this property will throw an exception.
    """
    res = clear_network_property_bypass('NETWORK_SCALE_FACTOR', network=network, base_url=base_url)
    return res


# TODO: Find out why this bypass=False instead of True like the others ... it messes up clear_network_zoom_bypass()
@cy_log
def set_network_center_bypass(x, y, bypass=False, network=None, base_url=DEFAULT_BASE_URL):
    """Set the bypass value for center x and y for the network.

    This function could be used to pan and scroll the Cytoscape canvas.

    This method permanently overrides any default values for this visual property. This method ultimately calls
    the generic function, ``set_network_property_bypass()``, which can be used to set any visual property.
    To restore defaults, use ``clear_network_property_bypass()``.

    Args:
        x  (float): Coordinate value, increases going to the right.
        y  (float): Coordinate value, increases going to the down.
        bypass (bool): Whether to set permanent bypass value. Default is ``False`` per common use of temporary zoom settings.
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
        >>> set_network_center_bypass(1.5, bypass=True)
        ''
        >>> set_network_center_bypass(0.25, bypass=True, network='galFiltered.sif')
        ''

    See Also:
        :meth:`set_network_property_bypass`, :meth:`clear_netowrk_property_bypass`
    """
    # TODO: Find out what bypass= is supposed to do
    # TODO: OK to lose first res result?
    res = set_network_property_bypass(x, 'NETWORK_CENTER_X_LOCATION', bypass=bypass, network=network, base_url=base_url)
    res = set_network_property_bypass(y, 'NETWORK_CENTER_Y_LOCATION', bypass=bypass, network=network, base_url=base_url)
    return res


@cy_log
def clear_network_center_bypass(network=None, base_url=DEFAULT_BASE_URL):
    """Clear the bypass value for center x and y for the network, effectively restoring prior default values.

    Args:
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'data': {}, 'errors': []}

    Raises:
        CyError: if center property or network name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> clear_network_center_bypass()
        {'data': {}, 'errors': []}
        >>> clear_network_center_bypass(network='galFiltered.sif')
        {'data': {}, 'errors': []}

    Warning:
        Before clearing the center coordinate bypass, the coordinate bypass must have been set via a call to either
        ``set_network_center_bypass()`` or ``set_network_property_bypass()`` with the bypass=True parameter set. Otherwise,
        clearing this property will throw an exception.
    """
    res = clear_network_property_bypass('NETWORK_CENTER_X_LOCATION', network=network, base_url=base_url)
    res = clear_network_property_bypass('NETWORK_CENTER_Y_LOCATION', network=network, base_url=base_url)
    return res

