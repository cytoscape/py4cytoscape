# -*- coding: utf-8 -*-

"""Functions for getting information about network COLLECTIONS.
"""

# External library imports
import sys

# Internal module imports
from . import commands
from . import networks

# Internal module convenience imports
from .exceptions import CyError
from .pycy3_utils import *
from .pycy3_logger import cy_log


@cy_log
def get_collection_list(base_url=DEFAULT_BASE_URL):
    """Get Collection List.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        list: list of collection names, one for each collection

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_collection_list()
        []
        >>> get_collection_list()
        ['galFiltered.sif', 'BINDyeast.sif']
    """
    res = commands.cyrest_get('collections', base_url=base_url)
    col_names = [get_collection_name(suid, base_url=base_url) for suid in res]
    return col_names


# TODO: It's hard to load a network into its own collection, so this is all hard to test.
# TODO: This function returns collection names, but not SUIDs ... it's hard to get a collection SUID given a collection name

@cy_log
def get_collection_suid(network=None, base_url=DEFAULT_BASE_URL):
    """Get Collection Suid.

    Args:
        network (SUID or str or None): Network name or SUID of a network in the collection
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        int: the SUID of the collection containing the network

    Raises:
        CyError: if no collection exists
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_collection_suid()
        [851280]
        >>> get_collection_suid('current')
        [851280]
        >>> get_collection_suid(851296)
        [851280]
        >>> get_collection_suid('galFiltered.sif')
        [851280]
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.cyrest_get('collections', parameters={'subsuid': net_suid}, base_url=base_url)
    return res[0]


@cy_log
def get_collection_name(collection_suid=None, base_url=DEFAULT_BASE_URL):
    """Get Collection Name.

    Args:
        collection_suid (SUID or None): SUID of a collection (or None for "current" collection)
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        str: the name of the collection associated with SUID

    Raises:
        CyError: if no collection exists
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error or SUID doesn't exist

    Examples:
        >>> get_collection_name()
        'galFiltered.sif'
        >>> get_collection_suid(851296)
        'galFiltered.sif'
    """
    if collection_suid is None: collection_suid = get_collection_suid(base_url=base_url)
    res = commands.cyrest_get('collections/' + str(collection_suid) + '/tables/default', base_url=base_url)
    return res['rows'][0]['name']


@cy_log
def get_collection_networks(collection_suid=None, base_url=DEFAULT_BASE_URL):
    """Get Collection Networks.

    Args:
        collection_suid (SUID or None): SUID of a collection (or None for "current" collection)
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        list: list of SUIDs for networks within the collection

    Raises:
        CyError: if no collection exists
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error or SUID doesn't exist

    Examples:
        >>> get_collection_name()
        'galFiltered.sif'
        >>> get_collection_suid(851296)
        'galFiltered.sif'
    """
    if collection_suid is None: collection_suid = get_collection_suid(base_url=base_url)
    res = commands.cyrest_get('collections/' + str(collection_suid) + '/subnetworks', base_url=base_url)
    return res
