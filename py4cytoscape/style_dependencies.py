# -*- coding: utf-8 -*-

"""# Functions for getting and setting style DEPEDENDENCIES, organized into sections:

I. General functions for getting and setting dependencies
II. Specific functions for setting particular dependencies
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

# External library imports
import sys
import time

# Internal module imports
from . import commands
from . import styles

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log
from .py4cytoscape_tuning import MODEL_PROPAGATION_SECS

# ==============================================================================
# I. General Functions
# ------------------------------------------------------------------------------

@cy_log
def get_style_dependencies(style_name=None, base_url=DEFAULT_BASE_URL):
    """Get the values of dependencies in a style.

    Args:
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: contains all dependencies and their current boolean value

    Raises:
        CyError: if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_style_dependencies(style_name='galFiltered Style')
        {'arrowColorMatchesEdge': False, 'nodeCustomGraphicsSizeSync': True, 'nodeSizeLocked': True}
        >>> get_style_dependencies()
        {'arrowColorMatchesEdge': False, 'nodeCustomGraphicsSizeSync': True, 'nodeSizeLocked': False}
    """
    if style_name is None:
        style_name = 'default'
        narrate(f'style_name not specified, so accessing "default" style.')

    # launch error if visual style name is missing
    if style_name not in styles.get_visual_style_names(base_url=base_url):
        raise CyError(f'No visual style named "{style_name}"')

    res = commands.cyrest_get(f'styles/{style_name}/dependencies', base_url=base_url)

    # make it a dict
    dep_list = {dep['visualPropertyDependency']: dep['enabled'] for dep in res}
    return dep_list

@cy_log
def set_style_dependencies(style_name=None, dependencies={}, base_url=DEFAULT_BASE_URL):
    """Set the values of dependencies in a style, overriding any prior setting.

    Args:
        style_name (str): Name of style; default is "default" style
        dependencies (dict): A ``list`` of style dependencies, see Available Dependencies below. Note: each dependency
            is set by a boolean, True or False
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: contains the ``views`` property with a value of the current view's SUID (e.g., {'views': [275240]})

    Raises:
        CyError: if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_style_dependencies(dependencies={'arrowColorMatchesEdge': True}, style_name='galFiltered Style')
        {'views': [275240]}
        >>> set_style_dependencies(dependencies={'arrowColorMatchesEdge': True, 'nodeCustomGraphicsSizeSync': False})
        {'views': [275240]}

    Available Dependencies:
        arrowColorMatchesEdge, nodeCustomGraphicsSizeSync, nodeSizeLocked
    """
    if style_name is None:
        style_name = 'default'
        narrate(f'style_name not specified, so updating "default" style.')

    # launch error if visual style name is missing
    if style_name not in styles.get_visual_style_names(base_url=base_url):
        raise CyError(f'No visual style named "{style_name}"')

    dep_list = [{'visualPropertyDependency': dep, 'enabled': val}    for dep, val in dependencies.items()]

    res = commands.cyrest_put(f'styles/{style_name}/dependencies', body=dep_list, base_url=base_url, require_json=False)
    res = commands.commands_post(f'vizmap apply styles="{style_name}"', base_url=base_url)
    # TODO: Do we really want to lose the first res value?
    return res


# ==============================================================================
# II. Specific Functions
# Pattern: (1) Call setStyleDependencies()
# ------------------------------------------------------------------------------

@cy_log
def match_arrow_color_to_edge(new_state, style_name=None, base_url=DEFAULT_BASE_URL):
    """Set a boolean value to have arrow shapes share the same color as the edge.

    Args:
        new_state (bool): Whether to match arrow color to edge.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: contains the ``views`` property with a value of the current view's SUID (e.g., {'views': [275240]})

    Raises:
        CyError: if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> match_arrow_color_to_edge(True, style_name='galFiltered Style')
        {'views': [275240]}
        >>> match_arrow_color_to_edge(False)
        {'views': [275240]}
    """
    toggle = 'true' if new_state else 'false'

    res = set_style_dependencies(style_name=style_name, dependencies={'arrowColorMatchesEdge': toggle}, base_url=base_url)

    return res

@cy_log
def lock_node_dimensions(new_state, style_name=None, base_url=DEFAULT_BASE_URL):
    """Set a boolean value to have node width and height fixed to a single size value.

    Args:
        new_state (bool): Whether to lock node width and height
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: contains the ``views`` property with a value of the current view's SUID (e.g., {'views': [275240]})

    Raises:
        CyError: if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> lock_node_dimensions(True, style_name='galFiltered Style')
        {'views': [275240]}
        >>> lock_node_dimensions(False)
        {'views': [275240]}
    """
    toggle = 'true' if new_state else 'false'

    res = set_style_dependencies(style_name=style_name, dependencies={'nodeSizeLocked': toggle}, base_url=base_url)

    return res

@cy_log
def sync_node_custom_graphics_size(new_state, style_name=None, base_url=DEFAULT_BASE_URL):
    """Set a boolean value to have the size of custom graphics match that of the node.

    Args:
        new_state (bool): Whether to sync node custom graphics size
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: contains the ``views`` property with a value of the current view's SUID (e.g., {'views': [275240]})

    Raises:
        CyError: if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> sync_node_custom_graphics_size(True, style_name='galFiltered Style')
        {'views': [275240]}
        >>> sync_node_custom_graphics_size(False)
        {'views': [275240]}
    """
    toggle = 'true' if new_state else 'false'

    res = set_style_dependencies(style_name=style_name, dependencies={'nodeCustomGraphicsSizeSync': toggle}, base_url=base_url)

    return res
