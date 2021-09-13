# -*- coding: utf-8 -*-

"""Functions for working with SELECTIONS of nodes and edges in networks, including
operations that perform selection and rely on prior selection events.

I. General selection functions
II. Node selection functions
III. Edge selection functions
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

# Internal module imports
from . import commands
from . import networks

# Internal module convenience imports
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log


# ==============================================================================
# I. General selection functions
# ------------------------------------------------------------------------------

@cy_log
def clear_selection(type='both', network=None, base_url=DEFAULT_BASE_URL):
    """If any nodes are selected in the network, they will be unselected.

    Args:
        type (str): What kinds of objects to deselect: 'nodes', 'edges' or 'both' (default)
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: '' empty

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> clear_selection()
        ''
        >>> clear_selection(type='both')
        ''
        >>> clear_selection(type='nodes', network=52)
        ''
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)

    if type in ['nodes', 'both']:
        res = commands.cyrest_put(f'networks/{net_suid}/tables/defaultnode/columns/selected',
                                  parameters={'default': 'false'}, base_url=base_url, require_json=False)
        # TODO: this result will get lost if type=='both'

    if type in ['edges', 'both']:
        res = commands.cyrest_put(f'networks/{net_suid}/tables/defaultedge/columns/selected',
                                  parameters={'default': 'false'}, base_url=base_url, require_json=False)

    return res


# ==============================================================================
# II. Node selection functions
# ------------------------------------------------------------------------------

@cy_log
def select_first_neighbors(direction='any', network=None, base_url=DEFAULT_BASE_URL):
    """Select nodes directly connected to currently selected nodes.

    Can specify connection directionality using the direction param.

    Args:
        direction (str): direction of connections to neighbors to follow, e.g., incoming, outgoing, undirected, or any (default)
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'nodes': [node list], 'edges': [edge list]}

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> select_first_neighbors()
        {'nodes': [107504, 107503, ...], 'edges': []}
        >>> select_first_neighbors(direction='undirected')
        {'nodes': [107514], 'edges': []}

    Note:
        In the return value, node list is the SUIDs of newly selected nodes and edge list is always empty
    """
    suid = networks.get_network_suid(network, base_url=base_url)
    cmd = f'network select firstNeighbors="{direction}" network=SUID:"{suid}"'
    res = commands.commands_post(cmd, base_url=base_url)
    return res


# TODO: Decide whether 'nodes' can be None ... the RCy3 documentation implies it can, but the code says no
@cy_log
def select_nodes(nodes, by_col='SUID', preserve_current_selection=True, network=None, base_url=DEFAULT_BASE_URL):
    """Select nodes in the network by SUID, name or other column values.

    Args:
        nodes (str or list or int or None): List of nodes as ``list`` of node names or SUIDs,
            comma-separated string of node names or SUIDs, or scalar node name
            or SUID. Node names should be found in the ``SUID`` column of the ``node table`` unless
            specified in ``nodes_by_col``.
        by_col (str): Node table column to lookup up provide node values. Default is 'SUID'.
        preserve_current_selection (bool): Whether to maintain previously selected nodes.
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'nodes': [node list], 'edges': [edge list]}

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> select_nodes(None)
        {}
        >>> select_nodes(['RAP1'], by_col='COMMON')
        {'nodes': [107514], 'edges': []}
        >>> select_nodes('RAP1, HIS4', by_col='COMMON')
        {'nodes': [107514, 107511], 'edges': []}
        >>> select_nodes([107514, 107511])
        {'nodes': [107514, 107511], 'edges': []}
        >>> select_nodes(107514])
        {'nodes': [107514], 'edges': []}

    Note:
        In the return value, node list is the SUIDs of newly selected nodes
        and edge list is always empty -- dict is {} if no nodes were selected
    """
    suid = networks.get_network_suid(network, base_url=base_url)

    if not preserve_current_selection: clear_selection(type='nodes', network=suid, base_url=base_url)

    # TODO: See why R version works with empty nodes list (which should mean "all") or a node list (which is missing a close ")
    if not nodes or nodes == '':  # take care of case where nodes is empty
        node_list_str = ''
    else:
        nodes = normalize_list(nodes)

        # create list of COL:VALUE that includes all requested nodes
        node_list_str = f'{by_col}:{nodes[0]}' # Allow leading or trailing blanks
        for n in range(1, len(nodes)):
            node_list_str += f',{by_col}:{nodes[n]}'
    res = commands.commands_post(f'network select network=SUID:"{suid}" nodeList="{node_list_str}"', base_url=base_url)
    return res


@cy_log
def select_all_nodes(network=None, base_url=DEFAULT_BASE_URL):
    """Selects all nodes in a Cytoscape Network.

    Args:
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: list of SUIDs selected

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> select_all_nodes()
        [107504, 107503, ...]
        >>> select_all_nodes('My Network')
        [107504, 107503, ...]
        >>> select_all_nodes(52)
        [107504, 107503, ...]

    See Also:
        :meth:`select_nodes`
    """
    suid = networks.get_network_suid(network, base_url=base_url)
    all_node_SUIDs = commands.cyrest_get(f'networks/{suid}/nodes', base_url=base_url)

    res = select_nodes(all_node_SUIDs)
    return res['nodes']
    # TODO: Does the RCy3 code work? It's passing an unusual list to CyREST


@cy_log
def get_selected_node_count(network=None, base_url=DEFAULT_BASE_URL):
    """Returns the number of nodes currently selected in the network.

    Args:
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        int: count of selected nodes

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_selected_node_count()
        330
        >>> get_selected_node_count('My Network')
        330
        >>> get_selected_node_count(52)
        330
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.cyrest_get(f'networks/{net_suid}/nodes',
                              parameters={'column': 'selected', 'query': 'true'}, base_url=base_url)
    return len(res)


@cy_log
def get_selected_nodes(node_suids=False, network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the names of all the nodes selected in the network.

    Args:
        node_suids (bool): Whether to return node SUIDs. Default is FALSE to return node names.
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: list of selected SUIDs or node names, or None if no nodes are selected

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_selected_nodes()
        None
        >>> get_selected_nodes(node_suids=False)
        ['YNL216W', 'YPL075W']
        >>> get_selected_nodes(node_suids=True, network='My Network')
        [10235, 10236]
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)

    if get_selected_node_count(net_suid, base_url=base_url) == 0:
        narrate('No nodes selected.')
        return None
    else:
        selected_node_suids = commands.cyrest_get(f'networks/{net_suid}/nodes',
                                                  parameters={'column': 'selected', 'query': 'true'})
        if node_suids:
            return selected_node_suids
        else:
            selected_node_names = node_suid_to_node_name(selected_node_suids, net_suid, base_url=base_url)
            return selected_node_names


@cy_log
def invert_node_selection(network=None, base_url=DEFAULT_BASE_URL):
    """Select all nodes that were not selected and deselect all nodes that were selected.

    Args:
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'nodes': [node list], 'edges': [edge list]}

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> invert_node_selection()
        {'nodes': [107504, 107503, ...], 'edges': []}
        >>> invert_node_selection(network='My Network')
        {'nodes': [107504, 107503, ...], 'edges': []}
        >>> invert_node_selection(network=52)
        {'nodes': [107504, 107503, ...], 'edges': []}

    Note:
        In return value, node list is the SUIDs of newly selected nodes and edge list is always empty.
    """
    suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.commands_post(f'network select invert=nodes network="SUID:{suid}"', base_url=base_url)
    # TODO: Added double quotes to SUID
    return res


@cy_log
def delete_selected_nodes(network=None, base_url=DEFAULT_BASE_URL):
    """Delete currently selected nodes from the network.

    Args:
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'nodes': [node list], 'edges': [edge list]} where node list is the SUIDs of deleted nodes
            and edge list is the SUIDs of deleted edges

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> delete_selected_nodes()
        {'nodes': [107504, 107503, ...], 'edges': [108033, 108034]}
        >>> delete_selected_nodes(network='My Network')
        {'nodes': [107504, 107503, ...], 'edges': [108033, 108034]}
        >>> delete_selected_nodes(network=52)
        {'nodes': [107504, 107503, ...], 'edges': [108033, 108034]}
    """
    title = networks.get_network_name(network, base_url=base_url)
    res = commands.commands_post(f'network delete nodeList=selected network="{title}"', base_url=base_url)
    # TODO: Added double quotes to network title
    return res


@cy_log
def select_nodes_connected_by_selected_edges(network=None, base_url=DEFAULT_BASE_URL):
    """Take currently selected edges and extends the selection to connected nodes, regardless of directionality.

    Args:
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'nodes': [node list], 'edges': [edge list]}

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> select_nodes_connected_by_selected_edges()
        {'nodes': [107504, 107503, ...], 'edges': [108033, 108034]}
        >>> select_nodes_connected_by_selected_edges(network='My Network')
        {'nodes': [107504, 107503, ...], 'edges': [108033, 108034]}
        >>> select_nodes_connected_by_selected_edges(network=52)
        {'nodes': [107504, 107503, ...], 'edges': [108033, 108034]}

    Note:
        In the return value, node list is the SUIDs of selected nodes, and
        edge list is the SUIDs of newly selected edges
    """
    suid = networks.get_network_suid(network, base_url=base_url)
    clear_selection(type='nodes', network=suid, base_url=base_url)
    res = commands.commands_post(f'network select extendEdges="true" edgeList="selected network="{suid}"',
                                 base_url=base_url)
    return res


# ==============================================================================
# II. Edge selection functions
# ------------------------------------------------------------------------------

@cy_log
def select_edges(edges, by_col='SUID', preserve_current_selection=True, network=None, base_url=DEFAULT_BASE_URL):
    """Select edges in the network by SUID, name or other column values.

    Args:
        edges (str or list or int or None): List of edges as ``list`` of edge names or SUIDs,
            comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID. Edge names should be found in the ``SUID`` column of the ``edge table`` unless
            specified in ``edges_by_col``.
        by_col (str): Edge table column to lookup up provide edge values. Default is 'SUID'.
        preserve_current_selection (bool): Whether to maintain previously selected edges.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'nodes': [node list], 'edges': [edge list]}

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> select_edges(None)
        {}
        >>> select_edges([103332, 108034], preserve_current_selection=False, network='My Network')
        {'nodes': [], 'edges': [108033, 108034]}
        >>> select_edges(103332, preserve_current_selection=False, network='My Network')
        {'nodes': [], 'edges': [108033]}
        >>> select_edges('YGL035C (pd) YIL162W', by_col='name', preserve_current_selection=False, network='My Network')
        {'nodes': [], 'edges': [108033]}
        >>> select_edges(['YGL035C (pd) YIL162W', 'YGL035C (pd) YLR044C', 'YNL216W (pd) YLR044C'], by_col='name', preserve_current_selection=True, network=52)
        {'nodes': [], 'edges': [108033, 108034, 108103]}
        >>> select_edges('YGL035C (pd) YIL162W, YGL035C (pd) YLR044C, YNL216W (pd) YLR044C', by_col='name', preserve_current_selection=True, network=52)
        {'nodes': [], 'edges': [108033, 108034, 108103]}

    Note:
        In the return value, node list is always empty, and edge list is the SUIDs of newly selected edges -- dict is
        {} if no edges were selected
    """
    suid = networks.get_network_suid(network, base_url=base_url)

    if not preserve_current_selection: clear_selection(type='edges', network=suid, base_url=base_url)

    # TODO: See why R version works with empty nodes list (which should mean "all") or a node list (which is missing a close ")
    # TODO: Should edges default to None?
    if not edges or edges == '':
        edge_list_str = ''
    else:
        edges = normalize_list(edges)

        # create list of COL:VALUE that includes all requested nodes
        edge_list_str = f'{by_col}:{edges[0]}'
        for n in range(1, len(edges)):
            edge_list_str += f',{by_col}:{edges[n]}'
    res = commands.commands_post(f'network select network=SUID:"{suid}" edgeList="{edge_list_str}"',
                                 base_url=base_url)
    return res


@cy_log
def select_all_edges(network=None, base_url=DEFAULT_BASE_URL):
    """Selects all edges in a Cytoscape Network.

    Args:
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: list of SUIDs for edges selected

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> select_all_edges()
        [104432, 104431, ...]
        >>> select_all_edges(network='My Network')
        [104432, 104431, ...]
        >>> select_all_edges(network=52)
        [104432, 104431, ...]
    """
    suid = networks.get_network_suid(network, base_url=base_url)
    all_edge_SUIDs = commands.cyrest_get(f'networks/{suid}/edges', base_url=base_url)

    res = select_edges(all_edge_SUIDs)
    return res['edges']
    # TODO: Does the RCy3 code work? It's passing an unusual list to CyREST


@cy_log
def invert_edge_selection(network=None, base_url=DEFAULT_BASE_URL):
    """Select all edges that were not selected and deselect all edges that were selected.

    Args:
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'nodes': [node list], 'edges': [edge list]}

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> invert_edge_selection()
        {'nodes': [], 'edges': [104432, 104431, ...]}
        >>> invert_edge_selection(network='My Network')
        {}
        >>> invert_edge_selection(network=52)
        {'nodes': [], 'edges': [104432, 104431, ...]}

    Note:
        In the return value, node list is always empty, and
        edge list is the SUIDs of selected edges -- dict is {} if no edges remain selected
    """
    suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.commands_post(f'network select invert=edges network="SUID:{suid}"', base_url=base_url)
    # TODO: Added double quotes for SUID
    return res


@cy_log
def delete_selected_edges(network=None, base_url=DEFAULT_BASE_URL):
    """Delete the currently selected edges in the network.

    Args:
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'nodes': [node list], 'edges': [edge list]} where node list is always empty, and
            edge list is the SUIDs of deleted edges -- dict is {} if no edges were deleted

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> delete_selected_edges()
        {'nodes': [], 'edges': [104432, 104431, ...]}
        >>> delete_selected_edges(network='My Network')
        {}
        >>> delete_selected_edges(network=52)
        {'nodes': [], 'edges': [104432, 104431, ...]}
    """
    title = networks.get_network_name(network, base_url=base_url)
    res = commands.commands_post(f'network delete edgeList=selected network="{title}"', base_url=base_url)
    # TODO: Added double quotes to network title
    return res


@cy_log
def get_selected_edge_count(network=None, base_url=DEFAULT_BASE_URL):
    """Return the number of edges currently selected in the network.

    Args:
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        int: count of edges selected in the network

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_selected_edge_count()
        0
        >>> get_selected_edge_count(network='My Network')
        359
        >>> get_selected_edge_count(network=52)
        359
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.cyrest_get(f'networks/{net_suid}/edges',
                              parameters={'column': 'selected', 'query': 'true'}, base_url=base_url)
    return len(res)


@cy_log
def get_selected_edges(edge_suids=False, network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the names of all the edges selected in the network.

    Args:
        edge_suids (bool): Whether to return edge SUIDs. Default is FALSE to return edge names.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: list of edge names (or SUIDs if edge_suids is True) -- None if no edges selected

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_selected_edges()
        None
        >>> get_selected_edge_count(network='My Network')
        ['YGL035C (pd) YIL162W', 'YGL035C (pd) YLR044C', 'YNL216W (pd) YLR044C']
        >>> get_selected_edge_count(edge_suids=True, network=52)
        [27656, 27658, 27716]
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)

    if get_selected_edge_count(net_suid, base_url=base_url) == 0:
        narrate('No edges selected.')
        return None
    else:
        selected_edge_suids = commands.cyrest_get(f'networks/{net_suid}/edges',
                                                  parameters={'column': 'selected', 'query': 'true'})
        if edge_suids:
            return selected_edge_suids
        else:
            selected_edge_names = edge_suid_to_edge_name(selected_edge_suids, net_suid, base_url=base_url)
            return selected_edge_names


@cy_log
def select_edges_connecting_selected_nodes(network=None, base_url=DEFAULT_BASE_URL):
    """Select edges in a Cytoscape Network connecting the selected nodes, including self loops connecting single nodes.

    Any edges selected beforehand are deselected before any new edges are selected

    Args:
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
         dict: {'nodes': [node list], 'edges': [edge list]} or None if no selected nodes
    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> select_edges_connecting_selected_nodes()
        None
        >>> select_edges_connecting_selected_nodes(network='My Network')
        {'nodes': [103990, 103991, ...], 'edges': [104432, 104431, ...]}
        >>> select_edges_connecting_selected_nodes(network=52)
        {'nodes': [103990, 103991, ...], 'edges': [104432, 104431, ...]}

    Note:
        In the return value node list is list of all selected nodes, and
        edge list is the SUIDs of selected edges -- dict is None if no nodes were selected or there were no newly
        created edges
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)

    selected_nodes = get_selected_nodes(network=net_suid, base_url=base_url)
    # TODO: In R version, NA test is after len() test ... shouldn't it be before?
    if not selected_nodes: return None

    all_edges = networks.get_all_edges(net_suid, base_url=base_url)

    selected_sources = set()
    selected_targets = set()
    for n in selected_nodes:
        selected_sources |= set(filter(re.compile('^' + n).search, all_edges))
        selected_targets |= set(filter(re.compile(n + '$').search, all_edges))

    selected_edges = list(selected_sources.intersection(selected_targets))

    if len(selected_edges) == 0: return None
    res = select_edges(selected_edges, by_col='name', preserve_current_selection=False, network=net_suid,
                       base_url=base_url)
    return res
    # TODO: isn't the pattern match a bit cheesy ... shouldn't it be ^+n+' ('    and    ') '+n+$ ???


@cy_log
def select_edges_adjacent_to_selected_nodes(network=None, base_url=DEFAULT_BASE_URL):
    """Take currently selected nodes and add to the selection all edges connected to those nodes, regardless of directionality.

    Any edges selected beforehand are deselected before any new edges are selected

    Args:
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
         dict: {'nodes': [node list], 'edges': [edge list]}
    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> select_edges_adjacent_to_selected_nodes()
        {}
        >>> select_edges_adjacent_to_selected_nodes(network='My Network')
        {'nodes': [103990, 103991, ...], 'edges': [104432, 104431, ...]}
        >>> select_edges_adjacent_to_selected_nodes(network=52)
        {'nodes': [103990, 103991, ...], 'edges': [104432, 104431, ...]}

    Note:
        In the return value, node list is list of all selected edges, and edge list is the SUIDs of selected
        edges -- dict is {} if no nodes were selected or there were no newly created edges
    """
    suid = networks.get_network_suid(title=network, base_url=base_url)
    clear_selection(type='edges', network=suid, base_url=base_url)
    res = commands.commands_post(f'network select adjacentEdges="true" nodeList="selected network="{suid}"',
                                 base_url=base_url)
    return res


@cy_log
def delete_duplicate_edges(network=None, base_url=DEFAULT_BASE_URL, *, ignore_direction=False):
    """Remove edges with duplicate names.

    Only considers cases with identical source, target, interaction and directionality. Duplicate edges are first
    selected and then deleted. Prior edge selections will be lost; node selections will not be affected.

    Args:
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.
        ignore_direction (bool): True to treat x->y as equal to y->x

    Returns:
         dict: {'nodes': [node list], 'edges': [edge list]} where node list is always empty, and edge list is the SUIDs of deleted edges -- dict is {} if no edges were deleted

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> delete_duplicate_edges()
        {}
        >>> delete_duplicate_edges(network='My Network')
        {'nodes': [], 'edges': [104432, 104431, ...]}
        >>> delete_duplicate_edges(network=52, ignore_direction=True)
        {'nodes': [], 'edges': [104432, 104431, ...]}
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    all_edges = networks.get_all_edges(net_suid, base_url=base_url)
    suid_to_name_map_df = tables.get_table_columns('edge', ['name'], 'default', network=net_suid, base_url=base_url)

    def build_sorted_edge_equivalents(parsed_edge):
        # Creates a tuple where first element is lexigraphically smaller than the second
        if parsed_edge[0] < parsed_edge[2]:
            forwards = f'{parsed_edge[0]} ({parsed_edge[1]}) {parsed_edge[2]}'
            backwards = f'{parsed_edge[2]} ({parsed_edge[1]}) {parsed_edge[0]}'
        else:
            forwards = f'{parsed_edge[2]} ({parsed_edge[1]}) {parsed_edge[0]}'
            backwards = f'{parsed_edge[0]} ({parsed_edge[1]}) {parsed_edge[2]}'
        return (forwards, backwards)

    def get_edge_suids(edge_name):
        if edge_name is None:
            return []
        else:
            try:
                return list(suid_to_name_map_df[suid_to_name_map_df.name.eq(edge_name)].index.values)
            except:
                return []

    # If ignoring direction, adjust all_edges to a canonical ordering of source and target
    if ignore_direction:
        all_edges = [build_sorted_edge_equivalents(x)  for x in parse_edges(all_edges)]
    else:
        all_edges = [(x, None)  for x in all_edges]

    # Find just the edges that duplicate other edges
    edge_counter = dict.fromkeys(all_edges, 0)
    for unique_edge in all_edges:
        edge_counter[unique_edge] += 1
    dup_edge_suids = [get_edge_suids(unique_edge[0]) + get_edge_suids(unique_edge[1])   for unique_edge in edge_counter if edge_counter[unique_edge] > 1]

    # Create one list out of each edge's dup list, but leave one edge out so they're not all removed
    dup_edge_suids = [edge_suid    for suid_list in dup_edge_suids    for edge_suid in suid_list[1:]]

    # With the list of duplicate edges, select and delete them
    select_edges(dup_edge_suids, by_col='SUID', preserve_current_selection=False, network=net_suid, base_url=base_url)
    res = delete_selected_edges(network=net_suid, base_url=base_url)
    return res


@cy_log
def delete_self_loops(network=None, base_url=DEFAULT_BASE_URL):
    """Removes edges that connect to a single node as both source and target.

    Self loop edges are first selected and then deleted. Prior edge and node selections will be lost.

    Args:
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
         str: ''

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> delete_self_loops()
        ''
        >>> delete_self_loops(network='My Network')
        ''
        >>> delete_self_loops(network=52)
        ''
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)

    clear_selection('both', net_suid, base_url=base_url)

    all_nodes = networks.get_all_nodes(net_suid, base_url=base_url)

    # TODO: This is the R implementation, and it's correct but horribly slow ....
    # For each node, select the node, then select each edge that connects it to itself, then zap the edge
    #    for n in all_nodes:
    #        select_nodes([n], by_col='name', preserve_current_selection=False, network=net_suid, base_url=base_url)
    #        select_edges_connecting_selected_nodes(network=net_suid, base_url=base_url)
    #        delete_selected_edges(network=net_suid, base_url=base_url)

    # TODO: Consider this for the actual implementation
    all_edges = networks.get_all_edges(net_suid, base_url=base_url)

    self_edges = []
    for node in all_nodes:
        r = re.compile('^' + node + '.*' + node + '$')
        self_edges.extend(filter(r.search, all_edges))

    select_edges(self_edges, by_col='name', preserve_current_selection=False, network=net_suid, base_url=base_url)
    delete_selected_edges(net_suid, base_url=base_url)  # TODO: Would be better to return this value instead

    return clear_selection('both', network=net_suid, base_url=base_url)  # shouldn't be necessary
