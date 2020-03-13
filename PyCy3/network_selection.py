# -*- coding: utf-8 -*-

"""==============================================================================
Functions for working with SELECTIONS of nodes and edges in networks, including
operations that perform selection and rely on prior selection events.

I. General selection functions
II. Node selection functions
III. Edge selection functions
"""

from . import commands
from . import networks
from .pycy3_utils import DEFAULT_BASE_URL, node_suid_to_node_name
from PyCy3.decorators import debug

# ==============================================================================
# I. General selection functions
# ------------------------------------------------------------------------------

# ' @title Clear Selection
# '
# ' @description If any nodes are selected in the network, they will be unselected.
# ' @param type 'nodes', 'edges' or 'both' (default)
# ' @param network (optional) Name or SUID of the network. Default is the
# ' "current" network active in Cytoscape.
# ' @param base.url (optional) Ignore unless you need to specify a custom domain,
# ' port or version to connect to the CyREST API. Default is http://localhost:1234
# ' and the latest version of the CyREST API supported by this version of RCy3.
# ' @return None
# ' @author AlexanderPico, Tanja Muetze, Georgi Kolishovski, Paul Shannon
# ' @examples \donttest{
# ' clearSelection()
# ' }
# ' @export
def clear_selection(type='both', network=None, base_url=DEFAULT_BASE_URL):
    net_suid = networks.get_network_suid(network, base_url=base_url)

    if type in ['nodes', 'both']:
        res = commands.cyrest_put('networks/' + str(net_suid) + '/tables/defaultnode/columns/selected', parameters={'default': 'false'}, base_url=base_url, require_json=False)
        # TODO: this result will get lost if type=='both'

    if type in ['edges', 'both']:
        res = commands.cyrest_put('networks/' + str(net_suid) + '/tables/defaultedge/columns/selected', parameters={'default': 'false'}, base_url=base_url, require_json=False)

    return res

# ==============================================================================
# II. Node selection functions
# ------------------------------------------------------------------------------

def select_first_neighbors(direction='any', network=None, base_url=DEFAULT_BASE_URL):
    """Select nodes directly connected to currently selected nodes.

    Can specify connection directionality using the direction param.

    Args:
        direction (str): direction of connections to neighbors to follow, e.g., incoming, outgoing, undirected, or any (default)
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        dict: {'nodes': [node list], 'edges': [edge list]} where node list is the SUIDs of newly selected nodes
            and edge list is always empty

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> select_first_neighbors()
        {'nodes': [107504, 107503, ...], 'edges': []}
        >>> select_first_neighbors(direction='undirected')
        {'nodes': [107514], 'edges': []}
    """
    suid = networks.get_network_suid(network, base_url=base_url)
    cmd = 'network select firstNeighbors="' + direction + '" network=SUID:"' + str(suid) + '"'
    res = commands.commands_post(cmd, base_url=base_url)
    return res

# TODO: Decide whether 'nodes' can be None ... the RCy3 documentation implies it can, but the code says no
def select_nodes(nodes, by_col='SUID', preserve_current_selection=True, network=None, base_url=DEFAULT_BASE_URL):
    """Select nodes in the network by SUID, name or other column values.

    Args:
        nodes (list): List of node SUIDs, names or other column values
        by_col (str): Node table column to lookup up provide node values. Default is 'SUID'.
        preserve_current_selection (bool): Whether to maintain previously selected nodes.
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        dict: {'nodes': [node list], 'edges': [edge list]} where node list is the SUIDs of newly selected nodes
            and edge list is always empty

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> select_nodes(None)
        {'nodes': [107504, 107503, ...], 'edges': []}
        >>> select_nodes(['RAP1'], by_col='COMMON')
        {'nodes': [107514], 'edges': []}
    """
    suid = networks.get_network_suid(network, base_url=base_url)

    if not preserve_current_selection: clear_selection(type='nodes', network=suid, base_url=base_url)

    # TODO: See why R version works with empty nodes list (which should mean "all") or a node list (which is missing a close ")
    if not nodes or len(nodes) == 0:
        node_list_str = 'all'
    else:
        # create list of COL:VALUE that includes all requested nodes
        node_list_str = by_col + ':' + str(nodes[0])
        for n in range(1, len(nodes)):
            node_list_str += ',' + by_col + ':' + str(nodes[n])
    res = commands.commands_post('network select network=SUID:"' + str(suid) + '" nodeList="' + node_list_str + '"', base_url=base_url)
    return res

def select_all_nodes(network=None, base_url=DEFAULT_BASE_URL):
    """Selects all nodes in a Cytoscape Network.

    Args:
        nodes (list): List of node SUIDs, names or other column values
        by_col (str): Node table column to lookup up provide node values. Default is 'SUID'.
        preserve_current_selection (bool): Whether to maintain previously selected nodes.
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

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
    """
    suid = networks.get_network_suid(network, base_url=base_url)
    all_node_SUIDs = commands.cyrest_get('networks/' + str(suid) + '/nodes', base_url=base_url)

    res = select_nodes(all_node_SUIDs)
    return res['nodes']
    # TODO: Does the RCy3 code work? It's passing an unusual list to CyREST

def get_selected_node_count(network=None, base_url=DEFAULT_BASE_URL):
    """Returns the number of nodes currently selected in the network.

    Args:
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

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
    res = commands.cyrest_get('networks/' + str(net_suid) + '/nodes', parameters={'column': 'selected', 'query': 'true'}, base_url=base_url)
    return len(res)

def get_selected_nodes(node_suids=False, network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the names of all the nodes selected in the network.

    Args:
        node_suids (bool): Whether to return node SUIDs. Default is FALSE to return node names.
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

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
        print('No nodes selected.')
        return None
    else:
        selected_node_suids = commands.cyrest_get('networks/' + str(net_suid) + '/nodes', parameters={'column': 'selected', 'query': 'true'})
        if node_suids:
            return selected_node_suids
        else:
            selected_node_names = node_suid_to_node_name(selected_node_suids, net_suid, base_url=base_url)
            return selected_node_names

def invert_node_selection(network=None, base_url=DEFAULT_BASE_URL):
    """Select all nodes that were not selected and deselect all nodes that were selected.

    Args:
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        dict: {'nodes': [node list], 'edges': [edge list]} where node list is the SUIDs of newly selected nodes
            and edge list is always empty

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
    """
    suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.commands_post('network select invert=nodes network=SUID:' + str(suid), base_url=base_url)
    return res

def delete_selected_nodes(network=None, base_url=DEFAULT_BASE_URL):
    """Delete currently selected nodes from the network.

    Args:
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        dict: {'nodes': [node list], 'edges': [edge list]} where node list is the SUIDs of deleted nodes
            and edge list is the SUIDs of deleted edges

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> invert_node_selection()
        {'nodes': [107504, 107503, ...], 'edges': [108033, 108034]}
        >>> invert_node_selection(network='My Network')
        {'nodes': [107504, 107503, ...], 'edges': [108033, 108034]}
        >>> invert_node_selection(network=52)
        {'nodes': [107504, 107503, ...], 'edges': [108033, 108034]}
    """
    title = networks.get_network_name(network, base_url=base_url)
    res = commands.commands_post('network delete nodeList=selected network="' + title + '"', base_url=base_url)
    # TODO: Added double quotes to network title
    return res