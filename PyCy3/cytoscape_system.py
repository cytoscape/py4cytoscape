# -*- coding: utf-8 -*-

"""Functions for inspecting and managing apps for Cytoscape.
"""

import sys

from . import commands
from .exceptions import CyError
from .pycy3_utils import *

def cytoscape_ping(base_url=DEFAULT_BASE_URL):
    """Ping Cytoscape

    Tests the connection to Cytoscape via CyREST and verifies that supported versions of Cytoscape and CyREST API are loaded.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        None

    Raises:
        CyError: if error connecting to CyREST or version is unsupported
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cytoscape_ping()
        You are connected to Cytoscape!
    """
    from .pycy3_utils import verify_supported_versions
    verify_supported_versions(1, 3.6, base_url=base_url)
    print('You are connected to Cytoscape!')
# TODO: Is this the way this should be reported in Python? In R?


def cytoscape_version_info(base_url=DEFAULT_BASE_URL):
    """Return the versions of the current Cytoscape and CyREST API.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        dict: {'apiVersion': <version>, 'cytoscapeVersion': <version>}

    Raises:
        CyError: if error connecting to CyREST
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cytoscape_version_info()
        {'apiVersion': 'v1', 'cytoscapeVersion': '3.8.0'}
    """
    versions = commands.cyrest_get('version', base_url=base_url)
    if len(versions) == 0:
# TODO: Figure out whether we really want to report this to stderr.
        error = 'CyREST connection problem. PyCy3 can not continue!'
        sys.stderr.write(error)
        raise CyError(error)
# TODO: R doesn't raise an exception ... perhaps it should?

    return versions

def cytoscape_api_versions(base_url=DEFAULT_BASE_URL):
    """Get the list of available CyREST API versions.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        list: list of available API versions

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cytoscape_api_versions()
        ['v1']
    """
    uri = base_url.split('/v')[0]
    res = commands.cyrest_get(base_url=uri)
    available_api_versions = res['availableApiVersions']
    return available_api_versions

def cytoscape_number_of_cores(base_url=DEFAULT_BASE_URL):
    """Returns the processor resources of the server running Cytoscape.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        int: count of available CPUs

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cytoscape_number_of_cores()
        4
    """
    res = commands.cyrest_get(base_url=base_url)
    return res['numberOfCores']

def cytoscape_memory_status(base_url=DEFAULT_BASE_URL):
    """Returns the memory resources of the server running Cytoscape.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        dict: {'usedMemory': <mem>, 'freeMemory': <mem>, 'totalMemory': <mem>, 'maxMemory': <mem>} where <mem> is a count of megabytes

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cytoscape_memory_status()
        {'usedMemory': 160, 'freeMemory': 1819, 'totalMemory': 1979, 'maxMemory': 5510}
    """
    res = commands.cyrest_get(base_url=base_url)
    return res['memoryStatus']

def cytoscape_free_memory(base_url=DEFAULT_BASE_URL):
    """Manually call Java's garbage collection ``System.gc()`` to free up unused memory.

    This process happens automatically, but may be useful to call explicitly for testing or evaluation purposes.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        str: 'Unused memory freed up.'

    Raises:
        CyError: if can't free memory
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cytoscape_free_memory()
        'Unused memory freed up.'
    """
    try:
        res = commands.cyrest_get('gc', require_json=False)
        return 'Unused memory freed up.'  # TODO: Is this what we want to return?
    except:
# TODO: Figure out whether we really want to report this to stderr.
        error = 'CyREST connection problem. PyCy3 can not continue!'
        sys.stderr.write(error)
        raise CyError(error)
# TODO: R doesn't raise an exception ... perhaps it should?
