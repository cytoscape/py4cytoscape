# -*- coding: utf-8 -*-

"""Functions for managing STYLES and retrieving general lists of properties relevant to multiple style modes.
Functions specific to Default, Mapping, Bypass, Dependencies and Values are in separate files.

I. Style management functions
II. General property functions
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
import warnings

# Internal module imports
from . import commands
from . import networks
from . import sandbox
from . import network_views

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log
from .py4cytoscape_notebook import running_remote
from .py4cytoscape_sandbox import get_abs_sandbox_path

# ==============================================================================
# I. Style management functions
# ------------------------------------------------------------------------------

@cy_log
def copy_visual_style(from_style, to_style, base_url=DEFAULT_BASE_URL):
    """Create a new visual style by copying a specified style.

    Args:
        from_style (str): Name of visual style to copy
        to_style (str): Name of new visual style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> copy_visual_style('Solid', 'SolidCopy')
        ''
    """
    current_names = get_visual_style_names(base_url=base_url)
    if from_style not in current_names:
        raise CyError(f'Cannot copy from a non-existent visual style "{from_style}"')

    # get the current style from Cytoscape
    res = commands.cyrest_get(f'styles/{from_style}', base_url=base_url)
    style_from_to = res
    style_from_to['title'] = to_style

    # and send it to Cytoscape as a new style with a new name
    res = commands.cyrest_post('styles', body=style_from_to, base_url=base_url)

    # get and update dependencies as well
    res = commands.cyrest_get(f'styles/{from_style}/dependencies', base_url=base_url)
    # TODO: Shouldn't we be throwing exceptions if these return results are bad?
    res = commands.cyrest_put(f'styles/{to_style}/dependencies', body=res, base_url=base_url, require_json=False)
    return res

@cy_log
def create_visual_style(style_name, defaults=None, mappings=None, base_url=DEFAULT_BASE_URL):
    """Create a style from defaults and predefined mappings.

    Requires visual property mappings to be previously created, see ``map_visual_property``.

    Args:
        style_name (str): name for style
        defaults (list): key-value pairs for default mappings.
        mappings (list): visual property mappings, see ``map_visual_property``
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'title': new style name}

    Raises:
        CyError: if mappings or defaults contain invalid values
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> defaults = {'NODE_SHAPE': 'diamond', 'NODE_SIZE': 30, 'EDGE_TRANSPARENCY': 120, 'NODE_LABEL_POSITION': 'W,E,c,0.00,0.00'}
        >>> node_labels = map_visual_property('node label', 'COMMON', 'p')
        >>> node_fills = map_visual_property('node fill color', 'Degree', 'd', ['1', '2'], ['#FF9900', '#66AAAA'])
        >>> arrow_shapes = map_visual_property('Edge Target Arrow Shape', 'interaction', 'd', ['pp', 'pd'], ['Arrow', 'T'])
        >>> edge_width = map_visual_property('edge width', 'EdgeBetweenness', 'p')
        >>> create_visual_style('NewStyle', defaults=defaults, mappings=[node_labels, node_fills, arrow_shapes, edge_width])
        {'title': 'NewStyle'}

    Note:
        To apply the style to a network, first create the network and then call ``set_visual_style``

    See Also:
        :meth:`map_visual_property`, :meth:`set_visual_style`
    """
    if mappings is None: mappings = []
    style_def = []
    if defaults is not None:
        style_def = [{'visualProperty': key, 'value': val}  for key, val in defaults.items()]
    style = {'title': style_name, 'defaults': style_def, 'mappings': mappings}
    res = commands.cyrest_post('styles', body=style, base_url=base_url)
    return res

@cy_log
def delete_visual_style(style_name, base_url=DEFAULT_BASE_URL):
    """Delete the specified visual style from current session.

    Args:
        style_name (str): name of style to delete
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if the style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> delete_visual_style('NewStyle')
        ''
    """
    res = commands.cyrest_delete(f'styles/{style_name}', base_url=base_url, require_json=False)
    return res

@cy_log
def export_visual_styles(filename=None, type='XML', styles=None, base_url=DEFAULT_BASE_URL, *, overwrite_file=False):
    """Save one or more visual styles to file.

    Args:
        filename (str): Full path or path relavtive to current working directory, in addition to
            the name of the file. Extension is automatically added based on the ``type`` argument.
            Default is "styles.xml"
        type (str): Type of data file to export, e.g., XML, JSON (case sensitive).
            Default is XML. Note: Only XML can be read by ``import_visual_styles()``.
        styles (str) The styles to be exported, listed as a comma-separated string. If no styles are
            specified, only the current one is exported.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.
        overwrite_file (bool): False allows Cytoscape show a message box before overwriting the file if the file already
            exists; True allows Cytoscape to overwrite it without asking
    Returns:
        dict: {'file': name of file written}

    Raises:
        CyError: if the output file can't be created, or if file exists and user opts to not overwrite it
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> export_visual_styles() # export the current style to styles.xml in the current directory
        {'file': 'C:\\Users\\CyDeveloper\\styles.xml'}
        >>> export_visual_styles('curstyle') # export the current style to curstyle.xml in the current directory
        {'file': 'C:\\Users\\CyDeveloper\\curstyle.xml'}
        >>> export_visual_styles('curstyle', overwrite_file=True) # overwrite any existing curstyle.xml file
        {'file': 'C:\\Users\\CyDeveloper\\curstyle.xml'}
        >>> export_visual_styles('curstyle', type='json') # export the current style in cytoscape.js format
        {'file': 'C:\\Users\\CyDeveloper\\curstyle.json'}

    See Also:
        :meth:`import_visual_styles`
    """
    cmd_string = 'vizmap export'  # minmum command
    if styles is not None: cmd_string += ' styles="' + styles + '"'
    cmd_string += ' options="' + type + '"'

    if filename is None: filename = 'styles'
    ext = '.' + type.lower() + '$'
    if re.search(ext, filename.lower()) is None: filename += '.' + type.lower()

    file_info = sandbox.sandbox_get_file_info(filename, base_url=base_url)
    if len(file_info['modifiedTime']) and file_info['isFile']:
        if overwrite_file:
            sandbox.sandbox_remove_file(filename, base_url=base_url)
        else:
            narrate('This file already exists. A Cytoscape popup will be generated to confirm overwrite.')
    full_filename = file_info['filePath']

    cmd_string += f' OutputFile="{full_filename}"'

    res = commands.commands_post(cmd_string, base_url=base_url)
    return res

@cy_log
def import_visual_styles(filename="styles.xml", base_url=DEFAULT_BASE_URL):
    """Load styles from an XML file and returns the names of the loaded styles.

    Note:
        To load a style file from cloud storage, use the file's URL and the ``sandbox_url_to`` function to download
        the file to a sandbox, and then use ``import_visual_styles`` to load it from there.

    Args:
        filename (str): Name of the style file to load. Only reads XML files. Default is "styles.xml".
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: [names of styles loaded]

    Raises:
        CyError: if the input file can't be read
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> import_visual_styles() # export styles.xml in the current directory
        ['galFiltered Style']
        >>> import_visual_styles('curstyle.xml') # export curstyle.xml in the current directory
        ['galFiltered Style']

    See Also:
        :meth:`export_visual_styles`
    """
    res = commands.commands_post(f'vizmap load file file="{get_abs_sandbox_path(filename)}"', base_url=base_url)
    return res

@cy_log
def get_visual_style_names(base_url=DEFAULT_BASE_URL):
    """Retrieve a list of all visual style names.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: [names of styles in session]

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> visual_style_names()
        ['Universe', 'Marquee', 'Big Labels', 'BioPAX_SIF', 'Ripple', 'Metallic', 'default black', ...]
    """
    res = commands.cyrest_get('apply/styles', base_url=base_url)
    return res


@cy_log
def set_visual_style(style_name, network=None, base_url=DEFAULT_BASE_URL):
    """Apply a visual style to a network.

    Args:
        style_name (str): Name of a visual style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'message': 'Visual Style applied.'}

    Raises:
        CyError: if style doesn't exist or network doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_visual_style('default')
        {'message': 'Visual Style applied.'}
        >>> set_visual_style('galFiltered Style', network=51)
        {'message': 'Visual Style applied.'}
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    current_names = get_visual_style_names(base_url=base_url)

    # inform user if they want to set style that does not exist
    if style_name not in current_names:
        raise CyError(f'Cannot use non-existent visual style "{style_name}"')

    res = commands.cyrest_get(f'apply/styles/{style_name}/{net_suid}', base_url=base_url)
    return res


@cy_log
def get_arrow_shapes(base_url=DEFAULT_BASE_URL):
    """Get Arrow Shapes.

    Retrieve the names of the currently supported 'arrows' -- the decorations can (optionally) appear at
    the ends of edges, adjacent to the nodes they connect, and conveying information about the nature of
    the nodes' relationship.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: [arrow shape names]

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_arrow_shapes()
        ['OPEN_CIRCLE', 'SQUARE', 'CIRCLE', 'DELTA_SHORT_2', 'DELTA', 'DIAMOND_SHORT_2', ...]
    """
    res = commands.cyrest_get('styles/visualproperties/EDGE_TARGET_ARROW_SHAPE/values', base_url=base_url)
    return res['values']


@cy_log
def get_line_styles(base_url=DEFAULT_BASE_URL):
    """Get Line Styles.

    Retrieve the names of the currently supported line types -- values which can be used to render edges, and thus
    can be used in calls to ``set_edge_line_style_rule()``.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: [line style names]

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_line_styles()
        ['MARQUEE_DASH_DOT', 'SOLID', 'BACKWARD_SLASH', 'EQUAL_DASH', 'CONTIGUOUS_ARROW', ...]
    """
    res = commands.cyrest_get('styles/visualproperties/EDGE_LINE_TYPE/values', base_url=base_url)
    return res['values']

@cy_log
def get_node_shapes(base_url=DEFAULT_BASE_URL):
    """Get Node Shapes.

    Retrieve the names of the currently supported node shapes, which can then be used in calls to
    ``set_node_shape_rule()`` and ``set_default_viz_map_value()``.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: [node shape names]

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_node_shapes()
        ['ROUND_RECTANGLE', 'VEE', 'TRIANGLE', 'HEXAGON', 'PARALLELOGRAM', 'ELLIPSE', 'OCTAGON', ...]
    """
    res = commands.cyrest_get('styles/visualproperties/NODE_SHAPE/values', base_url=base_url)
    return res['values']


@cy_log
def get_visual_property_names(base_url=DEFAULT_BASE_URL):
    """Retrieve the names of all possible visual properties.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: [visual property names]

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_visual_property_names()
        ['COMPOUND_NODE_PADDING', 'COMPOUND_NODE_SHAPE', 'DING_RENDERING_ENGINE_ROOT', 'EDGE', ...]
    """
    res = commands.cyrest_get('styles/default/defaults', base_url=base_url)
    visual_properties = [prop['visualProperty']     for prop in res['defaults']]
    return visual_properties


@cy_log
def get_current_style(network=None, base_url=DEFAULT_BASE_URL):
    """Get the current visual style applied to a network.

    Args:
        network (str or SUID or None): Name or SUID of the network or view. Default is the "current" network active in Cytoscape.
                If a network view SUID is provided, then it is validated and returned.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: Name of style

    Raises:
        CyError: if style doesn't exist or network doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_current_style()
        "default"
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    view_suid = network_views.get_network_view_suid(net_suid, base_url=base_url)
    res = commands.cyrest_get(f'networks/{net_suid}/views/{view_suid}/currentStyle', base_url=base_url)
    return res['title']
