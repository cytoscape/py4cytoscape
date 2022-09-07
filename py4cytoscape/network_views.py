# -*- coding: utf-8 -*-

"""Functions for performing VIEW operations in addition to getting and setting view properties.
"""

"""Dev Notes: refer to StyleValues.R, StyleDefaults.R and StyleBypasses.R for
getting/setting node, edge and network visual properties via VIEW operations.
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
import os

# Internal module imports
from . import commands
from . import networks
from . import sandbox

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log
from .py4cytoscape_utils import verify_supported_versions
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

# Note: All types must be lower case for followon code to work properly
_JPG_TYPE = 'jpg'
_PDF_TYPE = 'pdf'
_PNG_TYPE = 'png'
_PS_TYPE = 'ps'
_SVG_TYPE = 'svg'
_SUPPLIED_TYPE ='*'
_TYPE_MAP = {'jpg': (_SUPPLIED_TYPE, _JPG_TYPE),
             'jpeg': (_SUPPLIED_TYPE, _JPG_TYPE),
             'jpeg (*.jpeg, *.jpg)': (_JPG_TYPE, _JPG_TYPE),
             'pdf': (_SUPPLIED_TYPE, _PDF_TYPE),
             'pdf (*.pdf)': (_PDF_TYPE, _PDF_TYPE),
             'png': (_SUPPLIED_TYPE, _PNG_TYPE),
             'png (*.png)': (_PNG_TYPE, _PNG_TYPE),
             'ps': (_SUPPLIED_TYPE, _PS_TYPE),
             'postscript (*.ps)': (_PS_TYPE, _PS_TYPE),
             'svg': (_SUPPLIED_TYPE, _SVG_TYPE),
             'svg (*.svg)': (_SVG_TYPE, _SVG_TYPE)}


@cy_log
def export_image(filename=None, type='PNG', resolution=None, units=None, height=None, width=None, zoom=None,
                 network=None, base_url=DEFAULT_BASE_URL, *, overwrite_file=False, force_pre_3_10=False,
                 all_graphics_details=None, hide_labels=None, transparent_background=None,
                 export_text_as_font=None, orientation=None, page_size=None):
    """ Save the current network view as an image file.

    The image is cropped per the current view in Cytoscape. Consider applying :meth:`fit_content` prior to export.

    Args:
        filename (str): Full path or path relative to current working directory, in addition to the name of the file.
            Extension is automatically added based on the ``type`` argument. If blank, the current network name will be used.
        type (str): Type of image to export, e.g., PNG (default), JPEG, PDF, SVG, PS (PostScript).
        resolution (int): The resolution of the exported image, in DPI. Valid only for bitmap formats, when the selected
            width and height 'units' is inches. The possible values are: 72 (default), 100, 150, 300, 600. [DEPRECATED as of Cytoscape v3.10]
        units (str) The units for the 'width' and 'height' values. Valid only for bitmap formats, such as PNG and JPEG.
            The possible values are: pixels (default), inches. [DEPRECATED as of Cytoscape v3.10]
        height (float): The height of the exported image. Valid only for bitmap formats, such as PNG and JPEG. [DEPRECATED as of Cytoscape v3.10]
        width (float): The width of the exported image. Valid only for bitmap formats, such as PNG and JPEG. [DEPRECATED as of Cytoscape v3.10]
        zoom (float): The zoom value to proportionally scale the image. The default value is 100.0. Valid only for bitmap
            formats, such as PNG and JPEG.
        network (str or SUID or None): Name or SUID of the network or view. Default is the "current" network active in Cytoscape.
            If a network view SUID is provided, then it is validated and returned.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.
        overwrite_file (bool): False allows Cytoscape show a message box before overwriting the file if the file already
            exists; True allows Cytoscape to overwrite it without asking. In Cytoscape v3.10 and later, False
            causes failure if file already exists.
        force_pre_3_10 (bool): True results in pre-Cytoscape 3.10 image export being called, even if Cytoscape
            can perform the export using more advanced functionality -- provided for backward compatibility. The default is False. Available for Cytoscape v3.10 or later.
        all_graphics_details (bool): True results in image with highest detail; False allows faster image
            generation. The default is True. Valid for bitmap formats such as PNG and JPEG. Available for Cytoscape v3.10 or later.
        hide_labels (bool): True makes node and edge labels invisible in image. False allows them to be
            drawn. The default is False. Valid for all image formats. Available for Cytoscape v3.10 or later.
        transparent_background (bool): True causes background to be transparent. The default is False. Valid only for PNG format. Available for Cytoscape v3.10 or later.
        export_text_as_font (bool): True causes text to be exported as fonts. The default is True. Valid for PDF, PS and SVG formats. Available for Cytoscape v3.10 or later.
        orientation (str): 'Portrait' allows more height for drawing space, and 'Landscape' allows more width.
            The default is 'Portrait'. Valid for PDF format. Available for Cytoscape v3.10 or later.
        page_size (str): Chooses standard page size (i.e., 'Letter', 'Auto', 'Legal', 'Tabloid', 'A0',
            'A1', 'A2', 'A3', 'A4', or 'A5'). The default is 'Letter'. Valid for PDF format. Available for Cytoscape v3.10 or later.

    Note:
        This function starts with the assumption of using export functions available in Cytoscape v3.10
        or later, and accepts parameters pertinent to those functions (i.e., `all_graphics_details`,
        `hide_labels`, `transparent_background`, `export_text_as_font`, `orientation`, `page_size` and  `zoom`).
        If the caller supplies parameters appropriate for pre-3.10 Cytoscape (i.e., `resolution`, `units`,
        `height`, `width` and `zoom`) the pre-v3.10 functions will be used instead. If your Cytoscape
        is pre-v3.10, the pre-v3.10 functions will be called, and using v3.10 parameters will cause an
        exception. If your Cytoscape is v3.10 or later, passing no parameters or just the `zoom` parameter will result in
        the v3.10 functions will be called, but you can force the pre-v3.10 functions to be used by specifying
        `force_pre_3_10` as `True`. Mixing pre-v3.10 and v3.10 parameters will cause an exception.

    Returns:
        dict:  {'file': name of file} contains absolute path to file that was written

    Raises:
        CyError: if network or view doesn't exist, or if file exists and user opts to not overwrite it, or attempting to use v3.10 parameters with a pre-v3.10 Cytoscape, or mixing v3.10 and pre-v3.10 parameters
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> export_image('output/test', type='PDF', orientation='Landscape', hide_labels=True)
        {'file': 'C:\\Users\\CyDeveloper\\tests\\output\\test.pdf'}
        >>> export_image('output/test', type='JPEG', all_graphics_details=False, zoom=200)
        {'file': 'C:\\Users\\CyDeveloper\\tests\\output\\test.jpeg'}
        >>> export_image('output/test', type='JPG', hide_labels=True, zoom=200)
        {'file': 'C:\\Users\\CyDeveloper\\tests\\output\\test.jpg'}
        >>> export_image('output/test', zoom=200, transparent_background=True)
        {'file': 'C:\\Users\\CyDeveloper\\tests\\output\\test.png'}
        >>> export_image('output/test', force_pre_3_10=True) # use pre-v3.10 PNG renderer
        {'file': 'C:\\Users\\CyDeveloper\\tests\\output\\test.png'}
        >>> export_image('output/test', type='PDF', overwrite_file=True) # overwrite any existing test.pdf
        {'file': 'C:\\Users\\CyDeveloper\\tests\\output\\test.pdf'}
        >>> export_image('output/test', type='SVG', network='My Network')
        {'file': 'C:\\Users\\CyDeveloper\\tests\\output\\test.svg'}
        >>> export_image('output/test', type='jpeg (*.jpeg, *.jpg)', network=13098)
        {'file': 'C:\\Users\\CyDeveloper\\tests\\output\\test.jpg'}
    """
    # View must be supplied
    view_SUID = get_network_view_suid(network, base_url=base_url)

    # Determine which set of parameters are valid or invalid or deprecated based on Cytoscape version,
    # and then verify that the caller's parameters fit with the Cytoscape version
    has_v10_params = all_graphics_details is not None \
                     or hide_labels is not None \
                     or transparent_background is not None \
                     or export_text_as_font is not None \
                     or orientation is not None \
                     or page_size is not None
    has_pre_v10_params = resolution is not None \
                         or units is not None \
                         or height is not None \
                         or width is not None

    if check_supported_versions(1, "3.10", base_url=base_url):
        # Cytoscape appears to be pre-3.10
        if has_v10_params:
            raise CyError('Cannot use Cytoscape v3.10 parameters with pre-v3.10 Cytoscape')
        use_v10_calls = False
    else:
        # Cytoscape is 3.10 or later
        if has_v10_params:
            # Caller specified one or more 3.10 parameters
            if has_pre_v10_params:
                raise CyError('Cannot use both Cytoscape v3.10 parameters and pre-v3.10 parameters')
            if force_pre_3_10:
                raise CyError('Cannot force call to Cytoscape pre-3.10 if v3.10 parameters are used')
            use_v10_calls = True
        else:
            # Caller didn't specify any 3.10 parameters, but may have specified some pre-3.10 parameters
            if force_pre_3_10:
                use_v10_calls = False
            else:
                use_v10_calls = not has_pre_v10_params
                if not use_v10_calls:
                    narrate('Warning: use of resolution=, units=, height= and width= parameters for export_image() is deprecated')
        # if use_v10_calls: # For debugging
        #     narrate('Until 3.10 works properly, we will pretend we are using 3.9')
        #     use_v10_calls = False

    if zoom is None:
        zoom = 100

    # Determine which type of file image will be generated
    type = type.lower()
    if type in _TYPE_MAP:
        type_suffix, cy_type = _TYPE_MAP[type]
        if type_suffix == _SUPPLIED_TYPE:
            type_suffix = type
    else:
        raise CyError(f'Type {type} is unknown; options include {_TYPE_MAP.keys()}')

    # If the caller didn't supply a file name, deduce it from the network title, and
    # if the file name doesn't have a file suffix appropriate for the image file, add the right suffix
    if not filename: filename = networks.get_network_name(network, base_url=base_url)
    if re.search('\.' + type_suffix + '$', filename.lower()) is None: filename += '.' + type_suffix

    # Figure out whether the file already exists, and delete it if the caller asked for an overwrite
    # Either way, end up with a file name appropriate for Cytoscape's file system
    file_info = sandbox.sandbox_get_file_info(filename, base_url=base_url)
    if len(file_info['modifiedTime']) and file_info['isFile']:
        if overwrite_file:
            sandbox.sandbox_remove_file(filename, base_url=base_url)
        else:
            if use_v10_calls:
                raise CyError(f'This file already exists and will not be overwritten: {filename}')
            else:
                narrate('This file already exists. A Cytoscape popup will be generated to confirm overwrite.')
    full_filename = file_info['filePath']

    # Generate the parameters appropriate for the Cytoscape function being used
    if use_v10_calls:
        cmd_string = 'view export ' + cy_type

        # optional args
        if all_graphics_details is not None: cmd_string += f' allGraphicsDetails="{all_graphics_details}"'
        if hide_labels is not None: cmd_string += f' hideLabels="{hide_labels}"'
        if transparent_background is not None: cmd_string += f' transparentBackground="{transparent_background}"'
        if export_text_as_font is not None: cmd_string += f' exportTextAsFont="{export_text_as_font}"'
        if orientation is not None: cmd_string += f' orientation="{orientation}"'
        if page_size is not None: cmd_string += f' pageSize="{page_size}"'
    else:
        cmd_string = f'view export options="{cy_type.upper()}"'  # a good start

        # optional args
        if resolution is not None: cmd_string += ' Resolution="' + str(resolution) + '"'
        if units is not None: cmd_string += ' Units="' + str(units) + '"'
        if height is not None: cmd_string += ' Height="' + str(height) + '"'
        if width is not None: cmd_string += ' Width="' + str(width) + '"'

    # Call the actual Cytoscape export image function
    res = commands.commands_post(f'{cmd_string} Zoom="{zoom}" outputFile="{full_filename}" view="SUID:{view_SUID}"',
                                 base_url=base_url)
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
