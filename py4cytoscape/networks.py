# -*- coding: utf-8 -*-

"""Functions for NETWORK management and retrieving information on networks, nodes
and edges. Includes all functions that result in the creation of a new network
in Cytoscape, in addition to funcitons that extract network models into
other useful objects.

I. General network functions
II. General node functions
III. General edge functions
IV. Network creation
V. Network extraction
VI. Internal functions

Note:
     Go to network_selection.py for all selection-related functions
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

# ==============================================================================
# I. General network functions
# ------------------------------------------------------------------------------

# External library imports
import sys
import os
import time
import warnings
import pandas as pd
import igraph as ig
import networkx as nx

# Internal module imports
from . import commands
from . import tables
from . import network_selection
from . import layouts
from . import session

# Internal module convenience imports
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log
from .py4cytoscape_tuning import MODEL_PROPAGATION_SECS, CATCHUP_NETWORK_SECS
from .exceptions import CyError
from .py4cytoscape_notebook import running_remote

def __init__(self):
    pass


@cy_log
def set_current_network(network=None, base_url=DEFAULT_BASE_URL):
    """Selects the given network as "current".

    Args:
        network (SUID or str or None): Network name or SUID of the network that you want set as current
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {} (empty dict)

    Raises:
        ValueError: if server response has no JSON
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_current_network() # sets current network to current
        {}
        >>> set_current_network('MyNetwork') # sets network named 'MyNetwork' as current
        {}
        >>> set_current_network(1502) # sets network having SUID 1502 as current
        {}
    """
    suid = get_network_suid(network)
    cmd = f'network set current network="SUID:{suid}"'
    res = commands.commands_post(cmd, base_url=base_url)
    # TODO: Put double quotes around SUID
    return res


@cy_log
def rename_network(title, network=None, base_url=DEFAULT_BASE_URL):
    """Sets a new name for a network.

    Duplicate network names are not allowed

    Args:
        title (str): New name for the network
        network (SUID or str or None): name or SUID of the network that you want to rename; default is "current" network
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: server JSON response

    Raises:
        ValueError: if server response has no JSON
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> rename_network('renamed network') # changes "current" network's name to "renamed network"
        {'network': 22752, 'title': 'renamed network'}
        >>> rename_network('renamed network', 'MyNetwork') # changes network named 'MyNetwork' to be named "renamed network"
        {'network': 22752, 'title': 'renamed network'}
        >>> rename_network('renamed network', 1502) # sets network having SUID 1502 to be named "renamed network"
        {'network': 1502, 'title': 'renamed network'}
    """
    old_suid = get_network_suid(network, base_url=base_url)
    cmd = f'network rename name="{title}" sourceNetwork="SUID:{old_suid}"'
    # TODO: Put double quotes around SUID
    return commands.commands_post(cmd, base_url)


@cy_log
def get_network_count(base_url=DEFAULT_BASE_URL):
    """Get the number of Cytoscape networks in the current Cytoscape session.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        int: count of networks

    Raises:
        ValueError: if server response has no JSON
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_network_count()
        3
    """
    res = commands.cyrest_get('networks/count', base_url=base_url)
    return list(res.values())[0]


@cy_log
def get_network_name(suid=None, base_url=DEFAULT_BASE_URL):
    """Get the name of a network.

    Args:
        suid (SUID or str or None): SUID of the network; default is current network. If a name is
            provided, then it is validated and returned.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: network name

    Raises:
        ValueError: if server response has no JSON
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_network_name() # get name of current network
        galFiltered.sif
        >>> get_network_name(22752) # get name of network having SUID
        galFiltered.sif
        >>> get_network_name('galFiltered.sif') # verify that current network is galFiltered.sif
        galFiltered.sif

    Notes:
        Together with getNetworkSuid, this function attempts to handle all
        of the multiple ways we support network referencing (e.g., title, SUID,
        'current', and NULL). These functions are then used by all other functions
        that take a "network" argument.
    """
    if isinstance(suid, str):
        # title provided
        if suid == 'current':
            network_suid = get_network_suid(base_url=DEFAULT_BASE_URL)
        else:
            net_names = get_network_list(base_url=base_url)
            if suid in net_names:
                return suid
            else:
                raise CyError(f'Network does not exist for SUID "{suid}"')
    elif isinstance(suid, int):
        # suid provided
        network_suid = suid
    else:
        network_suid = get_network_suid(base_url=DEFAULT_BASE_URL)

    res = commands.cyrest_get('networks.names', {'column': 'suid', 'query': network_suid}, base_url=DEFAULT_BASE_URL)
    return res[0]['name']


@cy_log
def get_network_suid(title=None, base_url=DEFAULT_BASE_URL):
    """Get the SUID of a network.

    Args:
        suid (SUID or str or None): Name of the network; default is "current" network. If an SUID is
            provided, then it is validated and returned.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        int: network SUID

    Raises:
        ValueError: if server response has no JSON
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_network_suid() # get SUID of current network
        22752
        >>> get_network_suid('galFiltered.sif') # get SUID of network having name
        22752
        >>> get_network_suid(22752) # verify that current network has SUID 22752
        22752

    Notes:
        Together with getNetworkSuid, this function attempts to handle all
        of the multiple ways we support network referencing (e.g., title, SUID,
        'current', and NULL). These functions are then used by all other functions
        that take a "network" argument.
    """
    if isinstance(title, str):
        # Title was provided
        if title == 'current':
            network_title = title
        else:
            net_names = get_network_list(base_url=base_url)
            if title in net_names:
                network_title = title
            else:
                raise CyError(f'Network does not exist for name "{title}"')
    elif isinstance(title, int):
        # SUID was provided
        net_suids = commands.cyrest_get('networks', base_url=base_url)
        if title in net_suids:
            return title
        raise CyError(f'Network does not exist for SUID "{title}"')
    else:
        # Don't understand, so use current network
        network_title = 'current'

    # Make requested network current and return its SUID
    cmd = f'network get attribute network="{network_title}" namespace="default" columnList="SUID"'
    response = commands.commands_post(cmd, base_url=base_url)
    return int(response[0]['SUID'])


@cy_log
def get_network_list(base_url=DEFAULT_BASE_URL):
    """Returns the list of Cytoscape network names in the current Cytoscape session.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: network names

    Raises:
        ValueError: if server response has no JSON
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_network_list()
        ['yeastHighQuality.sif', 'galFiltered.sif']
    """
    if get_network_count(base_url=base_url):
        cy_networks_suids = commands.cyrest_get('networks', base_url=base_url)
        cy_network_names = [commands.cyrest_get(f'networks/{suid}', base_url=base_url)['data']['name'] for suid in
                            cy_networks_suids]
    else:
        cy_network_names = []

    return cy_network_names


@cy_log
def export_network(filename=None, type='SIF', network=None, base_url=DEFAULT_BASE_URL):
    """Export a network to one of mulitple file formats.

    Args:
        filename (str): Full path or path relavtive to current working directory,
            in addition to the name of the file. Extension is automatically added based
            on the ``type`` argument. If blank, then the current network name is used.
        type (str): File type. SIF (default), CX, cyjs, graphML, NNF,  xGMML.
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: server JSON response

    Raises:
        ValueError: if server response has no JSON
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> export_network('/path/filename','SIF')
        { 'data': {'file': 'C:\\Users\\CyDeveloper\\xx'}, 'errors': [] }
    """
    cmd = 'network export'  # a good start

    # filename must be suppled
    if filename is None: filename = get_network_name(network)

    # optional args
    if network is not None: cmd += ' network="SUID:' + str(get_network_suid(network, base_url=base_url)) + '"'

    type = type.upper()
    if type == 'CYS':
        narrate('Saving session as a CYS file...')
        return session.save_session(filename=filename, base_url=base_url)
    else:
        # e.g., CX, CYJS, GraphML, NNF, SIF, XGMML
        if type == 'GRAPHML': type = 'GraphML'
    cmd += ' options="' + type + '"'

    ext = '.' + type.lower()
    if re.search(ext + '$', filename) is None: filename += ext
    if not running_remote():
        filename = os.path.abspath(filename)
        if os.path.exists(filename): narrate(
            'This file already exists. A Cytoscape popup will be generated to confirm overwrite.')

    return commands.commands_post(f'{cmd} OutputFile="{filename}"', base_url=base_url)


@cy_log
def delete_network(network=None, base_url=DEFAULT_BASE_URL):
    """Delete a network from the current Cytoscape session.

    Args:
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> delete_network() # delete the current network
        >>> delete_network(22752) # delete network having SUID
        >>> delete_network('galFiltered.sif') # delete network having name
    """
    suid = get_network_suid(network)
    res = commands.cyrest_delete(f'networks/{suid}', base_url=base_url, require_json=False)
    return res


@cy_log
def delete_all_networks(base_url=DEFAULT_BASE_URL):
    """Delete all networks from the current Cytoscape session.

    Args:
         base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> delete_all_networks()
    """
    res = commands.cyrest_delete('networks', base_url=base_url, require_json=False)
    return res


# ==============================================================================
# II. General node functions
# ------------------------------------------------------------------------------

@cy_log
def get_first_neighbors(node_names=None, as_nested_list=False, network=None, base_url=DEFAULT_BASE_URL):
    """Returns a non-redundant list of first neighbors of the supplied list of nodes or current node selection.

    Args:
        node_names (str or list or None): A ``list`` of node names from the ``name`` column of the ``node table``.
            Default is currently selected nodes.
        as_nested_list (bool): Whether to return lists of neighbors per query node.
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: deduped list of nodes neighboring specified nodes.
            If as_nested_list parameter is True, a list of neighbor node lists, one per specified node

    Raises:
        CyError: if network name or SUID doesn't exist, if no nodes are selected, or if node doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_first_neighbors(node_names = None, as_nested_list=True)
        [['YBR020W', ['YGL035C', 'YOL051W', 'YPL248C', 'YML051W']], ['YGL035C', ['YLR044C', 'YLR377C', ...]], ...]
        >>> get_first_neighbors(['YBR020W', 'YGL035C'], as_nested_list=False)
        ['YGL035C', 'YOL051W', 'YPL248C', 'YML051W', 'YLR044C', 'YLR377C', 'YIL162W', ... ]
        >>> get_first_neighbors('YBR020W', as_nested_list=False)
        ['YGL035C', 'YOL051W', 'YPL248C', 'YML051W']

    See Also:
        :meth:`select_nodes`, :meth:`select_first_neighbors`
    """
    # TODO: This looks very inefficient because for each node, the entire node table is fetched from Cytoscape and the neighbor list is de-dupped ... verify this and maybe do better
    if node_names is None:
        node_names = network_selection.get_selected_nodes(network=network, base_url=base_url)
    elif isinstance(node_names, str):
        node_names = [node_names]

    if (node_names is None or len(node_names) == 0): return None

    net_suid = get_network_suid(network, base_url=base_url)
    neighbor_names = []

    for node_name in node_names:
        # get first neighbors for each node
        node_suid = node_name_to_node_suid([node_name], net_suid, base_url=base_url)[0]
        # TODO: Verify that this won't break if node_name_to_node_suid returns a list instead of a scalar ... I think it will break ... should we except??

        first_neighbors_suids = commands.cyrest_get(
            f'networks/{net_suid}/nodes/{node_suid}/neighbors', base_url=base_url)
        first_neighbors_names = node_suid_to_node_name(first_neighbors_suids, net_suid, base_url=base_url)

        if as_nested_list:
            neighbor_names.append([node_name, first_neighbors_names])
        else:
            neighbor_names += first_neighbors_names
            neighbor_names = list(dict.fromkeys(neighbor_names))  # dedup list

    return neighbor_names


@cy_log
def add_cy_nodes(node_names, skip_duplicate_names=True, network=None, base_url=DEFAULT_BASE_URL):
    """Add one or more nodes to a Cytoscape network.

    Args:
        node_names (list or None): A ``list`` of node names
        skip_duplicate_names (bool): Skip adding a node if a node with the same name is already in
            the network. If ``FALSE`` then a duplicate node (with a unique SUID) will be added.
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: A ``list`` of ``named lists`` of name and SUID for each node added.

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> add_cy_nodes(['newnode1', 'newnode2'], skip_duplicate_names=False)
        [{"name": "newnode1", "SUID": 1459}, {"name": "newnode2", "SUID": 1460}]
        >>> add_cy_nodes(['newnode2', 'newnode3'], skip_duplicate_names=True)
        [{"name": "newnode3", "SUID": 1460}]
    """
    net_suid = get_network_suid(network, base_url=base_url)
    if skip_duplicate_names:
        all_nodes_list = get_all_nodes(net_suid, base_url=base_url)
        node_names = list(set(node_names) - set(all_nodes_list))

    res = commands.cyrest_post(f'networks/{net_suid}/nodes', body=node_names, base_url=base_url)
    return res


@cy_log
def get_node_count(network=None, base_url=DEFAULT_BASE_URL):
    """Reports the number of nodes in the network.

    Args:
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        int: count of nodes in network.

    Raises:
        ValueError: if server response has no JSON
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_node_count()
        6
        >>> get_node_count(52)
        6
        >>> get_node_count('galFiltered.sif')
        6
    """
    net_suid = get_network_suid(network, base_url=base_url)
    res = commands.cyrest_get(f'networks/{net_suid}/nodes/count', base_url=base_url)
    return res['count']


@cy_log
def get_all_nodes(network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the names of all the nodes in the network.

    Args:
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: a ``list`` of nodes in the network

    Raises:
        ValueError: if server response has no JSON
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_all_nodes()
        ['YDL194W', 'YDR277C', 'YBR043C', ... ]
    """
    net_suid = get_network_suid(network, base_url=base_url)
    n_count = get_node_count(net_suid, base_url=base_url)
    if n_count == 0: return None

    res = commands.cyrest_get(f'networks/{net_suid}/tables/defaultnode/columns/name', base_url=base_url)
    return res['values']


# ==============================================================================
# III. General edge functions
# ------------------------------------------------------------------------------

@cy_log
def add_cy_edges(source_target_list, edge_type='interacts with', directed=False, network=None,
                 base_url=DEFAULT_BASE_URL):
    """Add one or more edges to a Cytoscape network by listing source and target node pairs.

    Args:
        source_target_list (list or list of lists): Source and target node pairs
        edgeType (str): The type of interaction. Default is 'interacts with'.
        directed (bool): Indicates whether interactions are directed. Default is ``FALSE``.
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list of dicts: A ``list`` of dicts for each edge (SUID, source, target) added.

    Raises:
        CyError: if network name or SUID doesn't exist, or if a source or target can't resolve to just one node.
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> add_cy_edges(['YLR075W', 'YKL028W'])
        [{'SUID': 2884, 'source': 1552, 'target': 1698}]
        >>> add_cy_edges([['YKL028W', 'YJR066W'], ['YJR066W', 'YLR452C'], ['YGR046W', 'YLR452C']])
        [{'SUID': 2886, 'source': 1698, 'target': 1645}, {'SUID': 2887, 'source': 1645, 'target': 1534} ...]
    """
    net_suid = get_network_suid(network, base_url=base_url)

    # Create list of all nodes in order presented
    # TODO: Find out what should happen if node name maps to multiple nodes
    if len(source_target_list) == 2 and isinstance(source_target_list, list) and isinstance(source_target_list[0],
                                                                                            str) and isinstance(
        source_target_list[1], str):
        flat_source_target_list = source_target_list
    else:
        flat_source_target_list = [item for sublist in source_target_list for item in sublist]
    edge_suid_list = node_name_to_node_suid(flat_source_target_list, net_suid, base_url=base_url)

    # Verify that each edge is unambiguous
    if True in [True if isinstance(x, list) else False for x in edge_suid_list]:
        raise CyError('More than one node found for a given source or target - no edges added')

    # Note: use str() for edge SUIDs in case the SUIDs exceed JSON's int encoding
    edge_data = [{'source': str(edge_suid_list[x]), 'target': str(edge_suid_list[x + 1]), 'directed': directed,
                  'interaction': edge_type} for x in range(0, len(edge_suid_list) - 1, 2)]

    res = commands.cyrest_post(f'networks/{net_suid}/edges', body=edge_data, base_url=base_url)
    return res


@cy_log
def get_edge_count(network=None, base_url=DEFAULT_BASE_URL):
    """Reports the number of the edges in the network.

    Args:
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
             port or version to connect to the CyREST API. Default is http://localhost:1234
             and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        int: count of edges in network.

    Raises:
        ValueError: if server response has no JSON
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_edge_count()
        6
        >>> get_edge_count(52)
        6
        >>> get_edge_count('galFiltered.sif')
        6
    """
    net_suid = get_network_suid(network, base_url=base_url)
    res = commands.cyrest_get(f'networks/{net_suid}/edges/count', base_url=base_url)
    return res['count']


@cy_log
def get_edge_info(edges, network=None, base_url=DEFAULT_BASE_URL):
    """Returns source, target and edge table row values.

    Args:
        edges (list): list of SUIDs or names of edges, i.e., values in the "name" column.
            Can also input single edge.
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
             port or version to connect to the CyREST API. Default is http://localhost:1234
             and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list of dicts: list of dicts describing each edge

    Raises:
        ValueError: if server response has no JSON
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_edge_info('YDR277C (pp) YDL194W')
        [{'source': 2919, 'target': 2918, 'SUID': 3248, 'shared name': 'YDR277C (pp) YDL194W',
          'shared interaction': 'pp', 'name': 'YDR277C (pp) YDL194W', 'selected': False,
          'interaction': 'pp', 'EdgeBetweenness': 496.0}]
        >>> get_edge_info(['YDR277C (pp) YDL194W', 'YDR277C (pp) YJR022W'])
        [{'source': 2919, 'target': 2918, 'SUID': 3248, 'shared name': 'YDR277C (pp) YDL194W',
          'shared interaction': 'pp', 'name': 'YDR277C (pp) YDL194W', 'selected': False,
          'interaction': 'pp', 'EdgeBetweenness': 496.0},
         {'source': 2919, 'target': 3220, 'SUID': 3249, 'shared name': 'YDR277C (pp) YJR022W',
          'shared interaction': 'pp', 'name': 'YDR277C (pp) YJR022W', 'selected': False,
          'interaction': 'pp', 'EdgeBetweenness': 988.0}]

    Notes: This function is kinda slow. It takes approximately 70ms per edge to return a result, e.g., 850 edges will take one minute.
    """
    net_suid = get_network_suid(network, base_url=base_url)
    if isinstance(edges, str): edges = [edges]

    def convert_edge_name_to_edge_info(edge_name):
        edge_suid = edge_name_to_edge_suid(edge_name, network, base_url=base_url)
        res = commands.cyrest_get('networks/%s/edges/%s' % (net_suid, edge_suid[0]), base_url=base_url)
        return res['data']

    edge_info = [convert_edge_name_to_edge_info(x) for x in edges]
    # TODO: Verify that it's always OK to return a list instead of a single dict ... this happens in many places
    return edge_info


@cy_log
def get_all_edges(network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the names of all the edges in the network.

    Args:
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: a ``list`` of edges in the network

    Raises:
        ValueError: if server response has no JSON
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
       >>> get_all_edges()
       ['YDR277C (pp) YDL194W', 'YDR277C (pp) YJR022W', 'YPR145W (pp) YMR117C', ...]
    """
    net_suid = get_network_suid(network, base_url=base_url)
    e_count = get_edge_count(network, base_url=base_url)
    if e_count == 0: return None

    res = commands.cyrest_get(f'networks/{net_suid}/tables/defaultedge/columns/name', base_url=base_url)
    return res['values']


# ==============================================================================
# IV. Network creation
# ------------------------------------------------------------------------------

@cy_log
def clone_network(network=None, base_url=DEFAULT_BASE_URL):
    """Makes a copy of a Cytoscape Network with all of its edges and nodes.

    Args:
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        int: The ``SUID`` of the new network

    Raises:
        ValueError: if server response has no JSON
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
       >>> clone_network()
       1477
    """
    net_suid = get_network_suid(network, base_url=base_url)
    res = commands.commands_post(f'network clone network="SUID:{net_suid}"', base_url=base_url)

    # TODO: Put double quotes around SUID
    return res['network']


@cy_log
def create_subnetwork(nodes=None, nodes_by_col='SUID', edges=None, edges_by_col='SUID', exclude_edges=False,
                      subnetwork_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Copies a subset of nodes and edges into a newly created subnetwork.

    Args:
        nodes (list): list of node names or keyword: selected, unselected or all. Default is currently selected nodes.
        nodes_by_col (str): name of node table column corresponding to provided nodes list; default is 'SUID'
        edges (list): list of edge names or keyword: selected, unselected or all. Default is currently selected edges.
        edges_by_col (str): name of edge table column corresponding to provided edges list; default is 'SUID'
        exclude_edges (bool): whether to exclude connecting edges; default is FALSE
        subnetwork_name (str): name of new subnetwork to be created; default is to add a numbered suffix to source network name
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        int: The ``SUID`` of the new subnetwork

    Raises:
        ValueError: if server response has no JSON
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> create_subnetwork(nodes='all') # choose all selected and unselected nodes
        1477
        >>> create_subnetwork(edges='selected') # choose only nodes whose edges are selected, and include those edges
        1477
        >>> create_subnetwork(nodes=['RAP1', 'HIS4', 'PDC1', 'RPL18A'], nodes_by_col='COMMON', subnetwork_name=base_name+'xx')
       1477
    """
    # TODO: Verify that node and edge names can't contain blanks or commas
    title = get_network_suid(network, base_url=base_url)
    exclude_edges = 'true' if exclude_edges else 'false'
    if isinstance(nodes, str) and nodes in ['all', 'selected', 'unselected']: nodes_by_col = None
    if isinstance(edges, str) and edges in ['all', 'selected', 'unselected']: edges_by_col = None
    json_sub = {'source': 'SUID:' + str(title), 'excludeEdges': exclude_edges,
                'nodeList': commands.prep_post_query_lists(nodes, nodes_by_col),
                'edgeList': commands.prep_post_query_lists(edges, edges_by_col)}
    if not subnetwork_name is None: json_sub['networkName'] = subnetwork_name

    res = commands.cyrest_post('commands/network/create', body=json_sub, base_url=base_url)
    return res['data']['network']


@cy_log
def create_network_from_igraph(igraph, title='From igraph', collection='My Igraph Network Collection',
                               base_url=DEFAULT_BASE_URL):
    """Create a Cytoscape network from an igraph network.

    Takes an igraph network and generates data frames for nodes and edges to
    send to the createNetwork function. Returns the network.suid and applies the perferred
    layout set in Cytoscape preferences.

    Notes:
        Vertices and edges from the igraph network will be translated into nodes and edges
        in Cytoscape. Associated attributes will also be passed to Cytoscape as node and edge
        table columns. Note: undirected networks will be implicitly modeled as directed
        in Cytoscape. Conversion back via ``createIgraphFromNetwork`` will result in
        a directed network. Also note: igraph attributes of type "other" denoted by "x"
        are converted to "String" in Cytoscape.

        Note that the extra ``id`` column is created in the node table because the ``id`` column is mandatory in the
        cytoscape.js format, which is what is sent to Cytoscape.

    Args:
        igraph (igraph): igraph network object
        title (str): network name
        collection (str): network collection name
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        int: The ``SUID`` of the new network

    Raises:
        ValueError: if server response has no JSON
        KeyError: igraph network doesn't contain required node or edge attributes
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> g = ig.Graph()
        >>> g.add_vertices(3)
        >>> g.vs['name'] = ['RAP1', 'HIS4', 'HIS3']
        >>> g.add_edges([(0, 1), (1, 2)])
        >>> g.es['source'] = [g.vs[0]['name'], g.vs[1]['name']]
        >>> g.es['target'] = [g.vs[1]['name'], g.vs[2]['name']]
        >>> g.es['interaction'] = ['enhances', 'inhibits']
        >>> create_network_from_igraph(g, 'new graph', 'my collection')
        138775

    See Also:
        :meth:`create_network_from_data_frames`, :meth:`create_igraph_from_network`
    """

    # TODO: Verify the type "other" behavior described above
    # TODO: Verify the undeclared parameter behaviors claimed in the R documents
    # TODO: Is this really faithful to the R implementation?

    def attrs_present(entity_collection):
        attrs = set()
        for entity in entity_collection:
            attrs |= set(entity.attributes().keys())
        return attrs

    def copy_attrs_to_dataframe(entity_collection):
        df = pd.DataFrame()
        for col in attrs_present(entity_collection):
            df[col] = entity_collection[col]
        return df

    node_df = copy_attrs_to_dataframe(igraph.vs)
    edge_df = copy_attrs_to_dataframe(igraph.es)

    # Make sure critical attributes are strings
    node_df['name'] = node_df['name'].astype(str)
    edge_df['source'] = edge_df['source'].astype(str)
    edge_df['target'] = edge_df['target'].astype(str)
    if 'interaction' in edge_df.columns: edge_df['interaction'] = edge_df['interaction'].astype(str)

    if len(node_df.index) == 0: node_df = None
    if len(edge_df.index) == 0: edge_df = None

    return create_network_from_data_frames(nodes=node_df, edges=edge_df, title=title, collection=collection,
                                           base_url=base_url, node_id_list='name')


@cy_log
def create_network_from_networkx(netx, title='From networkx', collection='My NetworkX Network Collection',
                              base_url=DEFAULT_BASE_URL):
    """Create a Cytoscape network from a NetworkX graph.

    Args:
        netx (MultiDiGraph): networkx MultiDiGraph object
        title (str): network name
        collection (str): network collection name
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        Dict: {'networkSUID': 31766}

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> n = create_network_from_networkx(netx)
        {'networkSUID': 31766}
        >>> n = create_network_from_networkx(netx, 'Cool Networkx', 'Collection of Cool Networks')
        {'networkSUID': 31766}

    See Also:
        :meth:`create_networkx_from_network`
    """
    netx_nodes = netx.nodes(data=True) # returns list of tuples (name, attrs)
    netx_node_list = [{**attrs, 'name': name}    for name, attrs in netx_nodes]
    node_df = pd.DataFrame.from_records(netx_node_list)

    netx_edges = netx.out_edges(data=True, keys=True) # returns list of tuples (src, targ, suid, attrs)
    netx_edge_list = [{**attrs, 'source': src, 'target': targ}    for src, targ, suid, attrs in netx_edges]
    edge_df = pd.DataFrame.from_records(netx_edge_list)

    # TODO: This will blow if there are no edges or no nodes ... so will create_network_from_igraph() ... will R blow, too?

    # Make sure critical attributes are strings
    node_df['name'] = node_df['name'].astype(str)
    edge_df['source'] = edge_df['source'].astype(str)
    edge_df['target'] = edge_df['target'].astype(str)
    if 'interaction' in edge_df.columns: edge_df['interaction'] = edge_df['interaction'].astype(str)

    if len(node_df.index) == 0: node_df = None
    if len(edge_df.index) == 0: edge_df = None

    return create_network_from_data_frames(nodes=node_df, edges=edge_df, title=title, collection=collection,
                                           base_url=base_url, node_id_list='name')

@cy_log
def create_network_from_data_frames(nodes=None, edges=None, title='From dataframe',
                                    collection='My Dataframe Network Collection', base_url=DEFAULT_BASE_URL, *,
                                    node_id_list='id', source_id_list='source', target_id_list='target',
                                    interaction_type_list='interaction'):
    """Create a network from data frames.

    Takes data frames for nodes and edges, as well as naming parameters to generate the JSON data format required by
    the "networks" POST operation via CyREST. Returns the network.suid and applies the preferred layout set in
    Cytoscape preferences.

    Notes:
        ``nodes`` should contain a column of character strings named: id. This name can be overridden by the arg:
        ``node_id_list``. Additional columns are loaded as node attributes. ``edges`` should contain columns of
        character strings named: source, target and interaction. These names can be overridden by args:
        source_id_list, target_id_list, interaction_type_list. Additional columns are loaded as edge attributes.
        The ``interaction`` list can contain a single value to apply to all rows; and if excluded altogether, the
        interaction type will be set to "interacts with". NOTE: attribute values of types (num) will be imported
        as (Double); (int) as (Integer); (chr) as (String); and (logical) as (Boolean). (Lists) will be imported as
        (Lists) in CyREST v3.9+.

        Note that the extra ``id`` column is created in the node table because the ``id`` column is mandatory in the
        cytoscape.js format, which is what is sent to Cytoscape.

    Args:
        nodes (DataFrame): see details and examples below; default NULL to derive nodes from edge sources and targets
        edges (DataFrame): see details and examples below; default NULL for disconnected set of nodes
        title (str): network name
        collection (str): network collection name
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.
        * :
        node_id_list (str): Name of column in ``nodes`` containing node id
        source_id_list (str): Name of column in ``edges`` containing source node name
        target_id_list (str): Name of column in ``edges``  containing target node name
        interaction_type_list (str): Name of column in ``edges``  containing interaction name

    Returns:
        int: The ``SUID`` of the new network

    Raises:
        ValueError: if server response has no JSON
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> node_data = {'id':["node 0","node 1","node 2","node 3"],
        >>>              'group':["A","A","B","B"],
        >>>              'score':[20,10,15,5]}
        >>> nodes = df.DataFrame(data=node_data, columns=['id', 'group', 'score'])
        >>> edge_data = {'source':["node 0","node 0","node 0","node 2"],
        >>>              'target':["node 1","node 2","node 3","node 3"],
        >>>              'interaction':["inhibits","interacts","activates","interacts"],
        >>>              'weight':[5.1,3.0,5.2,9.9]}
        >>> edges = df.DataFrame(data=edge_data, columns=['source', 'target', 'interaction', 'weight'])
        >>>
        >>> create_network_from_data_frames(nodes, edges, title='From node & edge dataframe')
        1477
    """

    # TODO: Verify the above documentation

    def compute_edge_name(source, target, interaction):
        return source + ' (' + interaction + ') ' + target

    # Create a node list even if we have to use the edges lists to infer nodes
    if nodes is None:
        if not edges is None:
            id_list = []
            for source, target in zip(edges['source'].values, edges['target'].values):
                id_list.append(source)
                id_list.append(target)
            nodes = pd.DataFrame(data=id_list, columns=['id'])
        else:
            raise CyError('Must provide either nodes or edges')

    # create the JSON for a node list ... in cytoscape.js format
    # TODO: Verify that we really do need this 'id' field ... or maybe we can kill it afterward?
    json_nodes = [{'data': {'id': node}} for node in nodes[node_id_list]]

    # create the JSON for an edge list ... in cytoscape.js format
    json_edges = []
    if not edges is None:
        if not interaction_type_list in edges.columns: edges[interaction_type_list] = 'interacts with'
        edges_sub = edges[[source_id_list, target_id_list, interaction_type_list]]
        json_edges = [{'data': {'name': compute_edge_name(source, target, interaction), 'source': source,
                                'target': target, 'interaction': interaction}} for source, target, interaction in
                      zip(edges_sub[source_id_list], edges_sub[target_id_list], edges_sub[interaction_type_list])]

    # create the full JSON for a cytoscape.js-style network ... see http://manual.cytoscape.org/en/stable/Supported_Network_File_Formats.html#cytoscape-js-json
    # Note that no node or edge attributes are included in this version of the network
    json_network = {'data': [{'name': title}], 'elements': {'nodes': json_nodes, 'edges': json_edges}}

    # call Cytoscape to create this network and return the SUID
    network_suid = commands.cyrest_post('networks', parameters={'title': title, 'collection': collection},
                                        body=json_network, base_url=base_url)
    # TODO: There appears to be a race condition here ... the view isn't set for a while. Without an explicit delay, the
    # "vizmap apply" command below fails for lack of a valid view.
    time.sleep(MODEL_PROPAGATION_SECS)

    # drop the SUID column if one is present
    nodes = nodes.drop(['SUID'], axis=1, errors='ignore')

    # load node attributes into Cytoscape network
    if len(set(nodes.columns) - {node_id_list}) != 0:
        tables.load_table_data(nodes, data_key_column=node_id_list, table_key_column=node_id_list, network=network_suid,
                               base_url=base_url)

    if not edges is None:
        # get rid of SUID column if one is present
        edges = edges.drop(['SUID'], axis=1, errors='ignore')
        # create edge name out of source/interaction/target
        edge_names = [compute_edge_name(source, target, interaction) for source, interaction, target in
                      zip(edges[source_id_list], edges[interaction_type_list], edges[target_id_list])]
        edges['name'] = edge_names
        # find out the SUID of each node so it can be used in a multigraph if needed
        edges['data.key.column'] = edge_name_to_edge_suid(edge_names, network_suid, base_url=base_url)

        # if the edge list looks real, add the edge attributes (if any)
        if len(set(edges.columns) - set(['source', 'target', 'interaction', 'name', 'data.key.column'])) != 0:
            tables.load_table_data(edges, data_key_column='data.key.column', table='edge', table_key_column='SUID',
                                   network=network_suid, base_url=base_url)

    narrate('Applying default style...')
    commands.commands_post('vizmap apply styles="default"', base_url=base_url)

    narrate('Applying preferred layout')
    layouts.layout_network(network=network_suid)

    # TODO: Verify that attribute types are properly set in Cytoscape

    return network_suid


@cy_log
def import_network_from_file(file=None, base_url=DEFAULT_BASE_URL):
    """Loads a network from specified file.

    Args:
        file (str): Name of file in any of the supported formats (e.g., SIF, GML, xGMML, etc).
            If None, a demo network file in SIF format is loaded.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {"networks": [network suid], "views": [suid for views]} where networks and views lists have length 1

    Raises:
        CyError: if file cannot be found or loaded
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> import_network_from_file() # import demo network
        {'networks': [131481], 'views': [131850]}
        >>> import_network_from_file('data/yeastHighQuality.sif')
        {'networks': [131481], 'views': [131850]}
    """
    if file is None:
        file = 'data/galFiltered.sif'
    if not running_remote():
        file = os.path.abspath(file)
    res = commands.commands_post(f'network load file file="{file}"', base_url=base_url)
    # TODO: Fix R documentation to match what's really returned
    # TODO: Put double quotes around file

    # should not be necessary, but is because "network load file" doesn't actually set the current network
    # until after it's done. So, without the sleep(), setting the current network will be superceded by
    # "network load file"'s own network. This is race condition that can be solved by "network load file"
    # not returning until it's actually done.
    # TODO: Fix this race condition
    time.sleep(CATCHUP_NETWORK_SECS)

    return res


# ==============================================================================
# V. Network extraction
# ------------------------------------------------------------------------------

@cy_log
def create_igraph_from_network(network=None, base_url=DEFAULT_BASE_URL):
    """Create an igraph network from a Cytoscape network.

    Notes:
        Takes a Cytoscape network and generates data frames for vertices and edges to send to the graph_from_data_frame
        function. Nodes and edges from the Cytoscape network will be translated into vertices and edges in igraph.
        Associated table columns will also be passed to igraph as vertex and edge attributes. All networks are
        implicitly modeled as directed in Cytoscape. Round-trip conversion of an undirected network in igraph via
        ``createNetworkFromIgraph`` to Cytoscape and back to igraph will result in a directed network.

    Args:
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        igraph: The new ``igraph`` object

    Raises:
        ValueError: if server response has no JSON
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> create_igraph_from_network()
        IGRAPH DN-- 330 359 --
        + attr: AverageShortestPathLength (v), BetweennessCentrality (v), COMMON (v),
          ClosenessCentrality (v), ClusteringCoefficient (v), Degree (v), Eccentricity
          (v), IsSingleNode (v), NeighborhoodConnectivity (v), NumberOfDirectedEdges
          (v), NumberOfUndirectedEdges (v), PartnerOfMultiEdgedNodePairs (v),
          Radiality (v), SelfLoops (v), Stress (v), TopologicalCoefficient (v),
          degree.layout (v), gal1RGexp (v), gal1RGsig (v), gal4RGexp (v), gal4RGsig
          (v), gal80Rexp (v), gal80Rsig (v), isExcludedFromPaths (v), name (v),
          selected (v), shared name (v), EdgeBetweenness (e), interaction (e), name
          (e), selected (e), shared interaction (e), shared name (e), source (e),
          target (e)
        + edges (vertex names):
        YML064C->YLR284C, YML064C->YHR198C, YKL074C->YGL035C, YDL081C->YLR340W,
        ...

    See Also:
        :meth:`create_network_from_data_frames`, :meth:`create_network_from_igraph`
    """
    suid = get_network_suid(network, base_url=base_url)

    # get dataframes
    cyedges = tables.get_table_columns('edge', network=suid, base_url=base_url)
    cynodes = tables.get_table_columns('node', network=suid, base_url=base_url)

    # check for source and target columns ... if they're not present, dig them out of the full name
    if not {'source', 'target'} <= set(cyedges.columns):
        src_trg = [re.split("\ \\(.*\\)\ ", x) for x in cyedges['name']]
        cyedges['source'] = [x[0] for x in src_trg]
        cyedges['target'] = [x[1] for x in src_trg]

    # set up iGraph vertices ... first create vertex by naming it, then pile on attributes
    # Tutorial: https://igraph.org/python/doc/tutorial/tutorial.html
    # Source: https://github.com/igraph/python-igraph/blob/master/src/igraph/__init__.py
    g = ig.Graph(directed=True)

    # add all nodes and their attributes
    g.add_vertices(list(cynodes['name']))
    for col in cynodes.columns:
        if not col in ['name', 'SUID']: g.vs[col] = list(cynodes[col])

    # add all edges and their nodes
    g.add_edges([(src, trg) for src, trg in zip(cyedges['source'], cyedges['target'])])
    # TODO: Find out why this rename happens ... is this an iGraph thing? ... how does the roundtrip work?
    cyedges.rename({'source': 'from', 'target': 'to'})
    for col in cyedges.columns:
        if not col in ['SUID']: g.es[col] = list(cyedges[col])

    return g


@cy_log
def create_networkx_from_network(network=None, base_url=DEFAULT_BASE_URL):
    """Return the Cytoscape network as a networkx multi-di-graph.

    Args:
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        MultiDiGraph: The new ``networkx`` object

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> n = create_networkx_from_network(network='galFiltered.sif')
        >>> print(nx.info(n))
        Name:
        Type: MultiDiGraph
        Number of nodes: 330
        Number of edges: 359
        Average in degree:   1.0879
        Average out degree:   1.0879

    See Also:
        :meth:`create_network_from_networkx`
    """
    suid = get_network_suid(network, base_url=base_url)

    # get dataframes
    cyedges = tables.get_table_columns('edge', network=suid, base_url=base_url)
    cynodes = tables.get_table_columns('node', network=suid, base_url=base_url)

    # check for source and target columns ... if they're not present, dig them out of the full name
    if not {'source', 'target'} <= set(cyedges.columns):
        src_trg = [re.split("\ \\(.*\\)\ ", x) for x in cyedges['name']]
        cyedges['source'] = [x[0] for x in src_trg]
        cyedges['target'] = [x[1] for x in src_trg]

    # Create a list of edges as tuples (src, targ, suid, attrs) with 'source' & 'target' removed from attrs
    edges_dict = cyedges.to_dict(orient='record')
    e_bunch = [(row['source'],
                row['target'],
                row['SUID'],
                {k: row[k]     for k in row if k not in {'source', 'target'}}
                ) for row in edges_dict]

    # Create a list of nodes as tuples (name, attrs) with 'name' removed from attrs
    nodes_dict = cynodes.to_dict(orient='record')
    n_bunch = [(row['name'], {k: row[k]     for k in row if k not in {'name'}}) for row in nodes_dict]

    # Create the networkx graph modeled as directed edges with ability to have multiple edges connecting two nodes
    md_graph = nx.MultiDiGraph()
    md_graph.add_edges_from(e_bunch)
    md_graph.add_nodes_from(n_bunch)

    return md_graph


# ==============================================================================
# VI. Internal functions
#
# Dev Notes: Prefix internal functions with a '_'. Skip doc_strings for these
# functions.
# ------------------------------------------------------------------------------
