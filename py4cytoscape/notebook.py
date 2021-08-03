# -*- coding: utf-8 -*-

"""Functions that support use of Cytoscape in a Jupyter Notebook environment.
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
from . import network_views
from . import sandbox

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log
from .py4cytoscape_notebook import get_notebook_is_running

@cy_log
def show_image_in_notebook(filename='image', type='PNG', resolution=None, units=None, height=None, width=None, zoom=None,
                           sandbox_name=None, network=None, base_url=DEFAULT_BASE_URL, *, overwrite_file=True):
    """Retrieve list of network view SUIDs.

    Args:
        network (str or SUID or None): Name or SUID of the network. Default is the "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: [list of SUIDs of views] where the list has length 1

    Raises:
        CyError: if network doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_network_views()
        [130223]
        >>> get_network_views(51)
        [130223]
        >>> get_network_views(network='galFiltered.sif')
        [130223]
    """
    if get_notebook_is_running():
        image_file = network_views.export_image(filename=filename, type=type, resolution=resolution, units=units, height=height, width=width, zoom=zoom,
                                                network=network, base_url=base_url, overwrite_file=overwrite_file)['file']
        print(str(image_file))
        res = sandbox.sandbox_get_from(image_file, overwrite=overwrite_file, sandbox_name=sandbox_name, base_url=base_url)
        print(str(res))

        from IPython import display
        return display.Image(filename)
    else:
        raise CyError('Cannot display network view image unless running as a Jupyter Notebook.')


