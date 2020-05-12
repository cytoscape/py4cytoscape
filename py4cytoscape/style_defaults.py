# -*- coding: utf-8 -*-

"""Functions for getting and setting DEFAULT values for visual properties, organized into sections:

I. General functions for setting node, edge and network defaults
II. Specific functions for setting particular node, edge and network defaults

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
import time
import re

# Internal module imports
from . import commands
from . import styles
from . import style_dependencies
from . import tables

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log
from .py4cytoscape_tuning import MODEL_PROPAGATION_SECS


# ==============================================================================
# I. General Functions
# ------------------------------------------------------------------------------
# TODO: Should we be validating style name with any of these default setters?

# TODO: R version is missing mapping from NODE_BORDER_LINE_TYPE to NODE_BORDER_STROKE??
# TODO: Consider moving property mapping to central function so map_visual_property can take advantage of it
def update_style_defaults(style_name, defaults, base_url=DEFAULT_BASE_URL):
    """Update the default values of visual properties in a style.

    Updates visual property defaults, overriding any prior settings. See ``map_visual_property()`` for the list of visual properties.

    Args:
        style_name (str): name for style
        defaults (dict): a dict of visual property default settings
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> update_style_defaults('galFiltered Style', {'edge width': '50.0', 'EDGE_TARGET_ARROW_SHAPE': 'CIRCLE'})
        ''
        >>> update_style_defaults(defaults={'node shape': 'OCTAGON', 'EDGE_LINE_TYPE': 'ZIGZAG'})
        ''

    See Also:
        :meth:`map_visual_property`
    """
    _PROPERTY_NAMES = {'EDGE_COLOR': 'EDGE_UNSELECTED_PAINT', 'EDGE_THICKNESS': 'EDGE_WIDTH',
                       'NODE_BORDER_COLOR': 'NODE_BORDER_PAINT', 'NODE_BORDER_LINE_TYPE': 'NODE_BORDER_STROKE'}

    def normalize_prop_name(prop_name):
        # Convert white space to '_' and uppercase everything (e.g., 'edge color' -> 'EDGE_COLOR')
        visual_prop_name = re.sub('\\s+', '_', prop_name).upper()
        if visual_prop_name in _PROPERTY_NAMES: visual_prop_name = _PROPERTY_NAMES[visual_prop_name]
        return visual_prop_name

    # process visual property, including common alternatives for vp names :)
    def_list = [{'visualProperty': normalize_prop_name(prop), 'value': val}     for prop, val in defaults.items()]

    res = commands.cyrest_put('styles/' + style_name + '/defaults', body=def_list, base_url=base_url, require_json=False)
    return res


def get_visual_property_default(property, style_name='default', base_url=DEFAULT_BASE_URL):
    """Retrieve the default value for a visual property.

    Args:
        property (str): Name of property, e.g., NODE_FILL_COLOR (see ``get_visual_property_names``)
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name, property or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_visual_property_default('EDGE_UNSELECTED_PAINT')
        ''
        >>> get_visual_property_default('NODE_SHAPE', style_name='galFiltered Style')
        ''
    """
    # TODO: Should the property name be mapped like in update_style_defaults?
    res = commands.cyrest_get('styles/' + style_name + '/defaults/' + property, base_url=base_url)
    return res['value']

def set_visual_property_default(style_string, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default value for a visual property.

    Args:
        style_string (dict): The name and value for the property as {'visualProperty': 'NODE_SIZE', 'value': '35'}
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name, property or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_visual_property_default({'visualProperty': 'EDGE_UNSELECTED_PAINT', 'value': '#CCCCCC'}, style_name='galFiltered Style')
        ''
        >>> set_visual_property_default({'visualProperty': 'EDGE_TARGET_ARROW_SHAPE', 'value': 'CIRCLE'})
        ''
    """
    # TODO: Should the property name be mapped like in update_style_defaults?
    res = commands.cyrest_put('styles/' + style_name + '/defaults', body=[style_string], base_url=base_url,
                              require_json=False)
    time.sleep(
        MODEL_PROPAGATION_SECS)  # wait for attributes to be applied ... it looks like Cytoscape returns before this is complete [BUG]
    return res

# ==============================================================================
# II. Specific Functions
# ==============================================================================
# II.a. Node Properties
# Pattern A: (1) prepare input value as named list, (2) call setVisualPropertyDefault()
# Pattern B: (1) call getVisualPropertyDefault()
# ------------------------------------------------------------------------------

def set_node_border_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default node border color.

    Args:
        new_color (str): color as hex code, e.g., #FD5903
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_border_color_default('#CCCCCC', style_name='galFiltered Style')
        ''
        >>> set_node_border_color_default('#CCCCCC')
        ''
    """
    if is_not_hex_color(new_color):
        return None

    style = {'visualProperty': 'NODE_BORDER_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


def set_node_border_width_default(new_width, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default node border width.

    Args:
        new_width (int): Numeric value for width
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_border_width_default(25, style_name='galFiltered Style')
        ''
        >>> set_node_border_width_default(10)
        ''
    """
    style = {'visualProperty': 'NODE_BORDER_WIDTH', 'value': new_width}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_node_border_opacity_default(new_opacity, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set defaults opacity value for all unmapped node borders.

    Args:
        new_opacity (int): Numeric values between 0 and 255; 0 is invisible.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_border_opacity_default(205, style_name='galFiltered Style')
        ''
        >>> set_node_border_opacity_default(10)
        ''
    """
    if new_opacity < 0 or new_opacity > 255:
        error = 'Error: opacity must be between 0 and 255.'
        sys.stderr.write(error)
        return None  # TODO: Is this what we want to return here?

    style = {'visualProperty': 'NODE_BORDER_TRANSPARENCY', 'value': new_opacity}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_node_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default node color.

    Args:
        new_color (str): color as hex code, e.g., #FD5903
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_color_default('#CCCCCC', style_name='galFiltered Style')
        ''
        >>> set_node_color_default('#CCCCCC')
        ''
    """
    if is_not_hex_color(new_color):
        return None # TODO: Shouldn't this be an exception?

    style = {'visualProperty': 'NODE_FILL_COLOR', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


def set_node_custom_bar_chart(columns, type='GROUPED', colors=None, range=None, orientation='VERTICAL', col_axis=False,
                              range_axis=False, zero_line=False, axis_width=0.25, axis_color='#000000',
                              axis_font_size=1, separation=0.0,
                              slot=1, style_name='default', base_url=DEFAULT_BASE_URL):
    if type not in ['GROUPED', 'STACKED', 'HEAT_STRIPS', 'UP_DOWN']:
        raise CyError('type must be one of the following: GROUPED, STACKED, HEAT_STRIPS, or UP_DOWN')

    if slot not in range(1, 9):
        raise CyError('slot must be an integer between 1 and 9')

    if colors is None:
        if type in ['GROUPED', 'STACKED']: colors = cyPalette('set1') * len(columns)
        elif type == 'HEAT_STRIPS':
            palette = cyPalette('rdbu')
            colors = [palette[index]   for index in [1,5,9]]
        else:
            palette = cyPalette('rdbu')
            colors = [palette[index]   for index in [1,9]]

    if range is None:
        cols = tables.get_table_columns(columns=columns, base_url=base_url)
        min = cols[columns].min().min()  # Make sure this works when column contains NANs
        max = cols[columns].max().max()
        range = [min, max]

    chart = {'cy_colors': str(colors), 'cy_colorScheme': 'Custom', 'cy_dataColumns': columns,
             'cy_orientation': orientation, 'cy_showRangeAxis': range_axis, 'cy_showRangeZeroBaseline': zero_line,
             'cy_axisWidth': axis_width, 'cy_axisColor': axis_color, 'cy_axisLabelFontSize': axis_font_size,
             'cy_range': str(range),
             }

    style_string = {'visualProperty': 'NODE_CUSTOMGRAPHICS_' + str(slot),
                    'value': 'org.cytoscape.BarChart:' + str(chart)}

    res = set_visual_property_default(style_string, style_name, base_url=base_url)
    return res


def set_node_custom_box_chart(columns, colors=None, range=None, orientation='VERTICAL', range_axis=False,
                              zero_line=False, axis_width=0.25, axis_color='#000000', axis_font_size=1,
                              slot=1, style_name='default', base_url=DEFAULT_BASE_URL):
    if slot not in range(1, 9):
        raise CyError('slot must be an integer between 1 and 9')

    if colors is None:
        colors = cyPalette('set1') * len(columns)

    if range is None:
        cols = tables.get_table_columns(columns=columns, base_url=base_url)
        min = cols[columns].min().min()  # Make sure this works when column contains NANs
        max = cols[columns].max().max()
        range = [min, max]

    chart = {'cy_colors': str(colors), 'cy_colorScheme': 'Custom', 'cy_dataColumns': columns,
             'cy_orientation': orientation, 'cy_showRangeAxis': range_axis, 'cy_showRangeZeroBaseline': zero_line,
             'cy_axisWidth': axis_width, 'cy_axisColor': axis_color, 'cy_axisLabelFontSize': axis_font_size,
             'cy_range': str(range),
             }

    style_string = {'visualProperty': 'NODE_CUSTOMGRAPHICS_' + str(slot),
                    'value': 'org.cytoscape.BoxChart:' + str(chart)}

    res = set_visual_property_default(style_string, style_name, base_url=base_url)
    return res


def set_node_custom_heat_map_chart(columns, colors=None, range=None, orientation='HORIZONTAL', range_axis=False,
                                   zero_line=False, axis_width=0.25, axis_color='#000000', axis_font_size=1,
                                   slot=1, style_name='default', base_url=DEFAULT_BASE_URL):
    if slot not in range(1, 9):
        raise CyError('slot must be an integer between 1 and 9')

    if colors is None:
        colors = cyPalette('set1') * len(columns)

    if range is None:
        cols = tables.get_table_columns(columns=columns, base_url=base_url)
        min = cols[columns].min().min()  # Make sure this works when column contains NANs
        max = cols[columns].max().max()
        range = [min, max]

    chart = {'cy_colors': str(colors), 'cy_colorScheme': 'Custom', 'cy_dataColumns': columns[::-1],
             'cy_orientation': orientation, 'cy_showRangeAxis': range_axis, 'cy_showRangeZeroBaseline': zero_line,
             'cy_axisWidth': axis_width, 'cy_axisColor': axis_color, 'cy_axisLabelFontSize': axis_font_size,
             'cy_range': str(range),
             }

    style_string = {'visualProperty': 'NODE_CUSTOMGRAPHICS_' + str(slot),
                    'value': 'org.cytoscape.HeatMapChart:' + str(chart)}

    res = set_visual_property_default(style_string, style_name, base_url=base_url)
    return res


def set_node_custom_line_chart(columns, colors=None, range=None, line_width=1.0, range_axis=False, zero_line=False,
                               axis_width=0.25, axis_color='#000000', axis_font_size=1,
                               slot=1, style_name='default', base_url=DEFAULT_BASE_URL):
    if slot not in range(1, 9):
        raise CyError('slot must be an integer between 1 and 9')

    if colors is None:
        colors = cyPalette('set1') * len(columns)

    if range is None:
        cols = tables.get_table_columns(columns=columns, base_url=base_url)
        min = cols[columns].min().min()  # Make sure this works when column contains NANs
        max = cols[columns].max().max()
        range = [min, max]

    chart = {'cy_colors': str(colors), 'cy_colorScheme': 'Custom', 'cy_dataColumns': columns,
             'cy_lineWidth': line_width, 'cy_showRangeAxis': range_axis, 'cy_showRangeZeroBaseline': zero_line,
             'cy_axisWidth': axis_width, 'cy_axisColor': axis_color, 'cy_axisLabelFontSize': axis_font_size,
             'cy_range': str(range),
             }

    style_string = {'visualProperty': 'NODE_CUSTOMGRAPHICS_' + str(slot),
                    'value': 'org.cytoscape.LineChart:' + str(chart)}

    res = set_visual_property_default(style_string, style_name, base_url=base_url)
    return res


def set_node_custom_pie_chart(columns, colors=None, start_angle=0.0,
                              slot=1, style_name='default', base_url=DEFAULT_BASE_URL):
    if slot not in range(1, 9):
        raise CyError('slot must be an integer between 1 and 9')

    if colors is None:
        colors = cyPalette('set1') * len(columns)
    chart = {'cy_colors': str(colors), 'cy_colorScheme': 'Custom', 'cy_dataColumns': columns,
             'cy_startAngle': start_angle}

    style_string = {'visualProperty': 'NODE_CUSTOMGRAPHICS_' + str(slot),
                    'value': 'org.cytoscape.PieChart:' + str(chart)}

    res = set_visual_property_default(style_string, style_name, base_url=base_url)
    return res


def set_node_custom_ring_chart(columns, colors: None, start_angle=0.0, hole_size=0.5,
                               slot=1, style_name='default', base_url=DEFAULT_BASE_URL):
    if slot not in range(1, 9):
        raise CyError('slot must be an integer between 1 and 9')

    if colors is None:
        colors = cyPalette('set1') * len(columns)
    chart = {'cy_colors': str(colors), 'cy_colorScheme': 'Custom', 'cy_dataColumns': columns,
             'cy_startAngle': start_angle, 'cy_holeSize': hole_size}

    style_string = {'visualProperty': 'NODE_CUSTOMGRAPHICS_' + str(slot),
                    'value': 'org.cytoscape.RingChart:' + str(chart)}

    res = set_visual_property_default(style_string, style_name, base_url=base_url)
    return res


def set_node_custom_linear_gradient(colors=['#DDDDDD', '#888888'], anchors=[0.0, 1.0], angle=0.0,
                                    slot=1, style_name='default', base_url=DEFAULT_BASE_URL):
    if slot not in range(1, 9):
        raise CyError('slot must be an integer between 1 and 9')

    chart = {'cy_angle': angle, 'cy_gradientColors': colors, 'cy_gradientFractions': anchors}
    style_string = {'visualProperty': 'NODE_CUSTOMGRAPHICS_' + str(slot),
                    'value': 'org.cytoscape.LinearGradient:' + str(chart)}

    res = set_visual_property_default(style_string, style_name, base_url=base_url)
    return res


def set_node_custom_radial_gradient(colors=['#DDDDDD', '#888888'], anchors=[0.0, 1.0], x_center=0.5, y_center=0.5,
                                    slot=1,
                                    style_name='default', base_url=DEFAULT_BASE_URL):
    if slot not in range(1, 9):
        raise CyError('slot must be an integer between 1 and 9')

    chart = {'cy_gradientColors': colors, 'cy_gradientFractions': anchors, 'cy_center': {'x': x_center, 'y': y_center}}
    style_string = {'visualProperty': 'NODE_CUSTOMGRAPHICS_' + str(slot),
                    'value': 'org.cytoscape.RadialGradient:' + str(chart)}

    res = set_visual_property_default(style_string, style_name, base_url=base_url)
    return res


def set_node_custom_position(node_anchor='C', graphic_anchor='C', justification='C', x_offset=0.0, y_offset=0.0, slot=1,
                             style_name='default', base_url=DEFAULT_BASE_URL):
    if slot not in range(1, 9):
        raise CyError('slot must be an integer between 1 and 9')
    style_string = {'visualProperty': 'NODE_CUSTOMGRAPHICS_' + str(slot),
                    'value': "'" + node_anchor + ',' + graphic_anchor + ',' + justification + ',' + x_offset + ',' + y_offset + "'"}

    res = set_visual_property_default(style_string, style_name, base_url=base_url)
    return res


def remove_node_custom_graphics(slot=1, style_name='default', base_url=DEFAULT_BASE_URL):
    if slot not in range(1, 9):
        raise CyError('slot must be an integer between 1 and 9')

    res = set_visual_property_default({'visualProperty': 'NODE_CUSTOMGRAPHICS_' + str(slot), 'value': None}, style_name,
                                      base_url=base_url)
    return res


def set_node_fill_opacity_default(new_opacity, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set default opacity value for all unmapped nodes.

    Args:
        new_opacity (int): Numeric values between 0 and 255; 0 is invisible.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_fill_opacity_default(205, style_name='galFiltered Style')
        ''
        >>> set_node_fill_opacity_default(10)
        ''
    """
    if new_opacity < 0 or new_opacity > 255:
        error = 'Error: opacity must be between 0 and 255.'
        sys.stderr.write(error)
        return None  # TODO: Is this what we want to return here?

    style = {'visualProperty': 'NODE_TRANSPARENCY', 'value': new_opacity}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_node_font_face_default(new_font, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default node font.

    Args:
        new_font (str): String specification of font face, style and size, e.g., ' "SansSerif,plain,12" or "Dialog,plain,10"
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_font_face_default('Dialog.italic,plain,12', style_name='galFiltered Style')
        ''
        >>> set_node_font_face_default('Dialog.italic,plain,12')
        ''
    """
    style = {'visualProperty': 'NODE_LABEL_FONT_FACE', 'value': new_font}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_node_font_size_default(new_size, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default node font size.

    Args:
        new_size (int): Numeric value for size
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_font_size_default(20, style_name='galFiltered Style')
        ''
        >>> set_node_font_size_default(20)
        ''
    """
    style = {'visualProperty': 'NODE_LABEL_FONT_SIZE', 'value': new_size}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_node_height_default(new_height, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default node height.

    Args:
        new_height (int): Numeric value for height.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_height_default(20, style_name='galFiltered Style')
        ''
        >>> set_node_height_default(20)
        ''
    """
    # TODO: Shouldn't we be setting this back to its original value? ... and checking return result?
    style_dependencies.lock_node_dimensions(False, style_name=style_name, base_url=base_url)

    style = {'visualProperty': 'NODE_HEIGHT', 'value': new_height}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_node_label_default(new_label, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default node label.

    Args:
        new_label (str): String label for unmapped nodes.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_label_default('test label', style_name='galFiltered Style')
        ''
        >>> set_node_label_default('test label')
        ''
    """
    style = {'visualProperty': 'NODE_LABEL', 'value': new_label}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_node_label_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default node label color.

    Args:
        new_color (str): color as hex code, e.g., #FD5903
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_label_color_default('#CCCCCC', style_name='galFiltered Style')
        ''
        >>> set_node_label_color_default('#CCCCCC')
        ''
    """
    if is_not_hex_color(new_color):
        return None

    style = {'visualProperty': 'NODE_LABEL_COLOR', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_node_label_opacity_default(new_opacity, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set default opacity value for all unmapped node labels.

    Args:
        new_opacity (int): Numeric values between 0 and 255; 0 is invisible.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_label_opacity_default(50, style_name='galFiltered Style')
        ''
        >>> set_node_label_opacity_default(50)
        ''
    """
    if new_opacity < 0 or new_opacity > 255:
        error = 'Error: opacity must be between 0 and 255.'
        sys.stderr.write(error)
        return None  # TODO: Is this what we want to return here?

    style = {'visualProperty': 'NODE_LABEL_TRANSPARENCY', 'value': new_opacity}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def get_node_selection_color_default(style_name='default', base_url=DEFAULT_BASE_URL):
    """Retrieve the default selection node color.

    Args:
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_node_selection_color_default(style_name='galFiltered Style')
        ''
        >>> get_node_selection_color_default()
        ''
    """
    res = get_visual_property_default('NODE_SELECTED_PAINT', style_name=style_name, base_url=base_url)
    return res

def set_node_selection_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default node border color.

    Args:
        new_color (str): color as hex code, e.g., #FD5903
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_selection_color_default('#CCCCCC', style_name='galFiltered Style')
        ''
        >>> set_node_selection_color_default('#CCCCCC')
        ''
    """
    if is_not_hex_color(new_color):
        return None

    style = {'visualProperty': 'NODE_SELECTED_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_node_shape_default(new_shape, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default node shape.

    Args:
        new_shape (str): Name of shape, e.g., ELLIPSE, RECTANGLE, etc (see ``get_node_shapes()``)
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_shape_default('ELLIPSE', style_name='galFiltered Style')
        ''
        >>> set_node_shape_default('ELLIPSE')
        ''
    """
    new_shape = new_shape.upper()
    if new_shape in styles.get_node_shapes(base_url=base_url):
        style = {'visualProperty': 'NODE_SHAPE', 'value': new_shape}
        res = set_visual_property_default(style, style_name, base_url=base_url)
        return res
    else:
        sys.stderr.write(new_shape + ' is not a valid shape. Use get_node_shapes() to find valid values.')
        return None  # TODO: Is this the best thing to return?? ... probably should be an exception

def set_node_size_default(new_size, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default node font size.

    Args:
        new_size (int): Numeric value for size
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_size_default(20, style_name='galFiltered Style')
        ''
        >>> set_node_size_default(20)
        ''
    """
    # TODO: Shouldn't we be setting this back to its original value? ... and checking return result?
    style_dependencies.lock_node_dimensions(True, style_name=style_name, base_url=base_url)

    style = {'visualProperty': 'NODE_SIZE', 'value': new_size}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_node_width_default(new_width, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default node width.

    Args:
        new_width (int): Numeric value for width
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_width_default(20, style_name='galFiltered Style')
        ''
        >>> set_node_width_default(20)
        ''
    """
    # TODO: Shouldn't we be setting this back to its original value? ... and checking return result?
    style_dependencies.lock_node_dimensions(False, style_name=style_name, base_url=base_url)

    style = {'visualProperty': 'NODE_WIDTH', 'value': new_width}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_node_tooltip_default(new_tooltip, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default node tooltip.

    Args:
        new_tooltip (str): String tooltip for unmapped nodes.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_tooltip_default('test tooltip', style_name='galFiltered Style')
        ''
        >>> set_node_tooltip_default('test tooltip')
        ''
    """
    style = {'visualProperty': 'NODE_TOOLTIP', 'value': new_tooltip}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

# ==============================================================================
# II.b. Edge Properties
# Pattern A: (1) prepare input value as named list, (2) call setVisualPropertyDefault()
# Pattern B: (1) call getVisualPropertyDefault()
# ------------------------------------------------------------------------------

def set_edge_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default edge color.

    Args:
        new_color (str): color as hex code, e.g., #FD5903
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_color_default('#CCCCCC', style_name='galFiltered Style')
        ''
        >>> set_edge_color_default('#CCCCCC')
        ''
    """
    if is_not_hex_color(new_color):
        return None # TODO: Shouldn't this be an exception?

    style = {'visualProperty': 'EDGE_UNSELECTED_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    # TODO: Is it OK to lose the res value?

    style = {'visualProperty': 'EDGE_STROKE_UNSELECTED_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_font_face_default(new_font, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default edge font.

    Args:
        new_font (str): String specification of font face, style and size, e.g., ' "SansSerif,plain,12" or "Dialog,plain,10"
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_font_face_default('Dialog.italic,plain,12', style_name='galFiltered Style')
        ''
        >>> set_edge_font_face_default('Dialog.italic,plain,12')
        ''
    """
    style = {'visualProperty': 'EDGE_LABEL_FONT_FACE', 'value': new_font}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_font_size_default(new_size, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default edge font size.

    Args:
        new_size (int): Numeric value for size
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_font_size_default(20, style_name='galFiltered Style')
        ''
        >>> set_edge_font_size_default(20)
        ''
    """
    style = {'visualProperty': 'EDGE_LABEL_FONT_SIZE', 'value': new_size}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_label_default(new_label, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default edge label.

    Args:
        new_label (str): String label for unmapped edges.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_label_default('test label', style_name='galFiltered Style')
        ''
        >>> set_node_label_default('test label')
        ''
    """
    style = {'visualProperty': 'EDGE_LABEL', 'value': new_label}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_label_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default edge label color.

    Args:
        new_color (str): color as hex code, e.g., #FD5903
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_label_color_default('#CCCCCC', style_name='galFiltered Style')
        ''
        >>> set_edge_label_color_default('#CCCCCC')
        ''
    """
    if is_not_hex_color(new_color):
        raise CyError('Color must be in hex code, e.g., #FD5903')

    style = {'visualProperty': 'EDGE_LABEL_COLOR', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_label_opacity_default(new_opacity, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set default opacity value for all unmapped edges.

    Args:
        new_opacity (int): Numeric values between 0 and 255; 0 is invisible.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_label_opacity_default(205, style_name='galFiltered Style')
        ''
        >>> set_edge_label_opacity_default(10)
        ''
    """
    if new_opacity < 0 or new_opacity > 255:
        error = 'Error: opacity must be between 0 and 255.'
        sys.stderr.write(error)
        return None  # TODO: Is this what we want to return here?

    style = {'visualProperty': 'EDGE_LABEL_TRANSPARENCY', 'value': new_opacity}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_line_width_default(new_width, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default edge width.

    Args:
        new_width (int): Numeric value for width.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_line_width_default(20, style_name='galFiltered Style')
        ''
        >>> set_edge_line_width_default(10)
        ''
    """
    style = {'visualProperty': 'EDGE_WIDTH', 'value': new_width}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_line_style_default(new_line_style, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default edge style.

    Args:
        new_line_style (str):  Name of line style, e.g., SOLID, LONG_DASH, etc (see ``get_line_styles()``)
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_line_width_default('SOLID', style_name='galFiltered Style')
        ''
        >>> set_edge_line_width_default('ZIGZAG')
        ''
    """
    style = {'visualProperty': 'EDGE_LINE_TYPE', 'value': new_line_style}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_opacity_default(new_opacity, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set default opacity value for all unmapped edges.

    Args:
        new_opacity (int): Numeric values between 0 and 255; 0 is invisible.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_opacity_default(205, style_name='galFiltered Style')
        ''
        >>> set_edge_opacity_default(10)
        ''
    """
    if new_opacity < 0 or new_opacity > 255:
        error = 'Error: opacity must be between 0 and 255.'
        sys.stderr.write(error)
        return None  # TODO: Is this what we want to return here?

    style = {'visualProperty': 'EDGE_TRANSPARENCY', 'value': new_opacity}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def get_edge_selection_color_default(style_name='default', base_url=DEFAULT_BASE_URL):
    """Retrieve the default selected edge color.

    Args:
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_edge_selection_color_default(style_name='galFiltered Style')
        ''
        >>> get_edge_selection_color_default()
        ''
    """
    if 'arrowColorMatchesEdge' in style_dependencies.get_style_dependencies():
        return get_visual_property_default('EDGE_SELECTED_PAINT', style_name=style_name, base_url=base_url)
    else:
        return get_visual_property_default('EDGE_STROKE_SELECTED_PAINT', style_name=style_name, base_url=base_url)

def set_edge_selection_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default selected edge color.

    Args:
        new_color (str): color as hex code, e.g., #FD5903
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_selection_color_default('#CCCCCC', style_name='galFiltered Style')
        ''
        >>> set_edge_selection_color_default('#CCCCCC')
        ''
    """
    if is_not_hex_color(new_color):
        raise CyError('Color must be in hex code, e.g., #FD5903')

    style = {'visualProperty': 'EDGE_SELECTED_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    # TODO: res is lost after this call

    # TODO: Should the property be SELECTED ?? ... The R code has ELECTED
    style = {'visualProperty': 'EDGE_STROKE_SELECTED_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_source_arrow_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default edge source arrow color.

    Args:
        new_color (str): color as hex code, e.g., #FD5903
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_source_arrow_color_default('#CCCCCC', style_name='galFiltered Style')
        ''
        >>> set_edge_source_arrow_color_default('#CCCCCC')
        ''
    """
    if is_not_hex_color(new_color):
        raise CyError('Color must be in hex code, e.g., #FD5903')

    style = {'visualProperty': 'EDGE_SOURCE_ARROW_UNSELECTED_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_target_arrow_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default edge target arrow color.

    Args:
        new_color (str): color as hex code, e.g., #FD5903
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_target_arrow_color_default('#CCCCCC', style_name='galFiltered Style')
        ''
        >>> set_edge_target_arrow_color_default('#CCCCCC')
        ''
    """
    if is_not_hex_color(new_color):
        raise CyError('Color must be in hex code, e.g., #FD5903')

    style = {'visualProperty': 'EDGE_TARGET_ARROW_UNSELECTED_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_source_arrow_shape_default(new_shape, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default edge source arrow shape.

    Args:
        new_shape (str): Name of shape, e.g., ARROW, T, etc (see ``get_arrow_shapes()``)
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_source_arrow_shape_default('ARROW', style_name='galFiltered Style')
        ''
        >>> set_edge_source_arrow_shape_default('ARROW')
        ''
    """
    style = {'visualProperty': 'EDGE_SOURCE_ARROW_SHAPE', 'value': new_shape}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_target_arrow_shape_default(new_shape, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default edge target arrow shape.

    Args:
        new_shape (str): Name of shape, e.g., ARROW, T, etc (see ``get_arrow_shapes()``)
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_target_arrow_shape_default('ARROW', style_name='galFiltered Style')
        ''
        >>> set_edge_target_arrow_shape_default('ARROW')
        ''
    """
    style = {'visualProperty': 'EDGE_TARGET_ARROW_SHAPE', 'value': new_shape}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_tooltip_default(new_tooltip, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default edge tooltip.

    Args:
        new_tooltip (str): String tooltip for unmapped edges.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_tooltip_default('test tooltip', style_name='galFiltered Style')
        ''
        >>> set_edge_tooltip_default('test tooltip')
        ''
    """
    style = {'visualProperty': 'EDGE_TOOLTIP', 'value': new_tooltip}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

# ==============================================================================
# II.c. Network Properties
# Pattern A: (1) prepare input value as named list, (2) call setVisualPropertyDefault()
# Pattern B: (1) call getVisualPropertyDefault()
# ------------------------------------------------------------------------------

def get_background_color_default(style_name='default', base_url=DEFAULT_BASE_URL):
    """Retrieve the default background color.

    Args:
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_background_color_default(style_name='galFiltered Style')
        ''
        >>> get_background_color_default()
        ''
    """
    res = get_visual_property_default('NETWORK_BACKGROUND_PAINT', style_name=style_name, base_url=base_url)
    return res

def set_background_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set the default background color.

    Args:
        new_color (str): color as hex code, e.g., #FD5903
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if network name or style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_background_color_default('#CCCCCC', style_name='galFiltered Style')
        ''
        >>> set_background_color_default('#CCCCCC')
        ''
    """
    if is_not_hex_color(new_color):
        return None # TODO: Shouldn't this return an exception?

    style = {'visualProperty': 'NETWORK_BACKGROUND_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res