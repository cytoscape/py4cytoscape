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
#' @title Select first neighbor nodes
#'
#' @description Select nodes directly connected to currently selected nodes. Can
#' specify connection directionality using the direction param.
#' @param direction direction of connections to neighbors to follow, e.g.,
#' incoming, outgoing, undirected, or any (default)
#' @param network (optional) Name or SUID of the network. Default is the
#' "current" network active in Cytoscape.
#' @param base.url (optional) Ignore unless you need to specify a custom domain,
#' port or version to connect to the CyREST API. Default is http://localhost:1234
#' and the latest version of the CyREST API supported by this version of RCy3.
#' @return list of suids of selected nodes, including original selection
#' @examples
#' \donttest{
#' selectFirstNeighbors()
#' selectFirstNeighors('outgoing')
#' selectFirstNeighors('incoming')
#' }
#' @export
def select_first_neighbors(direction='any', network=None, base_url=DEFAULT_BASE_URL):
    suid = networks.get_network_suid(network, base_url=base_url)
    cmd = 'network select firstNeighbors="' + direction + '" network=SUID:"' + str(suid) + '"'
    res = commands.commands_post(cmd, base_url=base_url)
    return res


# ' @title Select Nodes
# '
# ' @description Select nodes in the network by SUID, name or other column values.
# ' @param nodes List of node SUIDs, names or other column values
# ' @param by.col Node table column to lookup up provide node values. Default is
# ' 'SUID'.
# ' @param preserve.current.selection \code{boolean} Whether to maintain
# ' previously selected nodes.
# ' @param network (optional) Name or SUID of the network. Default is the
# ' "current" network active in Cytoscape.
# ' @param base.url (optional) Ignore unless you need to specify a custom domain,
# ' port or version to connect to the CyREST API. Default is http://localhost:1234
# ' and the latest version of the CyREST API supported by this version of RCy3.
# ' @return \code{list} of newly selected node SUIDs
# ' @author AlexanderPico, Tanja Muetze, Georgi Kolishovski, Paul Shannon
# ' @examples \donttest{
# ' selectNodes()
# ' }
# ' @export
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

def get_selected_node_count(network=None, base_url=DEFAULT_BASE_URL):
    net_suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.cyrest_get('networks/' + str(net_suid) + '/nodes', parameters={'column': 'selected', 'query': 'true'}, base_url=base_url)
    return len(res)

def get_selected_nodes(node_suids=False, network=None, base_url=DEFAULT_BASE_URL):
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
