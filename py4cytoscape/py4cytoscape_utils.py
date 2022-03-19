# -*- coding: utf-8 -*-

"""Utility functions useful across multiple modules.
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

import os

DEFAULT_BASE_URL = os.environ.get('DEFAULT_BASE_URL') or 'http://127.0.0.1:1234/v1'

# External library imports
import urllib.parse
import re
import sys

# Internal module imports
from . import tables
from . import cytoscape_system

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_logger import narrate

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
        raise CyError(f'"{bc}" is invalid. Value must be between -100 and 100).', caller=sys._getframe(1).f_code.co_name)

def verify_hex_color(color):
    """Validate and provide user feedback when hex color codes is required input.

    Args:
        colors (str): a single value, which is a 6 digit hex value

    Returns:
        None

    Raises:
        CyError: if color is invalid

    Examples:
        >>> verify_hex_color('#92C5DE')
    """
    if not color.startswith('#') or len(color) != 7:
        raise CyError(f'"{color}" is not a valid hexadecimal color (has to begin with # and be 7 characters long, for example: #FF00FF).', caller=sys._getframe(1).f_code.co_name)

def verify_hex_colors(colors):
    """Validate and provide user feedback when hex color codes (or a list of codes) are required input.

    Args:
        colors (str or list): a single value or a list of colors, which are 6 digit hex values

    Returns:
        None

    Raises:
        CyError: if color is invalid

    Examples:
        >>> verify_hex_colors('#92C5DE')
        >>> verify_hex_colors(['#053061', '#2166AC', '#4393C3', '#92C5DE', '#D1E5F0', '#F7F7F7', '#FDDBC7', '#F4A582', '#D6604D', '#B2182B', '#67001F'])
    """
    if colors is None: return
    if not isinstance(colors, list): colors = [colors]

    for color in colors:
        verify_hex_color(color)

def verify_opacity(opacity, max_opacity=100):
    """Validate and provide user feedback when opacity is required input.

    Args:
        opacity (int or float): a number between 0 and a max

    Returns:
        None

    Raises:
        CyError: if opacity is invalid

    Examples:
        >>> verify_opacity(77)
    """
    if not (isinstance(opacity, float) or isinstance(opacity, int)) or opacity < 0 or opacity > max_opacity:
        raise CyError(f'"{opacity}" is not a valid opacity (has to be an integer between 0 and {max_opacity}).', caller=sys._getframe(1).f_code.co_name)

def verify_opacities(opacities):
    """Validate and provide user feedback when opacity is required input.

    Args:
        opacities (int, float or list): a single value or a list of values, all of which are integers or floats

    Returns:
        None

    Raises:
        CyError: if opacity is invalid

    Examples:
        >>> verify_opacities(177)
        >>> verify_opacities([177, 200])
    """
    if opacities is None: return
    if not isinstance(opacities, list):  opacities = [opacities]

    for opacity in opacities:
        verify_opacity(opacity, max_opacity=255)

def verify_dimensions(dimension, sizes):
    """Validate and provide user feedback when dimensions is required input.

    Args:
        dimension (str): name of the sizes being examined (e.g., 'width')
        sizes (int, float or list): a single value or a list of values, all of which are integers or floats

    Returns:
        None

    Raises:
        CyError: if size is invalid

    Examples:
        >>> verify_dimensions('width', 50)
        >>> verify_dimensions('width', [10, 20])
    """
    if sizes is None: return
    if not isinstance(sizes, list): sizes = [sizes]

    for size in sizes:
        if not isinstance(size, float) and not isinstance(size, int):
            raise CyError(f'Illegal {dimension} "{size}". It needs to be a number.', caller=sys._getframe(1).f_code.co_name)

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
        raise CyError(f'{number} is invalid. Number must be greater than or equal to 0', caller=sys._getframe(1).f_code.co_name)

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
    if node_suids is None: return None
    node_suids = normalize_list(node_suids)

    df = tables.get_table_columns('node', ['name'], 'default', network, base_url=base_url)
    all_names = df['name'].values

    test_present = [x in all_names   for x in node_suids]
    if not False in test_present:
        return node_suids

    all_suids_list = df.index.tolist()
    try:
        # map all SUIDS into column names ... all SUIDs *must* be actual SUIDs
        node_names = [all_names[all_suids_list.index(node_suid)] for node_suid in node_suids]
        return node_names
    except Exception as e:
        raise CyError(f'Invalid node SUID in list: {node_suids}')


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
    if edge_suids is None: return None
    edge_suids = normalize_list(edge_suids)

    df = tables.get_table_columns('edge', ['name'], 'default', network, base_url=base_url)
    all_names = df['name'].values

    test = [edge_suid in all_names   for edge_suid in edge_suids]
    if not False in test: return edge_suids  # the list already had valid names

    all_suids_list = df.index.tolist()
    try:
        # map all SUIDS into column names ... all SUIDs *must* be actual SUIDs
        edge_names = [all_names[all_suids_list.index(edge_suid)]   for edge_suid in edge_suids]
        return edge_names
    except Exception as e:
        raise CyError(f'Invalid edge SUID in list: {edge_suids}')



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
def check_supported_versions(cyrest=1, cytoscape=3.6, base_url=DEFAULT_BASE_URL, caller=None):
    """Checks to see if min supported versions of api and cytoscape are running.

    Extracts numerics from api and major cytoscape versions before making comparison.

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
        >>> check__supported_versions(1, '3.10')
    """
    if isinstance(cytoscape, float): cytoscape = str(cytoscape)

    v = cytoscape_system.cytoscape_version_info(base_url=base_url)
    v_api_str = v['apiVersion']
    v_cy_str = v['cytoscapeVersion']
    v_api_num = int(re.match('v([0-9]+)$', v_api_str).group(1))
    nogo = None

    # Check the CyREST version
    if cyrest > v_api_num:
        nogo = 'CyREST API version %d or greater is required. You are currently working with version %d.' % (cyrest, v_api_num)

    # Check the Cytoscape version
    re_v_cytoscape = re.match('([0-9]+)\\.([0-9]+)\\..*$', v_cy_str)
    v_cytoscape_major = int(re_v_cytoscape.group(1))
    v_cytoscape_minor = int(re_v_cytoscape.group(2))

    re_cytoscape = re.match('([0-9]+)\\.([0-9]+)*$', cytoscape)
    required_cytoscape_major = int(re_cytoscape.group(1))
    required_cytoscape_minor = int(re_cytoscape.group(2))

    if required_cytoscape_major > v_cytoscape_major or (required_cytoscape_major == v_cytoscape_major and required_cytoscape_minor > v_cytoscape_minor):
        nogo = f'Cytoscape version {cytoscape} or greater is required. You are currently working with version {v_cy_str}.'

    return nogo

def verify_supported_versions(cyrest=1, cytoscape=3.6, base_url=DEFAULT_BASE_URL, caller=None):
    """Throws exception if min supported versions of api and cytoscape are not running.

    Extracts numerics from api and major cytoscape versions before making comparison.

    Args:
        cyrest (int): minimum CyREST version
        cytoscape (float or str): minimum Cytoscape version ... should be str if version > 3.9
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
         None

    Raises:
        CyError: if required version is greater than current version
        AttributeError: if required version can't be parsed

    Examples:
        >>> verify_supported_versions(1, 3.7)
        >>> verify_supported_versions(1, '3.10')
    """
    nogo = check_supported_versions(cyrest=cyrest, cytoscape=cytoscape, base_url=base_url)

    if nogo:
        if caller is None: caller = sys._getframe(1).f_code.co_name
        raise CyError(f'Function not run due to unsupported version: {nogo}', caller=caller)


def normalize_list(entity):
    # Return a Python list of strings given a Python list, a string list of strings, a string list of ints, or a scalar
    if isinstance(entity, str):  # If it's a string, it could be names, SUIDs, or whatever
        scalar_list = str.split(entity, ',')
        try:
            return [int(x)    for x in scalar_list] # for each entry, see if it's a number
        except:
            return [str.strip(x)   for x in scalar_list] # for each entry, get rid of leading/trialing spaces
    elif not isinstance(entity, list):  # If it's not a string, it could be int, int64 or whatever
        # Note that list could contain strings with leading/trailing spaces. Caller will likely think this is an error.
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
            cmd_list_normal = [f'{cmd}'   for cmd in cmd_list_normal]
        else:
            cmd_list_normal = [f'{cmd_by_col}:{cmd}' for cmd in cmd_list_normal]
        cmd_list_ready = ','.join(cmd_list_normal)

    return cmd_list_ready

def parse_edges(edge_list):
    # Convert edge list into list of parts: ["xxx (pp) yyy", "zzz (pp) aaa"] into [("xxx", "pp", "yyy"), ("zzz", "pp", "aaa")]

    def split_edge(edge):
        res = re.match('(.*) \((.*)\) (.*)', edge)
        return (res.group(1), res.group(2), res.group(3))

    return [split_edge(x)   for x in edge_list]


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
def normalize_mapping(mapping_type, visual_prop_name, supported_mappings):
    if mapping_type in ['continuous', 'c', 'interpolate']:
        mapping_type = 'c'
    elif mapping_type in ['discrete', 'd', 'lookup']:
        mapping_type = 'd'
    elif mapping_type in ['passthrough', 'p']:
        mapping_type = 'p'

    if mapping_type in supported_mappings:
        return mapping_type
    else:
        raise CyError(f'mapping_type "{mapping_type}" for property "{visual_prop_name}" not recognized ... must be "{supported_mappings}"')

def _item_to_suid(item_names, table_name, network=None, base_url=DEFAULT_BASE_URL, unique_list=False):
    # Translate a list of node or edge names into a list of SUIDs ... account for duplicatated names if list is unique
    if item_names is None: return None
    item_names = normalize_list(item_names)

    df = tables.get_table_columns(table_name, ['name'], 'default', network, base_url=base_url)

    # Check all item names to see if they're all valid SUIDs ... if so, we're already done
    all_suids = df.index
    try:
        item_names = [int(i) for i in item_names]
        found_valid_suids = [i in all_suids for i in item_names]
        if False not in found_valid_suids:
            return item_names
    except:
        pass

    # map all names into SUIDs ... all names *must* be actual names
    item_name_to_suid_list = {item_name: list(df[df.name.eq(item_name)].index.values) for item_name in item_names}
    try:
        if unique_list:
            suid_list = [item_name_to_suid_list[item_name].pop(0) for item_name in item_names]
        else:
            suid_list = [item_name_to_suid_list[item_name] for item_name in item_names]
            suid_list = [s[0] if len(s) <= 1 else s    for s in suid_list] # return scalar if len(list) = 1, blow up if len(list) = 0
    except:
        raise CyError(f'Invalid name in {table_name} name list: {item_names}')

    return suid_list















