# -*- coding: utf-8 -*-

"""Functions for managing STYLES and retrieving general lists of properties relevant to multiple style modes.
Functions specific to Default, Mapping, Bypass, Dependencies and Values are in separate files.

I. Style management functions
II. General property functions

License:
    Copyright 2020 The Cytoscape Consortium

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
    documentation files (the "Software"), to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
    and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions
    of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
    WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
    OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
    OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

# External library imports
import sys

# Internal module imports
from . import commands

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log


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
            port or version to connect to the CyREST API. Default is http://localhost:1234
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
        raise CyError('Cannot copy from a non-existent visual style ( + ' + from_style + ')')

    # get the current style from Cytoscape
    res = commands.cyrest_get('styles/' + from_style, base_url=base_url)
    style_from_to = res
    style_from_to['title'] = to_style

    # and send it to Cytoscape as a new style with a new name
    res = commands.cyrest_post('styles', body=style_from_to, base_url=base_url)

    # get and update dependencies as well
    res = commands.cyrest_get('styles/' + from_style + '/dependencies', base_url=base_url)
    # TODO: Shouldn't we be throwing exceptions if these return results are bad?
    res = commands.cyrest_put('styles/' + to_style + '/dependencies', body=res, base_url=base_url, require_json=False)
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
            port or version to connect to the CyREST API. Default is http://localhost:1234
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
def get_visual_style_names(base_url=DEFAULT_BASE_URL):
    res = commands.cyrest_get('apply/styles', base_url=base_url)
    return res

@cy_log
def get_visual_property_names(base_url=DEFAULT_BASE_URL):
    res = commands.cyrest_get('styles/default/defaults', base_url=base_url)
    visual_properties = [prop['visualProperty']     for prop in res['defaults']]
    return visual_properties
