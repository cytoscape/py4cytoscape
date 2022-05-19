# -*- coding: utf-8 -*-

"""Functions for communicating with NDEx from within Cytoscape.
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
import re
import time

# Internal module imports
from . import commands
from . import networks

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log

@cy_log
def import_network_from_ndex(ndex_id, username=None, password=None, access_key=None, ndex_url="http://ndexbio.org", ndex_version="v2", base_url=DEFAULT_BASE_URL):
    """Import a network from the NDEx database into Cytoscape.

    Args:
        ndex_id (str): Network ``externalId`` provided by NDEx. This is not the same as a Cytoscape SUID.
        username (str): NDEx account username; required for private content
        password (str): NDEx account password; required for private content
        access_key (str): NDEx accessKey; alternate acccess to private content
        ndex_url (str): NDEX website url; Default is http://ndexbio.org
        ndex_version(str): NDEX version number; Default is v2
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        int: SUID of imported network

    Raises:
        CyError: if credentials, NDEx ID or access_key are invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> import_network_from_ndex(galFiltered_uuid, 'userid', 'password')
        52
        >>> import_network_from_ndex(galFiltered_uuid, access_key=test_key)
        52

    Note:
        Importing a network that has recently been stored on NDEx may result in an error if NDEx has not finished indexing it. Lags can range from a few seconds to a few minutes.
    """
    if re.search("^https?://", ndex_url) == None:
        ndex_url = "".join(["http://", ndex_url])
    server_Url = "/".join([ndex_url, ndex_version])
    ndex_body = {'serverUrl': server_Url, 'uuid': ndex_id}
    if username is not None: ndex_body.update({'username': username})
    if password is not None: ndex_body.update({'password': password})
    if access_key is not None: ndex_body.update({'accessKey': access_key})

    res = commands.cyrest_post('networks', body=ndex_body, base_url=_cy_ndex_base_url(base_url))
    return res['data']['suid']

@cy_log
def export_network_to_ndex(username, password, is_public, network=None, metadata=None, ndex_url="http://ndexbio.org", ndex_version="v2", base_url=DEFAULT_BASE_URL):
    """Send a copy of a Cytoscape network to NDEx as a new submission.

    Args:
        username (str): NDEx account username; required for private content
        password (str): NDEx account password; required for private content
        is_public (bool): Whether to make the network publicly accessible at NDEx.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        metadata (dict): A list of structured information describing the network
        ndex_url (str): NDEX website url; Default is http://ndexbio.org
        ndex_version(str): NDEX version number; Default is v2
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: NDEx identifier ``externalId`` for new submission

    Raises:
        CyError: if credentials or network are invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> export_network_to_ndex('userid', 'password', False)
        '7bc2548c-9c93-11ea-aaef-0ac135e8bacf'
        >>> export_network_to_ndex('userid', 'password', False, network='galFiltered.sif')
        '7bc2548c-9c93-11ea-aaef-0ac135e8bacf'

    Note:
        Storing a network on NDEx and then immediately retrieving it may result in an error if NDEx has not finished indexing the network. Lags can range from a few seconds to a few minutes.
    """
    if re.search("^https?://", ndex_url) == None:
        ndex_url = "".join(["http://", ndex_url])
    server_Url = "/".join([ndex_url, ndex_version])
    suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.cyrest_post(f'networks/{suid}', body={'serverUrl': server_Url,
                                                         'username': username,
                                                         'password': password,
                                                         'metadata': metadata,
                                                         'isPublic': is_public},
                               base_url=_cy_ndex_base_url(base_url))
    return res['data']['uuid']

@cy_log
def update_network_in_ndex(username, password, is_public, network=None, metadata=None, ndex_url = "http://ndexbio.org", ndex_version = "v2", base_url=DEFAULT_BASE_URL):
    """Update Network In NDEx.

    Update an existing network in NDEx, given a previously assoicaiated Cytoscape network, e.g., previously
    exported to NDEx or imported from NDEx.

    Args:
        username (str): NDEx account username; required for private content
        password (str): NDEx account password; required for private content
        is_public (bool): Whether to make the network publicly accessible at NDEx.
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        metadata (dict): A list of structured information describing the network
        ndex_url (str): NDEX website url; Default is http://ndexbio.org
        ndex_version(str): NDEX version number; Default is v2
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: NDEx identifier ``externalId`` for the updated submission

    Raises:
        CyError: if credentials or network are invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> update_network_in_ndex('userid', 'password', False)
        '7bc2548c-9c93-11ea-aaef-0ac135e8bacf'
        >>> update_network_in_ndex('userid', 'password', False, network='galFiltered.sif')
        '7bc2548c-9c93-11ea-aaef-0ac135e8bacf'

    Note:
        Storing a network on NDEx and then immediately retrieving it may result in an error if NDEx has not finished indexing the network. Lags can range from a few seconds to a few minutes.
    """
    if re.search("^https?://", ndex_url) == None:
        ndex_url = "".join(["http://", ndex_url])
    server_Url = "/".join([ndex_url, ndex_version])
    suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.cyrest_put(f'networks/{suid}', body={'serverUrl': server_Url,
                                                        'username': username,
                                                        'password': password,
                                                        'metadata': metadata,
                                                        'isPublic': is_public},
                              base_url=_cy_ndex_base_url(base_url)
                              )
    return res['data']['uuid']


# TODO: It looks like [0] picks up the first sub-network instead of the one that was requested ... is this how it should work?

@cy_log
def get_network_ndex_id(network=None, base_url=DEFAULT_BASE_URL):
    """Get Network NDEx Id.

    Retrieve the NDEx externalId for a Cytoscape network, presuming it has already been exported to NDEx.

    If the Cytoscape network is not associated with an NDEx network, the return value will be None.

    Args:
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        metadata (dict): A list of structured information describing the network
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: NDEx identifier ``externalId`` or NULL

    Raises:
        CyError: if network is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_network_ndex_id()
        '7bc2548c-9c93-11ea-aaef-0ac135e8bacf'
        >>> get_network_ndex_id(network='galFiltered.sif')
        '7bc2548c-9c93-11ea-aaef-0ac135e8bacf'
    """
    suid = networks.get_network_suid(network, base_url=base_url)

    res = commands.cyrest_get(f'networks/{suid}', base_url=_cy_ndex_base_url(base_url))
    return res['data']['members'][0].get('uuid', None)


# ------------------------------------------------------------------------------
# Transforms generic base.url into a specific cyndex.base.url
def _cy_ndex_base_url(base_url):
    return re.sub('(.+?)\\/(v\\d+)$', '\\1/cyndex2/\\2', base_url)
