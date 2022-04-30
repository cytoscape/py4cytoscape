# -*- coding: utf-8 -*-

"""Functions for performing VIEW operations in addition to getting and setting view properties.
"""

"""Dev Notes: refer to StyleValues.R, StyleDefaults.R and StyleBypasses.R for
getting/setting node, edge and network visual properties via VIEW operations.
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
import os

# Internal module imports
from . import commands
from . import networks
from . import sandbox

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log
from .py4cytoscape_notebook import running_remote
from .py4cytoscape_sandbox import get_abs_sandbox_path

@cy_log
def create_view(layout=True, network=None, base_url=DEFAULT_BASE_URL):
    """Create a network view if one does not already exist

    Args:
        layout (bool): If True, the preferred layout will be applied to the new view; otherwise, no layout will be applied.
        network (str or SUID or None): Name or SUID of the network. Default is the "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        int: SUID of the view for the network

    Raises:
        CyError: if network doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> create_view()
        130223
        >>> create_view(False)
        130223
        >>> create_view(network='galFiltered.sif')
        130223
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    view_suid = get_network_view_suid(net_suid, base_url=base_url)

    if view_suid:
        return view_suid

    res = commands.commands_post(f'view create network="SUID:{net_suid}" layout={layout}', base_url=base_url)
    return res[0]['view']



@cy_log
def get_network_views(network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve list of network view SUIDs.

    Args:
        network (str or SUID or None): Name or SUID of the network. Default is the "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: [list of SUIDs of views] where the list has length 1 or 0 (for no views)

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
    net_suid = networks.get_network_suid(network, base_url=base_url)
    try:
        return commands.cyrest_get(f'networks/{net_suid}/views', base_url=base_url)
    except:
        return []


@cy_log
def get_network_view_suid(network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the SUID of a network view.

    Args:
        network (str or SUID or None): Name or SUID of the network or view. Default is the "current" network active in Cytoscape.
            If a network view SUID is provided, then it is validated and returned.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        int or None: SUID of the view for the network, or None if no view. The first (presummably only) view associated a network is returned.

    Raises:
        CyError: if network or view doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_network_view_suid()
        130223
        >>> get_network_view_suid(51)
        130223
        >>> get_network_view_suid(network='galFiltered.sif')
        130223

    Dev Notes:
        analogous to getNetworkSuid, this function attempts to handle all of the multiple ways we support network view referencing (e.g., title, SUID, 'current', and NULL). These functions are then used by functions that take a "network" argument and requires a view SUID.
"""
    if isinstance(network, str):
        # network name (or "current") was provided, warn if multiple view
        network_views = get_network_views(network, base_url=base_url)
        if len(network_views) > 1:
            narrate('Warning: This network has multiple views. Returning last.')
        return network_views[-1] if len(network_views) >= 1 else None
    elif isinstance(network, int):
        # suid provided, but is it a network or a view?
        net_suids = commands.cyrest_get('networks', base_url=base_url)
        if network in net_suids:  # network SUID, warn if multiple view
            network_views = get_network_views(network, base_url=base_url)
            if len(network_views) > 1:
                narrate('Warning: This network has multiple views. Returning last.')
            return network_views[-1] if len(network_views) >= 1 else None
        else:
            view_suids = [] # Explicitly collect view_suids in case one network doesn't have any views
            for x in net_suids:
                network_view_suids = get_network_views(x, base_url=base_url)
                if len(network_view_suids) > 0:
                    view_suids.append(network_view_suids[0])
            if network in view_suids:  # view SUID, return it
                return network
            else:
                raise CyError(f'Network view does not exist for network "{network}"')
    else:
        # use current network, return first view
        # TODO: R sets this but never uses it ...is this an error?
        network_title = 'current'
        # warn if multiple views
        network_views = get_network_views(network, base_url=base_url)
        if len(network_views) > 1:
            narrate(f'Warning: This network "{network}" has multiple views. Returning last.')
        return network_views[-1] if len(network_views) >= 1 else None


@cy_log
def fit_content(selected_only=False, network=None, base_url=DEFAULT_BASE_URL):
    """Zoom and pan network view to maximize either height or width of current network window.

    Takes first (presumably only) view associated with provided network

    Args:
        selected_only (bool): Whether to fit only current selection. Default is false, i.e., to fit the entire network
        network (str or SUID or None): Name or SUID of the network or view. Default is the "current" network active in Cytoscape.
            If a network view SUID is provided, then it is validated and returned.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {}

    Raises:
        CyError: if network or view doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> fit_content()
        {}
        >>> fit_content(51, selected_only=True)
        {}
        >>> fit_content(network='galFiltered.sif')
        {}
    """
    view_suid = get_network_view_suid(network, base_url=base_url)
    if selected_only:
        res = commands.commands_post(f'view fit selected view="SUID:{view_suid}"', base_url=base_url)
    else:
        res = commands.commands_post(f'view fit content view="SUID:{view_suid}"', base_url=base_url)
    # TODO: Added double quotes for SUID
    return res


@cy_log
def set_current_view(network=None, base_url=DEFAULT_BASE_URL):
    """Set which network view is "current".

    Takes first (presumably only) view associated with provided network

    Args:
        network (str or SUID or None): Name or SUID of the network or view. Default is the "current" network active in Cytoscape.
            If a network view SUID is provided, then it is validated and returned.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {}

    Raises:
        CyError: if network or view doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_current_view()
        {}
        >>> set_current_view(51)
        {}
        >>> set_current_view(network='galFiltered.sif')
        {}
    """
    view_suid = get_network_view_suid(network, base_url=base_url)
    res = commands.commands_post(f'view set current view="SUID:{view_suid}"', base_url=base_url)
    # Added double quotes for SUID
    return res


# TODO: Need parameter to automatically overwrite file if it exists
@cy_log
def export_image(filename=None, type='PNG', resolution=None, units=None, height=None, width=None, zoom=None,
                 network=None, base_url=DEFAULT_BASE_URL, *, overwrite_file=False):
    """ Save the current network view as an image file.

    The image is cropped per the current view in Cytoscape. Consider applying :meth:`fit_content` prior to export.

    Args:
        filename (str): Full path or path relative to current working directory, in addition to the name of the file.
            Extension is automatically added based on the ``type`` argument. If blank, the current network name will be used.
        type (str): Type of image to export, e.g., PNG (default), JPEG, PDF, SVG, PS (PostScript).
        resolution (int): The resolution of the exported image, in DPI. Valid only for bitmap formats, when the selected
            width and height 'units' is inches. The possible values are: 72 (default), 100, 150, 300, 600.
        units (str) The units for the 'width' and 'height' values. Valid only for bitmap formats, such as PNG and JPEG.
            The possible values are: pixels (default), inches.
        height (float): The height of the exported image. Valid only for bitmap formats, such as PNG and JPEG.
        width (float): The width of the exported image. Valid only for bitmap formats, such as PNG and JPEG.
        zoom (float): The zoom value to proportionally scale the image. The default value is 100.0. Valid only for bitmap
            formats, such as PNG and JPEG
        network (str or SUID or None): Name or SUID of the network or view. Default is the "current" network active in Cytoscape.
            If a network view SUID is provided, then it is validated and returned.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.
        overwrite_file (bool): False allows Cytoscape show a message box before overwriting the file if the file already
            exists; True allows Cytoscape to overwrite it without asking

    Returns:
        dict:  {'file': name of file} contains absolute path to file that was written

    Raises:
        CyError: if network or view doesn't exist, or if file exists and user opts to not overwrite it
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> export_image('output/test', type='JPEG', units='pixels', height=1000, width=2000, zoom=200)
        {'file': 'C:\\Users\\CyDeveloper\\tests\\output\\test.jpeg'}
        >>> export_image('output/test', type='PDF', network='My Network')
        {'file': 'C:\\Users\\CyDeveloper\\tests\\output\\test.pdf'}
        >>> export_image('output/test', type='PDF', overwrite_file=True) # overwrite any existing test.pdf
        {'file': 'C:\\Users\\CyDeveloper\\tests\\output\\test.pdf'}
        >>> export_image(type='PNG', resolution=600, units='inches', height=1.7, width=3.5, zoom=500, network=13098)
        {'file': 'C:\\Users\\CyDeveloper\\tests\\output\\test.png'}
    """
    cmd_string = 'view export'  # a good start

    # filename must be supplied
    if not filename: filename = networks.get_network_name(network, base_url=base_url)

    # view must be supplied
    view_SUID = get_network_view_suid(network, base_url=base_url)

    # optional args
    if resolution: cmd_string += ' Resolution="' + str(resolution) + '"'
    if units: cmd_string += ' Units="' + str(units) + '"'
    if height: cmd_string += ' Height="' + str(height) + '"'
    if width: cmd_string += ' Width="' + str(width) + '"'
    if zoom: cmd_string += ' Zoom="' + str(zoom) + '"'

    # TODO: It looks like the '.' should be escaped ... true?
    # TODO: If a lower case comparison is going to be done, shouldn't filename also be lower-case?
    if re.search('.' + type.lower() + '$', filename) is None: filename += '.' + type.lower()

    file_info = sandbox.sandbox_get_file_info(filename, base_url=base_url)
    if len(file_info['modifiedTime']) and file_info['isFile']:
        if overwrite_file:
            sandbox.sandbox_remove_file(filename, base_url=base_url)
        else:
            narrate('This file already exists. A Cytoscape popup will be generated to confirm overwrite.')
    full_filename = file_info['filePath']

    res = commands.commands_post(
        '%s OutputFile="%s" options="%s" view="SUID:%s"' % (cmd_string, full_filename, type.upper(), view_SUID),
        base_url=base_url)
    # TODO: Added double quotes to SUID
    return res


@cy_log
def toggle_graphics_details(base_url=DEFAULT_BASE_URL):
    """Toggle Graphics Details.

    Regardless of the current zoom level and network size, show (or hide) graphics details, e.g., node labels.

    Displaying graphics details on a very large network will affect pan and zoom performance, depending on your available RAM.
    See :meth:`cytoscape_memory_status`.

    Args:
        network (str or SUID or None): Name or SUID of the network or view. Default is the "current" network active in Cytoscape.
            If a network view SUID is provided, then it is validated and returned.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'message': 'Toggled Graphics level of details.'}

    Raises:
        CyError: if network or view doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> toggle_graphics_details()
        {'message': 'Toggled Graphics level of details.'}
    """
    res = commands.cyrest_put('ui/lod', base_url=base_url)
    return res
