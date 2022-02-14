# -*- coding: utf-8 -*-

"""Functions for working with ANNOTATIONS for the addition and modification of
graphical annotation objects. In the Cytoscape user interface, annotations are
managed in the Annotation tab of the Control Panel.
"""

"""Copyright 2022 The Cytoscape Consortium

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
# import base64
# import os
# import time

# Internal module imports
from . import commands
from . import networks
from . import network_views
from . import style_values

# Internal module convenience imports
# from .exceptions import CyError
# from .py4cytoscape_sandbox import *
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log

@cy_log
def add_annotation_text(text=None, x_pos=None, y_pos=None, font_size=None, font_family=None, font_style=None,
                        color=None, angle=None, name=None, canvas=None, z_order=None, network=None,
                        base_url=DEFAULT_BASE_URL):
    """Add Text Annotation

    Adds a text annotation to a Cytoscape network view. The object will also be added to the
    Annotation Panel in the GUI.

    Args:
        text (str): The text to be displayed
        x_pos (int): X position in pixels from left; default is center of current view
        y_pos (int): Y position in pixels from top; default is center of current view
        font_size (int): Numeric value; default is 12
        font_family (str): Font family; default is Arial
        font_style (str): Font style; default is none
        color (str): Hexidecimal color; default is #000000 (black)
        angle (float): Angle of text orientation; default is 0.0 (horizontal)
        name (str): Name of annotation object; default is "Text"
        canvas (str): Canvas to display annotation, i.e., foreground (default) or background
        z_order (int): Arrangement order specified by number (larger values are in front of smaller values); default is 0
        network (SUID or str or None): Name or SUID of the network. Default is the "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: A named list of annotation properties, including UUID

    Raises:
        CyError: if network name doesn't exist
        requests.exceptions.HTTPError: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> add_annotation_text()
        >>> add_annotation_text(canvas='foreground', color='#000000', angle=41.0, font_style='plain', font_family='Arial', name='Text', x_pos=2168.2290309432974, y_pos=1823.4642987952689, z_order=0, font_size=14, text='Text')
        {'canvas': 'foreground', 'color': '#000000', 'rotation': '41.0', 'type': 'org.cytoscape.view.presentation.annotations.TextAnnotation', 'fontStyle': 'plain', 'uuid': '293eeee1-b7e1-4d6b-bcf8-fd17fd2a2e5c', 'fontFamily': 'Arial', 'name': 'Text', 'x': '2168.2290309432974', 'y': '1823.4642987952689', 'z': '0', 'fontSize': '14', 'text': 'Text'}
    """

    cmd_string = 'annotation add text'  # a good start

    net_SUID = networks.get_network_suid(network, base_url=base_url)
    view_SUID = network_views.get_network_view_suid(net_SUID, base_url=base_url)

    # add view
    cmd_string += f' view="SUID:{view_SUID}"'

    # add type
    cmd_string += f' type="org.cytoscape.view.presentation.annotations.TextAnnotation"'

    # text to add
    if text is None:
        raise CyError("Must provide the text string to add.")
    cmd_string += f' text="{text}"'

    # x and y position
    if x_pos is None:
        x_pos = style_values.get_network_center(net_SUID, base_url=base_url)['x']
    if y_pos is None:
        y_pos = style_values.get_network_center(net_SUID, base_url=base_url)['y']
    cmd_string += f' x="{x_pos}" y="{y_pos}"'

    # optional params
    if font_size is not None:
        verify_positive(font_size)
        cmd_string += f' fontSize="{font_size}"'

    if font_family is not None:
        cmd_string += f' fontFamily="{font_family}"'

    if font_style is not None:
        verify_font_style(font_style)
        cmd_string += f' fontStyle="{font_style}"'

    if color is not None:
        verify_hex_color(color)
        cmd_string += f' color="{color}"'

    if angle is not None:
        rotation = normalize_rotation(angle)
        cmd_string += f' angle="{rotation}"'

    if name is not None:
        all_annotations = get_annotation_list(network, base_url=base_url)
        all_names = [x['name'] for x in all_annotations]
        verify_unique(name, all_names)
        cmd_string += f' newName="{name}"'

    if canvas is not None:
        verify_canvas(canvas)
        cmd_string += f' canvas="{canvas}"'

    if z_order is not None:
        if not (isinstance(z_order, float) or isinstance(z_order, int)):
            raise CyError(f'{z_order} is invalid. Z order must be a number.')
        cmd_string += f' z="{z_order}"'

    # execute command
    res = commands.commands_post(cmd_string, base_url=base_url)

    return res

@cy_log
def get_annotation_list(network=None, base_url=DEFAULT_BASE_URL):
    """Get Annotation List

    A list of named lists with annotation information

    Args:
        network (SUID or str or None): Name or SUID of the network. Default is the "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: List of annotation records

    Raises:
        CyError: if network name doesn't exist
        requests.exceptions.HTTPError: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_annotation_list()
        [{'canvas': 'foreground', 'color': '#000000', 'rotation': '41.0', 'type': 'org.cytoscape.view.presentation.annotations.TextAnnotation', 'fontStyle': 'plain', 'uuid': '92aafea6-0653-4df1-a017-cf3edfa5fdc8', 'fontFamily': 'Arial', 'name': 'TextExample', 'x': '2168', 'y': '1823', 'z': '0', 'fontSize': '14', 'text': 'Text'}, ...]
    """

    cmd_string = 'annotation list'  # a good start

    net_SUID = networks.get_network_suid(network, base_url=base_url)
    view_SUID = network_views.get_network_view_suid(net_SUID, base_url=base_url)

    # add view
    cmd_string += f' view="SUID:{view_SUID}"'

    res = commands.commands_post(cmd_string, base_url=base_url)

    return res
