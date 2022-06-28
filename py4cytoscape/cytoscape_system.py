# -*- coding: utf-8 -*-

"""Functions for inspecting and managing apps for Cytoscape.
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

# Internal module imports
from . import commands

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log, narrate
from ._version import __version__, _automation_api_version


@cy_log
def cytoscape_ping(base_url=DEFAULT_BASE_URL):
    """Ping Cytoscape

    Tests the connection to Cytoscape via CyREST and verifies that supported versions of Cytoscape and CyREST API are loaded.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        None

    Raises:
        CyError: if error connecting to CyREST or version is unsupported
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cytoscape_ping()
        You are connected to Cytoscape!
    """
    from .py4cytoscape_utils import verify_supported_versions
    verify_supported_versions(1, 3.6, base_url=base_url)
    return narrate('You are connected to Cytoscape!')

@cy_log
def cytoscape_version_info(base_url=DEFAULT_BASE_URL):
    """Return the versions of the current Cytoscape and CyREST API.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'apiVersion': <version>, 'cytoscapeVersion': <version>, 'automationAPIVersion': <version>, 'py4cytoscapeVersion': <version>}

    Raises:
        CyError: if error connecting to CyREST
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cytoscape_version_info()
        {'apiVersion': 'v1', 'cytoscapeVersion': '3.8.1', 'automationAPIVersion': '0.0.0', 'py4cytoscapeVersion': '0.0.2'}
    """
    versions = commands.cyrest_get('version', base_url=base_url)
    if len(versions) == 0:
        raise CyError('CyREST connection problem. py4cytoscape cannot continue!')
    versions.update({'automationAPIVersion': _automation_api_version, 'py4cytoscapeVersion': __version__})
    versions.update(commands.sub_versions(base_url=base_url))

    return versions


@cy_log
def cytoscape_api_versions(base_url=DEFAULT_BASE_URL):
    """Get the list of available CyREST API versions.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

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


@cy_log
def cytoscape_number_of_cores(base_url=DEFAULT_BASE_URL):
    """Returns the processor resources of the server running Cytoscape.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

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


@cy_log
def cytoscape_memory_status(base_url=DEFAULT_BASE_URL):
    """Returns the memory resources of the server running Cytoscape.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

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


@cy_log
def cytoscape_free_memory(base_url=DEFAULT_BASE_URL):
    """Manually call Java's garbage collection ``System.gc()`` to free up unused memory.

    This process happens automatically, but may be useful to call explicitly for testing or evaluation purposes.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

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
        res = commands.cyrest_get('gc', base_url=base_url, require_json=False)
        return narrate('Unused memory freed up.')
    except:
        raise CyError('CyREST connection problem. py4cytoscape cannot continue!')

