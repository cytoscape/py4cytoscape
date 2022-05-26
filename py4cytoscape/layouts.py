# -*- coding: utf-8 -*-

"""Functions for performing LAYOUTS in addition to getting and setting layout properties.

I. Perform layout functions
II. Get layout properties
III. Set layout properties

Note that yFiles layouts are not available due to licensing restrictions with yWorks,
the owner of yFiles.
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

# Internal module imports
from . import commands
from . import networks

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log


# ==============================================================================
# I. Perform layout functions
# ------------------------------------------------------------------------------

@cy_log
def bundle_edges(network=None, base_url=DEFAULT_BASE_URL):
    """Apply edge bundling to the network specified.

    Edge bundling is executed with default parameters; optional parameters are not supported.

    Args:
        network (SUID or str or None): Name or SUID of the network; default is "current" network.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'message': 'Edge bundling success.'}

    Raises:
        CyError: if layout_name is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> bundle_edges() # Bundle edges in current network
        {'message': 'Edge bundling success.'}
        >>> bundle_edges('yeastHighQuality.sif') # Bundle edges in named network
        {'message': 'Edge bundling success.'}
    """
    suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.cyrest_get(f'apply/edgebundling/{suid}', base_url=base_url)
    return res


@cy_log
def clear_edge_bends(network=None, base_url=DEFAULT_BASE_URL):
    """Clear all edge bends created from edge bundling.

    Args:
        network (SUID or str or None): Name or SUID of the network; default is "current" network.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'message': 'Clear all edge bends success.'}

    Raises:
        CyError: if layout_name is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> clear_edge_bends() # Clear edge bends in current network
        {'message': 'Edge bundling success.'}
        >>> clear_edge_bends('yeastHighQuality.sif') # Clear edge bends in named network
        {'message': 'Edge bundling success.'}
    """
    suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.cyrest_get(f'apply/clearalledgebends/{suid}', base_url=base_url)
    return res


@cy_log
def layout_network(layout_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Apply a layout to a network.

    Run ``getLayoutNames`` to list available layouts.

    Note that yFiles layouts are not available due to licensing restrictions with yWorks, the owner of yFiles.

    Args:
        layout_name (str): Name of the layout (with optional parameters). If not specified,
            then the preferred layout set in the Cytoscape UI is applied.
        network (SUID or str or None): Name or SUID of the network; default is "current" network.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {} empty

    Raises:
        CyError: if layout_name is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> layout_network() # Layout current network using default layout
        {}
        >>> layout_network('force-directed') # Layout current network using force-directed layout
        {}
        >>> layout_network('grid', 'yeastHighQuality.sif') # layout named network using grid layout
        {}
    """
    suid = networks.get_network_suid(network, base_url=base_url)
    if layout_name is None:
        res = commands.commands_post('layout apply preferred networkSelected="SUID:' + str(suid) + '"',
                                     base_url=base_url)
        return res
    else:
        res = commands.commands_post(f'layout {layout_name} network="SUID:{suid}"', base_url=base_url)
        return res


@cy_log
def layout_copycat(source_network, target_network, source_column='name', target_column='name',
                   grid_unmapped=True, select_unmapped=True, base_url=DEFAULT_BASE_URL):
    """Copy a layout from one network to another.

    Sets the coordinates for each node in the target network to the coordinates of a matching node
    in the source network. Optional parameters such as ``gridUnmapped`` and ``selectUnmapped``
    determine the behavior of target network nodes that could not be matched.

    Args:
        source_network (SUID or str or None): Name of the network to get node coordinates from; default is
            "current" network. If an SUID is provided, the corresponding network name is used.
        target_network (SUID or str or None): Name of the network to apply coordinates to; default is
            "current" network. If an SUID is provided, the corresponding network name is used.
        source_column (str): The name of column in the source_network node table used to match nodes;
            default is 'name'
        target_column (str): The name of column in the target_network node table used to match nodes; default is 'name'
        grid_unmapped (bool): If this is set to True, any nodes in the target network that could not be matched
            to a node in the source network will be laid out in a grid; default is True
        select_unmapped (bool): If this is set to True, any nodes in the target network that could not be matched
            to a node in the source network will be selected in the target network; default is True
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'mappedNodeCount': 330, 'unmappedNodeCount': 0} containing count of nodes coordinates modified

    Raises:
        CyError: if source_network, target_network, source_column or target_column are invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> layout_copycat('galFiltered.sif', galFiltered.sif_1)
        {'mappedNodeCount': 330, 'unmappedNodeCount': 0}
        >>> layout_copycat('galFiltered.sif', galFiltered.sif_1, source_column='shared name', target_column='shared name')
        {'mappedNodeCount': 330, 'unmappedNodeCount': 0}
    """
    source_network = networks.get_network_name(source_network)
    target_network = networks.get_network_name(target_network)
    res = commands.commands_post(
        f'layout copycat sourceNetwork="{source_network}" targetNetwork="{target_network}" sourceColumn="{source_column}" targetColumn="{target_column}" gridUnmapped="{grid_unmapped}" selectUnmapped="{select_unmapped}"',
        base_url=base_url)
    return res


# ==============================================================================
# II. Get layout properties
# ------------------------------------------------------------------------------

@cy_log
def get_layout_names(base_url=DEFAULT_BASE_URL):
    """Retrieve the names of the currently supported layout algorithms.

    These may be used in subsequent calls to the ``layout_network`` function.

    Note that yFiles layouts are not available due to licensing restrictions with yWorks, the owner of yFiles.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: a list of layout names as strings

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_layout_names()
        ['attribute-circle', 'stacked-node-layout', 'degree-circle', 'circular', 'attributes-layout', 'kamada-kawai', 'force-directed', 'cose', 'grid', 'hierarchical', 'fruchterman-rheingold', 'isom']
    """
    res = commands.cyrest_get('apply/layouts', base_url=base_url)
    return res


@cy_log
def get_layout_name_mapping(base_url=DEFAULT_BASE_URL):
    """Get Layout Name Mapping.

    The Cytoscape 'Layout' menu lists many layout algorithms, but the names presented there are different
    from the names by which these algorithms are known to ```layout_network``` method. This
    method returns a named list in which the names are from the GUI, and the values identify the
    names you must use to choose an algorithms in the programmatic interface.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {gui-layout-name: layout_name, ...}

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_layout_name_mapping()
        {'Attribute Circle Layout': 'attribute-circle', 'Stacked Node Layout': 'stacked-node-layout' ...}
    """
    layout_names = get_layout_names(base_url=base_url)
    layout_mapping = {}

    # get the full name of a layout and create {fullname:layoutname} in dictionary
    for layout_name in layout_names:
        res = commands.cyrest_get(f'apply/layouts/{layout_name}', base_url=base_url)
        layout_mapping.update({res['longName']: layout_name})

    return layout_mapping


@cy_log
def get_layout_property_names(layout_name, base_url=DEFAULT_BASE_URL):
    """Returns a list of the tunable properties for the specified layout.

    Run ``getLayoutNames`` to list available layouts

    Args:
        layout_name (str): Name of the layout
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: strings naming layout parameters

    Raises:
        requests.exceptions.RequestException: if layout_name is invalid or can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_layout_property_names('force-directed')
        ['numIterations', 'defaultSpringCoefficient', 'defaultSpringLength', 'defaultNodeMass', 'isDeterministic', 'singlePartition']
    """
    res = commands.cyrest_get(f'apply/layouts/{layout_name}/parameters', base_url=base_url)
    param_names = [param_def['name'] for param_def in res]
    return param_names


@cy_log
def get_layout_property_type(layout_name, property_name, base_url=DEFAULT_BASE_URL):
    """Returns the type of one of the tunable properties (property_name) for the specified layout.

    Run ``getLayoutNames`` to list available layouts. Run ``getLayoutPropertyNames`` to list properties per layout.

    Args:
        layout_name (str): Name of the layout
        property_name (str): Name of the property
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: strings naming layout parameters

    Raises:
        KeyError: if property_name is invalid
        requests.exceptions.RequestException: if layout_name is invalid or can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_layout_property_names('force-directed','defaultSpringLength')
        "double"
    """
    res = commands.cyrest_get(f'apply/layouts/{layout_name}/parameters', base_url=base_url)
    param_types = {param['name']: param['type'] for param in res}
    return param_types[property_name]


@cy_log
def get_layout_property_value(layout_name, property_name, base_url=DEFAULT_BASE_URL):
    """Returns the appropriately typed value of the specified tunable property for the specified layout.

    Run ``getLayoutNames`` to list available layouts. Run ``getLayoutPropertyNames`` to list properties per layout.

    Args:
        layout_name (str): Name of the layout
        property_name (str): Name of the property
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: strings naming layout parameters

    Raises:
        KeyError: if property_name is invalid
        requests.exceptions.RequestException: if layout_name is invalid or can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_layout_property_value('force-directed','defaultSpringLength')
        50
    """
    res = commands.cyrest_get(f'apply/layouts/{layout_name}/parameters', base_url=base_url)
    param_values = {param['name']: param['value'] for param in res}
    return param_values[property_name]


# ==============================================================================
# III. Set layout properties
# ------------------------------------------------------------------------------------------------------------------------

@cy_log
def set_layout_properties(layout_name, properties_dict, base_url=DEFAULT_BASE_URL):
    """Sets the specified properties for the specified layout.

    Unmentioned properties are left unchanged.

    Run ``getLayoutNames`` to list available layouts. Run ``getLayoutPropertyNames`` to list properties per layout.

    Args:
        layout_name (str): Name of the layout
        properties_dict (dict): List of one or more ``property=value`` pairs
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        requests.exceptions.RequestException: if layout_name is invalid or can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_layout_properties('force-directed', {'defaultSpringLength': 50, 'defaultSpringCoefficient': 6E-01})
        ''
    """
    all_possible_properties = get_layout_property_names(layout_name)

    res = ''
    for prop, value in properties_dict.items():
        if not prop in all_possible_properties:
            raise CyError(f'"{prop}" is not a property in layout "{layout_name}"')
        else:
            each_property = [{'name': prop, 'value': value}]
            res = commands.cyrest_put(f'apply/layouts/{layout_name}/parameters', body=each_property,
                                      base_url=base_url, require_json=False)
    return res
