# -*- coding: utf-8 -*-

"""Functions for getting and setting DEFAULT values for visual properties, organized into sections:

I. General functions for setting node, edge and network defaults
II. Specific functions for setting particular node, edge and network defaults
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
import time
import re
import json

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
@cy_log
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
        CyError: if style name doesn't exist
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

    if style_name is None:
        style_name = 'default'
        narrate(f'style_name not specified, so updating "default" style.')

    # process visual property, including common alternatives for vp names :)
    def_list = [{'visualProperty': normalize_prop_name(prop), 'value': val} for prop, val in defaults.items()]

    res = commands.cyrest_put(f'styles/{style_name}/defaults', body=def_list, base_url=base_url,
                              require_json=False)
    return res


@cy_log
def get_visual_property_default(property, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_visual_property_default('EDGE_UNSELECTED_PAINT')
        ''
        >>> get_visual_property_default('NODE_SHAPE', style_name='galFiltered Style')
        ''
    """
    if style_name is None:
        style_name = 'default'
        narrate(f'style_name not specified, so accessing "default" style.')

    # TODO: Should the property name be mapped like in update_style_defaults?
    res = commands.cyrest_get(f'styles/{style_name}/defaults/{property}', base_url=base_url)
    return res['value']


@cy_log
def set_visual_property_default(style_string, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if property or style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_visual_property_default({'visualProperty': 'EDGE_UNSELECTED_PAINT', 'value': '#CCCCCC'}, style_name='galFiltered Style')
        ''
        >>> set_visual_property_default({'visualProperty': 'EDGE_TARGET_ARROW_SHAPE', 'value': 'CIRCLE'})
        ''
    """
    if style_name is None:
        style_name = 'default'
        narrate(f'style_name not specified, so updating "default" style.')

    # TODO: Should the property name be mapped like in update_style_defaults?
    res = commands.cyrest_put(f'styles/{style_name}/defaults', body=[style_string], base_url=base_url,
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

@cy_log
def set_node_border_color_default(new_color, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_border_color_default('#CCCCCC', style_name='galFiltered Style')
        ''
        >>> set_node_border_color_default('#CCCCCC')
        ''
    """
    verify_hex_colors(new_color)

    style = {'visualProperty': 'NODE_BORDER_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def set_node_border_width_default(new_width, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist, or if width is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_border_width_default(25, style_name='galFiltered Style')
        ''
        >>> set_node_border_width_default(10)
        ''
    """
    verify_dimensions('width', new_width)

    style = {'visualProperty': 'NODE_BORDER_WIDTH', 'value': new_width}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def set_node_border_opacity_default(new_opacity, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist, or if opacity is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_border_opacity_default(205, style_name='galFiltered Style')
        ''
        >>> set_node_border_opacity_default(10)
        ''
    """
    verify_opacities(new_opacity)

    style = {'visualProperty': 'NODE_BORDER_TRANSPARENCY', 'value': new_opacity}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def set_node_color_default(new_color, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if invalid color, or if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_color_default('#CCCCCC', style_name='galFiltered Style')
        ''
        >>> set_node_color_default('#CCCCCC')
        ''
    """
    verify_hex_colors(new_color)

    style = {'visualProperty': 'NODE_FILL_COLOR', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def set_node_custom_bar_chart(columns, type='GROUPED', colors=None, range=None, orientation='VERTICAL', col_axis=False,
                              range_axis=False, zero_line=False, axis_width=0.25, axis_color='#000000',
                              axis_font_size=1, separation=0.0,
                              slot=1, style_name=None, base_url=DEFAULT_BASE_URL):
    """Set Node Custom Bar Chart.

    Makes a bar chart per node using specified node table columns by setting a default custom graphic style.

    Args:
        columns (list): List of node column names to be displayed, in order.
        type (str): Type of bar chart: GROUPED (default), STACKED, HEAT_STRIPS, or UP_DOWN
        colors (list): List of colors to be matched with columns or with range, depending on type. Default is a
            set of colors from an appropriate Brewer cy_palette.
        range (list): Min and max values of chart. Default is to use min and max from specified data columns.
        orientation (str): HORIZONTAL or VERTICAL (default).
        col_axis (bool): Show axis with column labels. Default is False.
        range_axis (bool): Show axis with range of values. Default is False.
        zero_line (book): Show a line at zero. Default is False.
        axis_width (float): Width of axis lines, if shown. Default is 0.25.
        axis_color (str): Color of axis lines, if shown. Default is black ('#000000').
        axis_font_size(int): Font size of axis labels, if shown. Default is 1.
        separation (float): Distance between bars. Default is 0.0.
        slot (int): Which custom graphics slot to modify. Slots 1-9 are available for independent charts, gradients
            and images. Default is 1.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if style name, chart type or slot doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_custom_bar_chart(['AverageShortestPath', 'BetweennessCentrality'], style_name='galFiltered Style')
        ''
        >>> set_node_custom_bar_chart(['AverageShortestPath', 'BetweennessCentrality'], colors=['#FF00FF', '#00FF00'], slot=2, style_name='galFiltered Style')
        ''

    See Also:
        :meth:`set_node_custom_position`, :meth:`remove_node_custom_graphics`
    """
    if type not in ['GROUPED', 'STACKED', 'HEAT_STRIPS', 'UP_DOWN']:
        raise CyError(f'Type "{type}" must be one of the following: GROUPED, STACKED, HEAT_STRIPS, or UP_DOWN')

    verify_slot(slot)

    if colors is None:
        if type in ['GROUPED', 'STACKED']:
            colors = cyPalette('set1') * len(columns)
        elif type == 'HEAT_STRIPS':
            palette = cyPalette('rdbu')
            colors = [palette[index] for index in [1, 5, 9]]
        else:
            palette = cyPalette('rdbu')
            colors = [palette[index] for index in [1, 9]]

    if range is None:
        cols = tables.get_table_columns(columns=columns, base_url=base_url)
        min = cols[columns].min().min()  # Make sure this works when column contains NANs
        max = cols[columns].max().max()
        range = [min, max]

    chart = {'cy_colors': colors, 'cy_colorScheme': 'Custom', 'cy_dataColumns': columns, 'cy_type': type,
             'cy_orientation': orientation, 'cy_showDomainAxis': col_axis, 'cy_showRangeAxis': range_axis,
             'cy_showRangeZeroBaseline': zero_line, 'cy_axisWidth': axis_width, 'cy_axisColor': axis_color,
             'cy_axisLabelFontSize': axis_font_size, 'cy_separation': separation, 'cy_range': range,
             }

    style_string = {'visualProperty': f'NODE_CUSTOMGRAPHICS_{slot}',
                    'value': 'org.cytoscape.BarChart:' + json.dumps(chart)}

    res = set_visual_property_default(style_string, style_name, base_url=base_url)
    return res


@cy_log
def set_node_custom_box_chart(columns, colors=None, range=None, orientation='VERTICAL', range_axis=False,
                              zero_line=False, axis_width=0.25, axis_color='#000000', axis_font_size=1,
                              slot=1, style_name=None, base_url=DEFAULT_BASE_URL):
    """Set Node Custom Box Chart.

    Makes a box chart per node using specified node table columns by setting a default custom graphic style.

    Args:
        columns (list): List of node column names to be displayed, in order.
        colors (list): List of colors to be matched with columns or with range, depending on type. Default is a
            set of colors from an appropriate Brewer cy_palette.
        range (list): Min and max values of chart. Default is to use min and max from specified data columns.
        orientation (str): HORIZONTAL or VERTICAL (default).
        col_axis (bool): Show axis with column labels. Default is False.
        range_axis (bool): Show axis with range of values. Default is False.
        zero_line (book): Show a line at zero. Default is False.
        axis_width (float): Width of axis lines, if shown. Default is 0.25.
        axis_color (str): Color of axis lines, if shown. Default is black ('#000000').
        axis_font_size(int): Font size of axis labels, if shown. Default is 1.
        slot (int): Which custom graphics slot to modify. Slots 1-9 are available for independent charts, gradients
            and images. Default is 1.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if style name or slot doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_custom_box_chart(['AverageShortestPath', 'BetweennessCentrality'], style_name='galFiltered Style')
        ''
        >>> set_node_custom_box_chart(['AverageShortestPath', 'BetweennessCentrality'], colors=['#FF00FF', '#00FF00'], slot=2, style_name='galFiltered Style')
        ''

    See Also:
        :meth:`set_node_custom_position`, :meth:`remove_node_custom_graphics`
    """
    verify_slot(slot)

    if colors is None:
        colors = cyPalette('rdbu') * len(columns)

    if range is None:
        cols = tables.get_table_columns(columns=columns, base_url=base_url)
        min = cols[columns].min().min()  # Make sure this works when column contains NANs
        max = cols[columns].max().max()
        range = [min, max]

    chart = {'cy_colors': colors, 'cy_colorScheme': 'Custom', 'cy_dataColumns': columns,
             'cy_orientation': orientation, 'cy_showRangeAxis': range_axis, 'cy_showRangeZeroBaseline': zero_line,
             'cy_axisWidth': axis_width, 'cy_axisColor': axis_color, 'cy_axisLabelFontSize': axis_font_size,
             'cy_range': range,
             }

    style_string = {'visualProperty': f'NODE_CUSTOMGRAPHICS_{slot}',
                    'value': 'org.cytoscape.BoxChart:' + json.dumps(chart)}

    res = set_visual_property_default(style_string, style_name, base_url=base_url)
    return res


@cy_log
def set_node_custom_heat_map_chart(columns, colors=None, range=None, orientation='HORIZONTAL', range_axis=False,
                                   zero_line=False, axis_width=0.25, axis_color='#000000', axis_font_size=1,
                                   slot=1, style_name=None, base_url=DEFAULT_BASE_URL):
    """Set Node Custom HeatMap Chart.

    Makes a heat map per node using specified node table columns by setting a default custom graphic style.

    Args:
        columns (list): List of node column names to be displayed, in order.
        colors (list): List of colors to be matched with columns or with range, depending on type. Default is a
            set of colors from an appropriate Brewer cy_palette.
        range (list): Min and max values of chart. Default is to use min and max from specified data columns.
        orientation (str): HORIZONTAL (default) or VERTICAL.
        range_axis (bool): Show axis with range of values. Default is False.
        zero_line (book): Show a line at zero. Default is False.
        axis_width (float): Width of axis lines, if shown. Default is 0.25.
        axis_color (str): Color of axis lines, if shown. Default is black ('#000000').
        axis_font_size(int): Font size of axis labels, if shown. Default is 1.
        slot (int): Which custom graphics slot to modify. Slots 1-9 are available for independent charts, gradients
            and images. Default is 1.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if style name or slot doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_custom_heat_map_chart(['AverageShortestPath', 'BetweennessCentrality'], style_name='galFiltered Style')
        ''
        >>> set_node_custom_heat_map_chart(['AverageShortestPath', 'BetweennessCentrality'], colors=['#123456', '#654321', '#112233', '#888888'], slot=2, style_name='galFiltered Style')
        ''

    See Also:
        :meth:`set_node_custom_position`, :meth:`remove_node_custom_graphics`
    """
    verify_slot(slot)

    if colors is None:
        palette = cyPalette('rdbu')
        colors = [palette[index] for index in [2, 6, 10]]
        colors.append('#888888')

    if range is None:
        cols = tables.get_table_columns(columns=columns, base_url=base_url)
        min = cols[columns].min().min()  # Make sure this works when column contains NANs
        max = cols[columns].max().max()
        range = [min, max]

    chart = {'cy_colors': colors, 'cy_colorScheme': 'Custom', 'cy_dataColumns': columns[::-1],
             'cy_orientation': orientation, 'cy_showRangeAxis': range_axis, 'cy_showRangeZeroBaseline': zero_line,
             'cy_axisWidth': axis_width, 'cy_axisColor': axis_color, 'cy_axisLabelFontSize': axis_font_size,
             'cy_range': range,
             }

    style_string = {'visualProperty': f'NODE_CUSTOMGRAPHICS_{slot}',
                    'value': 'org.cytoscape.HeatMapChart:' + json.dumps(chart)}

    res = set_visual_property_default(style_string, style_name, base_url=base_url)
    return res


@cy_log
def set_node_custom_line_chart(columns, colors=None, range=None, line_width=1.0, range_axis=False, zero_line=False,
                               axis_width=0.25, axis_color='#000000', axis_font_size=1,
                               slot=1, style_name=None, base_url=DEFAULT_BASE_URL):
    """Set Node Custom Line Chart.

    Makes a line chart per node using specified node table columns by setting a default custom graphic style.

    Args:
        columns (list): List of node column names to be displayed, in order.
        colors (list): List of colors to be matched with columns or with range, depending on type. Default is a
            set of colors from an appropriate Brewer cy_palette.
        range (list): Min and max values of chart. Default is to use min and max from specified data columns.
        line_width (float): Width of chart line. Default is 1.0.
        range_axis (bool): Show axis with range of values. Default is False.
        zero_line (book): Show a line at zero. Default is False.
        axis_width (float): Width of axis lines, if shown. Default is 0.25.
        axis_color (str): Color of axis lines, if shown. Default is black ('#000000').
        axis_font_size(int): Font size of axis labels, if shown. Default is 1.
        slot (int): Which custom graphics slot to modify. Slots 1-9 are available for independent charts, gradients
            and images. Default is 1.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if style name or slot doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_custom_line_chart(['AverageShortestPath', 'BetweennessCentrality'], style_name='galFiltered Style')
        ''
        >>> set_node_custom_line_chart(['AverageShortestPath', 'BetweennessCentrality'], colors=['#FF00FF', '#00FF00'], slot=2, style_name='galFiltered Style')
        ''

    See Also:
        :meth:`set_node_custom_position`, :meth:`remove_node_custom_graphics`
    """
    verify_slot(slot)

    if colors is None:
        colors = cyPalette('set1') * len(columns)

    if range is None:
        cols = tables.get_table_columns(columns=columns, base_url=base_url)
        min = cols[columns].min().min()  # Make sure this works when column contains NANs
        max = cols[columns].max().max()
        range = [min, max]

    chart = {'cy_colors': colors, 'cy_colorScheme': 'Custom', 'cy_dataColumns': columns,
             'cy_lineWidth': line_width, 'cy_showRangeAxis': range_axis, 'cy_showRangeZeroBaseline': zero_line,
             'cy_axisWidth': axis_width, 'cy_axisColor': axis_color, 'cy_axisLabelFontSize': axis_font_size,
             'cy_range': range,
             }

    style_string = {'visualProperty': f'NODE_CUSTOMGRAPHICS_{slot}',
                    'value': 'org.cytoscape.LineChart:' + json.dumps(chart)}

    res = set_visual_property_default(style_string, style_name, base_url=base_url)
    return res


@cy_log
def set_node_custom_pie_chart(columns, colors=None, start_angle=0.0,
                              slot=1, style_name=None, base_url=DEFAULT_BASE_URL):
    """Set Node Custom Pie Chart.

    Makes a pie chart per node using specified node table columns by setting a default custom graphic style.

    Args:
        columns (list): List of node column names to be displayed, in order.
        colors (list): List of colors to be matched with columns or with range, depending on type. Default is a
            set of colors from an appropriate Brewer cy_palette.
        start_angle (float): Angle to start filling pie. Default is 0.0.
        slot (int): Which custom graphics slot to modify. Slots 1-9 are available for independent charts, gradients
            and images. Default is 1.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if style name or slot doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_custom_pie_chart(['AverageShortestPath', 'BetweennessCentrality'], style_name='galFiltered Style')
        ''
        >>> set_node_custom_pie_chart(['AverageShortestPath', 'BetweennessCentrality'], colors=['#FF00FF', '#00FF00'], slot=2, style_name='galFiltered Style')
        ''

    See Also:
        :meth:`set_node_custom_position`, :meth:`remove_node_custom_graphics`
    """
    verify_slot(slot)

    if colors is None:
        colors = cyPalette('set1') * len(columns)
    chart = {'cy_colors': colors, 'cy_colorScheme': 'Custom', 'cy_dataColumns': columns,
             'cy_startAngle': start_angle}

    style_string = {'visualProperty': f'NODE_CUSTOMGRAPHICS_{slot}',
                    'value': 'org.cytoscape.PieChart:' + json.dumps(chart)}

    res = set_visual_property_default(style_string, style_name, base_url=base_url)
    return res


@cy_log
def set_node_custom_ring_chart(columns, colors=None, start_angle=0.0, hole_size=0.5,
                               slot=1, style_name=None, base_url=DEFAULT_BASE_URL):
    """Set Node Custom Ring Chart.

    Makes a ring chart per node using specified node table columns by setting a default custom graphic style.

    Args:
        columns (list): List of node column names to be displayed, in order.
        colors (list): List of colors to be matched with columns or with
        start_angle (float): Angle to start filling ring. Default is 0.0.
        hole_size (float): Size of hole in ring. Ranges 0-1. Default is 0.5.
        slot (int): Which custom graphics slot to modify. Slots 1-9 are available for independent charts, gradients
            and images. Default is 1.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if style name or slot doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_custom_ring_chart(['AverageShortestPath', 'BetweennessCentrality'], style_name='galFiltered Style')
        ''
        >>> set_node_custom_ring_chart(['AverageShortestPath', 'BetweennessCentrality'], colors=['#FF00FF', '#00FF00'], slot=2, style_name='galFiltered Style')
        ''

    See Also:
        :meth:`set_node_custom_position`, :meth:`remove_node_custom_graphics`
    """
    verify_slot(slot)

    if colors is None:
        colors = cyPalette('set1') * len(columns)
    chart = {'cy_colors': colors, 'cy_colorScheme': 'Custom', 'cy_dataColumns': columns,
             'cy_startAngle': start_angle, 'cy_holeSize': hole_size}

    style_string = {'visualProperty': f'NODE_CUSTOMGRAPHICS_{slot}',
                    'value': 'org.cytoscape.RingChart:' + json.dumps(chart)}

    res = set_visual_property_default(style_string, style_name, base_url=base_url)
    return res


@cy_log
def set_node_custom_linear_gradient(colors=['#DDDDDD', '#888888'], anchors=[0.0, 1.0], angle=0.0,
                                    slot=1, style_name=None, base_url=DEFAULT_BASE_URL):
    """Set Node Custom Linear Gradient.

    Makes a gradient fill per node by setting a default custom graphic style.

    Args:
        colors (list): List of colors to define gradient
        anchors (list): Position of colors from 0.0 to 1.0.
        angle (float): Angle of gradient. Default is 0 (left-to-right).
        slot (int): Which custom graphics slot to modify. Slots 1-9 are available for independent charts, gradients
            and images. Default is 1.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if style name or slot doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_custom_linear_gradient(style_name='galFiltered Style')
        ''
        >>> set_node_custom_linear_gradient(colors=['#FF00FF', '#00FF00'], angle=90.0, slot=2, style_name='galFiltered Style')
        ''
    """
    verify_slot(slot)

    chart = {'cy_angle': angle, 'cy_gradientColors': colors, 'cy_gradientFractions': anchors}
    style_string = {'visualProperty': f'NODE_CUSTOMGRAPHICS_{slot}',
                    'value': 'org.cytoscape.LinearGradient:' + json.dumps(chart)}

    res = set_visual_property_default(style_string, style_name, base_url=base_url)
    return res


@cy_log
def set_node_custom_radial_gradient(colors=['#DDDDDD', '#888888'], anchors=[0.0, 1.0], x_center=0.5, y_center=0.5,
                                    slot=1,
                                    style_name=None, base_url=DEFAULT_BASE_URL):
    """Set Node Custom Radial Gradient.

    Makes a gradient fill per node by setting a default custom graphic style.

    Args:
        colors (list): List of colors to define gradient
        anchors (list): Position of colors from 0.0 to 1.0.
        x_center (float): X position for center of radial effect from 0.0 to 1.0. Default is 0.5.
        y_center (float): Y position for center of radial effect from 0.0 to 1.0. Default is 0.5.
        slot (int): Which custom graphics slot to modify. Slots 1-9 are available for independent charts, gradients
            and images. Default is 1.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if style name or slot doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_custom_radial_gradient(style_name='galFiltered Style')
        ''
        >>> set_node_custom_radial_gradient(colors=['#FF00FF', '#00FF00'], x_center=0.0, y_center=0.0, slot=2, style_name='galFiltered Style')
        ''
    """
    verify_slot(slot)

    chart = {'cy_gradientColors': colors, 'cy_gradientFractions': anchors, 'cy_center': {'x': x_center, 'y': y_center}}
    style_string = {'visualProperty': f'NODE_CUSTOMGRAPHICS_{slot}',
                    'value': 'org.cytoscape.RadialGradient:' + json.dumps(chart)}

    res = set_visual_property_default(style_string, style_name, base_url=base_url)
    return res


@cy_log
def set_node_custom_position(node_anchor='C', graphic_anchor='C', justification='C', x_offset=0.0, y_offset=0.0, slot=1,
                             style_name=None, base_url=DEFAULT_BASE_URL):
    """Set Node Custom Position.

    Adjust the position of a custom graphic relative to its node.

    Args:
        node_anchor (str): Position on node to place the graphic: NW,N,NE,E,SE,S,SW,W or C for center (default)
        graphic_anchor (str): Position on graphic to place on node: NW,N,NE,E,SE,S,SW,W or C for center (default)
        justification (str): Positioning of content within graphic: l,r,c (default)
        x_offset (float): Additional offset in the x direction
        y_offset (float): Additional offset in the y direction
        slot (int): Which custom graphics slot to modify. Slots 1-9 are available for independent charts, gradients
            and images. Default is 1.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if style name or slot doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_custom_position(node_anchor='W', graphic_anchor='E', style_name='galFiltered Style')
        ''
        >>> set_node_custom_position(justification='l', slot=2, style_name='galFiltered Style')
        ''
    """
    verify_slot(slot)

    style_string = {'visualProperty': f'NODE_CUSTOMGRAPHICS_POSITION_{slot}',
                    'value': f'{node_anchor},{graphic_anchor},{justification},{x_offset},{y_offset}'}

    res = set_visual_property_default(style_string, style_name, base_url=base_url)
    return res


@cy_log
def remove_node_custom_graphics(slot=1, style_name=None, base_url=DEFAULT_BASE_URL):
    """Remove Node Custom Graphics.

    Remove the default custom charts, images and gradients.

    Args:
        slot (int): Which custom graphics slot to modify. Slots 1-9 are available for independent charts, gradients
            and images. Default is 1.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if style name or slot doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> remove_node_custom_graphics(style_name='galFiltered Style')
        ''
        >>> remove_node_custom_graphics(slot=2, style_name='galFiltered Style')
        ''
    """
    verify_slot(slot)

    res = set_visual_property_default({'visualProperty': f'NODE_CUSTOMGRAPHICS_{slot}', 'value': None}, style_name,
                                      base_url=base_url)
    return res


@cy_log
def set_node_fill_opacity_default(new_opacity, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist, or if opacity is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_fill_opacity_default(205, style_name='galFiltered Style')
        ''
        >>> set_node_fill_opacity_default(10)
        ''
    """
    verify_opacities(new_opacity)

    style = {'visualProperty': 'NODE_TRANSPARENCY', 'value': new_opacity}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def set_node_font_face_default(new_font, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist
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


@cy_log
def set_node_font_size_default(new_size, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist, or if size is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_font_size_default(20, style_name='galFiltered Style')
        ''
        >>> set_node_font_size_default(20)
        ''
    """
    verify_dimensions('size', new_size)

    style = {'visualProperty': 'NODE_LABEL_FONT_SIZE', 'value': new_size}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def set_node_height_default(new_height, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist, if height is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_height_default(20, style_name='galFiltered Style')
        ''
        >>> set_node_height_default(20)
        ''
    """
    verify_dimensions('height', new_height)
    # TODO: Shouldn't we be setting this back to its original value? ... and checking return result?
    style_dependencies.lock_node_dimensions(False, style_name=style_name, base_url=base_url)

    style = {'visualProperty': 'NODE_HEIGHT', 'value': new_height}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def set_node_label_default(new_label, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist
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


@cy_log
def set_node_label_color_default(new_color, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if invalid color, or if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_label_color_default('#CCCCCC', style_name='galFiltered Style')
        ''
        >>> set_node_label_color_default('#CCCCCC')
        ''
    """
    verify_hex_colors(new_color)

    style = {'visualProperty': 'NODE_LABEL_COLOR', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def set_node_label_opacity_default(new_opacity, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist, or if opacity is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_label_opacity_default(50, style_name='galFiltered Style')
        ''
        >>> set_node_label_opacity_default(50)
        ''
    """
    verify_opacities(new_opacity)

    style = {'visualProperty': 'NODE_LABEL_TRANSPARENCY', 'value': new_opacity}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def get_node_selection_color_default(style_name=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the default selection node color.

    Args:
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_node_selection_color_default(style_name='galFiltered Style')
        ''
        >>> get_node_selection_color_default()
        ''
    """
    res = get_visual_property_default('NODE_SELECTED_PAINT', style_name=style_name, base_url=base_url)
    return res


@cy_log
def set_node_selection_color_default(new_color, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if invalid color, or if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_selection_color_default('#CCCCCC', style_name='galFiltered Style')
        ''
        >>> set_node_selection_color_default('#CCCCCC')
        ''
    """
    verify_hex_colors(new_color)

    style = {'visualProperty': 'NODE_SELECTED_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def set_node_shape_default(new_shape, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist, or if shape is invalid
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
        raise CyError(f'"{new_shape}" is not a valid shape. For valid ones, check get_node_shapes().')


@cy_log
def set_node_size_default(new_size, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist, or if size is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_size_default(20, style_name='galFiltered Style')
        ''
        >>> set_node_size_default(20)
        ''
    """
    verify_dimensions('size', new_size)

    # TODO: Shouldn't we be setting this back to its original value? ... and checking return result?
    style_dependencies.lock_node_dimensions(True, style_name=style_name, base_url=base_url)

    style = {'visualProperty': 'NODE_SIZE', 'value': new_size}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def set_node_width_default(new_width, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist, or if invalid width
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_width_default(20, style_name='galFiltered Style')
        ''
        >>> set_node_width_default(20)
        ''
    """
    verify_dimensions('width', new_width)

    # TODO: Shouldn't we be setting this back to its original value? ... and checking return result?
    style_dependencies.lock_node_dimensions(False, style_name=style_name, base_url=base_url)

    style = {'visualProperty': 'NODE_WIDTH', 'value': new_width}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def set_node_tooltip_default(new_tooltip, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist
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

@cy_log
def set_edge_color_default(new_color, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if invalid color, or if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_color_default('#CCCCCC', style_name='galFiltered Style')
        ''
        >>> set_edge_color_default('#CCCCCC')
        ''
    """
    verify_hex_colors(new_color)

    style = {'visualProperty': 'EDGE_UNSELECTED_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    # TODO: Is it OK to lose the res value?

    style = {'visualProperty': 'EDGE_STROKE_UNSELECTED_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def set_edge_font_face_default(new_font, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist
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


@cy_log
def set_edge_font_size_default(new_size, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist, or if size is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_font_size_default(20, style_name='galFiltered Style')
        ''
        >>> set_edge_font_size_default(20)
        ''
    """
    verify_dimensions('size', new_size)

    style = {'visualProperty': 'EDGE_LABEL_FONT_SIZE', 'value': new_size}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def set_edge_label_default(new_label, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist
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


@cy_log
def set_edge_label_color_default(new_color, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if invalid color, or if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_label_color_default('#CCCCCC', style_name='galFiltered Style')
        ''
        >>> set_edge_label_color_default('#CCCCCC')
        ''
    """
    verify_hex_colors(new_color)

    style = {'visualProperty': 'EDGE_LABEL_COLOR', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def set_edge_label_opacity_default(new_opacity, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist, or if opacity is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_label_opacity_default(205, style_name='galFiltered Style')
        ''
        >>> set_edge_label_opacity_default(10)
        ''
    """
    verify_opacities(new_opacity)

    style = {'visualProperty': 'EDGE_LABEL_TRANSPARENCY', 'value': new_opacity}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def set_edge_line_width_default(new_width, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist, or if width is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_line_width_default(20, style_name='galFiltered Style')
        ''
        >>> set_edge_line_width_default(10)
        ''
    """
    verify_dimensions('width', new_width)

    style = {'visualProperty': 'EDGE_WIDTH', 'value': new_width}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def set_edge_line_style_default(new_line_style, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_line_style_default('SOLID', style_name='galFiltered Style')
        ''
        >>> set_edge_line_style_default('ZIGZAG')
        ''
    """
    style = {'visualProperty': 'EDGE_LINE_TYPE', 'value': new_line_style}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def set_edge_opacity_default(new_opacity, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist, or if opacity is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_opacity_default(205, style_name='galFiltered Style')
        ''
        >>> set_edge_opacity_default(10)
        ''
    """
    verify_opacities(new_opacity)

    style = {'visualProperty': 'EDGE_TRANSPARENCY', 'value': new_opacity}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def get_edge_selection_color_default(style_name=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the default selected edge color.

    Args:
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_edge_selection_color_default(style_name='galFiltered Style')
        ''
        >>> get_edge_selection_color_default()
        ''
    """
    if style_dependencies.get_style_dependencies(style_name=style_name)['arrowColorMatchesEdge']:
        return get_visual_property_default('EDGE_SELECTED_PAINT', style_name=style_name, base_url=base_url)
    else:
        return get_visual_property_default('EDGE_STROKE_SELECTED_PAINT', style_name=style_name, base_url=base_url)


@cy_log
def set_edge_selection_color_default(new_color, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if invalid color, or if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_selection_color_default('#CCCCCC', style_name='galFiltered Style')
        ''
        >>> set_edge_selection_color_default('#CCCCCC')
        ''
    """
    verify_hex_colors(new_color)

    style = {'visualProperty': 'EDGE_SELECTED_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    # TODO: res is lost after this call

    # TODO: Should the property be SELECTED ?? ... The R code has ELECTED
    style = {'visualProperty': 'EDGE_STROKE_SELECTED_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def set_edge_source_arrow_color_default(new_color, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if invalid color, or if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_source_arrow_color_default('#CCCCCC', style_name='galFiltered Style')
        ''
        >>> set_edge_source_arrow_color_default('#CCCCCC')
        ''
    """
    verify_hex_colors(new_color)

    style = {'visualProperty': 'EDGE_SOURCE_ARROW_UNSELECTED_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def set_edge_target_arrow_color_default(new_color, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if invalid color, or if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_target_arrow_color_default('#CCCCCC', style_name='galFiltered Style')
        ''
        >>> set_edge_target_arrow_color_default('#CCCCCC')
        ''
    """
    verify_hex_colors(new_color)

    style = {'visualProperty': 'EDGE_TARGET_ARROW_UNSELECTED_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


@cy_log
def set_edge_source_arrow_shape_default(new_shape, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist
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


@cy_log
def set_edge_target_arrow_shape_default(new_shape, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist
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


@cy_log
def set_edge_tooltip_default(new_tooltip, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if style name doesn't exist
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

@cy_log
def get_background_color_default(style_name=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the default background color.

    Args:
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_background_color_default(style_name='galFiltered Style')
        ''
        >>> get_background_color_default()
        ''
    """
    res = get_visual_property_default('NETWORK_BACKGROUND_PAINT', style_name=style_name, base_url=base_url)
    return res


@cy_log
def set_background_color_default(new_color, style_name=None, base_url=DEFAULT_BASE_URL):
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
        CyError: if invalid color, or if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_background_color_default('#CCCCCC', style_name='galFiltered Style')
        ''
        >>> set_background_color_default('#CCCCCC')
        ''
    """
    verify_hex_colors(new_color)

    style = {'visualProperty': 'NETWORK_BACKGROUND_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res
