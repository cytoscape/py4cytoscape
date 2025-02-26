# -*- coding: utf-8 -*-

"""Utility functions useful across multiple modules.
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

import os

LOCAL_BASE_URL = 'http://127.0.0.1:1234/v1'
DEFAULT_BASE_URL = os.environ.get('DEFAULT_BASE_URL') or LOCAL_BASE_URL

# External library imports
import urllib.parse
import re
import sys
from colour import Color

# Internal module imports
from . import tables
from . import cytoscape_system

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_logger import narrate
from .style_visual_props import PROPERTY_NAME_MAP


# print(f'Starting {__name__} module')


# ==============================================================================
# I. Package Utility Functions
# ------------------------------------------------------------------------------

def cyPalette(name='set1'):
    """Supply a set of colors from Brewer palettes (without requiring rColorBrewer).

    Args:
        name (str): name of a set of colors (e.g., 'set1', 'burd')

    Returns:
        list: list of color values in the cy_palette

    Raises:
        KeyError: if cy_palette name is invalid

    Examples:
        >>> cyPalette()
        ['#E41A1C', '#377EB8', '#4DAF4A', '#984EA3', '#FF7F00', '#FFFF33', '#A65628', '#F781BF', '#999999']
        >>> cyPalette('burd')
        ['#053061', '#2166AC', '#4393C3', '#92C5DE', '#D1E5F0', '#F7F7F7', '#FDDBC7', '#F4A582', '#D6604D', '#B2182B', '#67001F']
    """
    PALETTES = {
        'set1': ['#E41A1C', '#377EB8', '#4DAF4A', '#984EA3', '#FF7F00', '#FFFF33', '#A65628', '#F781BF', '#999999'],
        'set2': ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854', '#FFD92F', '#E5C494', '#B3B3B3'],
        'set3': ['#8DD3C7', '#FFFFB3', '#BEBADA', '#FB8072', '#80B1D3', '#FDB462', '#B3DE69', '#FCCDE5', '#D9D9D9',
                 '#BC80BD', '#CCEBC5', '#FFED6F'],
        'reds': ['#FFF5F0', '#FEE0D2', '#FCBBA1', '#FC9272', '#FB6A4A', '#EF3B2C', '#CB181D', '#A50F15', '#67000D'],
        'rdbu': ['#67001F', '#B2182B', '#D6604D', '#F4A582', '#FDDBC7', '#F7F7F7', '#D1E5F0', '#92C5DE', '#4393C3',
                 '#2166AC', '#053061'],
        'burd': ['#053061', '#2166AC', '#4393C3', '#92C5DE', '#D1E5F0', '#F7F7F7', '#FDDBC7', '#F4A582', '#D6604D',
                 '#B2182B', '#67001F']
    }
    return PALETTES[name]

# ------------------------------------------------------------------------------
def verify_brightness_contrast(bc):
    """Validate and provide user feedback when brightness or contrast is required input.

    Args:
        bc (int or float): a number between 0 and 100

    Returns:
        None

    Raises:
        CyError: if value is invalid

    Examples:
        >>> verify_brightness_contrast(77)
    """
    if not (isinstance(bc, float) or isinstance(bc, int)) or bc < -100 or bc > 100:
        raise CyError(f'"{bc}" is invalid. Value must be between -100 and 100).',
                      caller=sys._getframe(1).f_code.co_name)


def verify_hex_color(color):
    """Validate and provide user feedback when hex color code is required input.

    Args:
        colors (str): a single value, which is a 6 digit hex value or a color name

    Returns:
        str: '#' followed by 6 digit hex value

    Raises:
        CyError: if color is invalid

    Examples:
        >>> verify_hex_color('#92C5DE')
        '#92C5DE'
        >>> verify_hex_color('red')
        '#FF0000'
    """
    try:
        if color.startswith('#') and len(color) == 7:
            return color
        else:
            return Color(color).get_hex_l().upper()
    except:
        raise CyError(
            f'"{color}" is not a valid color name (e.g., "red") or a hexadecimal color (has to begin with # and be 7 characters long, e.g., #FF00FF).',
            caller=sys._getframe(1).f_code.co_name)


def verify_hex_colors(colors):
    """Validate and provide user feedback when hex color code (or a list of codes) are required input.

    Args:
        colors (str or list): a single value or a list of colors, which are 6 digit hex values

    Returns:
        str or list: colors as '#' followed by 6 digit hex value

    Raises:
        CyError: if color is invalid

    Examples:
        >>> verify_hex_colors('#92C5DE')
        '#92C5DE'
        >>> verify_hex_colors(['#053061', '#2166AC', '#4393C3', '#92C5DE', '#D1E5F0', '#F7F7F7', '#FDDBC7', '#F4A582', '#D6604D', '#B2182B', '#67001F'])
        ['#053061', '#2166AC', '#4393C3', '#92C5DE', '#D1E5F0', '#F7F7F7', '#FDDBC7', '#F4A582', '#D6604D', '#B2182B', '#67001F']
        >>> verify_hex_colors(['red', 'blue', '#4393C3'])
        ['#FF0000', '#0000FF', '#4393C3']
    """
    if colors is None: return None
    if isinstance(colors, list):
        return [verify_hex_color(c) for c in colors]
    else:
        return verify_hex_color(colors)


def verify_opacity(opacity, max_opacity=100):
    """Validate and provide user feedback when opacity is required input.

    Args:
        opacity (int or float): a number between 0 and a max

    Returns:
        int or float: validated opacity

    Raises:
        CyError: if opacity is invalid

    Examples:
        >>> verify_opacity(77)
    """
    if not (isinstance(opacity, float) or isinstance(opacity, int)) or opacity < 0 or opacity > max_opacity:
        raise CyError(f'"{opacity}" is not a valid opacity (has to be an integer between 0 and {max_opacity}).',
                      caller=sys._getframe(1).f_code.co_name)

    return opacity


def verify_opacities(opacities):
    """Validate and provide user feedback when opacity is required input.

    Args:
        opacities (int, float or list): a single value or a list of values, all of which are integers or floats

    Returns:
        str or list: verified opacities

    Raises:
        CyError: if opacity is invalid

    Examples:
        >>> verify_opacities(177)
        >>> verify_opacities([177, 200])
    """
    if opacities is None: return None
    if isinstance(opacities, list):
        return [verify_opacity(opacity, max_opacity=255) for opacity in opacities]
    else:
        return verify_opacity(opacities, max_opacity=255)


def verify_dimensions(dimension, sizes):
    """Validate and provide user feedback when dimensions is required input.

    Args:
        dimension (str): name of the sizes being examined (e.g., 'width')
        sizes (int, float or list): a single value or a list of values, all of which are integers or floats

    Returns:
        list: verified dimensions

    Raises:
        CyError: if size is invalid

    Examples:
        >>> verify_dimensions('width', 50)
        >>> verify_dimensions('width', [10, 20])
    """

    def verify_dimension(dimension, size):
        if not isinstance(size, float) and not isinstance(size, int):
            raise CyError(f'Illegal {dimension} "{size}". It needs to be a number.',
                          caller=sys._getframe(2).f_code.co_name)
        return size

    if sizes is None: return None
    if isinstance(sizes, list):
        return [verify_dimension(dimension, size) for size in sizes]
    else:
        return verify_dimension(dimension, sizes)


def verify_slot(slot):
    """Validate and provide user feedback when slot is required input.

    Args:
        slot (int or float): a slot number between 1 and 9

    Returns:
        None

    Raises:
        CyError: if slot is invalid

    Examples:
        >>> verify_slot(5)
    """
    if not (isinstance(slot, float) or isinstance(slot, int)) or slot < 1 or slot > 9:
        raise CyError(f'slot must be an integer between 1 and 9', caller=sys._getframe(1).f_code.co_name)


def verify_unique(value, existing_values):
    if value in existing_values:
        raise CyError(f'{value} is not unique. Please provide a unique value.', caller=sys._getframe(1).f_code.co_name)


def verify_positive(number):
    """Validate and provide user feedback when positive number is required input.

    Args:
        number (int or float): a number greater than 0

    Returns:
        None

    Raises:
        CyError: if number is invalid

    Examples:
        >>> verify_positive(5)
    """
    if not (isinstance(number, float) or isinstance(number, int)):
        raise CyError(f'Value must be a positive number.', caller=sys._getframe(1).f_code.co_name)
    if number <= 0:
        raise CyError(f'{number} is invalid. Number must be positive', caller=sys._getframe(1).f_code.co_name)


def verify_non_negative(number):
    """Validate and provide user feedback when a non-negative number is required input.

    Args:
        number (int or float): a number greater than or equal to 0

    Returns:
        None

    Raises:
        CyError: if number is invalid

    Examples:
        >>> verify_non_negative(5)
    """
    if not (isinstance(number, float) or isinstance(number, int)):
        raise CyError(f'Value must be a non-negative number.', caller=sys._getframe(1).f_code.co_name)
    if number <= 0:
        raise CyError(f'{number} is invalid. Number must be greater than or equal to 0',
                      caller=sys._getframe(1).f_code.co_name)


def verify_font_style(style):
    """Validate and provide user feedback when font style is required input.

    Args:
        font_style (str): a font style ['plain', 'bold', 'italic', 'bolditalic']

    Returns:
        None

    Raises:
        CyError: if style is invalid

    Examples:
        >>> verify_font_style('plain')
    """
    valid_styles = ['plain', 'bold', 'italic', 'bolditalic']
    if style not in valid_styles:
        raise CyError(f'{style} is invalid. Use {valid_styles}', caller=sys._getframe(1).f_code.co_name)


def verify_canvas(canvas):
    """Validate acceptable canvas

    Args:
        canvas (str): a canvas ['foreground', 'background']

    Returns:
        None

    Raises:
        CyError: if canvas is invalid

    Examples:
        >>> verify_canvas('foreground')
    """
    valid_canvases = ['foreground', 'background']
    if canvas not in valid_canvases:
        raise CyError(f'{canvas} is invalid. Use {valid_canvases}', caller=sys._getframe(1).f_code.co_name)


def verify_node_shapes(shapes, valid_shapes):
    """Validate list of proposed shapes for nodes

    Args:
        shapes (list or str): shapes (e.g., 'RECTANGLE', 'HEXAGON')
        valid_shapes (list): a list of valid shapes

    Returns:
        list or str: shape(s), updated old shape names to new ones

    Raises:
        CyError: if a shape is invalid

    Examples:
        >>> verify_node_shapes('RECTANGLE', styles.get_node_shapes())
        ['RECTANGLE']
        >>> verify_node_shapes(['RECTANGLE', 'DIAMOND'], styles.get_node_shapes())
        ['RECTANGLE', 'DIAMOND']
    """

    def verify_node_shape(shape, valid_shapes):
        shape = 'ROUND_RECTANGLE' if shape == 'round_rect' else shape
        shape = 'RECTANGLE' if shape == 'rect' else shape.upper()

        if shape in valid_shapes:
            return shape
        raise CyError(
            f'"{shape}" is not a valid shape. Please note that some older shapes are no longer available. For valid ones check get_node_shapes().',
            caller=sys._getframe(2).f_code.co_name)

    if shapes is None: return None
    if isinstance(shapes, list):
        return [verify_node_shape(shape, valid_shapes) for shape in shapes]
    else:
        return verify_node_shape(shapes, valid_shapes)


def verify_edge_shapes(shapes, valid_shapes, style_name, style_authority):
    """Validate list of proposed shapes for edges

    Args:
        shapes (list or str): line styles (e.g., 'ZIGZAG', 'SOLID')
        valid_line_styles (list): a list of valid shapes
        style_name (str): name of the style being validated
        style_authority (str): plausible function for getting list of valid shapes

    Returns:
        list or str: the style

    Raises:
        CyError: if a style is invalid

    Examples:
        >>> verify_edge_shapes('SOLID', styles.get_line_styles(), 'line style', 'get_line_styles')
        ['SOLID']
        >>> verify_edge_shapes(['SOLID', 'ZIGZAG'], styles.get_line_styles(), 'line style', 'get_line_styles')
        ['SOLID', 'ZIGZAG']
    """

    def verify_edge_shape(shape, valid_shapes, style_name, style_authority):
        shape = shape.upper()
        if shape in valid_shapes:
            return shape
        raise CyError(f'"{shape}" is not a valid {style_name}. For valid ones check {style_authority}().',
                      caller=sys._getframe(2).f_code.co_name)

    if shapes is None: return None
    if isinstance(shapes, list):
        return [verify_edge_shape(shape, valid_shapes, style_name, style_authority) for shape in shapes]
    else:
        return verify_edge_shape(shapes, valid_shapes, style_name, style_authority)


def verify_bools(bool_values):
    """Validate list of boolean values

    Args:
         (list or str): boolean values (e.g., True or False)

    Returns:
        list or str: the style

    Raises:
        CyError: if a style is invalid

    Examples:
        >>> verify_bools(True)
        True
        >>> verify_bools('True')
        'True'
        >>> verify_bools([True, False])
        [True, False]
    """

    def verify_bool(bool_value):
        if isinstance(bool_value, bool):
            return bool_value
        elif isinstance(bool_value, str) and bool_value.upper() in {'TRUE', 'FALSE'}:
            return bool_value
        raise CyError(f'"{bool_value}" is not a valid boolean. It must be either true or false.',
                      caller=sys._getframe(2).f_code.co_name)

    if bool_values is None: return None
    if isinstance(bool_values, list):
        return [verify_bool(bool_value) for bool_value in bool_values]
    else:
        return verify_bool(bool_values)

def verify_strs(str_values):
    """Validate list of string values

    Args:
         (list or str): string values (e.g., 'happy'

    Returns:
        list or str: the style

    Raises:
        CyError: if a style is invalid

    Examples:
        >>> verify_strs('happy')
        'happy'
        >>> verify_bools(['happy', 'sad'])
        ['happy', 'sad']
    """

    def verify_str(str_value):
        if isinstance(str_value, str):
            return str_value
        raise CyError(f'"{str_value}" is not a valid string.',
                      caller=sys._getframe(2).f_code.co_name)

    if str_values is None: return None
    if isinstance(str_values, list):
        return [verify_str(str_value) for str_value in str_values]
    else:
        return verify_str(str_values)

def normalize_rotation(degree):
    """Validates and fixes rotation values from -180 to +180 range to match GUI

    Args:
        degree (int or float): an angle in degrees

    Returns:
        int or float: angle normalized to [-180..+180]

    Raises:
        CyError: if angle is invalid

    Examples:
        >>> normalize_rotation(200)
    """
    if not (isinstance(degree, float) or isinstance(degree, int)):
        raise CyError(f'Angle must be a number.', caller=sys._getframe(1).f_code.co_name)
    while degree < -180:
        degree += 360
    while degree > 180:
        degree -= 360
    return degree


def node_name_to_node_suid(node_names, network=None, base_url=DEFAULT_BASE_URL, *, unique_list=False):
    """Translate one node name or a list of node names into a list of SUIDs.

    List can contain either names or SUIDs. If the list contains all SUIDs and no names, the list
    is returned.

    If a name occurs multiple times in the list and unique_list=True, a different SUID is returned
    for each name instance, provided that the network has enough same-named edges. If not, an error is returned.

    If a name occures multiple times but unique_list=False, a list of SUIDs is returned for each name instance. If there
    is only one name, the SUID is returned as a scalar.

    Args:
        node_names (str or list): an node name or a list of node names
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.
        unique_list (bool): True if duplicate node names refer to different nodes; False if it doesn't matter

    Returns:
        list: [<SUID or SUID list corresponding to each name>] or None if node_names is None

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> node_name_to_node_suid('YDR277C')
        [1022]
        >>> node_name_to_node_suid(['YDR277C', 'YDL194W'], network='myNetwork')
        [1022, 1023]
        >>> node_name_to_node_suid('YDR277C, YDL194W', network='myNetwork')
        [1022, 1023]
        >>> node_name_to_node_suid([1022, 1023], network='myNetwork')
        [1022, 1023]
        >>> node_name_to_node_suid(['YDR277C', 'YDR277C'], network='myNetwork', unique_list=True)
        [1022, 1024]
        >>> node_name_to_node_suid(['YDR277C', 'YDR277C', 'YDL194W'], network='myNetwork')
        [[1022, 1024], [1022, 1024], 1023]

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1, node\\\\,2' identifies 'node1' and 'node,2'.
    """
    return _item_to_suid(node_names, 'node', network=network, base_url=base_url, unique_list=unique_list)


def node_suid_to_node_name(node_suids, network=None, base_url=DEFAULT_BASE_URL):
    """Translate one node SUID or a list of node SUIDs into a list of names.

    List can contain a mixture of names and SUIDs. If it does, only the SUIDs are translated,
    but all entries are returned. If the list contains all names and no SUIDs, the list is returned.

    Args:
        node_suids (SUID or list): an edge SUID or a list of edge SUIDs
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: [<name corresponding to each SUID>] or None if node_suids is None

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> node_suid_to_node_name(1022)
        ['YDR277C']
        >>> node_suid_to_node_name([1022, 1023], network='myNetwork')
        ['YDR277C', 'YDL194W']
        >>> node_suid_to_node_name(['YDR277C', 'YDL194W'], network='myNetwork')
        ['YDR277C', 'YDL194W']
        >>> node_suid_to_node_name('YDR277C, YDL194W', network='myNetwork')
        ['YDR277C', 'YDL194W']
    """
    if node_suids is None:
        return None
    
    node_suids = normalize_list(node_suids)
    
    # Fetch the node data from Cytoscape
    df = tables.get_table_columns('node', ['name'], 'default', network, base_url=base_url)
    suid_to_name = dict(zip(df.index, df['name']))
    all_names = set(df['name'])

    # Determine if the list contains only SUIDs or only names
    are_all_suids = all(isinstance(item, int) for item in node_suids)
    are_all_names = all(isinstance(item, str) for item in node_suids)

    if not (are_all_suids or are_all_names):
        raise CyError(f'List contains a mix of SUIDs and names: {node_suids}')
    
    node_names = []
    for item in node_suids:
        if are_all_suids:
            if item in suid_to_name:
                node_names.append(suid_to_name[item])
            else:
                raise CyError(f'Invalid node SUID in list: {item}')
        elif are_all_names:
            if item in all_names:
                node_names.append(item)
            else:
                raise CyError(f'Invalid node name in list: {item}')
    
    return node_names


def edge_name_to_edge_suid(edge_names, network=None, base_url=DEFAULT_BASE_URL, *, unique_list=False):
    """Translate one edge name or a list of edge names into a list of SUIDs.

    List can contain either names or SUIDs. If the list contains all SUIDs and no names, the list
    is returned.

    If a name occurs multiple times in the list and unique_list=True, a different SUID is returned
    for each name instance, provided that the network has enough same-named edges. If not, an error is returned.

    If a name occures multiple times but unique_list=False, a list of SUIDs is returned for each name instance. If there
    is only one name, the SUID is returned as a scalar.

    Args:
        edge_names (str or list): an edge name or a list of edge names
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.
        unique_list (bool): True if duplicate edge names refer to different edges; False if it doesn't matter

    Returns:
        list: [<SUID or SUID listcorresponding to each name>] or None if edge_names is None

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> edge_name_to_edge_suid('YDR277C (pp) YDL194W')
        [1022]
        >>> edge_name_to_edge_suid(1022)
        [1022]
        >>> edge_name_to_edge_suid(['YDR277C (pp) YDL194W', 'YDR277C (pp) YDR206W'], network='myNetwork')
        [1022, 1023]
        >>> edge_name_to_edge_suid('YDR277C (pp) YDL194W, YDR277C (pp) YDR206W', network='myNetwork')
        [1022, 1023]
        >>> edge_name_to_edge_suid([1022, 1023], network='myNetwork')
        [1022, 1023]
        >>> edge_name_to_edge_suid(['YDR277C (pp) YDL194W', 'YDR277C (pp) YDL194W'], network='myNetwork', unique_list=True)
        [1022, 1024]
        >>> edge_name_to_edge_suid(['YDR277C (pp) YDL194W', 'YDR277C (pp) YDL194W', 'YDR277C (pp) YDR206W'], network='myNetwork')
        [[1022, 1024], [1022, 1024], 1023]

    Note:
        To identify a node whose name contains a comma, use '\\\\' to escape the comma. For example,
        'node1 (pd) node\\\\,2' identifies 'node1 (pd) node,2'.
    """
    return _item_to_suid(edge_names, 'edge', network=network, base_url=base_url, unique_list=unique_list)


def edge_suid_to_edge_name(edge_suids, network=None, base_url=DEFAULT_BASE_URL):
    """Translate one edge SUID or a list of edge SUIDs into a list of names.

    List can contain a mixture of names and SUIDs. If it does, only the SUIDs are translated,
    but all entries are returned. If the list contains all names and no SUIDs, the list is returned.

    Args:
        edge_suids (SUID or list): an edge SUID or a list of edge SUIDs
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
         list: [<name corresponding to each SUID>] or None if edge_suids is None

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> edge_suid_to_edge_name(1022)
        ['YDR277C (pp) YDL194W']
        >>> edge_suid_to_edge_name('1022, 1023')
        ['YDR277C (pp) YDL194W', 'YDR277C (pp) YDR206W']
        >>> edge_suid_to_edge_name([1022, 1023], network='myNetwork')
        ['YDR277C (pp) YDL194W', 'YDR277C (pp) YDR206W']
        >>> edge_suid_to_edge_name(['YDR277C (pp) YDL194W', 'YDR277C (pp) YDR206W'], network='myNetwork')
        ['YDR277C (pp) YDL194W', 'YDR277C (pp) YDR206W']
    """
    if edge_suids is None:
        return None

    edge_suids = normalize_list(edge_suids)

    # Fetch the edge data from Cytoscape
    df = tables.get_table_columns('edge', ['name'], 'default', network, base_url=base_url)
    suid_to_name = dict(zip(df.index, df['name']))
    all_names = set(df['name'])

    # Determine if the list contains only SUIDs or only names
    are_all_suids = all(isinstance(item, int) for item in edge_suids)
    are_all_names = all(isinstance(item, str) for item in edge_suids)

    if not (are_all_suids or are_all_names):
        raise CyError(f'List contains a mix of SUIDs and names: {edge_suids}')

    edge_names = []
    for item in edge_suids:
        if are_all_suids:
            if item in suid_to_name:
                edge_names.append(suid_to_name[item])
            else:
                raise CyError(f'Invalid edge SUID in list: {item}')
        elif are_all_names:
            if item in all_names:
                edge_names.append(item)
            else:
                raise CyError(f'Invalid edge name in list: {item}')

    return edge_names    


# ------------------------------------------------------------------------------
# TODO: R had netowrk=network, which looks like a typo
def table_column_exists(table_column, table, network=None, base_url=DEFAULT_BASE_URL):
    """Checks to see if a particular column name exists in the specific table.

    Args:
        table_column (str): name of column within table
        table (str): name of table to check (e.g., 'node', 'edge', 'network')
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        bool: True if column exists, False if not

    Raises:
        CyError: if table or network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> table_column_exists('YDL194W', 'node')
        True
        >>> table_column_exists('bogus', 'edge', network='myNetwork')
        False
    """
    if table_column not in tables.get_table_column_names(table, network=network, base_url=base_url):
        narrate('Column ' + table_column + ' does not exist in the ' + table + ' table.')
        return False
    return True


# ------------------------------------------------------------------------------
def check_supported_versions(cyrest=1, cytoscape=3.6, base_url=DEFAULT_BASE_URL, caller=None, test_cytoscape=None):
    """Checks to see if min supported versions of api and cytoscape are running.

    Extracts numerics from api, major and patch cytoscape versions before making comparison, per semantic versioning @ https://semver.org/

    Args:
        cyrest (int): minimum CyREST version
        cytoscape (float or str): minimum Cytoscape version ... should be str if version > 3.9
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
         None or Str: Str is explanation if error was found: otherwise, None

    Raises:
        AttributeError: if required version can't be parsed

    Examples:
        >>> check_supported_versions(1, 3.7)
        >>> check_supported_versions(1, '3.10')
        >>> check_supported_versions(1, '3.10.0')
    """
    if isinstance(cytoscape, float): cytoscape = str(cytoscape)

    v = cytoscape_system.cytoscape_version_info(base_url=base_url)
    v_api_str = v['apiVersion']
    v_cy_str = v['cytoscapeVersion']  if test_cytoscape is None else test_cytoscape
    v_api_num = int(re.match('v([0-9]+)$', v_api_str).group(1))

    # Check the CyREST version
    if cyrest > v_api_num:
        return 'CyREST API version %d or greater is required. You are currently working with version %d.' % (cyrest, v_api_num)

    # Check the Cytoscape version
    re_v_cytoscape = re.match('^([0-9]+)\\.([0-9]+)\\.([0-9]+).*$', v_cy_str)
    v_cytoscape_major = int(re_v_cytoscape.group(1))
    v_cytoscape_minor = int(re_v_cytoscape.group(2))
    v_cytoscape_patch = int(re_v_cytoscape.group(3))

    re_cytoscape = re.match('^([0-9]+)\\.([0-9]+)?(\\.[0-9]+)?(-.*)*$', cytoscape)
    required_cytoscape_major = int(re_cytoscape.group(1))
    required_cytoscape_minor = int(re_cytoscape.group(2))
    if re_cytoscape.group(3) is None:
        required_cytoscape_patch = 0
    else:
        required_cytoscape_patch = int(re_cytoscape.group(3)[1:]) # Strip leading '.' and take the rest

    if v_cytoscape_major > required_cytoscape_major or \
        (v_cytoscape_major == required_cytoscape_major and v_cytoscape_minor > required_cytoscape_minor) or \
        (v_cytoscape_major == required_cytoscape_major and v_cytoscape_minor == required_cytoscape_minor and v_cytoscape_patch >= required_cytoscape_patch):
        return None
    else:
        return f'Cytoscape version {cytoscape} or greater is required. You are currently working with version {v_cy_str}.'


def verify_supported_versions(cyrest=1, cytoscape=3.6, base_url=DEFAULT_BASE_URL, caller=None):
    """Throws exception if min supported versions of api and cytoscape are not running.

    Extracts numerics from api and major cytoscape versions before making comparison.

    Args:
        cyrest (int): minimum CyREST version
        cytoscape (float or str): minimum Cytoscape version ... should be str if version > 3.9
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.
        caller (str): name of function in which error is to be reported

    Returns:
         None

    Raises:
        CyError: if required version is greater than current version
        AttributeError: if required version can't be parsed

    Examples:
        >>> verify_supported_versions(1, 3.7)
        >>> verify_supported_versions(1, '3.10')
        >>> verify_supported_versions(1, '3.10.1')
    """
    nogo = check_supported_versions(cyrest=cyrest, cytoscape=cytoscape, base_url=base_url)

    if nogo:
        if caller is None: caller = sys._getframe(1).f_code.co_name
        raise CyError(f'Function not run due to unsupported version: {nogo}', caller=caller)


def normalize_list(entity):
    # Try to return a list representing entity, but the actual return value depends on the entity passed in
    # If the entity is str, it could contain a single value or a comma-separated list of values
    #     if all of these values look like integers, the return value is a python list of integers (e.g., '1,2,3' -> [1,2,3] or '1'->[1])
    #     if at least one value doesn't look like an integer, the return value is a python list of strings (e.g., 'A,B,1' -> ['A','B','1'] or 'A' -> ['A'])
    # If the entity is a list, the list is just returned as is (e.g., ['A','B','C'] -> ['A','B','C'] or [1,2,3] -> [1,2,3])
    #     Note that this could defeat the intention of normalization if the list contains values of mixed
    #     type (e.g., [1, 'A']) that are likely an error. But we let the caller detect this error.
    # If the entity is neither list nor string, it is returned as a python list of length 1 (e.g., 123 -> [123]
    if isinstance(entity, str):  # If it's a string, it could be names, SUIDs, or whatever
        scalar_list = str.split(entity, ',')
        try:
            return [int(x) for x in scalar_list]  # for each entry, see if it's a number
        except:
            return [str.strip(x) for x in scalar_list]  # for each entry, get rid of leading/trialing spaces
    elif not isinstance(entity, list):  # If it's not a string, it could be int, int64 or whatever
        return [entity]
    else:
        return entity


def prep_post_query_lists(cmd_list=None, cmd_by_col=None):
    # Return 'selected' or a comma-separated list of strings as either 'x,y,x' or 'col:x,col:y,col:z'
    if cmd_list is None:
        cmd_list_ready = 'selected'
    else:
        cmd_list_normal = normalize_list(cmd_list)
        if cmd_by_col is None:
            cmd_list_normal = [f'{cmd}' for cmd in cmd_list_normal]
        else:
            cmd_list_normal = [f'{cmd_by_col}:{cmd}' for cmd in cmd_list_normal]
        cmd_list_ready = ','.join(cmd_list_normal)

    return cmd_list_ready


def parse_edges(edge_list):
    # Convert edge list into list of parts: ["xxx (pp) yyy", "zzz (pp) aaa"] into [("xxx", "pp", "yyy"), ("zzz", "pp", "aaa")]

    def split_edge(edge):
        res = re.match(r'(.*) \((.*)\) (.*)', edge)
        return (res.group(1), res.group(2), res.group(3))

    return [split_edge(x) for x in edge_list]


def build_url(base_url=DEFAULT_BASE_URL, command=None):
    """Append a command (if it exists) to a base URL.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.
        command (str): the command (if any) to append to the base_url

    Returns:
         str: URL composed of base and URL-encoded command

    Raises:
        none

    Examples:
        >>> build_url()
        'http://127.0.0.1:1234/v1'
        >>> build_url('collections/1043355/tables/default')
        'http://127.0.0.1:1234/v1/collections/1043355/tables/default'
    """
    if command is not None:
        return base_url + "/" + urllib.parse.quote(command)
    else:
        return base_url


# Figure out which kind of visual style mapping is being used
def normalize_mapping(mapping_type, visual_prop_name, supported_mappings, long_name=True):
    if mapping_type in ['continuous', 'c', 'interpolate']:
        mapped = ('continuous', 'c')
    elif mapping_type in ['discrete', 'd', 'lookup']:
        mapped = ('discrete', 'd')
    elif mapping_type in ['passthrough', 'p']:
        mapped = ('passthrough', 'p')
    else:
        mapped = ('?', '?')

    if mapped[1] in supported_mappings:
        return mapped[0 if long_name else 1]
    else:
        raise CyError(
            f'mapping_type "{mapping_type}" for property "{visual_prop_name}" not recognized ... must be "{supported_mappings}"')

def normalize_prop_name(prop_name):
    if prop_name is None:
        raise CyError(f'Invalid visual property ... visual_property must be non-null')

    # Convert white space to '_' and uppercase everything (e.g., 'edge color' -> 'EDGE_COLOR')
    visual_prop_name = re.sub('\\s+', '_', prop_name).upper()
    if visual_prop_name in PROPERTY_NAME_MAP: visual_prop_name = PROPERTY_NAME_MAP[visual_prop_name]
    return visual_prop_name

def _item_to_suid(item_names, table_name, network=None, base_url=DEFAULT_BASE_URL, unique_list=False):
    # Translate a list of node or edge names into a list of SUIDs ... account for duplicated names if the list is unique
    if item_names is None:
        return None
    
    # Normalize input item names ... item_names could come back as a list of name ints (if all items look
    # like ints) or strings (if at least one name isn't an int). Normal situation is list of strings, but
    # list of ints is legitimate if the input names are already a list of SUIDs or if the table's name
    # column contains names that look like ints.
    item_names = normalize_list(item_names)

    # Get a table of column names indexed by SUID and a set containing all of the SUIDs
    df = tables.get_table_columns(table_name, ['name'], 'default', network, base_url=base_url)
    all_suids = set(df.index)

    # Check if all item names are valid SUIDs, return immediately if true
    # (... fails if any item is a string or a number that's not a SUID but could be an item name)
    if all(item_name in all_suids for item_name in item_names):
        return item_names

    # Map all names to SUIDs for O(1) lookup, allowing multiple SUIDs per name
    item_name_to_suid_list = {}
    for suid, name in zip(df.index, df['name']): # loop through all known SUIDS/names
        try:
            name = int(name)    # name looks like a number ... important because item_names will contain number if item looks like a number
        except (ValueError, TypeError):
            pass    # name looks like a string ... use it as is

        # Add name and SUID(s) to map
        if name not in item_name_to_suid_list:
            item_name_to_suid_list[name] = []  # Initialize the key with an empty list if it doesn't exist.
        item_name_to_suid_list[name].append(suid)  # Add the suid to the list associated with the name.

    # Convert item names to SUIDs
    suid_list = []
    try:
        for item_name in item_names:
            if unique_list:
                suid_entry = item_name_to_suid_list[item_name].pop(0)
            else:
                suid_entry = item_name_to_suid_list[item_name]
                suid_entry = suid_entry[0] if len(suid_entry) == 1 else suid_entry 
                # return scalar if len(list) = 1, blow up if len(list) = 0
            suid_list.append(suid_entry)
    except:
        raise CyError(f'Invalid name in {table_name} name list: {item_names}')

    return suid_list

