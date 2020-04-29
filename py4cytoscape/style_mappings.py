# -*- coding: utf-8 -*-

"""Functions for defining MAPPINGS between table column values and visual properties, organized into sections:

I. General functions for creating and applying mappings for node, edge and network properties
II. Specific functions for defining particular node, edge and network properties

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
from . import networks
from . import commands
from . import styles

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log


# ==============================================================================
# I. General Functions
# ------------------------------------------------------------------------------

# TODO: R seems to allow table_column_value, visual_prop_values to be unspecified ... Python does this with optional parameters
@cy_log
def map_visual_property(visual_prop, table_column, mapping_type, table_column_values=[],
                        visual_prop_values=[], network=None, base_url=DEFAULT_BASE_URL):
    """Creates a mapping between an attribute and a visual property.

    Generates the appropriate data structure for the "mapping" parameter in ``update_style_mapping``.

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
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'mappingType': type of mapping, 'mappingColumn': column to map, 'mappingColumnType': column data type, 'visualProperty': name of property, cargo}

    Raises:
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>>map_visual_property('node fill color', 'gal1RGexp', 'c', [-2.426, 0.0, 2.058], ['#0066CC', '#FFFFFF','#FFFF00'])
        {'mappingType': 'continuous', 'mappingColumn': 'gal1RGexp', 'mappingColumnType': 'Double', 'visualProperty': 'NODE_FILL_COLOR', 'points': [{'value': -2.426, 'lesser': '#0066CC', 'equal': '#0066CC', 'greater': '#0066CC'}, {'value': 0.0, 'lesser': '#FFFFFF', 'equal': '#FFFFFF', 'greater': '#FFFFFF'}, {'value': 2.058, 'lesser': '#FFFF00', 'equal': '#FFFF00', 'greater': '#FFFF00'}]}
        >>>map_visual_property('node shape', 'degree.layout', 'd', [1, 2], ['ellipse', 'rectangle'])
        {'mappingType': 'discrete', 'mappingColumn': 'degree.layout', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_SHAPE', 'map': [{'key': 1, 'value': 'ellipse'}, {'key': 2, 'value': 'rectangle'}]}
        >>>map_visual_property('node label', 'COMMON', 'p')
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

    # processs visual property, including common alternatives for vp names :)
    visual_prop_name = re.sub('\\s+', '_', visual_prop).upper()
    if visual_prop_name in PROPERTY_NAMES: visual_prop_name = PROPERTY_NAMES[visual_prop_name]

    # check visual prop name
    if visual_prop_name not in styles.get_visual_property_names(base_url=base_url):
        raise CyError(
            'Could not find ' + visual_prop_name + '. Run get_visual_property_names() to retrieve property names.')

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
        raise CyError('Could not find ' + table_column + ' column in ' + table + ' table.')

    # construct visual property map
    visual_prop_map = {'mappingType': mapping_type_name, 'mappingColumn': table_column,
                       'mappingColumnType': table_column_type, 'visualProperty': visual_prop_name}
    if mapping_type_name == 'discrete':
        visual_prop_map['map'] = [{'key': col_val, 'value': prop_val}    for col_val, prop_val in zip(table_column_values, visual_prop_values)]
    elif mapping_type_name == 'continuous':
        # check for extra lesser and greater values
        prop_val_count = len(visual_prop_values)
        col_val_count = len(table_column_values)
        if prop_val_count - col_val_count == 2:
            matched_visual_prop_values = visual_prop_values[1:]
            points = [{'value': col_val, 'lesser': prop_val, 'equal': prop_val, 'greater': prop_val}    for col_val, prop_val in zip(table_column_values, matched_visual_prop_values)]

            # then correct extreme values
            points[0]['lesser'] = visual_prop_values[0]
            points[col_val_count - 1]['greater'] = visual_prop_values[-1]
        elif prop_val_count - col_val_count == 0:
            points = [{'value': col_val, 'lesser': prop_val, 'equal': prop_val, 'greater': prop_val}    for col_val, prop_val in zip(table_column_values, visual_prop_values)]
        else:
            error = 'Error: table.column.values and visual.prop.values don\'t match up.'
            sys.stderr.write(error)
            raise CyError(error)

        visual_prop_map['points'] = points

    return visual_prop_map

@cy_log
def update_style_mapping(style_name, mapping, base_url=DEFAULT_BASE_URL):
    """Update a visual property mapping in a style.

    Updates the visual property mapping, overriding any prior mapping. Creates a visual property mapping if it doesn't
    already exist in the style. Requires visual property mappings to be previously created, see ``map_visual_property``.

    Args:
        style_name (str): name for style
        mapping (dict): a single visual property mapping, see ``map_visual_property``
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if style doesn't exist
        TypeError: if mapping isn't a visual property mapping
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>>update_style_mapping('galFiltered Style', map_visual_property('node label', 'name', 'p'))
        ''

    See Also:
        :meth:`map_visual_property`
    """
    visual_prop_name = mapping['visualProperty']

    # check if vp exists already
    res = commands.cyrest_get('styles/' + style_name + '/mappings', base_url=base_url)
    vp_list = [prop['visualProperty']   for prop in res]
    exists = visual_prop_name in vp_list

    if exists:
        res = commands.cyrest_put('styles/' + style_name + '/mappings/' + visual_prop_name, body=[mapping], base_url=base_url, require_json=False)
    else:
        res = commands.cyrest_post('styles/' + style_name + '/mappings', body=[mapping], base_url=base_url, require_json=False)
    return res


# TODO: Note that R documentation for this is wrong ... we really do want a property name, not a map
@cy_log
def delete_style_mapping(style_name, visual_prop, base_url=DEFAULT_BASE_URL):
    """Delete a specified visual style mapping from specified style.

    Args:
        style_name (str): name for style
        visual_prop (str): name of visual property to delete
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str or None: '' or None (if property doesn't exist)

    Raises:
        CyError: if style doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>>delete_style_mapping('galFiltered Style', 'node label')
        ''
    """
    # check if vp exists already
    res = commands.cyrest_get('styles/' + style_name + '/mappings', base_url=base_url)
    vp_list = [prop['visualProperty']   for prop in res]
    exists = visual_prop in vp_list

    if exists:
        res = commands.cyrest_delete('styles/' + style_name + '/mappings/' + visual_prop, base_url=base_url, require_json=False)
    else:
        res = None
    return res
# TODO: Verify that it's OK to return None if the style doesn't exist ... maybe should be a CyError?

# TODO: Are we missing a get_style_mapping here?? ... probably ... I'm adding one to help with testing ...
@cy_log
def get_style_mapping(style_name, visual_prop, base_url=DEFAULT_BASE_URL):
    """Fetch a visual property mapping in a style.

    The property mapping is the same as a dict created by ``map_visual_property``.

    Args:
        style_name (str): name for style
        visual_prop (str): the name of the visual property
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: see ``map_visual_property``

    Raises:
        CyError: if style or property name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>>get_style_mapping('galFiltered Style', 'node label')
        {"mappingType": "passthrough", "mappingColumn": "COMMON", "mappingColumnType": "String", "visualProperty": "NODE_LABEL"}

    See Also:
        :meth:`map_visual_property`
    """
    # check if vp exists already
    res = commands.cyrest_get('styles/' + style_name + '/mappings', base_url=base_url)
    for prop in res:
        if prop['visualProperty'] == visual_prop:
            return prop
    raise CyError('Property "' + visual_prop + '" does not exist in style "' + style_name + '"')

# TODO: Are we missing a get_style_all_mappings here?? ... probably ... I'm adding one to help with testing ...
@cy_log
def get_style_all_mappings(style_name, base_url=DEFAULT_BASE_URL):
    """Fetch all visual property mapping in a style.

    The property mappings are the same as a dict created by ``map_visual_property``.

    Args:
        style_name (str): name for style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: list of dicts of the type created by ``map_visual_property``

    Raises:
        CyError: if style or property name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>>get_style_all_mappings('galFiltered Style')
        [{"mappingType": "passthrough", "mappingColumn": "name", "mappingColumnType": "String", "visualProperty": "NODE_LABEL"},
         {"mappingType": "passthrough", "mappingColumn": "interaction", "mappingColumnType": "String", "visualProperty": "EDGE_LABEL"}]

    See Also:
        :meth:`map_visual_property`
    """
    res = commands.cyrest_get('styles/' + style_name + '/mappings', base_url=base_url)
    return res
