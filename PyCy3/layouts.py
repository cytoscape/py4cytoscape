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
# ' @title Bundle Edges
# '
# ' @description Apply edge bundling to the network specified. Edge bundling is
# ' executed with default parameters; optional parameters are not supported.
# ' @param network (optional) Name or SUID of the network. Default is the "current"
# ' network active in Cytoscape.
# ' @param base.url (optional) Ignore unless you need to specify a custom domain,
# ' port or version to connect to the CyREST API. Default is http://localhost:1234
# ' and the latest version of the CyREST API supported by this version of RCy3.
# ' @return None
# ' @examples \donttest{
# ' bundleEdges()
# ' }
# ' @export
def bundle_edges(network=None, base_url=DEFAULT_BASE_URL):
    raise CyError('Not implemented')  # TODO: implement bundle_edges

# ------------------------------------------------------------------------------
# ' @title Clear Edge Bends
# '
# ' @description Clear all edge bends, e.g., those created from edge bundling.
# ' @param network (optional) Name or SUID of the network. Default is the "current"
# ' network active in Cytoscape.
# ' @param base.url (optional) Ignore unless you need to specify a custom domain,
# ' port or version to connect to the CyREST API. Default is http://localhost:1234
# ' and the latest version of the CyREST API supported by this version of RCy3.
# ' @return None
# ' @examples \donttest{
# ' clearEdgeBends()
# ' }
# ' @export
def clear_edge_bends(network=None, base_url=DEFAULT_BASE_URL):
    raise CyError('Not implemented')  # TODO: implement clear_edge_bends

def layout_network(layout_name=None, network=None, base_url=DEFAULT_BASE_URL):
    """Apply a layout to a network.

    Run ``getLayoutNames`` to list available layouts.

    Args:
        layout_name (str): Name of the layout (with optional parameters). If not specified,
            then the preferred layout set in the Cytoscape UI is applied.
        network (SUID or str or None): Name of the network; default is "current" network. If an SUID is
            provided, then it is validated and returned.
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

# ------------------------------------------------------------------------------
# ' @title Copy a layout from one network to another
# '
# ' @description Sets the coordinates for each node in the target network to the
# ' coordinates of a matching node in the source network.
# ' @details Optional parameters such as \code{gridUnmapped} and \code{selectUnmapped}
# ' determine the behavior of target network nodes that could not be matched.
# ' @param sourceNetwork (\code{character}) The name of network to get node coordinates from
# ' @param targetNetwork (\code{character}) The name of the network to apply coordinates to
# ' @param sourceColumn (optional \code{character}) The name of column in the sourceNetwork node
# ' table used to match nodes; default is 'name'
# ' @param targetColumn (optional \code{character}) The name of column in the targetNetwork node
# ' table used to match nodes; default is 'name'
# ' @param gridUnmapped (optional \code{character}) If this is set to true, any nodes in the target
# ' network that could not be matched to a node in the source network will be laid out in a grid;
# ' default is TRUE
# ' @param selectUnmapped optional \code{character}) If this is set to true, any nodes in the target network
# ' that could not be matched to a node in the source network will be selected in the target network;
# ' default is TRUE
# ' @param base.url (optional) Ignore unless you need to specify a custom domain,
# ' port or version to connect to the CyREST API. Default is http://localhost:1234
# ' and the latest version of the CyREST API supported by this version of RCy3.
# ' @return None
# ' @examples
# ' \donttest{
# ' layoutCopycat('network1','network2')
# ' }
# ' @export
def layout_copycat(source_network, target_network, source_column='name', target_column='name',
                           grid_unmapped=True, select_unmapped=True, base_url=DEFAULT_BASE_URL):
    raise CyError('Not implemented')  # TODO: implement layout_copycat


# ==============================================================================
# II. Get layout properties
# ------------------------------------------------------------------------------
# ' @title Get Layout Names
# '
# ' @description Retrieve the names of the currently supported layout algorithms.  These
# ' may be used in subsequent calls to the 'layoutNetwork' function.
# ' @param base.url (optional) Ignore unless you need to specify a custom domain,
# ' port or version to connect to the CyREST API. Default is http://localhost:1234
# ' and the latest version of the CyREST API supported by this version of RCy3.
# ' @return A \code{list} of \code{character} strings, e.g., "force-directed" "circular" "grid"
# ' @author Alexander Pico, Tanja Muetze, Georgi Kolishovski, Paul Shannon
# ' @examples \donttest{
# ' getLayoutNames()
# ' # [1] "degree-circle"         "attributes-layout"      "kamada-kawai"
# ' # [4] "force-directed"        "cose"                   "hierarchical"
# ' # [7] "attribute-circle"      "stacked-node-layout"    "circular"
# ' }
# ' @export
def get_layout_names(base_url=DEFAULT_BASE_URL):
    raise CyError('Not implemented')  # TODO: implement get_layout_names


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

