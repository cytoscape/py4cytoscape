# -*- coding: utf-8 -*-

"""Functions for inspecting and managing apps for Cytoscape.
"""

import sys

from . import commands
from .exceptions import CyError
from .pycy3_utils import *
from . import networks

def add_to_group(group_name, nodes=None, nodes_by_col='SUID', edges=None, edges_by_col='SUID', network=None, base_url=DEFAULT_BASE_URL):
    """Add the specified nodes and edges to the specified group.

    Args:
        group_name (str): Specifies the name used to identify the group
        nodes (list or str or None): List of node SUIDs, names, other column values, or keyword: selected,
            unselected or all. Default is currently selected nodes.
        nodes_by_col (str): name of node table column corresponding to provided nodes list. Default is 'SUID'.
        edges (list or str or None): List of edge SUIDs, names, other column values, or keyword: selected,
            unselected or all. Default is currently selected edges.
        edges_by_col (str): name of edge table column corresponding to provided edges list. Default is 'SUID'.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
         dict: {}

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> add_to_group('Group 1', ['GDS1', 'SIP4', 'PDC1'], nodes_by_col='COMMON') # add nodes by common name & all selected edges
        {}
        >>> add_to_group('Group 1') # add all selected nodes and edges
        {}
        >>> add_to_group('Group 1', ['GDS1', 'SIP4', 'PDC1'], nodes_by_col='COMMON', edges=[]) # add all selected nodes and no edges
        {}
        >>> add_to_group('Group 1', nodes='unselected', edges='unselected') # add all unselected nodes and edges
        {}
    """
    if isinstance(nodes, str) and nodes in {'all', 'selected', 'unselected'}: nodes_by_col = None
    node_list = _prep_post_query_lists(nodes, nodes_by_col)

    if isinstance(edges, str) and edges in {'all', 'selected', 'unselected'}: edges_by_col = None
    edge_list = _prep_post_query_lists(edges, edges_by_col)

    net_suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.commands_post('group add groupName="' + group_name + '" nodeList="' + node_list + '" edgeList="' + edge_list + '" network="SUID:' + str(net_suid) + '"', base_url=base_url)
    return res

def create_group(group_name, nodes=None, nodes_by_col='SUID', network=None, base_url=DEFAULT_BASE_URL):
    """Create a group from the specified nodes.

    Args:
        group_name (str): The name used to identify and optionaly label the group
        nodes (list or str or None): List of node SUIDs, names, other column values, or keyword: selected,
            unselected or all. Default is currently selected nodes.
        nodes_by_col (str): name of node table column corresponding to provided nodes list. Default is 'SUID'.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
         dict: {'group': SUID} where SUID identifies the node corresponding to the group

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> create_group('Group 1', ['GDS1', 'SIP4', 'PDC1'], nodes_by_col='COMMON') # create group containing nodes by common name
        {'group': 95335}
        >>> create_group('Group 1') # create group containing all selected nodes
        {'group': 95335}
        >>> create_group('Group 1', []) # create group with no nodes
        {'group': 95335}
        >>> create_group('Group 1', nodes='unselected') # create group with all unselected nodes
        {'group': 95335}
    """
    # TODO: Determine whether group_name can be null ... Commands help says it can be optional
    if isinstance(nodes, str) and nodes in ['all', 'selected', 'unselected']: nodes_by_col = None

    node_list =_prep_post_query_lists(nodes, nodes_by_col)
    net_suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.commands_post('group create groupName="' + group_name + '" nodeList="' + node_list + '" network="SUID:' + str(net_suid), base_url=base_url)
    return res


# ' @title Get Group Information
# '
# ' @description Retrieve information about a group by name or identifier.
# ' @param group Group name or SUID.
# ' @param network (optional) Name or SUID of the network. Default is the "current" network active in Cytoscape.
# ' @param base.url (optional) Ignore unless you need to specify a custom domain,
# ' port or version to connect to the CyREST API. Default is http://localhost:1234
# ' and the latest version of the CyREST API supported by this version of RCy3.
# ' @return Group information
# ' @examples \donttest{
# ' getGroupInfo('mygroup')
# ' }
# ' @export
def get_group_info(group, network=None, base_url=DEFAULT_BASE_URL):
    """Create a group from the specified nodes.

    Args:
        group_name (str or SUID): Group name or SUID.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
         dict: {'group': SUID, 'name': name, 'nodes': [node SUIDs], 'internalEdges': [edge SUIDs], 'externalEdges': [edge SUIDs], 'collapsed': bool}
            where ``SUID`` identifies the node corresponding to the group, ``name`` is the name given to the group at create time,
            ``node SUIDs`` is a list of nodes in the group, ``edge SUIDs`` is a list of edges within or reaching out of the group, and
            ``collapsed`` is True if the group is collapsed.

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_group_info('group 1')
        {'group': 95335,
         'name': 'group 1',
         'nodes': [94214, 94038, 94122],
         'internalEdges': [],
         'externalEdges': [94450, 94564, 94403, 94362, 94506, 94537],
         'collapsed': False}
        >>> get_group_info(95335, network='My Network')
        {'group': 95335,
         'name': 'group 1',
         'nodes': [94214, 94038, 94122],
         'internalEdges': [],
         'externalEdges': [94450, 94564, 94403, 94362, 94506, 94537],
         'collapsed': False}    """
    net_suid = networks.get_network_suid(network, base_url=base_url)

    # group.suid <- .nodeNameToNodeSUID(group, network, base.url)
    ## Note: if not yet collapsed, then group node is not in node list!
    ## so work with the user-provided group name or SUID directly instead
    prefix = 'SUID:' if isinstance(group, int) else ''

    res = commands.commands_post('group get node="' + prefix + str(group) + '" network="SUID:' + str(net_suid) + '"', base_url=base_url)
    return res

def list_groups(network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve a list of all group SUIDs in a network.

    Args:
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
         dict: {groups: [SUID list]} as list of SUIDs for group nodes

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> list_groups()
        {'groups': [94214, 94038, 94122]}
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.commands_post('group list network="SUID:' + str(net_suid) + '"', base_url=base_url)
    return res

# ------------------------------------------------------------------------------
# Parses all the possible list types and keywords accepted by Commands API.
# If column designation is supported, simply provide a column name; otherwise
# it is assumed to not be supported and returns a simple list.
def _prep_post_query_lists(cmd_list=None, cmd_by_col=None):
    if cmd_list is None:
        return "selected" # need something here for edge selections to work
    elif cmd_by_col and isinstance(cmd_list, list):
        return ','.join([cmd_by_col + ':' + str(cmd)   for cmd in cmd_list])
    else:
        return cmd_list # Note that this supposes the string is already a comma-separated list of COL:NAME ... and cmd_by_col is safely ignored
# TODO: Verify that this produces the same thing as R would for all cases ... particularly for [], which should select nothing