# -*- coding: utf-8 -*-

"""Functions for defining MAPPINGS between table column values and visual properties, organized into sections:

I. General functions for creating and applying mappings for node, edge and network properties
II. Specific functions for defining particular node, edge and network properties

See style_auto_mappings for automatic mapping generation
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

# Internal module imports
from . import networks
from . import commands
from . import styles
from . import style_defaults
from . import style_dependencies

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log
from .py4cytoscape_tuning import MODEL_PROPAGATION_SECS


# ==============================================================================
# I. General Functions
# ------------------------------------------------------------------------------

# TODO: R seems to allow table_column_value, visual_prop_values to be unspecified ... Python does this with optional parameters
@cy_log
def map_visual_property(visual_prop, table_column, mapping_type, table_column_values=[],
                        visual_prop_values=[], network=None, base_url=DEFAULT_BASE_URL):
    """Create a mapping between an attribute and a visual property.

    Generates the appropriate data structure for the "mapping" parameter in ``update_style_mapping()``.

    The paired list of values must be of the same length or mapping will fail. For gradient mapping,
    you may include two additional ``visual_prop_values`` in the first and last positions to map respectively
    to values less than and greater than those specified in ``table_column_values``. Mapping will also fail if the
    data type of ``table_column_values`` does not match that of the existing ``table_column``. Note that all imported
    numeric data are stored as Integers or Doubles in Cytosacpe tables; and character or mixed data are
    stored as Strings.

    Args:
        visual_prop (str): name of visual property to map
        table_column (str): name of table column to map
        mapping_type (str): continuous, discrete or passthrough (c,d,p)
        table_column_values (list): list of values paired with ``visual_prop_values``; skip for passthrough mapping
        visual_prop_values (list): list of values paired with ``table_column_values``; skip for passthrough mapping
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'mappingType': type of mapping, 'mappingColumn': column to map, 'mappingColumnType': column data type, 'visualProperty': name of property, cargo}

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> map_visual_property('node fill color', 'gal1RGexp', 'c', [-2.426, 0.0, 2.058], ['#0066CC', '#FFFFFF','#FFFF00'])
        {'mappingType': 'continuous', 'mappingColumn': 'gal1RGexp', 'mappingColumnType': 'Double', 'visualProperty': 'NODE_FILL_COLOR', 'points': [{'value': -2.426, 'lesser': '#0066CC', 'equal': '#0066CC', 'greater': '#0066CC'}, {'value': 0.0, 'lesser': '#FFFFFF', 'equal': '#FFFFFF', 'greater': '#FFFFFF'}, {'value': 2.058, 'lesser': '#FFFF00', 'equal': '#FFFF00', 'greater': '#FFFF00'}]}
        >>> map_visual_property('node shape', 'degree.layout', 'd', [1, 2], ['ellipse', 'rectangle'])
        {'mappingType': 'discrete', 'mappingColumn': 'degree.layout', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_SHAPE', 'map': [{'key': 1, 'value': 'ellipse'}, {'key': 2, 'value': 'rectangle'}]}
        >>> map_visual_property('node label', 'COMMON', 'p')
        {'mappingType': 'passthrough', 'mappingColumn': 'COMMON', 'mappingColumnType': 'String', 'visualProperty': 'NODE_LABEL'}

    Note:
        For the return value, ``mapping type`` can be 'continuous', 'discrete' or 'passthrough'. For the
        ``mappingColumn``, the name of the column. For the ``mappingColumnType``, the Cytoscape data type (Double,
        Integer, String, Boolean). For the ``visualProperty``, the canonical name of the visual property. The ``cargo``
        depends on the ``mapping type``. For 'continuous', it's a list of way points as 'points': [waypoint, waypoint, ...]
        where a waypoint is {'value': a Double, 'lesser': a color, 'equal': a color, 'greater': a color}. For 'discrete',
        it's a list of mappings as 'map': [key-value, key-value, ...] where a key-value is {'key': column data value,
        'value': value appropriate for ``visualProperty``}.

    See Also:
        :meth:`update_style_mapping`, :meth:`get_visual_property_names`
    """
    MAPPING_TYPES = {'c': 'continuous', 'd': 'discrete', 'p': 'passthrough'}
    PROPERTY_NAMES = {'EDGE_COLOR': 'EDGE_UNSELECTED_PAINT', 'EDGE_THICKNESS': 'EDGE_WIDTH',
                      'NODE_BORDER_COLOR': 'NODE_BORDER_PAINT', 'NODE_BORDER_LINE_TYPE': 'NODE_BORDER_STROKE'}

    suid = networks.get_network_suid(network, base_url=base_url)

    # process mapping type
    mapping_type_name = MAPPING_TYPES[mapping_type] if mapping_type in MAPPING_TYPES else mapping_type

    # process visual property, including common alternatives for vp names :)
    visual_prop_name = re.sub('\\s+', '_', visual_prop).upper()
    if visual_prop_name in PROPERTY_NAMES: visual_prop_name = PROPERTY_NAMES[visual_prop_name]

    # check visual prop name
    if visual_prop_name not in styles.get_visual_property_names(base_url=base_url):
        raise CyError(
            f'Could not find visual property "{visual_prop_name}". For valid ones, check get_visual_property_names().')

    # check mapping column and get type
    tp = visual_prop_name.split('_')[0].lower()
    table = 'default' + tp
    res = commands.cyrest_get('networks/' + str(suid) + '/tables/' + table + '/columns', base_url=base_url)
    table_column_type = None
    for col in res:
        if col['name'] == table_column:
            table_column_type = col['type']
            break
    if table_column_type is None:
        raise CyError(f'Could not find "{table_column}" column in "{table}" table.')

    # construct visual property map
    visual_prop_map = {'mappingType': mapping_type_name, 'mappingColumn': table_column,
                       'mappingColumnType': table_column_type, 'visualProperty': visual_prop_name}
    if mapping_type_name == 'discrete':
        visual_prop_map['map'] = [{'key': col_val, 'value': prop_val} for col_val, prop_val in
                                  zip(table_column_values, visual_prop_values)]
    elif mapping_type_name == 'continuous':
        # check for extra lesser and greater values
        prop_val_count = len(visual_prop_values)
        col_val_count = len(table_column_values)
        if prop_val_count - col_val_count == 2:
            matched_visual_prop_values = visual_prop_values[1:]
            points = [{'value': col_val, 'lesser': prop_val, 'equal': prop_val, 'greater': prop_val} for
                      col_val, prop_val in zip(table_column_values, matched_visual_prop_values)]

            # then correct extreme values
            points[0]['lesser'] = visual_prop_values[0]
            points[col_val_count - 1]['greater'] = visual_prop_values[-1]
        elif prop_val_count - col_val_count == 0:
            points = [{'value': col_val, 'lesser': prop_val, 'equal': prop_val, 'greater': prop_val} for
                      col_val, prop_val in zip(table_column_values, visual_prop_values)]
        else:
            raise CyError(f'table_column_values "{table_column_values}" and visual_prop_values "{visual_prop_values}" don\'t match up.')

        visual_prop_map['points'] = points

    return visual_prop_map


@cy_log
def update_style_mapping(style_name, mapping, base_url=DEFAULT_BASE_URL):
    """Update a visual property mapping in a style.

    Updates the visual property mapping, overriding any prior mapping. Creates a visual property mapping if it doesn't
    already exist in the style. Requires visual property mappings to be previously created, see ``map_visual_property()``.

    Args:
        style_name (str): name for style
        mapping (dict): a single visual property mapping, see ``map_visual_property()``
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if style doesn't exist
        TypeError: if mapping isn't a visual property mapping
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> update_style_mapping('galFiltered Style', map_visual_property('node label', 'name', 'p'))
        ''

    See Also:
        :meth:`map_visual_property`
    """
    visual_prop_name = mapping['visualProperty']

    if style_name is None:
        style_name = 'default'
        narrate(f'style_name not specified, so updating "default" style.')

    # check if vp exists already
    res = commands.cyrest_get(f'styles/{style_name}/mappings', base_url=base_url)
    vp_list = [prop['visualProperty'] for prop in res]
    exists = visual_prop_name in vp_list

    if exists:
        res = commands.cyrest_put(f'styles/{style_name}/mappings/{visual_prop_name}', body=[mapping],
                                  base_url=base_url, require_json=False)
    else:
        res = commands.cyrest_post(f'styles/{style_name}/mappings', body=[mapping], base_url=base_url,
                                   require_json=False)
    time.sleep(
        MODEL_PROPAGATION_SECS)  # wait for attributes to be applied ... it looks like Cytoscape returns before this is complete [Cytoscape BUG]
    return res


# TODO: Note that R documentation for this is wrong ... we really do want a property name, not a map
@cy_log
def delete_style_mapping(style_name, visual_prop, base_url=DEFAULT_BASE_URL):
    """Delete a specified visual style mapping from specified style.

    Args:
        style_name (str): name for style
        visual_prop (str): name of visual property to delete
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str or None: '' or None (if property doesn't exist)

    Raises:
        CyError: if style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> delete_style_mapping('galFiltered Style', 'node label')
        ''
    """
    # check if vp exists already
    res = commands.cyrest_get(f'styles/{style_name}/mappings', base_url=base_url)
    vp_list = [prop['visualProperty'] for prop in res]
    exists = visual_prop in vp_list

    if exists:
        res = commands.cyrest_delete(f'styles/{style_name}/mappings/{visual_prop}',
                                     base_url=base_url, require_json=False)
    else:
        res = None
    return res


# TODO: Verify that it's OK to return None if the style doesn't exist ... maybe should be a CyError?

# TODO: Are we missing a get_style_mapping here?? ... probably ... I'm adding one to help with testing ...
@cy_log
def get_style_mapping(style_name, visual_prop, base_url=DEFAULT_BASE_URL):
    """Fetch a visual property mapping in a style.

    The property mapping is the same as a dict created by ``map_visual_property()``.

    Args:
        style_name (str): name for style
        visual_prop (str): the name of the visual property
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: see ``map_visual_property()``

    Raises:
        CyError: if style or property name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_style_mapping('galFiltered Style', 'node label')
        {"mappingType": "passthrough", "mappingColumn": "COMMON", "mappingColumnType": "String", "visualProperty": "NODE_LABEL"}

    See Also:
        :meth:`map_visual_property`
    """
    if style_name is None:
        style_name = 'default'
        narrate(f'style_name not specified, so accessing "default" style.')

    # check if vp exists already
    res = commands.cyrest_get(f'styles/{style_name}/mappings', base_url=base_url)
    for prop in res:
        if prop['visualProperty'] == visual_prop:
            return prop
    raise CyError(f'Property "{visual_prop}" does not exist in style "{style_name}"')


# TODO: Are we missing a get_style_all_mappings here?? ... probably ... I'm adding one to help with testing ...
@cy_log
def get_style_all_mappings(style_name, base_url=DEFAULT_BASE_URL):
    """Fetch all visual property mapping in a style.

    The property mappings are the same as a dict created by ``map_visual_property()``.

    Args:
        style_name (str): name for style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: list of dicts of the type created by ``map_visual_property()``

    Raises:
        CyError: if style or property name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_style_all_mappings('galFiltered Style')
        [{"mappingType": "passthrough", "mappingColumn": "name", "mappingColumnType": "String", "visualProperty": "NODE_LABEL"},
         {"mappingType": "passthrough", "mappingColumn": "interaction", "mappingColumnType": "String", "visualProperty": "EDGE_LABEL"}]

    See Also:
        :meth:`map_visual_property`
    """
    if style_name is None:
        style_name = 'default'
        narrate(f'style_name not specified, so accessing "default" style.')

    res = commands.cyrest_get(f'styles/{style_name}/mappings', base_url=base_url)
    return res


# ==============================================================================
# II. Specific Functions
# ==============================================================================
# II.a. Node Properties
# Pattern: (1) prepare map_visual_property, (2) call update_style_mapping()
# ------------------------------------------------------------------------------

# TODO: R documented colors list incorrectly
@cy_log
def set_node_border_color_mapping(table_column, table_column_values=None, colors=None, mapping_type='c',
                                  default_color=None, style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Map table column values to colors to set the node border color.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        colors (list): list of hex colors
        mapping_type (str): continuous, discrete or passthrough (c,d,p); default is continuous
        default_color (str): Hex color to set as default
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if invalid color, table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_border_color_mapping('AverageShortestPathLength', [1.0, 16.36], ['#FBE723', '#440256'], style_name='galFiltered Style')
        ''
        >>> set_node_border_color_mapping('Degree', ['1', '2'], ['#FFFF00', '#00FF00'], 'd', style_name='galFiltered Style')
        ''
        >>> set_node_border_color_mapping(**gen_node_color_map('Degree', mapping_type='d'))
        ''
        >>> set_node_border_color_mapping(**gen_node_color_map('Degree', palette_color_brewer_q_Accent(), mapping_type='d'))
        ''
        >>> set_node_border_color_mapping(**gen_node_color_map('AverageShortestPathLength'))
        ''
        >>> set_node_border_color_mapping(**gen_node_color_map('AverageShortestPathLength', palette_color_brewer_s_Blues()))
        ''
        >>> set_node_border_color_mapping(**gen_node_color_map('AverageShortestPathLength', (palette_color_brewer_s_Blues(), palette_color_brewer_d_BrBG()))
        ''
        >>> set_node_border_color_mapping('ColorCol', mapping_type='p', default_color='#654321', style_name='galFiltered Style')
        ''

    See Also:
        :meth:`gen_node_color_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    verify_hex_colors(colors)

    # set default
    if default_color is not None:
        style_defaults.set_node_border_color_default(default_color, style_name, base_url=base_url)
    # TODO: An error here will be missed ... shouldn't this throw an exception?

    return _update_visual_property('NODE_BORDER_PAINT', table_column, table_column_values=table_column_values,
                                   range_map=colors, mapping_type=mapping_type, style_name=style_name, network=network,
                                   base_url=base_url)


@cy_log
def set_node_border_opacity_mapping(table_column, table_column_values=None, opacities=None, mapping_type='c',
                                    default_opacity=None, style_name=None, network=None,
                                    base_url=DEFAULT_BASE_URL):
    """Set opacity for node border only.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        opacities (list): int values between 0 and 255; 0 is invisible
        mapping_type (str): continuous, discrete or passthrough (c,d,p); default is continuous
        default_opacity (int): Opacity value to set as default for all unmapped values
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type, or if invalid opacity
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_border_opacity_mapping('AverageShortestPathLength', table_column_values=[1.0, 16.36], opacities=[50, 100], style_name='galFiltered Style')
        ''
        >>> set_node_border_opacity_mapping('Degree', table_column_values=['1', '2'], opacities=[50, 100], mapping_type='d', style_name='galFiltered Style')
        ''
        >>> set_node_border_opacity_mapping(**gen_node_opacity_map('Degree', mapping_type='d'))
        ''
        >>> set_node_border_opacity_mapping(**gen_node_opacity_map('AverageShortestPathLength', scheme_c_number_continuous(100, 200), style_name='galFiltered Style'))
        ''
        >>> set_node_border_opacity_mapping('PassthruCol', mapping_type='p', default_opacity=225, style_name='galFiltered Style')
        ''

    See Also:
        :meth:`gen_node_opacity_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    # TODO: Moved check to _update_style_mapping
    #    if not table_column_exists(table_column, 'node', network=network, base_url=base_url):
    #        raise CyError(f'Table column "{table_column}" does not exist')

    verify_opacities(opacities)

    # TODO: there is a set_node_border_opacity_default() ... shouldn't we be using that instead?
    if default_opacity is not None:
        verify_opacities(default_opacity)

        style_defaults.set_visual_property_default(
            {'visualProperty': 'NODE_BORDER_TRANSPARENCY', 'value': str(default_opacity)},
            style_name=style_name, base_url=base_url)

    return _update_visual_property('NODE_BORDER_TRANSPARENCY', table_column, table_column_values=table_column_values,
                                   range_map=opacities, mapping_type=mapping_type, style_name=style_name,
                                   network=network, base_url=base_url)


@cy_log
def set_node_border_width_mapping(table_column, table_column_values=None, widths=None, mapping_type='c',
                                  default_width=None, style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Map table column values to widths to set the node border width.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        widths (list): List of width values to map to ``table_column_values``
        mapping_type (str): continuous, discrete or passthrough (c,d,p); default is continuous
        default_width (int): Width value to set as default for all unmapped values
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type, or if invalid width
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_border_width_mapping('AverageShortestPathLength', table_column_values=[1.0, 16.36], widths=[5, 10], style_name='galFiltered Style')
        ''
        >>> set_node_border_width_mapping('Degree', table_column_values=['1', '2'], widths=[5, 10], mapping_type='d', style_name='galFiltered Style')
        ''
        >>> set_node_border_width_mapping(**gen_node_width_map('Degree', mapping_type='d'))
        ''
        >>> set_node_border_width_mapping(**gen_node_width_map('AverageShortestPathLength', scheme_c_number_continuous(100, 200), style_name='galFiltered Style'))
        ''
        >>> set_node_border_width_mapping('PassthruCol', mapping_type='p', default_width=3, style_name='galFiltered Style')
        ''

    See Also:
        :meth:`gen_node_width_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    verify_dimensions('width', widths)

    # set default
    if default_width is not None:
        style_defaults.set_node_border_width_default(default_width, style_name, base_url=base_url)

    return _update_visual_property('NODE_BORDER_WIDTH', table_column, table_column_values=table_column_values,
                                   range_map=widths, mapping_type=mapping_type, style_name=style_name, network=network,
                                   base_url=base_url)


@cy_log
def set_node_color_mapping(table_column, table_column_values=None, colors=None, mapping_type='c', default_color=None,
                           style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Map table column values to colors to set the node fill color.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        colors (list): list of hex colors to map to ``table_column_values``
        mapping_type (str): continuous, discrete or passthrough (c,d,p); default is continuous
        default_color (str): Hex color to set as default
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if invalid color, table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_color_mapping('AverageShortestPathLength', [1.0, 16.36], ['#FBE723', '#440256'], style_name='galFiltered Style')
        ''
        >>> set_node_color_mapping('Degree', ['1', '2'], ['#FFFF00', '#00FF00'], 'd', style_name='galFiltered Style')
        ''
        >>> set_node_color_mapping(**gen_node_color_map('Degree', mapping_type='d'))
        ''
        >>> set_node_color_mapping(**gen_node_color_map('Degree', palette_color_brewer_q_Accent(), mapping_type='d'))
        ''
        >>> set_node_color_mapping(**gen_node_color_map('AverageShortestPathLength'))
        ''
        >>> set_node_color_mapping(**gen_node_color_map('AverageShortestPathLength', palette_color_brewer_s_Blues()))
        ''
        >>> set_node_color_mapping(**gen_node_color_map('AverageShortestPathLength', (palette_color_brewer_s_Blues(), palette_color_brewer_d_BrBG()))
        ''
        >>> set_node_color_mapping('ColorCol', mapping_type='p', default_color='#654321', style_name='galFiltered Style')
        ''

    See Also:
        :meth:`gen_node_color_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    # TODO: Moved to _update_style_mapping
    #    if not table_column_exists(table_column, 'node', network=network, base_url=base_url):
    #        raise CyError(f'Table column "{table_column}" does not exist')

    # check if colors are formatted correctly
    verify_hex_colors(colors)

    # set default
    if default_color is not None:
        style_defaults.set_node_color_default(default_color, style_name, base_url=base_url)
    # TODO: An error here will be missed ... shouldn't this throw an exception?

    return _update_visual_property('NODE_FILL_COLOR', table_column, table_column_values=table_column_values,
                                   range_map=colors, mapping_type=mapping_type, style_name=style_name, network=network,
                                   base_url=base_url)


@cy_log
def set_node_combo_opacity_mapping(table_column, table_column_values=None, opacities=None, mapping_type='c',
                                   default_opacity=None, style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Set opacity for node fill, border and label all together.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        opacities (list): int values between 0 and 255; 0 is invisible
        mapping_type (str): continuous, discrete or passthrough (c,d,p); default is continuous
        default_opacity (int): Opacity value to set as default for all unmapped values
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type, or if invalid opacity
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_combo_opacity_mapping('AverageShortestPathLength', table_column_values=[1.0, 16.36], opacities=[50, 100], style_name='galFiltered Style')
        ''
        >>> set_node_combo_opacity_mapping('Degree', table_column_values=['1', '2'], opacities=[50, 100], mapping_type='d', style_name='galFiltered Style')
        ''
        >>> set_node_combo_opacity_mapping(**gen_node_opacity_map('Degree', mapping_type='d'))
        ''
        >>> set_node_combo_opacity_mapping(**gen_node_opacity_map('AverageShortestPathLength', scheme_c_number_continuous(100, 200), style_name='galFiltered Style'))
        ''
        >>> set_node_combo_opacity_mapping('PassthruCol', mapping_type='p', default_opacity=225, style_name='galFiltered Style')
        ''

    See Also:
        :meth:`gen_node_opacity_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    verify_opacities(opacities)

    if default_opacity is not None:
        verify_opacities(default_opacity)

        style_defaults.set_visual_property_default(
            {'visualProperty': 'NODE_TRANSPARENCY', 'value': str(default_opacity)},
            style_name=style_name, base_url=base_url)
        style_defaults.set_visual_property_default(
            {'visualProperty': 'NODE_BORDER_TRANSPARENCY', 'value': str(default_opacity)},
            style_name=style_name, base_url=base_url)
        style_defaults.set_visual_property_default(
            {'visualProperty': 'NODE_LABEL_TRANSPARENCY', 'value': str(default_opacity)},
            style_name=style_name, base_url=base_url)

    # TODO: function results are ignored ... shouldn't we be capturing them?
    _update_visual_property('NODE_TRANSPARENCY', table_column, table_column_values=table_column_values,
                            range_map=opacities, mapping_type=mapping_type, style_name=style_name, network=network,
                            base_url=base_url)
    _update_visual_property('NODE_BORDER_TRANSPARENCY', table_column, table_column_values=table_column_values,
                            range_map=opacities, mapping_type=mapping_type, style_name=style_name, network=network,
                            base_url=base_url)
    res = _update_visual_property('NODE_LABEL_TRANSPARENCY', table_column, table_column_values=table_column_values,
                                  range_map=opacities, mapping_type=mapping_type, style_name=style_name,
                                  network=network, base_url=base_url)
    return res


@cy_log
def set_node_fill_opacity_mapping(table_column, table_column_values=None, opacities=None, mapping_type='c',
                                  default_opacity=None, style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Set opacity for node fill only.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        opacities (list): int values between 0 and 255; 0 is invisible
        mapping_type (str): continuous, discrete or passthrough (c,d,p); default is continuous
        default_opacity (int): Opacity value to set as default for all unmapped values
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type, or if invalid opacity
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_fill_opacity_mapping('AverageShortestPathLength', table_column_values=[1.0, 16.36], opacities=[50, 100], style_name='galFiltered Style')
        ''
        >>> set_node_fill_opacity_mapping('Degree', table_column_values=['1', '2'], opacities=[50, 100], mapping_type='d', style_name='galFiltered Style')
        ''
        >>> set_node_fill_opacity_mapping(**gen_node_opacity_map('Degree', mapping_type='d'))
        ''
        >>> set_node_fill_opacity_mapping(**gen_node_opacity_map('AverageShortestPathLength', scheme_c_number_continuous(100, 200), style_name='galFiltered Style'))
        ''
        >>> set_node_fill_opacity_mapping('PassthruCol', mapping_type='p', default_opacity=225, style_name='galFiltered Style')
        ''

    See Also:
        :meth:`gen_node_opacity_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    # TODO: Moved to _update_style_mapping
    #    if not table_column_exists(table_column, 'node', network=network, base_url=base_url):
    #        raise CyError(f'Table column "{table_column}" does not exist')

    verify_opacities(opacities)

    # TODO: There is a set_node_fill_opacity_default() ... should that be called instead?
    if default_opacity is not None:
        verify_opacities(default_opacity)

        style_defaults.set_visual_property_default(
            {'visualProperty': 'NODE_TRANSPARENCY', 'value': str(default_opacity)},
            style_name=style_name, base_url=base_url)

    return _update_visual_property('NODE_TRANSPARENCY', table_column, table_column_values=table_column_values,
                                   range_map=opacities, mapping_type=mapping_type, style_name=style_name,
                                   network=network, base_url=base_url)


@cy_log
def set_node_font_face_mapping(table_column, table_column_values=None, fonts=None, mapping_type='d', default_font=None,
                               style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Sets font face for node labels.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        fonts (list): List of string specifications of font face, style and size, e.g., ["SansSerif,plain,12", "Dialog,plain,10"]
        mapping_type (str): discrete or passthrough (d,p); default is discrete
        default_font (str): String specification of font face, style and size, e.g., "SansSerif,plain,12" or "Dialog,plain,10"
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_font_face_mapping('Degree', table_column_values=['1', '2'], fonts=['Arial,plain,12', 'Arial Bold,bold,12'], mapping_type='d', style_name='galFiltered Style')
        ''
        >>> set_node_font_face_mapping('PassthruCol', mapping_type='p', default_font='Arial,plain,12', style_name='galFiltered Style')
        ''
    """
    # TODO: moved to _update_style_mapping
    # TODO: R documentation examples look wrong ... check this out
    #    if not table_column_exists(table_column, 'node', network=network, base_url=base_url):
    #        raise CyError(f'Table column "{table_column}" does not exist')

    if default_font is not None:
        style_defaults.set_node_font_face_default(default_font, style_name=style_name, base_url=base_url)

    return _update_visual_property('NODE_LABEL_FONT_FACE', table_column, table_column_values=table_column_values,
                                   range_map=fonts, mapping_type=mapping_type, style_name=style_name, network=network,
                                   base_url=base_url, supported_mappings=['d', 'p'])


def set_node_font_size_mapping(table_column, table_column_values=None, sizes=None, mapping_type='c', default_size=None,
                               style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Map table column values to sizes to set the node size.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        sizes (list): List of size values to map to ``table_column_values``
        mapping_type (str): discrete or passthrough (d,p); default is discrete
        default_size (int): Size value to set as default
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type, or if invalid size
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_font_size_mapping('AverageShortestPathLength', table_column_values=[1.0, 16.36], sizes=[20, 80], style_name='galFiltered Style')
        ''
        >>> set_node_font_size_mapping('Degree', table_column_values=['1', '2'], sizes=[40, 90], mapping_type='d', style_name='galFiltered Style')
        ''
        >>> set_node_font_size_mapping(**gen_node_size_map('Degree', mapping_type='d'))
        ''
        >>> set_node_font_size_mapping(**gen_node_size_map('AverageShortestPathLength', scheme_c_number_continuous(100, 200), style_name='galFiltered Style'))
        ''
        >>> set_node_font_size_mapping('PassthruCol', mapping_type='p', default_size=20, style_name='galFiltered Style')
        ''

    See Also:
        :meth:`gen_node_size_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    verify_dimensions('size', sizes)

    if default_size is not None:
        style_defaults.set_node_font_size_default(default_size, style_name=style_name, base_url=base_url)

    return _update_visual_property('NODE_LABEL_FONT_SIZE', table_column, table_column_values=table_column_values,
                                   range_map=sizes, mapping_type=mapping_type,
                                   style_name=style_name, network=network, base_url=base_url)


@cy_log
def set_node_height_mapping(table_column, table_column_values=None, heights=None, mapping_type='c', default_height=None,
                            style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Map table column values to the node heights.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        heights (list): List of height values to map to ``table_column_values``
        mapping_type (str): discrete or passthrough (d,p); default is discrete
        default_height (int): Height value to set as default
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type, or if invalid height
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_height_mapping('AverageShortestPathLength', table_column_values=[1.0, 16.36], sizes=[120, 180], style_name='galFiltered Style')
        ''
        >>> set_node_height_mapping('Degree', table_column_values=['1', '2'], sizes=[140, 190], mapping_type='d', style_name='galFiltered Style')
        ''
        >>> set_node_height_mapping(**gen_node_height_map('Degree', mapping_type='d'))
        ''
        >>> set_node_height_mapping(**gen_node_height_map('AverageShortestPathLength', scheme_c_number_continuous(100, 200), style_name='galFiltered Style'))
        ''
        >>> set_node_height_mapping('PassthruCol', mapping_type='p', default_size=120, style_name='galFiltered Style')
        ''

    See Also:
        :meth:`gen_node_height_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    verify_dimensions('height', heights)

    if default_height is not None:
        style_defaults.set_node_height_default(default_height, style_name=style_name, base_url=base_url)

    # TODO: Added this because otherwise, could not set mapping ... the PUT failed silently. Shouldn't we be restoring to its original setting? Same with set_default_node_height?
    style_dependencies.lock_node_dimensions(False, style_name=style_name, base_url=base_url)

    return _update_visual_property('NODE_HEIGHT', table_column, table_column_values=table_column_values,
                                   range_map=heights, mapping_type=mapping_type,
                                   style_name=style_name, network=network, base_url=base_url)


@cy_log
def set_node_label_mapping(table_column, style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Pass the values from a table column to display as node labels.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str or None: '' if successful or None if error

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_label_mapping('name', style_name='galFiltered Style')
        ''
        >>> set_node_label_mapping('name')
        ''
    """
    # TODO: The return value in the R code is None ... probably should be throwing an exception, which I'm doing
    if not table_column_exists(table_column, 'node', network=network, base_url=base_url):
        raise CyError(f'Table column "{table_column}" does not exist')

    # TODO: Should there be the ability to set the node label default here? The call exists in styles_defaults

    mvp = map_visual_property('NODE_LABEL', table_column, 'p', network=network, base_url=base_url)

    res = update_style_mapping(style_name, mvp, base_url=base_url)
    return res


@cy_log
def set_node_label_color_mapping(table_column, table_column_values=None, colors=None, mapping_type='c',
                                 default_color=None, style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Map table column values to colors to set the node border color.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        colors (list): values between 0 and 255; 0 is invisible
        mapping_type (str): discrete or passthrough (d,p); default is discrete
        default_color (str): Hex color to set as default
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if invalid color, table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_label_color_mapping('AverageShortestPathLength', [1.0, 16.36], ['#FBE723', '#440256'], style_name='galFiltered Style')
        ''
        >>> set_node_label_color_mapping('Degree', ['1', '2'], ['#FFFF00', '#00FF00'], 'd', style_name='galFiltered Style')
        ''
        >>> set_node_label_color_mapping(**gen_node_color_map('Degree', mapping_type='d'))
        ''
        >>> set_node_label_color_mapping(**gen_node_color_map('Degree', palette_color_brewer_q_Accent(), mapping_type='d'))
        ''
        >>> set_node_label_color_mapping(**gen_node_color_map('AverageShortestPathLength'))
        ''
        >>> set_node_label_color_mapping(**gen_node_color_map('AverageShortestPathLength', palette_color_brewer_s_Blues()))
        ''
        >>> set_node_label_color_mapping(**gen_node_color_map('AverageShortestPathLength', (palette_color_brewer_s_Blues(), palette_color_brewer_d_BrBG()))
        ''
        >>> set_node_label_color_mapping('ColorCol', mapping_type='p', default_color='#654321', style_name='galFiltered Style')
        ''

    See Also:
        :meth:`gen_node_color_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    verify_hex_colors(colors)

    # set default
    if default_color is not None:
        style_defaults.set_node_label_color_default(default_color, style_name, base_url=base_url)
    # TODO: An error here will be missed ... shouldn't this throw an exception?

    return _update_visual_property('NODE_LABEL_COLOR', table_column, table_column_values=table_column_values,
                                   range_map=colors, mapping_type=mapping_type,
                                   style_name=style_name, network=network, base_url=base_url)


@cy_log
def set_node_label_opacity_mapping(table_column, table_column_values=None, opacities=None, mapping_type='c',
                                   default_opacity=None, style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Sets opacity for node label only.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        opacities (list): int values between 0 and 255; 0 is invisible
        mapping_type (str): continuous, discrete or passthrough (c,d,p); default is continuous
        default_opacity (int): Opacity value to set as default for all unmapped values
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type, or if invalid opacity
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_label_opacity_mapping('AverageShortestPathLength', table_column_values=[1.0, 16.36], opacities=[50, 100], style_name='galFiltered Style')
        ''
        >>> set_node_label_opacity_mapping('Degree', table_column_values=['1', '2'], opacities=[50, 100], mapping_type='d', style_name='galFiltered Style')
        ''
        >>> set_node_label_opacity_mapping(**gen_node_opacity_map('Degree', mapping_type='d'))
        ''
        >>> set_node_label_opacity_mapping(**gen_node_opacity_map('AverageShortestPathLength', scheme_c_number_continuous(100, 200), style_name='galFiltered Style'))
        ''
        >>> set_node_label_opacity_mapping('PassthruCol', mapping_type='p', default_opacity=225, style_name='galFiltered Style')
        ''

    See Also:
        :meth:`gen_node_opacity_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    # TODO: Moved check to _update_style_mapping
    #    if not table_column_exists(table_column, 'node', network=network, base_url=base_url):
    #        raise CyError(f'Table column "{table_column}" does not exist')

    verify_opacities(opacities)

    # TODO: There is a set_node_label_opacity_default ... should that be called here?
    if default_opacity is not None:
        verify_opacities(default_opacity)

        style_defaults.set_visual_property_default(
            {'visualProperty': 'NODE_LABEL_TRANSPARENCY', 'value': str(default_opacity)},
            style_name=style_name, base_url=base_url)

    return _update_visual_property('NODE_LABEL_TRANSPARENCY', table_column, table_column_values=table_column_values,
                                   range_map=opacities, mapping_type=mapping_type, style_name=style_name,
                                   network=network, base_url=base_url)


@cy_log
def set_node_shape_mapping(table_column, table_column_values=None, shapes=None, default_shape=None,
                           style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Map table column values to shapes to set the node shape.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        shapes (list): List of shapes to map to ``table_column_values``. See ``get_node_shapes()``
        default_shape (str): Shape to set as default. See ``get_node_shapes()``
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_shape_mapping('Degree', table_column_values=['1', '2'], shapes=['TRIANGLE', 'OCTAGON'], default_shape='ELLIPSE', style_name='galFiltered Style')
        ''
        >>> set_node_shape_mapping(**gen_node_shape_map('Degree', style_name='galFiltered Style'))
        ''

    See Also:
        :meth:`gen_node_shape_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    # TODO: Verify shapes

    if default_shape is not None:
        style_defaults.set_node_shape_default(default_shape, style_name, base_url=base_url)

    return _update_visual_property('NODE_SHAPE', table_column, table_column_values=table_column_values,
                                   range_map=shapes, mapping_type='d', style_name=style_name, network=network,
                                   base_url=base_url, supported_mappings=['d'])


# TODO: R documentation claims this is about font sizes
@cy_log
def set_node_size_mapping(table_column, table_column_values=None, sizes=None, mapping_type='c', default_size=None,
                          style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Map table column values to node sizes.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        sizes (list): List of sizes of nodes
        mapping_type (str): continuous, discrete or passthrough (c,d,p); default is continuous
        default_size (int): Size value to set as default
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type, or if invalid size
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_size_mapping('AverageShortestPathLength', table_column_values=[1.0, 16.36], sizes=[60, 100], style_name='galFiltered Style')
        ''
        >>> set_node_size_mapping('Degree', table_column_values=['1', '2'], sizes=[60, 100], mapping_type='d', style_name='galFiltered Style')
        ''
        >>> set_node_size_mapping(**gen_node_size_map('Degree', mapping_type='d'))
        ''
        >>> set_node_size_mapping(**gen_node_size_map('AverageShortestPathLength', scheme_c_number_continuous(100, 200), style_name='galFiltered Style'))
        ''
        >>> set_node_size_mapping('PassthruCol', mapping_type='p', default_opacity=40, style_name='galFiltered Style')
        ''

    See Also:
        :meth:`gen_node_size_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    verify_dimensions('size', sizes)

    # set default
    if default_size is not None:
        style_defaults.set_node_size_default(default_size, style_name, base_url=base_url)

    # TODO: Added this because otherwise, could not set mapping ... the PUT failed silently. Shouldn't we be restoring to its original setting? Same with set_default_node_height?
    style_dependencies.lock_node_dimensions(True, style_name=style_name, base_url=base_url)

    return _update_visual_property('NODE_SIZE', table_column, table_column_values=table_column_values, range_map=sizes,
                                   mapping_type=mapping_type, style_name=style_name, network=network, base_url=base_url)


@cy_log
def set_node_tooltip_mapping(table_column, style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Pass the values from a table column to display as node tooltips.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_tooltip_mapping('PassthruCol', style_name='galFiltered Style')
        ''
    """
    # TODO: The return value in the R code is None ... probably should be throwing an exception, which I'm doing
    if not table_column_exists(table_column, 'node', network=network, base_url=base_url):
        raise CyError(f'Table column "{table_column}" does not exist')

    # TODO: There is a set_node_tooltip_default function ... should there be a default value here??

    mvp = map_visual_property('NODE_TOOLTIP', table_column, 'p', network=network, base_url=base_url)

    res = update_style_mapping(style_name, mvp, base_url=base_url)
    return res


@cy_log
def set_node_width_mapping(table_column, table_column_values=None, widths=None, mapping_type='c', default_width=None,
                           style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Map table column values to the node widths.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        widths (list): List of widths values to map to ``table_column_values``
        mapping_type (str): discrete or passthrough (d,p); default is discrete
        default_width (int): Width value to set as default
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type, or if invalid width
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_node_width_mapping('AverageShortestPathLength', table_column_values=[1.0, 16.36], sizes=[120, 180], style_name='galFiltered Style')
        ''
        >>> set_node_width_mapping('Degree', table_column_values=['1', '2'], sizes=[140, 190], mapping_type='d', style_name='galFiltered Style')
        ''
        >>> set_node_width_mapping(**gen_node_width_map('degree', mapping_type='d'))
        ''
        >>> set_node_width_mapping(**gen_node_width_map('AverageShortestPathLength', scheme_c_number_continuous(100, 200), style_name='galFiltered Style'))
        ''
        >>> set_node_width_mapping('PassthruCol', mapping_type='p', default_size=120, style_name='galFiltered Style')
        ''

    See Also:
        :meth:`gen_node_width_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    verify_dimensions('width', widths)

    if default_width is not None:
        style_defaults.set_node_width_default(default_width, style_name=style_name, base_url=base_url)

    # TODO: Added this because otherwise, could not set mapping ... the PUT failed silently. Shouldn't we be restoring to its original setting? Same with set_default_node_height?
    style_dependencies.lock_node_dimensions(False, style_name=style_name, base_url=base_url)

    return _update_visual_property('NODE_WIDTH', table_column, table_column_values=table_column_values,
                                   range_map=widths, mapping_type=mapping_type,
                                   style_name=style_name, network=network, base_url=base_url)


# ==============================================================================
# II.b. Edge Properties
# Pattern: (1) prepare mapVisualProperty, (2) call updateStyleMapping()
# ------------------------------------------------------------------------------

# TODO: Come back to this once we figure out what it should be doing
@cy_log
def set_edge_color_mapping(table_column, table_column_values=None, colors=None, mapping_type='c', default_color=None,
                           style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Map table column values to colors to set the edge color.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        colors (list): list of hex colors to map to ``table_column_values``
        mapping_type (str): continuous, discrete or passthrough (c,d,p); default is continuous
        default_color (str): Hex color to set as default
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if invalid color, table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_color_mapping('EdgeBetweenness', [1.0, 16.36], ['#FBE723', '#440256'], style_name='galFiltered Style')
        ''
        >>> set_edge_color_mapping('EdgeBetweenness', ['1', '2'], ['#FFFF00', '#00FF00'], 'd', style_name='galFiltered Style')
        ''
        >>> set_edge_color_mapping(**gen_node_color_map('Degree', mapping_type='d'))
        ''
        >>> set_edge_color_mapping(**gen_edge_color_map('interaction', palette_color_brewer_q_Accent(), mapping_type='d'))
        ''
        >>> set_edge_color_mapping(**gen_edge_color_map('EdgeBetweenness'))
        ''
        >>> set_edge_color_mapping(**gen_edge_color_map('EdgeBetweenness', palette_color_brewer_s_Blues()))
        ''
        >>> set_edge_color_mapping(**gen_edge_color_map('EdgeBetweenness', (palette_color_brewer_s_Blues(), palette_color_brewer_d_BrBG()))
        ''
        >>> set_edge_color_mapping('EdgeBetweennessColor', mapping_type='p', default_color='#654321', style_name='galFiltered Style')
        ''

    See Also:
        :meth:`gen_edge_color_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    verify_hex_colors(colors)

    # set default
    if default_color is not None:
        style_defaults.set_edge_color_default(default_color, style_name, base_url=base_url)
    # TODO: An error here will be missed ... shouldn't this throw an exception?

    # perform mapping for COLOR (i.e., when arrowColorMatchesEdge=T)
    # TODO: This code checks table_column, but the R code does not
    res = _update_visual_property('EDGE_UNSELECTED_PAINT', table_column, table_column_values=table_column_values, range_map=colors,
                                  mapping_type=mapping_type, style_name=style_name, network=network,
                                  base_url=base_url, table='edge')
    if res is not None:
        # perform mapping for STROKE (i.e., when arrowColorMatchesEdge=F)
        res = _update_visual_property('EDGE_STROKE_UNSELECTED_PAINT', table_column,
                                      table_column_values=table_column_values, range_map=colors,
                                      mapping_type=mapping_type, style_name=style_name, network=network,
                                      base_url=base_url, table='edge')
    return res


@cy_log
def set_edge_font_face_mapping(table_column, table_column_values=None, fonts=None, mapping_type='d', default_font=None,
                               style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Sets font face for edge labels.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        fonts (list): List of string specifications of font face, style and size, e.g., ["SansSerif,plain,12", "Dialog,plain,10"]
        mapping_type (str): discrete or passthrough (d,p); default is discrete
        default_font (str): String specification of font face, style and size, e.g., "SansSerif,plain,12" or "Dialog,plain,10"
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_font_face_mapping('interaction', table_column_values=['pp', 'pd'], fonts=['Arial,plain,12', 'Arial Bold,bold,12'], mapping_type='d', style_name='galFiltered Style')
        ''
        >>> set_edge_font_face_mapping('PassthruCol', mapping_type='p', default_font='Arial,plain,12', style_name='galFiltered Style')
        ''
    """
    if default_font is not None:
        style_defaults.set_visual_property_default({'visualProperty': 'EDGE_LABEL_FONT_FACE', 'value': default_font},
                                                   style_name=style_name, base_url=base_url)
    # TODO: An error here will be missed ... shouldn't this throw an exception?

    return _update_visual_property('EDGE_LABEL_FONT_FACE', table_column, table_column_values=table_column_values,
                                   range_map=fonts, mapping_type=mapping_type,
                                   style_name=style_name, network=network, base_url=base_url,
                                   supported_mappings=['d', 'p'], table='edge')


@cy_log
def set_edge_font_size_mapping(table_column, table_column_values=None, sizes=None, mapping_type='c', default_size=None,
                               style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Map table column values to sizes to set the edge size.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        sizes (list): List of size values to map to ``table_column_values``
        mapping_type (str): discrete or passthrough (d,p); default is discrete
        default_size (int): Size value to set as default
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type, or if invalid size
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_font_size_mapping('EdgeBetweenness', table_column_values=[2.0, 20000.0], sizes=[20, 80], style_name='galFiltered Style')
        ''
        >>> set_edge_font_size_mapping('interaction', table_column_values=['pp', 'pd'], sizes=[40, 90], mapping_type='d', style_name='galFiltered Style')
        ''
        >>> set_edge_font_size_mapping(**gen_edge_size_map('interaction', mapping_type='d'))
        ''
        >>> set_edge_font_size_mapping(**gen_edge_size_map('EdgeBetweenness', scheme_c_number_continuous(100, 200), style_name='galFiltered Style'))
        ''
        >>> set_edge_font_size_mapping('PassthruCol', mapping_type='p', default_size=20, style_name='galFiltered Style')
        ''

    See Also:
        :meth:`gen_edge_size_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    verify_dimensions('size', sizes)

    if default_size is not None:
        style_defaults.set_edge_font_size_default(default_size, style_name=style_name, base_url=base_url)

    return _update_visual_property('EDGE_LABEL_FONT_SIZE', table_column, table_column_values=table_column_values,
                                   range_map=sizes, mapping_type=mapping_type, style_name=style_name, network=network,
                                   base_url=base_url, table='edge')


@cy_log
def set_edge_label_mapping(table_column, style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Pass the values from a table column to display as edge labels.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_label_mapping('name', style_name='galFiltered Style')
        ''
        >>> set_edge_label_mapping('name')
        ''
    """
    # TODO: The return value in the R code is None ... probably should be throwing an exception, which I'm doing
    if not table_column_exists(table_column, 'edge', network=network, base_url=base_url):
        raise CyError(f'Table column "{table_column}" does not exist')

    # TODO: Should there be the ability to set the edge label default here? The call exists in styles_defaults

    mvp = map_visual_property('EDGE_LABEL', table_column, 'p', network=network, base_url=base_url)

    res = update_style_mapping(style_name, mvp, base_url=base_url)
    return res


@cy_log
def set_edge_label_color_mapping(table_column, table_column_values=None, colors=None, mapping_type='c',
                                 default_color=None, style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Map table column values to colors to set the edge border color.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        colors (list): values between 0 and 255; 0 is invisible
        mapping_type (str): continuous, discrete or passthrough (c,d,p); default is continuou
        default_color (str): Hex color to set as default
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if invalid color, table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_label_color_mapping('EdgeBetweenness', [2.0, 20000.0], ['#FBE723', '#440256'], style_name='galFiltered Style')
        ''
        >>> set_edge_label_color_mapping('interaction', ['pp', 'pd'], ['#FFFF00', '#00FF00'], 'd', style_name='galFiltered Style')
        ''
        >>> set_edge_label_color_mapping(**gen_edge_color_map('interaction', palette_color_brewer_q_Accent(), mapping_type='d'))
        ''
        >>> set_edge_label_color_mapping(**gen_edge_color_map('EdgeBetweenness'))
        ''
        >>> set_edge_label_color_mapping(**gen_edge_color_map('EdgeBetweenness', palette_color_brewer_s_Blues()))
        ''
        >>> set_edge_label_color_mapping(**gen_edge_color_map('EdgeBetweenness', (palette_color_brewer_s_Blues(), palette_color_brewer_d_BrBG()))
        ''
        >>> set_edge_label_color_mapping('ColorCol', mapping_type='p', default_color='#654321', style_name='galFiltered Style')
        ''

    See Also:
        :meth:`gen_edge_color_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    verify_hex_colors(colors)

    # set default
    if default_color is not None:
        style_defaults.set_edge_label_color_default(default_color, style_name, base_url=base_url)
    # TODO: An error here will be missed ... shouldn't this throw an exception?

    return _update_visual_property('EDGE_LABEL_COLOR', table_column, table_column_values=table_column_values,
                                   range_map=colors, mapping_type=mapping_type, style_name=style_name, network=network,
                                   base_url=base_url, table='edge')


@cy_log
def set_edge_label_opacity_mapping(table_column, table_column_values=None, opacities=None, mapping_type='c',
                                   default_opacity=None, style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Sets opacity for edge label only.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        opacities (list): int values between 0 and 255; 0 is invisible
        mapping_type (str): continuous, discrete or passthrough (c,d,p); default is continuous
        default_opacity (int): Opacity value to set as default for all unmapped values
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type, or if invalid opacity
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_label_opacity_mapping('EdgeBetweenness', [2.0, 20000.0], opacities=[50, 100], style_name='galFiltered Style')
        ''
        >>> set_edge_label_opacity_mapping('interaction', ['pp', 'pd'], opacities=[50, 100], mapping_type='d', style_name='galFiltered Style')
        ''
        >>> set_edge_label_opacity_mapping(**gen_edge_opacity_map('interaction', mapping_type='d'))
        ''
        >>> set_edge_label_opacity_mapping(**gen_edge_opacity_map('EdgeBetweenness', scheme_c_number_continuous(100, 200), style_name='galFiltered Style'))
        ''
        >>> set_edge_label_opacity_mapping('PassthruCol', mapping_type='p', default_opacity=225, style_name='galFiltered Style')
        ''

    See Also:
        :meth:`gen_edge_opacity_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    # TODO: Moved check to _update_style_mapping
    #    if not table_column_exists(table_column, 'edge', network=network, base_url=base_url):
    #        raise CyError(f'Table column "{table_column}" does not exist')

    verify_opacities(opacities)

    # TODO: There is a set_edge_label_opacity_default ... should that be called here?
    if default_opacity is not None:
        verify_opacities(default_opacity)

        style_defaults.set_visual_property_default(
            {'visualProperty': 'EDGE_LABEL_TRANSPARENCY', 'value': str(default_opacity)},
            style_name=style_name, base_url=base_url)

    return _update_visual_property('EDGE_LABEL_TRANSPARENCY', table_column, table_column_values=table_column_values,
                                   range_map=opacities, mapping_type=mapping_type, style_name=style_name,
                                   network=network, base_url=base_url, table='edge')


@cy_log
def set_edge_line_style_mapping(table_column, table_column_values=None, line_styles=None, default_line_style='SOLID',
                                style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Map table column values to styles to set the edge style.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        line_styles (list): List of styles to map to ``table_column_values``. See ``get_line_styles()``
        default_line_style (str): Style to set as default. See ``get_line_styles()``
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_line_style_mapping('interaction', table_column_values=['pp','pd'], shapes=['ZIGZAG', 'SINEWAVE'], default_shape='EQUAL_DASH', style_name='galFiltered Style')
        ''
        >>> set_edge_line_style_mapping(**gen_edge_line_style_map('interaction', style_name='galFiltered Style'))
        ''

    See Also:
        :meth:`gen_edge_line_style_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    # TODO: Validate line style

    # TODO: R code does not check for valid table_column ... this code does
    if default_line_style is not None:
        style_defaults.set_edge_line_style_default(default_line_style, style_name=style_name, base_url=base_url)
        # TODO: If this fails, flow continues anyway

    return _update_visual_property('EDGE_LINE_TYPE', table_column, table_column_values=table_column_values,
                                   range_map=line_styles, mapping_type='d', style_name=style_name, network=network,
                                   base_url=base_url, table='edge')


@cy_log
def set_edge_line_width_mapping(table_column, table_column_values=None, widths=None, mapping_type='c',
                                default_width=None, style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Map table column values to widths to set the node border width.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        widths (list): List of width values to map to ``table_column_values``
        mapping_type (str): continuous, discrete or passthrough (c,d,p); default is continuous
        default_width (int): Width value to set as default for all unmapped values
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type, or if invalid width
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_line_width_mapping('EdgeBetweenness', table_column_values=[2.0, 20000.0], widths=[5, 10], style_name='galFiltered Style')
        ''
        >>> set_edge_line_width_mapping('interaction', table_column_values=['pp','pd'], widths=[5, 10], mapping_type='d', style_name='galFiltered Style')
        ''
        >>> set_edge_line_width_mapping(**gen_edge_width_map('interaction', mapping_type='d'))
        ''
        >>> set_edge_line_width_mapping(**gen_edge_width_map('EdgeBetweenness', scheme_c_number_continuous(100, 200), style_name='galFiltered Style'))
        ''
        >>> set_edge_line_width_mapping('PassthruCol', mapping_type='p', default_width=3, style_name='galFiltered Style')
        ''

    See Also:
        :meth:`gen_edge_width_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    verify_dimensions('width', widths)

    # TODO: R code does not check for valid table_column ... this code does
    # set default
    if default_width is not None:
        style_defaults.set_edge_line_width_default(default_width, style_name=style_name, base_url=base_url)
        # TODO: If this fails, flow continues anyway

    return _update_visual_property('EDGE_WIDTH', table_column, table_column_values=table_column_values,
                                   range_map=widths, mapping_type=mapping_type, style_name=style_name, network=network,
                                   base_url=base_url, table='edge')


@cy_log
def set_edge_opacity_mapping(table_column, table_column_values=None, opacities=None, mapping_type='c',
                             default_opacity=None, style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Map table column values to opacities to set the edge opacity.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        opacities (list): int values between 0 and 255; 0 is invisible
        mapping_type (str): continuous, discrete or passthrough (c,d,p); default is continuous
        default_opacity (int): Opacity value to set as default for all unmapped values
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type, or if invalid opacity
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_opacity_mapping('EdgeBetweenness', table_column_values=[2.0, 20000.0], opacities=[50, 100], style_name='galFiltered Style')
        ''
        >>> set_edge_opacity_mapping('interaction', table_column_values=['pp','pd'], opacities=[50, 100], mapping_type='d', style_name='galFiltered Style')
        ''
        >>> set_edge_opacity_mapping(**gen_edge_opacity_map('interaction', mapping_type='d'))
        ''
        >>> set_edge_opacity_mapping(**gen_edge_opacity_map('EdgeBetweenness', scheme_c_number_continuous(100, 200), style_name='galFiltered Style'))
        ''
        >>> set_edge_opacity_mapping('PassthruCol', mapping_type='p', default_opacity=225, style_name='galFiltered Style')
        ''

    See Also:
        :meth:`gen_edge_opacity_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    # TODO: This code checks the table_column ... the R code does not

    verify_opacities(opacities)

    # TODO: There is a set_edge_opacity_default ... should that be called here?
    if default_opacity is not None:
        verify_opacities(default_opacity)

        style_defaults.set_visual_property_default(
            {'visualProperty': 'EDGE_TRANSPARENCY', 'value': str(default_opacity)},
            style_name=style_name, base_url=base_url)

    return _update_visual_property('EDGE_TRANSPARENCY', table_column, table_column_values=table_column_values,
                                   range_map=opacities, mapping_type=mapping_type, style_name=style_name,
                                   network=network, base_url=base_url, table='edge')


# TODO: R spelled 'Mapping' as 'Maping' ... how to fix this??
# TODO: This is the same as set_edge_target_arrow_shape_mapping???
@cy_log
def set_edge_target_arrow_maping(table_column, table_column_values=None, shapes=None, default_shape='ARROW',
                                  style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Map table column values to shapes to set the target arrow shape.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        shapes (list): List of shapes to map to ``table_column_values``. See ``get_arrow_shapes()``
        default_shape (str): Style to set as default. See ``get_arrow_shapes()``
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_target_arrow_maping('interaction', table_column_values=['pp','pd'], shapes=['CIRCLE', 'ARROW'], default_shape='NONE', style_name='galFiltered Style')
        ''
        >>> set_edge_target_arrow_maping(**gen_edge_arrow_map('interaction', style_name='galFiltered Style'))
        ''

    See Also:
        :meth:`gen_edge_arrow_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    # TODO: Validate shape

    # TODO: Isn't this the same as set_edge_target_arrow_shape_mapping? ... shouldn't this be renamed?
    # TODO: R code does not check for valid table_column ... this code does
    # set default
    if default_shape is not None:
        style_defaults.set_edge_target_arrow_shape_default(default_shape, style_name=style_name, base_url=base_url)
        # TODO: If this fails, flow continues anyway

    return _update_visual_property('EDGE_TARGET_ARROW_SHAPE', table_column, table_column_values=table_column_values,
                                   range_map=shapes, mapping_type='d', style_name=style_name, network=network,
                                   base_url=base_url, table='edge', supported_mappings=['d'])


# TODO: This is the same as set_edge_source_arrow_shape_mapping???
@cy_log
def set_edge_source_arrow_mapping(table_column, table_column_values=None, shapes=None, default_shape='ARROW',
                                  style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Map table column values to shapes to set the source arrow shape.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        shapes (list): List of shapes to map to ``table_column_values``. See ``get_arrow_shapes()``
        default_shape (str): Style to set as default. See ``get_arrow_shapes()``
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_source_arrow_mapping('interaction', table_column_values=['pp','pd'], shapes=['CIRCLE', 'ARROW'], default_shape='NONE', style_name='galFiltered Style')
        ''
        >>> set_edge_source_arrow_mapping(**gen_edge_arrow_map('interaction', style_name='galFiltered Style'))
        ''

    See Also:
        :meth:`gen_edge_arrow_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    # TODO: Validate shape

    # TODO: Isn't this the same as set_edge_source_arrow_shape_mapping? ... shouldn't this be renamed?
    # TODO: R code does not check for valid table_column ... this code does
    # set default
    if default_shape is not None:
        style_defaults.set_edge_source_arrow_shape_default(default_shape, style_name=style_name, base_url=base_url)
        # TODO: If this fails, flow continues anyway

    return _update_visual_property('EDGE_SOURCE_ARROW_SHAPE', table_column, table_column_values=table_column_values,
                                   range_map=shapes, mapping_type='d', style_name=style_name, network=network,
                                   base_url=base_url, table='edge', supported_mappings=['d'])


@cy_log
def set_edge_target_arrow_color_mapping(table_column, table_column_values=None, colors=None, mapping_type='c',
                                        default_color=None, style_name=None, network=None,
                                        base_url=DEFAULT_BASE_URL):
    """Map table column values to colors to set the target arrow color.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        colors (list): values between 0 and 255; 0 is invisible
        mapping_type (str): continuous, discrete or passthrough (c,d,p); default is continuoue
        default_color (str): Hex color to set as default
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if invalid color, table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_target_arrow_color_mapping('EdgeBetweenness', [2.0, 20000.0], ['#FBE723', '#440256'], style_name='galFiltered Style')
        ''
        >>> set_edge_target_arrow_color_mapping('interaction', ['pp','pd'], ['#FFFF00', '#00FF00'], 'd', style_name='galFiltered Style')
        ''
        >>> set_edge_target_arrow_color_mapping(**gen_edge_color_map('interaction', mapping_type='d'))
        ''
        >>> set_edge_target_arrow_color_mapping(**gen_edge_color_map('interaction', palette_color_brewer_q_Accent(), mapping_type='d'))
        ''
        >>> set_edge_target_arrow_color_mapping(**gen_edge_color_map('EdgeBetweenness'))
        ''
        >>> set_edge_target_arrow_color_mapping(**gen_edge_color_map('EdgeBetweenness', palette_color_brewer_s_Blues()))
        ''
        >>> set_edge_target_arrow_color_mapping(**gen_edge_color_map('EdgeBetweenness', (palette_color_brewer_s_Blues(), palette_color_brewer_d_BrBG()))
        ''
        >>> set_edge_target_arrow_color_mapping('ColorCol', mapping_type='p', default_color='#654321', style_name='galFiltered Style')
        ''

    See Also:
        :meth:`gen_edge_color_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    verify_hex_colors(colors)

    # set default
    if default_color is not None:
        style_defaults.set_edge_target_arrow_color_default(default_color, style_name, base_url=base_url)
    # TODO: An error here will be missed ... shouldn't this throw an exception?

    return _update_visual_property('EDGE_TARGET_ARROW_UNSELECTED_PAINT', table_column,
                                   table_column_values=table_column_values, range_map=colors,
                                   mapping_type=mapping_type, style_name=style_name, network=network, base_url=base_url,
                                   table='edge')


@cy_log
def set_edge_source_arrow_color_mapping(table_column, table_column_values=None, colors=None, mapping_type='c',
                                        default_color=None, style_name=None, network=None,
                                        base_url=DEFAULT_BASE_URL):
    """Map table column values to colors to set the source arrow color.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        colors (list): values between 0 and 255; 0 is invisible
        mapping_type (str): continuous, discrete or passthrough (c,d,p); default is continuoue
        default_color (str): Hex color to set as default
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if invalid color, table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_source_arrow_color_mapping('EdgeBetweenness', [2.0, 20000.0], ['#FBE723', '#440256'], style_name='galFiltered Style')
        ''
        >>> set_edge_source_arrow_color_mapping('interaction', ['pp','pd'], ['#FFFF00', '#00FF00'], 'd', style_name='galFiltered Style')
        ''
        >>> set_edge_source_arrow_color_mapping(**gen_edge_color_map('interaction', palette_color_brewer_q_Accent(), mapping_type='d'))
        ''
        >>> set_edge_source_arrow_color_mapping('ColorCol', mapping_type='p', default_color='#654321', style_name='galFiltered Style')
        ''

    See Also:
        :meth:`gen_edge_color_map`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    verify_hex_colors(colors)

    # set default
    if default_color is not None:
        style_defaults.set_edge_source_arrow_color_default(default_color, style_name, base_url=base_url)
    # TODO: An error here will be missed ... shouldn't this throw an exception?

    return _update_visual_property('EDGE_SOURCE_ARROW_UNSELECTED_PAINT', table_column,
                                   table_column_values=table_column_values, range_map=colors,
                                   mapping_type=mapping_type, style_name=style_name, network=network, base_url=base_url,
                                   table='edge')

@cy_log
def set_edge_target_arrow_shape_mapping(table_column, table_column_values=None, shapes=None,
                                        default_shape=None, style_name=None, network=None,
                                        base_url=DEFAULT_BASE_URL):
    """Map table column values to colors to set the target arrow color.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        shapes (list): List of arrow shapes to map to ``table_column_values``. See ``get_arrow_shapes()``
        default_shape (str): Shape to set as default. See ``get_arrow_shapes()``
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_source_arrow_target_mapping('interaction', table_column_values=['pp','pd'], shapes=['DIAMOND', 'CIRCLE'], style_name='galFiltered Style')
        ''
        >>> set_edge_source_arrow_target_mapping(**gen_edge_arrow_map('interaction', style_name='galFiltered Style'))
        ''

    Note:
        This is the same function as ``set_edge_target_arrow_mapping()``

    See also:
        :meth:`set_edge_arrow_mapping`

    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    return set_edge_target_arrow_maping(table_column, table_column_values=table_column_values, shapes=shapes,
                                         default_shape=default_shape, style_name=style_name, network=network,
                                         base_url=base_url)


@cy_log
def set_edge_source_arrow_shape_mapping(table_column, table_column_values=None, shapes=None,
                                        default_shape=None, style_name=None, network=None,
                                        base_url=DEFAULT_BASE_URL):
    """Map table column values to colors to set the source arrow color.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        table_column_values (list): List of values from Cytoscape table to be used in mapping
        shapes (list): List of arrow shapes to map to ``table_column_values``. See ``get_arrow_shapes()``
        default_shape (str): Shape to set as default. See ``get_arrow_shapes()``
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_source_arrow_shape_mapping('interaction', table_column_values=['pp','pd'], shapes=['DIAMOND', 'CIRCLE'], style_name='galFiltered Style')
        ''
        >>> set_edge_source_arrow_shape_mapping(**gen_edge_arrow_map('interaction', style_name='galFiltered Style'))
        ''

    Note:
        This is the same function as ``set_edge_source_arrow_mapping()``

    See also:
        :meth:`set_edge_source_arrow_mapping`, :meth:`gen_edge_arrow_map`


    See Also:
        `Value Generators <https://py4cytoscape.readthedocs.io/en/0.0.9/concepts.html#value-generators>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    return set_edge_source_arrow_mapping(table_column, table_column_values=table_column_values, shapes=shapes,
                                        default_shape=default_shape, style_name=style_name, network=network,
                                        base_url=base_url)

@cy_log
def set_edge_tooltip_mapping(table_column, style_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Pass the values from a table column to display as edge tooltips.

    Args:
        table_column (str): Name of Cytoscape table column to map values from
        style_name (str): name for style
        network (SUID or str or None): Name or SUID of a network or view. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if table column doesn't exist, table column values doesn't match values list, or invalid style name, network or mapping type
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_edge_tooltip_mapping('PassthruCol', style_name='galFiltered Style')
        ''
    """
    # TODO: Won't this miss setting the default tooltip?
    return _update_visual_property('EDGE_TOOLTIP', table_column, mapping_type='p', style_name=style_name,
                                   network=network, base_url=base_url, table='edge', supported_mappings=['p'])

# Check table column, create the visual property map, and update Cytoscape's copy of the visual property
def _update_visual_property(visual_prop_name, table_column, table_column_values=[], range_map=[], mapping_type='c',
                            style_name=None, network=None, base_url=DEFAULT_BASE_URL,
                            supported_mappings=['c', 'd', 'p'], table='node'):
    if range_map is not None: range_map = [str(x) for x in range_map]  # CyREST requires strings

    # TODO: Added because all mappings need to do this. R code should probably adopt this, too
    if not table_column_exists(table_column, table, network=network, base_url=base_url):
        raise CyError(f'Table column "{table_column}" does not exist')

    # perform mapping
    mapping_type = normalize_mapping(mapping_type, visual_prop_name, supported_mappings)
    if mapping_type == 'c':
        mvp = map_visual_property(visual_prop_name, table_column, 'c', table_column_values, range_map,
                                  network=network, base_url=base_url)
    elif mapping_type == 'd':
        mvp = map_visual_property(visual_prop_name, table_column, 'd', table_column_values, range_map,
                                  network=network, base_url=base_url)
    elif mapping_type == 'p':
        mvp = map_visual_property(visual_prop_name, table_column, 'p', network=network, base_url=base_url)
    else:
        raise CyError(f'mapping_type "{mapping_type}" for property "{visual_prop_name}" not recognized ... must be "{supported_mappings}"')

    res = update_style_mapping(style_name, mvp, base_url=base_url)
    return res



