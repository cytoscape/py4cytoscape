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

def get_visual_property_default(property, style_name='default', base_url=DEFAULT_BASE_URL):
    res = commands.cyrest_get('styles/' + style_name + '/defaults/' + property, base_url=base_url)
    return res['value']

def set_visual_property_default(style_string, style_name='default', base_url=DEFAULT_BASE_URL):
    res = commands.cyrest_put('styles/' + style_name + '/defaults', body=[style_string], base_url=base_url,
                              require_json=False)
    time.sleep(
        MODEL_PROPAGATION_SECS)  # wait for attributes to be applied ... it looks like Cytoscape returns before this is complete [BUG]
    return res

def set_node_border_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
    if is_not_hex_color(new_color):
        return None

    style = {'visualProperty': 'NODE_BORDER_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


def set_node_border_width_default(new_width, style_name='default', base_url=DEFAULT_BASE_URL):
    style = {'visualProperty': 'NODE_BORDER_WIDTH', 'value': new_width}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_node_border_opacity_default(new_opacity, style_name='default', base_url=DEFAULT_BASE_URL):
    if new_opacity < 0 or new_opacity > 255:
        error = 'Error: opacity must be between 0 and 255.'
        sys.stderr.write(error)
        return None  # TODO: Is this what we want to return here?

    style = {'visualProperty': 'NODE_BORDER_TRANSPARENCY', 'value': new_opacity}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_node_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
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
    if new_opacity < 0 or new_opacity > 255:
        error = 'Error: opacity must be between 0 and 255.'
        sys.stderr.write(error)
        return None  # TODO: Is this what we want to return here?

    style = {'visualProperty': 'NODE_TRANSPARENCY', 'value': new_opacity}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


def set_node_font_face_default(new_font, style_name='default', base_url=DEFAULT_BASE_URL):
    style = {'visualProperty': 'NODE_LABEL_FONT_FACE', 'value': new_font}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


def set_node_font_size_default(new_size, style_name='default', base_url=DEFAULT_BASE_URL):
    style = {'visualProperty': 'NODE_LABEL_FONT_SIZE', 'value': new_size}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


def set_node_height_default(new_height, style_name='default', base_url=DEFAULT_BASE_URL):
    # TODO: Shouldn't we be setting this back to its original value? ... and checking return result?
    style_dependencies.lock_node_dimensions(False, style_name=style_name, base_url=base_url)

    style = {'visualProperty': 'NODE_HEIGHT', 'value': new_height}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


def set_node_label_default(new_label, style_name='default', base_url=DEFAULT_BASE_URL):
    style = {'visualProperty': 'NODE_LABEL', 'value': new_label}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


def set_node_label_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
    if is_not_hex_color(new_color):
        return None

    style = {'visualProperty': 'NODE_LABEL_COLOR', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


def set_node_label_opacity_default(new_opacity, style_name='default', base_url=DEFAULT_BASE_URL):
    if new_opacity < 0 or new_opacity > 255:
        error = 'Error: opacity must be between 0 and 255.'
        sys.stderr.write(error)
        return None  # TODO: Is this what we want to return here?

    style = {'visualProperty': 'NODE_LABEL_TRANSPARENCY', 'value': new_opacity}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


def set_node_selection_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
    if is_not_hex_color(new_color):
        return None

    style = {'visualProperty': 'NODE_SELECTED_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


def set_node_shape_default(new_shape, style_name='default', base_url=DEFAULT_BASE_URL):
    new_shape = new_shape.upper()
    if new_shape in styles.get_node_shapes(base_url=base_url):
        style = {'visualProperty': 'NODE_SHAPE', 'value': new_shape}
        res = set_visual_property_default(style, style_name, base_url=base_url)
        return res
    else:
        sys.stderr.write(new_shape + ' is not a valid shape. Use get_node_shapes() to find valid values.')
        return None  # TODO: Is this the best thing to return?? ... probably should be an exception


def set_node_size_default(new_size, style_name='default', base_url=DEFAULT_BASE_URL):
    # TODO: Shouldn't we be setting this back to its original value? ... and checking return result?
    style_dependencies.lock_node_dimensions(True, style_name=style_name, base_url=base_url)

    style = {'visualProperty': 'NODE_SIZE', 'value': new_size}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


def set_node_width_default(new_width, style_name='default', base_url=DEFAULT_BASE_URL):
    # TODO: Shouldn't we be setting this back to its original value? ... and checking return result?
    style_dependencies.lock_node_dimensions(False, style_name=style_name, base_url=base_url)

    style = {'visualProperty': 'NODE_WIDTH', 'value': new_width}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


def set_node_tooltip_default(new_tooltip, style_name='default', base_url=DEFAULT_BASE_URL):
    style = {'visualProperty': 'NODE_TOOLTIP', 'value': new_tooltip}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


# ==============================================================================
# II.b. Edge Properties
# Pattern A: (1) prepare input value as named list, (2) call setVisualPropertyDefault()
# Pattern B: (1) call getVisualPropertyDefault()
# ------------------------------------------------------------------------------

def set_edge_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
    if is_not_hex_color(new_color):
        return None # TODO: Shouldn't this be an exception?

    style = {'visualProperty': 'EDGE_UNSELECTED_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    # TODO: Is it OK to lose the res value?

    style = {'visualProperty': 'EDGE_STROKE_UNSELECTED_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_font_face_default(new_font, style_name='default', base_url=DEFAULT_BASE_URL):
    style = {'visualProperty': 'EDGE_LABEL_FONT_FACE', 'value': new_font}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_font_size_default(new_size, style_name='default', base_url=DEFAULT_BASE_URL):
    style = {'visualProperty': 'EDGE_LABEL_FONT_SIZE', 'value': new_size}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_label_default(new_label, style_name='default', base_url=DEFAULT_BASE_URL):
    style = {'visualProperty': 'EDGE_LABEL', 'value': new_label}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_label_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
    if is_not_hex_color(new_color):
        raise CyError('Color must be in hex code, e.g., #FD5903')

    style = {'visualProperty': 'EDGE_LABEL_COLOR', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_label_opacity_default(new_opacity, style_name='default', base_url=DEFAULT_BASE_URL):
    if new_opacity < 0 or new_opacity > 255:
        error = 'Error: opacity must be between 0 and 255.'
        sys.stderr.write(error)
        return None  # TODO: Is this what we want to return here?

    style = {'visualProperty': 'EDGE_LABEL_TRANSPARENCY', 'value': new_opacity}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_line_width_default(new_width, style_name='default', base_url=DEFAULT_BASE_URL):
    style = {'visualProperty': 'EDGE_WIDTH', 'value': new_width}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_line_style_default(new_line_style, style_name='default', base_url=DEFAULT_BASE_URL):
    style = {'visualProperty': 'EDGE_LINE_TYPE', 'value': new_line_style}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_opacity_default(new_opacity, style_name='default', base_url=DEFAULT_BASE_URL):
    if new_opacity < 0 or new_opacity > 255:
        error = 'Error: opacity must be between 0 and 255.'
        sys.stderr.write(error)
        return None  # TODO: Is this what we want to return here?

    style = {'visualProperty': 'EDGE_TRANSPARENCY', 'value': new_opacity}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def get_edge_selection_color_default(style_name='default', base_url=DEFAULT_BASE_URL):
    if 'arrowColorMatchesEdge' in style_dependencies.get_style_dependencies():
        return get_visual_property_default('EDGE_SELECTED_PAINT', style_name=style_name, base_url=base_url)
    else:
        return get_visual_property_default('EDGE_STROKE_SELECTED_PAINT', style_name=style_name, base_url=base_url)

def set_edge_selection_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
    if is_not_hex_color(new_color):
        raise CyError('Color must be in hex code, e.g., #FD5903')

    style = {'visualProperty': 'EDGE_SELECTED_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    # TODO: res is lost after this call

    style = {'visualProperty': 'EDGE_STROKE_ELECTED_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_source_arrow_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
    if is_not_hex_color(new_color):
        raise CyError('Color must be in hex code, e.g., #FD5903')

    style = {'visualProperty': 'EDGE_SOURCE_ARROW_UNSELECTED_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_target_arrow_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
    if is_not_hex_color(new_color):
        raise CyError('Color must be in hex code, e.g., #FD5903')

    style = {'visualProperty': 'EDGE_TARGET_ARROW_UNSELECTED_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_source_arrow_shape_default(new_shape, style_name='default', base_url=DEFAULT_BASE_URL):
    style = {'visualProperty': 'EDGE_SOURCE_ARROW_SHAPE', 'value': new_shape}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_target_arrow_shape_default(new_shape, style_name='default', base_url=DEFAULT_BASE_URL):
    style = {'visualProperty': 'EDGE_TARGET_ARROW_SHAPE', 'value': new_shape}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

def set_edge_tooltip_default(new_tooltip, style_name='default', base_url=DEFAULT_BASE_URL):
    style = {'visualProperty': 'EDGE_TOOLTIP', 'value': new_tooltip}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res

# ==============================================================================
# II.c. Network Properties
# Pattern A: (1) prepare input value as named list, (2) call setVisualPropertyDefault()
# Pattern B: (1) call getVisualPropertyDefault()
# ------------------------------------------------------------------------------

def get_background_color_default(style_name='default', base_url=DEFAULT_BASE_URL):
    res = get_visual_property_default('NETWORK_BACKGROUND_PAINT', style_name=style_name, base_url=base_url)
    return res

def set_background_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
    if is_not_hex_color(new_color):
        return None # TODO: Shouldn't this return an exception?

    style = {'visualProperty': 'NETWORK_BACKGROUND_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res