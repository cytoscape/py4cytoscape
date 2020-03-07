# -*- coding: utf-8 -*-

"""Functions for performing LAYOUTS in addition to getting and setting layout properties.

I. Perform layout functions
II. Get layout properties
III. Set layout properties
"""

from . import commands
from . import networks
from .exceptions import CyError
from .pycy3_utils import DEFAULT_BASE_URL

# ==============================================================================
# I. Perform layout functions
# ------------------------------------------------------------------------------

def bundle_edges(network=None, base_url=DEFAULT_BASE_URL):
    """Apply edge bundling to the network specified.

    Edge bundling is executed with default parameters; optional parameters are not supported.

    Args:
        network (SUID or str or None): Name or SUID of the network; default is "current" network.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

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
    res = commands.cyrest_get('apply/edgebundling/' + str(suid), base_url=base_url)
    return res


def clear_edge_bends(network=None, base_url=DEFAULT_BASE_URL):
    """Clear all edge bends created from edge bundling.

    Args:
        network (SUID or str or None): Name or SUID of the network; default is "current" network.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

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
    res = commands.cyrest_get('apply/clearalledgebends/' + str(suid), base_url=base_url)
    return res

def layout_network(layout_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Apply a layout to a network.

    Run ``getLayoutNames`` to list available layouts.

    Args:
        layout_name (str): Name of the layout (with optional parameters). If not specified,
            then the preferred layout set in the Cytoscape UI is applied.
        network (SUID or str or None): Name or SUID of the network; default is "current" network.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

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
        res = commands.commands_post('layout apply preferred networkSelected="SUID:' + str(suid) + '"', base_url=base_url)
        return res
    else:
        res = commands.commands_post('layout ' + layout_name + ' network="SUID:' + str(suid) + '"', base_url=base_url)
        return res

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
            and the latest version of the CyREST API supported by this version of PyCy3.

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
    res = commands.commands_post('layout copycat sourceNetwork="' + source_network + '" targetNetwork="' + target_network +
                                 '" sourceColumn="' + source_column + '" targetColumn="' + target_column +
                                 '" gridUnmapped="' + str(grid_unmapped) + '" selectUnmapped="' + str(select_unmapped),
                        base_url=base_url)
    return res

# ==============================================================================
# II. Get layout properties
# ------------------------------------------------------------------------------

def get_layout_names(base_url=DEFAULT_BASE_URL):
    """Retrieve the names of the currently supported layout algorithms.

    These may be used in subsequent calls to the ``layout_network`` function.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

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


# ------------------------------------------------------------------------------
# ' @title Get Layout Name Mapping
# '
# ' @description The Cytoscape 'Layout' menu lists many layout algorithms, but the names presented
# ' there are different from the names by which these algorithms are known to layout method. This
# ' method returns a named list in which the names are from the GUI, and the values identify the
# ' names you must use to choose an algorithms in the programmatic interface.
# ' @param base.url (optional) Ignore unless you need to specify a custom domain,
# ' port or version to connect to the CyREST API. Default is http://localhost:1234
# ' and the latest version of the CyREST API supported by this version of RCy3.
# ' @return A named \code{list} of \code{character} strings
# ' @author Alexander Pico, Tanja Muetze, Georgi Kolishovski, Paul Shannon
# ' @examples \donttest{
# ' getLayoutNameMapping()
# ' # Degree Sorted Circle Layout    Group Attributes Layout    Edge-weighted Spring Embedded Layout
# ' #              "degree-circle"       "attributes-layout"                          "kamada-kawai"
# ' }
# ' @export
def get_layout_name_mapping(base_url=DEFAULT_BASE_URL):
    raise CyError('Not implemented')  # TODO: implement get_layout_name_mapping

# ------------------------------------------------------------------------------
# ' @title Get Layout Property Names
# '
# ' @description Returns a list of the tunable properties for the specified layout.
# ' @details Run \link{getLayoutNames} to list available layouts.
# ' @param layout.name (\code{character}) Name of the layout
# ' @param base.url (optional) Ignore unless you need to specify a custom domain,
# ' port or version to connect to the CyREST API. Default is http://localhost:1234
# ' and the latest version of the CyREST API supported by this version of RCy3.
# ' @return A \code{list} of \code{character} strings
# ' @author Alexander Pico, Tanja Muetze, Georgi Kolishovski, Paul Shannon
# ' @examples \donttest{
# ' getLayoutPropertyNames('force-directed')
# ' # [1] "numIterations"            "defaultSpringCoefficient" "defaultSpringLength"
# ' # [4] "defaultNodeMass"          "isDeterministic"          "singlePartition"
# ' }
# ' @export
def get_layout_property_names(layout_name, base_url=DEFAULT_BASE_URL):
    raise CyError('Not implemented')  # TODO: implement get_layout_property_names

# ------------------------------------------------------------------------------
# ' @title Get Layout Property Type
# '
# ' @description Returns the type of one of the tunable properties (property.name) for the specified layout.
# ' @details Run \link{getLayoutNames} to list available layouts. Run \link{getLayoutPropertyNames} to list properties per layout.
# ' @param layout.name (\code{character}) Name of the layout
# ' @param property.name (\code{character}) Name of the property
# ' @param base.url (optional) Ignore unless you need to specify a custom domain,
# ' port or version to connect to the CyREST API. Default is http://localhost:1234
# ' and the latest version of the CyREST API supported by this version of RCy3.
# ' @return A \code{character} string specifying the type
# ' @author Alexander Pico, Tanja Muetze, Georgi Kolishovski, Paul Shannon
# ' @examples \donttest{
# ' getLayoutPropertyType('force-directed','defaultSpringLength')
# ' # "double"
# ' }
# ' @export
def get_layout_property_type(layout_name, property_name, base_url=DEFAULT_BASE_URL):
    raise CyError('Not implemented')  # TODO: implement get_layout_property_type

# ------------------------------------------------------------------------------------------------------------------------
# ' @title Get Layout Property Value
# '
# ' @description Returns the appropriately typed value of the specified tunable property for the specified layout.
# ' @details Run \link{getLayoutNames} to list available layouts. Run \link{getLayoutPropertyNames} to list properties per layout.
# ' @param layout.name (\code{character}) Name of the layout
# ' @param property.name (\code{character}) Name of the property
# ' @param base.url (optional) Ignore unless you need to specify a custom domain,
# ' port or version to connect to the CyREST API. Default is http://localhost:1234
# ' and the latest version of the CyREST API supported by this version of RCy3.
# ' @return The current value set for this layout property. Typically an \code{integer}, \code{numeric} or \code{character} string value.
# ' @author Alexander Pico, Tanja Muetze, Georgi Kolishovski, Paul Shannon
# ' @examples \donttest{
# ' getLayoutPropertyValue('force-directed','defaultSpringLength')
# ' # 80
# ' }
# ' @export
def get_layout_property_value(layout_name, property_name, base_url=DEFAULT_BASE_URL):
    raise CyError('Not implemented')  # TODO: implement get_layout_property_value

# ==============================================================================
# III. Set layout properties
# ------------------------------------------------------------------------------------------------------------------------
# ' @title Set Layout Properties
# '
# ' @description Sets the specified properties for the specified layout. Unmentioned properties are left unchanged.
# ' @details Run \link{getLayoutNames} to list available layouts. Run \link{getLayoutPropertyNames} to list properties per layout.
# ' @param layout.name (\code{character}) Name of the layout
# ' @param properties.list (\code{list}) List of one or more \code{property=value} pairs
# ' @param base.url (optional) Ignore unless you need to specify a custom domain,
# ' port or version to connect to the CyREST API. Default is http://localhost:1234
# ' and the latest version of the CyREST API supported by this version of RCy3.
# ' @return None
# ' @author Alexander Pico, Tanja Muetze, Georgi Kolishovski, Paul Shannon
# ' @examples \donttest{
# ' setLayoutProperties('force-directed', list(defaultSpringLength=50, defaultSpringCoefficient=6E-04))
# ' # Successfully updated the property 'defaultSpringLength'.
# ' # Successfully updated the property 'defaultSpringCoefficient'.
# ' }
# ' @export
def set_layout_properties(layout_name, properties_list, base_url=DEFAULT_BASE_URL):
    raise CyError('Not implemented')  # TODO: implement set_layout_properties

