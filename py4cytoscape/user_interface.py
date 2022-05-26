# -*- coding: utf-8 -*-

"""Functions affecting the USER INTERFACE, such as panel management.
"""

"""Dev Note: ui/lod is toggleGraphicsDetails() in NetworkViews.R
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

# Internal module imports
from . import commands

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log


@cy_log
def dock_panel(panel_name, base_url=DEFAULT_BASE_URL):
    """Dock a panel back into the UI of Cytoscape.

    Args:
        panel_name (str): Name of the panel. Multiple ways of referencing panels is supported:
           (WEST == control panel, control, c), (SOUTH == table panel, table, ta), (SOUTH_WEST == tool panel, tool, to), (EAST == results panel, results, r)
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if panel name is not recognized
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> dock_panel('control panel')
        ''
        >>> dock_panel('WEST')
        ''
    """
    panel_name = _check_panel_name(panel_name)
    panel_name_state = {'name': panel_name, 'state': 'DOCK'}
    res = commands.cyrest_put('ui/panels', body=[panel_name_state], base_url=base_url, require_json=False)
    return res


@cy_log
def float_panel(panel_name, base_url=DEFAULT_BASE_URL):
    """Pop out a panel from the UI of Cytoscape.

    Other panels will expand into the space.

    Args:
        panel_name (str): Name of the panel. Multiple ways of referencing panels is supported:
           (WEST == control panel, control, c), (SOUTH == table panel, table, ta), (SOUTH_WEST == tool panel, tool, to), (EAST == results panel, results, r)
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if panel name is not recognized
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> float_panel('control panel')
        ''
        >>> float_panel('WEST')
        ''
    """
    panel_name = _check_panel_name(panel_name)
    panel_name_state = {'name': panel_name, 'state': 'FLOAT'}
    res = commands.cyrest_put('ui/panels', body=[panel_name_state], base_url=base_url, require_json=False)
    return res


@cy_log
def hide_panel(panel_name, base_url=DEFAULT_BASE_URL):
    """Hide a panel in the UI of Cytoscape.

    Other panels will expand into the space.

    Args:
        panel_name (str): Name of the panel. Multiple ways of referencing panels is supported:
           (WEST == control panel, control, c), (SOUTH == table panel, table, ta), (SOUTH_WEST == tool panel, tool, to), (EAST == results panel, results, r)
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        CyError: if panel name is not recognized
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> hide_panel('control panel')
        ''
        >>> hide_panel('WEST')
        ''
    """
    panel_name = _check_panel_name(panel_name)
    panel_name_state = {'name': panel_name, 'state': 'HIDE'}
    res = commands.cyrest_put('ui/panels', body=[panel_name_state], base_url=base_url, require_json=False)
    return res


@cy_log
def hide_all_panels(base_url=DEFAULT_BASE_URL):
    """Hide control, table, tool and results panels.

    Args:
        panel_name (str): Name of the panel. Multiple ways of referencing panels is supported:
           (WEST == control panel, control, c), (SOUTH == table panel, table, ta), (SOUTH_WEST == tool panel, tool, to), (EAST == results panel, results, r)
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        None

    Raises:
        CyError: if panel name is not recognized
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> hide_all_panels()
        ''
        >>> hide_all_panels()
        ''
    """
    hide_panel("SOUTH", base_url=base_url)
    hide_panel("EAST", base_url=base_url)
    hide_panel("WEST", base_url=base_url)
    hide_panel("SOUTH_WEST", base_url=base_url)


# ------------------------------------------------------------------------------
# internal utility function to validate and support references to panels by name
def _check_panel_name(panel_name):
    if panel_name.lower() in {'table panel', 'table', 'ta'}:
        panel_name = 'SOUTH'
    elif panel_name.lower() in {'tool panel', 'tool', 'to'}:
        panel_name = 'SOUTH_WEST'
    elif panel_name.lower() in {'control panel', 'control', 'c'}:
        panel_name = 'WEST'
    elif panel_name.lower() in {'results panel', 'results', 'r'}:
        panel_name = 'EAST'
    elif panel_name in {'WEST', 'EAST', 'SOUTH', 'SOUTH_WEST'}:
        pass
    else:
        raise CyError(f'Panel name "{panel_name}" is invalid. Common panel names include SOUTH, EAST, WEST and SOUTH_WEST.')

    return panel_name
