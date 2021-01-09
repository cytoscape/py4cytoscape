# -*- coding: utf-8 -*-

"""Functions for working with GROUPS in Cytoscape.
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

# Internal module imports
from . import commands
from . import networks

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log


@cy_log
def add_to_group(group_name, nodes=None, nodes_by_col='SUID', edges=None, edges_by_col='SUID', network=None,
                 base_url=DEFAULT_BASE_URL):
    """Add the specified nodes and edges to the specified group.

    Args:
        group_name (str): Specifies the name used to identify the group
        nodes (list or str or int or None): List of nodes or keyword: selected, unselected or all. If node list:
            ``list`` of node names or SUIDs, comma-separated string of node names or SUIDs, or scalar node name
            or SUID). Node names should be found in the ``SUID`` column of the ``node table`` unless
            specified in ``nodes_by_col``. If list is None, default is currently selected nodes.
        nodes_by_col (str): name of node table column corresponding to provided nodes list. Default is 'SUID'.
        edges (list or str or None): List of edges or keyword: selected, unselected or all. If edge list:
            ``list`` of edge names or SUIDs, comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID). Edge names should be found in the ``SUID`` column of the ``edge table`` unless
            specified in ``edges_by_col``. If list is None, default is currently selected edges.
        edges_by_col (str): name of edge table column corresponding to provided edges list. Default is 'SUID'.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

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
        >>> add_to_group('Group 1', ['GDS1', 'SIP4', 'PDC1'], nodes_by_col='COMMON', edges=[]) # add named nodes and no edges
        {}
        >>> add_to_group('Group 1', 'GDS1, SIP4, PDC1', nodes_by_col='COMMON', edges=[]) # add named nodes and no edges
        {}
        >>> add_to_group('Group 1', [1544, 1444, 1522], edges=[]) # add named nodes and no edges
        {}
        >>> add_to_group('Group 1', '1544, 1444, 1522', edges=[]) # add named nodes and no edges
        {}
        >>> add_to_group('Group 1', nodes='unselected', edges='unselected') # add all unselected nodes and edges
        {}
    """
    if isinstance(nodes, str) and nodes in {'all', 'selected', 'unselected'}: nodes_by_col = None
    node_list = prep_post_query_lists(nodes, nodes_by_col)

    if isinstance(edges, str) and edges in {'all', 'selected', 'unselected'}: edges_by_col = None
    edge_list = prep_post_query_lists(edges, edges_by_col)

    net_suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.commands_post(
        f'group add groupName="{group_name}" nodeList="{node_list}" edgeList="{edge_list}" network="SUID:{net_suid}"',
        base_url=base_url)
    return res


@cy_log
def collapse_group(groups=None, network=None, base_url=DEFAULT_BASE_URL):
    """Replace the representation of all of the nodes and edges in a group with a single node.

    Args:
        groups (list or str): List of group names or keywords: all, selected, unselected. Default is the currently selected group.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
         dict: {'groups': [List of SUIDs]} where SUID identifies the node corresponding to the group that was collapsed (even if it was already collapsed)

    Raises:
        CyError: if network name or SUID, or group name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> collapse_group() # collapse all selected groups
        {'groups': [95335, 95336]}
        >>> collapse_group('all') # collapse all groups
        {'groups': [95335, 95336, 95337]}
        >>> collapse_group(['Group 1', 'Group 2']) # collapse 2 groups
        {'groups': [95335, 95336]}
        >>> collapse_group('Group 1,Group 2') # collapse 2 groups
        {'groups': [95335, 95336]}
        >>> collapse_group(['SUID:95335', 'SUID:95336']) # collapse 2 groups
        {'groups': [95335, 95336]}
        >>> collapse_group('SUID:95335,SUID:95336') # collapse 2 groups
        {'groups': [95335, 95336]}
    """
    group_list = prep_post_query_lists(groups)
    net_suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.commands_post(f'group collapse groupList="{group_list}" network="SUID:{net_suid}"',
                                 base_url=base_url)
    return res


@cy_log
def create_group(group_name, nodes=None, nodes_by_col='SUID', network=None, base_url=DEFAULT_BASE_URL):
    """Create a group from the specified nodes.

    Args:
        group_name (str): The name used to identify and optionaly label the group
        nodes (list or str or int or None): List of nodes or keyword: selected, unselected or all. If node list:
            ``list`` of node names or SUIDs, comma-separated string of node names or SUIDs, or scalar node name
            or SUID). Node names should be found in the ``SUID`` column of the ``node table`` unless
            specified in ``nodes_by_col``. If list is None, default is currently selected nodes.
        nodes_by_col (str): name of node table column corresponding to provided nodes list. Default is 'SUID'.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
         dict: {'group': SUID} where SUID identifies the node corresponding to the group

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> create_group('Group 1', ['GDS1', 'SIP4', 'PDC1'], nodes_by_col='COMMON') # create group containing nodes by common name
        {'group': 95335}
        >>> create_group('Group 1', 'GDS1, SIP4, PDC1', nodes_by_col='COMMON') # create group containing nodes by common name
        {'group': 95335}
        >>> create_group('Group 1', [1344, 1502, 1723]) # create group containing nodes by node SUID
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

    node_list = prep_post_query_lists(nodes, nodes_by_col)
    net_suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.commands_post(
        f'group create groupName="{group_name}" nodeList="{node_list}" network="SUID:{net_suid}"',
        base_url=base_url)
    return res


@cy_log
def create_group_by_column(group_name, column=None, value=None, network=None, base_url=DEFAULT_BASE_URL):
    """Create a group of nodes defined by a column value.

    Args:
        group_name (str): The name used to identify and optionaly label the new group
        column (str): The name or header of the Node Table column to use for selecting nodes to group
        value (str or int or float or bool): The value in the column to use for selecting nodes to group
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
         dict: {'group': group SUID} where the SUID identifies new group

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> create_group_by_column('Group 1', 'Cluster', 'A')
        {'group': 95336}
    """
    # TODO: The default column and value will make the call blow up ... are we sure we want these defaults?
    net_suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.commands_post(
        f'group create groupName="{group_name}" nodeList="{column}":"{value}" network="SUID:{net_suid}"',
        base_url=base_url)
    return res


@cy_log
def expand_group(groups=None, network=None, base_url=DEFAULT_BASE_URL):
    """Replaces the group node with member nodes for a set of groups.

    Args:
        groups (list or str): List of group names or keywords: all, selected, unselected. Default is the currently selected group.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
         dict: {'groups': [List of SUIDs]} where SUID identifies the node corresponding to the group that was expanded (even if it was already expanded)

    Raises:
        CyError: if network name or SUID, or group name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> expand_group() # expand all selected groups
        {'groups': [95335, 95336]}
        >>> expand_group('all') # expand all groups
        {'groups': [95335, 95336, 95337]}
        >>> expand_group(['Group 1', 'Group 2']) # expand 2 groups
        {'groups': [95335, 95336]}
        >>> expand_group('Group 1,Group 2') # expand 2 groups
        {'groups': [95335, 95336]}
        >>> expand_group(['SUID:95335', 'SUID:95336']) # expand 2 groups
        {'groups': [95335, 95336]}
        >>> expand_group('SUID:95335,SUID:95336') # expand 2 groups
        {'groups': [95335, 95336]}
    """
    group_list = prep_post_query_lists(groups)
    net_suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.commands_post(
        f'group expand groupList="{group_list}" network="SUID:{net_suid}"', base_url=base_url)
    return res


@cy_log
def get_group_info(group, network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve information about a group by name or identifier.

    Args:
        group_name (str or SUID): Group name or SUID.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

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
         'collapsed': False}
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)

    # group.suid <- .nodeNameToNodeSUID(group, network, base.url)
    ## Note: if not yet collapsed, then group node is not in node list!
    ## so work with the user-provided group name or SUID directly instead
    prefix = 'SUID:' if isinstance(group, int) else ''

    res = commands.commands_post(f'group get node="{prefix}{group}" network="SUID:{net_suid}"',
                                 base_url=base_url)
    return res


@cy_log
def list_groups(network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve a list of all group SUIDs in a network.

    Args:
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

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
    res = commands.commands_post(f'group list network="SUID:{net_suid}"', base_url=base_url)
    return res


@cy_log
def remove_from_group(group_name, nodes=None, nodes_by_col='SUID', edges=None, edges_by_col='SUID', network=None,
                      base_url=DEFAULT_BASE_URL):
    """Remove the specified nodes and edges from the specified group.

    Args:
        group_name (str): Specifies the name used to identify the group
        nodes (list or str or int or None): List of nodes or keyword: selected, unselected or all. If node list:
            ``list`` of node names or SUIDs, comma-separated string of node names or SUIDs, or scalar node name
            or SUID). Node names should be found in the ``SUID`` column of the ``node table`` unless
            specified in ``nodes_by_col``. If list is None, default is currently selected nodes.
        nodes_by_col (str): name of node table column corresponding to provided nodes list. Default is 'SUID'.
        edges (str or list or int or None): List of edges or keyword: selected, unselected or all. If edge list:
            ``list`` of edge names or SUIDs, comma-separated string of edge names or SUIDs, or scalar edge name
            or SUID). Edge names should be found in the ``SUID`` column of the ``edge table`` unless
            specified in ``edges_by_col``. If list is None, default is currently selected edges.
        edges_by_col (str): name of edge table column corresponding to provided edges list. Default is 'SUID'.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
         dict: {}

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> remove_from_group('Group 1', ['GDS1', 'SIP4', 'PDC1'], nodes_by_col='COMMON') # remove nodes by common name & all their edges
        {}
        >>> remove_from_group('Group 1', 'GDS1, SIP4, PDC1', nodes_by_col='COMMON') # remove nodes by common name & all their edges
        {}
        >>> remove_from_group('Group 1', [76545, 75499, 80299]) # remove nodes by SUID & all their edges
        {}
        >>> remove_from_group('Group 1', 80299) # remove node by SUID & all its edges
        {}
        >>> remove_from_group('Group 1') # remove all selected nodes and edges
        {}
        >>> remove_from_group('Group 1', nodes=[], edges=[78565, 79565]) # remove edges but not any nodes
        {}
        >>> remove_from_group('Group 1', nodes='unselected', edges='unselected') # remove all unselected nodes and edges
        {}
    """
    if isinstance(nodes, str) and nodes in {'all', 'selected', 'unselected'}: nodes_by_col = None
    node_list = prep_post_query_lists(nodes, nodes_by_col)

    if isinstance(edges, str) and edges in {'all', 'selected', 'unselected'}: edges_by_col = None
    edge_list = prep_post_query_lists(edges, edges_by_col)

    net_suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.commands_post(
        f'group remove groupName="{group_name}" nodeList="{node_list}" edgeList="{edge_list}" network="SUID:{net_suid}"',
        base_url=base_url)
    return res


@cy_log
def delete_group(groups=None, groups_by_col='SUID', network=None, base_url=DEFAULT_BASE_URL):
    """Delete one or more groups, while leaving member nodes intact.

    Args:
        groups (list or str or None) List of group SUIDs, names, other column values or keywords: all, selected,
            unselected. Default is the currently selected group.
        groups_by_col (str): name of node table column corresponding to provided groups list. Default is 'SUID'.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
         dict: {'groups': [group SUIDs]} with the SUID for each deleted group in the list

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> delete_group(['Group 1', 'Group 2'], groups_by_col='shared name') # delete groups by name
        {'groups':[7970, 7980]}
        >>> delete_group('Group 1,Group 2', groups_by_col='shared name') # delete groups by name
        {'groups':[7970, 7980]}
        >>> delete_group([7970]) # delete groups by SUID
        {'groups':[7970]}
        >>> delete_group(7970) # delete groups by SUID
        {'groups':[7970]}
        >>> delete_group() # delete all selected groups
        {'groups':[7970, 7980]}
        >>> delete_group(groups='all') # delete all groups
        {'groups':[7970, 7980]}

    Note:
        Group nodes are ungrouped but not deleted in Cytoscape 3.6.1
    """
    if isinstance(groups, str) and groups in {'all', 'selected', 'unselected'}: groups_by_col = None
    group_list = prep_post_query_lists(groups, groups_by_col)

    net_suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.commands_post(f'group ungroup nodeList="{group_list}" network="SUID:{net_suid}"', base_url=base_url)
    # TODO: The R implementation uses the groupList parameter, which conflicts with the command documentation
    return res

