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
import re

# Internal module imports
from . import commands
from . import networks
from . import network_views
from . import style_values
from . import styles
from . import sandbox

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
        color (str): hexadecimal color; default is #000000 (black)
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
        CyError: if network name doesn't exist or error in parameter value
        requests.exceptions.HTTPError: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> add_annotation_text(text='ann1')
        {'canvas': 'foreground', 'color': '#000000', 'rotation': '0.0', 'type': 'org.cytoscape.view.presentation.annotations.TextAnnotation', 'fontStyle': 'plain', 'uuid': '62748d4f-f412-423d-aa95-e269f0e4722c', 'fontFamily': 'Arial', 'name': 'Text', 'x': '2449.9784057344455', 'y': '1882.9888145962157', 'z': '0', 'fontSize': '12', 'text': 'ann1'}
        >>> add_annotation_text(canvas='foreground', color='#000000', angle=41.0, font_style='plain', font_family='Arial', name='Text', x_pos=2168.2290309432974, y_pos=1823.4642987952689, z_order=0, font_size=14, text='Text')
        {'canvas': 'foreground', 'color': '#000000', 'rotation': '41.0', 'type': 'org.cytoscape.view.presentation.annotations.TextAnnotation', 'fontStyle': 'plain', 'uuid': '293eeee1-b7e1-4d6b-bcf8-fd17fd2a2e5c', 'fontFamily': 'Arial', 'name': 'Text', 'x': '2168.2290309432974', 'y': '1823.4642987952689', 'z': '0', 'fontSize': '14', 'text': 'Text'}
    """

    cmd_string, net_SUID = _build_base_cmd_string('annotation add text', network, base_url)  # a good start

    # add type
    cmd_string += f' type="org.cytoscape.view.presentation.annotations.TextAnnotation"'

    # text to add
    cmd_string += _get_text_cmd_string(text)

    # x and y position
    cmd_string += _get_x_y_pos_cmd_string(x_pos, y_pos, net_SUID, base_url)

    # optional params
    cmd_string += _get_font_cmd_string(font_size, font_family, font_style)

    cmd_string += _get_color_cmd_string(color)

    cmd_string += _get_angle_cmd_string(angle)

    cmd_string += _get_name_cmd_string(name, network, base_url)

    cmd_string += _get_canvas_cmd_string(canvas)

    cmd_string += _get_z_order_cmd_string(z_order)

    # execute command
    res = commands.commands_post(cmd_string, base_url=base_url)

    return res

@cy_log
def add_annotation_bounded_text(text=None, x_pos=None, y_pos=None, font_size=None, font_family=None, font_style=None,
                        color=None, angle=None, type=None, custom_shape=None, fill_color=None, opacity=None,
                        border_thickness=None, border_color=None, border_opacity=None, height=None, width=None,
                        name=None, canvas=None, z_order=None, network=None,
                        base_url=DEFAULT_BASE_URL):
    """Add Bounded Text Annotation

    Adds a bounded text annotation to a Cytoscape network view. The object will also be added to the
    Annotation Panel in the GUI.

    Args:
        text (str): The text to be displayed
        x_pos (int): X position in pixels from left; default is center of current view
        y_pos (int): Y position in pixels from top; default is center of current view
        font_size (int): Numeric value; default is 12
        font_family (str): Font family; default is Arial
        font_style (str): Font style; default is none
        color (str): hexadecimal color; default is #000000 (black)
        angle (float): Angle of text orientation; default is 0.0 (horizontal)
        type (str): The type of the shape, default is RECTANGLE. Seee get_node_shapes() for valid options
        custom_shape (str): If a custom shape, this is the text of the shape
        fill_color (str): hexadecimal color; default is #000000 (black)
        opacity (int): Opacity of fill color. Must be an integer between 0 and 100; default is 100
        border_thickness (int): non-negative integer
        border_color (str): hexadecimal color; default is #000000 (black)
        border_opacity (int): Integer between 0 and 100; default is 100
        height (int): Height of bounding shape; default is based on text height
        width (int) Width of bounding shape; default is based on text length
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
        CyError: if network name doesn't exist or error in parameter value
        requests.exceptions.HTTPError: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> add_annotation_bounded_text(text='ann1')
        {'edgeThickness': '1.0', 'canvas': 'foreground', 'fillOpacity': '100.0', 'color': '#000000', 'rotation': '0.0', 'type': 'org.cytoscape.view.presentation.annotations.BoundedTextAnnotation', 'fontStyle': 'plain', 'uuid': '250660b5-f371-48a6-9942-bdacacf1ec8a', 'shapeType': 'RECTANGLE', 'edgeColor': '#000000', 'fontFamily': 'Arial', 'edgeOpacity': '100.0', 'name': 'ann1', 'x': '2449.9784057344455', 'width': '34.6953125', 'y': '1882.9888145962157', 'z': '0', 'fontSize': '12', 'text': 'ann1', 'height': '21.798828125'}
        >>> add_annotation_bounded_text(text='ann3', x_pos=100, y_pos=200, font_size=25, font_family='Courier New', font_style='bold', color='#F0F0F0', angle=45, type='ELLIPSE', custom_shape=None, fill_color='#A0A0A0', opacity=50, border_thickness=2, border_color='#0F0F0F', border_opacity=75, height=30, width=31, name='ann3 name', canvas='background')
        {'edgeThickness': '2.0', 'canvas': 'background', 'fillOpacity': '50.0', 'color': '#F0F0F0', 'rotation': '45.0', 'type': 'org.cytoscape.view.presentation.annotations.BoundedTextAnnotation', 'fontStyle': 'bold', 'uuid': '5578e7b1-7edf-4588-824f-72d9dccfb215', 'fillColor': '#A0A0A0', 'shapeType': 'ELLIPSE', 'edgeColor': '#0F0F0F', 'fontFamily': 'Courier New', 'edgeOpacity': '75.0', 'name': 'ann3 name', 'x': '100.0', 'width': '31.0', 'y': '200.0', 'z': '0', 'fontSize': '25', 'text': 'ann3', 'height': '30.0'}
    """

    cmd_string, net_SUID = _build_base_cmd_string('annotation add bounded text', network, base_url)  # a good start

    # text to add
    cmd_string += _get_text_cmd_string(text)

    # x and y position
    cmd_string += _get_x_y_pos_cmd_string(x_pos, y_pos, net_SUID, base_url)

    # optional params
    cmd_string += _get_font_cmd_string(font_size, font_family, font_style)

    cmd_string += _get_color_cmd_string(color)

    cmd_string += _get_angle_cmd_string(angle)

    cmd_string += _get_type_cmd_string(type)

    cmd_string += _get_custom_shape_cmd_string(custom_shape)

    cmd_string += _get_fill_color_cmd_string(fill_color)

    cmd_string += _get_opacity_cmd_string(opacity)

    cmd_string += _get_border_cmd_string(border_thickness, border_color, border_opacity)

    cmd_string += _get_height_width_cmd_string(height, width)

    cmd_string += _get_name_cmd_string(name, network, base_url)

    cmd_string += _get_canvas_cmd_string(canvas)

    cmd_string += _get_z_order_cmd_string(z_order)

    # execute command
    res = commands.commands_post(cmd_string, base_url=base_url)

    return res

@cy_log
def add_annotation_image(url=None, x_pos=None, y_pos=None, angle=None, opacity=None, brightness=None, contrast=None,
                         border_thickness=None, border_color=None, border_opacity=None, height=None, width=None,
                        name=None, canvas=None, z_order=None, network=None,
                        base_url=DEFAULT_BASE_URL):
    """Add Image Annotation

    Adds an image annotation to a Cytoscape network view. The object will also be added to the
    Annotation Panel in the GUI.

    Args:
        url (str): URL or path to image file. File paths can be absolute or relative to current working directory or sandbox. URLs must start with http:// or https://.
        x_pos (int): X position in pixels from left; default is center of current view
        y_pos (int): Y position in pixels from top; default is center of current view
        angle (float): Angle of text orientation; default is 0.0 (horizontal)
        opacity (int): Opacity of fill color. Must be an integer between 0 and 100; default is 100
        brightness (int): Image brightness. Must be an integer between -100 and 100; default is 0.
        contrast (int): Image contrast. Must be an integer between -100 and 100; default is 0.
        border_thickness (int): non-negative integer
        border_color (str): hexadecimal color; default is #000000 (black)
        border_opacity (int): Integer between 0 and 100; default is 100
        height (int): Height of bounding shape; default is based on text height
        width (int) Width of bounding shape; default is based on text length
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
        CyError: if network name doesn't exist or error in parameter value
        requests.exceptions.HTTPError: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> add_annotation_image(url='https://www.ucsd.edu/_resources/img/logo_UCSD.png')
        {'edgeThickness': '1.0', 'canvas': 'foreground', 'rotation': '0.0', 'type': 'org.cytoscape.view.presentation.annotations.ImageAnnotation', 'uuid': '683b7c67-dcb3-459f-9505-b8ec05f3c76f', 'URL': 'https://www.ucsd.edu/_resources/img/logo_UCSD.png', 'shapeType': 'RECTANGLE', 'edgeColor': '#000000', 'brightness': '0', 'edgeOpacity': '100.0', 'contrast': '0', 'name': 'Image 1', 'x': '2449.9784057344455', 'width': '500.0', 'y': '1882.9888145962157', 'z': '0', 'opacity': '1.0', 'height': '100.0'}
        >>> add_annotation_image(url='https://www.ucsd.edu/_resources/img/logo_UCSD.png', x_pos=100, y_pos=200, angle=45, opacity=50, brightness=60, contrast=70, border_thickness=2, border_color='#0F0F0F', border_opacity=75, height=30, width=31, name='ann3 name', canvas='background')
        {'edgeThickness': '2.0', 'canvas': 'background', 'rotation': '45.0', 'type': 'org.cytoscape.view.presentation.annotations.ImageAnnotation', 'uuid': 'a67674cf-f787-4b7c-bae5-3a6b00a2f00c', 'URL': 'https://www.ucsd.edu/_resources/img/logo_UCSD.png', 'shapeType': 'RECTANGLE', 'edgeColor': '#0F0F0F', 'brightness': '60', 'edgeOpacity': '75.0', 'contrast': '70', 'name': 'ann3 name', 'x': '100.0', 'width': '31.0', 'y': '200.0', 'z': '0', 'opacity': '0.5', 'height': '30.0'}
    """

    cmd_string, net_SUID = _build_base_cmd_string('annotation add image', network, base_url)  # a good start

    # add type
    cmd_string += f' type="org.cytoscape.view.presentation.annotations.ImageAnnotation"'

    # Image to add
    cmd_string += _get_url_cmd_string(url)

    # x and y position
    cmd_string += _get_x_y_pos_cmd_string(x_pos, y_pos, net_SUID, base_url)

    # optional params
    cmd_string += _get_angle_cmd_string(angle)

    cmd_string += _get_opacity_cmd_string(opacity)

    cmd_string += _get_brightness_contrast_cmd_string(brightness, contrast)

    cmd_string += _get_border_cmd_string(border_thickness, border_color, border_opacity)

    cmd_string += _get_height_width_cmd_string(height, width)

    cmd_string += _get_name_cmd_string(name, network, base_url)

    cmd_string += _get_canvas_cmd_string(canvas)

    cmd_string += _get_z_order_cmd_string(z_order)

    # execute command
    res = commands.commands_post(cmd_string, base_url=base_url)

    return res

@cy_log
def add_annotation_shape(type=None, custom_shape=None, x_pos=None, y_pos=None, angle=None, fill_color=None, opacity=None,
                         border_thickness=None, border_color=None, border_opacity=None, height=None, width=None,
                         name=None, canvas=None, z_order=None, network=None,
                         base_url=DEFAULT_BASE_URL):
    """Add Shape Annotation

    Adds a shape annotation to a Cytoscape network view. The object will also be added to the
    Annotation Panel in the GUI.

    Args:
        type (str): The type of the shape, default is RECTANGLE. See get_node_shapes() for valid options.
        custom_shape (str): If a custom shape, this is the text of the shape
        x_pos (int): X position in pixels from left; default is center of current view
        y_pos (int): Y position in pixels from top; default is center of current view
        angle (float): Angle of text orientation; default is 0.0 (horizontal)
        fill_color (str): hexadecimal color; default is #000000 (black)
        opacity (int): Opacity of fill color. Must be an integer between 0 and 100; default is 100
        border_thickness (int): non-negative integer
        border_color (str): hexadecimal color; default is #000000 (black)
        border_opacity (int): Integer between 0 and 100; default is 100
        height (int): Height of bounding shape; default is based on text height
        width (int) Width of bounding shape; default is based on text length
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
        CyError: if network name doesn't exist or error in parameter value
        requests.exceptions.HTTPError: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> add_annotation_shape()
        {'edgeThickness': '1.0', 'canvas': 'foreground', 'fillOpacity': '100.0', 'rotation': '0.0', 'type': 'org.cytoscape.view.presentation.annotations.ShapeAnnotation', 'uuid': '4e189482-6acb-472b-8077-683a548361b2', 'shapeType': 'RECTANGLE', 'edgeColor': '#000000', 'edgeOpacity': '100.0', 'name': 'Shape 1', 'x': '2449.9784057344455', 'width': '100.0', 'y': '1882.9888145962157', 'z': '0', 'height': '100.0'}
        >>> add_annotation_shape(type='ELLIPSE', custom_shape=None, x_pos=100, y_pos=200, angle=45, fill_color='#F0F0F0', opacity=50, border_thickness=2, border_color='#0F0F0F', border_opacity=75, height=30, width=31, name='ann3 name', canvas='background')
        {'edgeThickness': '2.0', 'canvas': 'background', 'fillOpacity': '50.0', 'rotation': '45.0', 'type': 'org.cytoscape.view.presentation.annotations.ShapeAnnotation', 'uuid': '5a590eec-5281-44d2-9e51-1a4476381cf1', 'fillColor': '#F0F0F0', 'shapeType': 'ELLIPSE', 'edgeColor': '#0F0F0F', 'edgeOpacity': '75.0', 'name': 'ann3 name', 'x': '100.0', 'width': '31.0', 'y': '200.0', 'z': '0', 'height': '30.0'}
    """

    cmd_string, net_SUID = _build_base_cmd_string('annotation add shape', network, base_url)  # a good start

    cmd_string += _get_type_cmd_string(type)

    cmd_string += _get_custom_shape_cmd_string(custom_shape)

    # x and y position
    cmd_string += _get_x_y_pos_cmd_string(x_pos, y_pos, net_SUID, base_url)

    # optional params
    cmd_string += _get_angle_cmd_string(angle)

    cmd_string += _get_fill_color_cmd_string(fill_color)

    cmd_string += _get_opacity_cmd_string(opacity)

    cmd_string += _get_border_cmd_string(border_thickness, border_color, border_opacity)

    cmd_string += _get_height_width_cmd_string(height, width)

    cmd_string += _get_name_cmd_string(name, network, base_url)

    cmd_string += _get_canvas_cmd_string(canvas)

    cmd_string += _get_z_order_cmd_string(z_order)

    # execute command
    res = commands.commands_post(cmd_string, base_url=base_url)

    return res

@cy_log
def delete_annotation(names=None, base_url=DEFAULT_BASE_URL):
    """Delete Annotation

    Remove an annotation from the current network view in Cytoscape

    Args:
        names (UUID or str or list): Single UUID or str, or list of UUIDs or str
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        None

    Raises:
        CyError: if invalid name list
        requests.exceptions.HTTPError: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> delete_annotation('ann1')
        >>> delete_annotation(['ann1', 'ann2'])
        >>> delete_annotation(['016a4af1-69bc-4b99-8183-d6f118847f96', '016a4af1-69bc-4b99-8183-d6f118847f97'])
    """

    if names is None:
        raise CyError(f'Must provide the UUID (or list of UUIDs) to delete')

    if isinstance(names, str):  # If it's a string, force it into a list
        names = [names]

    for ann in names:
        res = commands.commands_post(f'annotation delete uuidOrName="{ann}"', base_url=base_url)

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

    cmd_string, net_SUID = _build_base_cmd_string('annotation list', network, base_url)  # a good start

    res = commands.commands_post(cmd_string, base_url=base_url)

    return res

@cy_log
def group_annotation(names=None, network=None, base_url=DEFAULT_BASE_URL):
    """Group Annotation

    Group annotation from the network view in Cytoscape

    Args:
        names (UUID or str or list): Single UUID or str, or list of UUIDs or str
        network (SUID or str or None): Name or SUID of the network. Default is the "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: A named list of annotation properties, including UUID

    Raises:
        CyError: if invalid name list
        requests.exceptions.HTTPError: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> group_annotation(['016a4af1-69bc-4b99-8183-d6f118847f96', '016a4af1-69bc-4b99-8183-d6f118847f97'])
        {'canvas': 'foreground', 'rotation': '0.0', 'name': 'Group 1', 'x': '2449.0', 'y': '1882.0', 'z': '0', 'type': 'org.cytoscape.view.presentation.annotations.GroupAnnotation', 'uuid': '303ac590-495b-44a9-8743-0a8c13e22e6f', 'memberUUIDs': '016a4af1-69bc-4b99-8183-d6f118847f96,016a4af1-69bc-4b99-8183-d6f118847f97'}
    """

    cmd_string, net_SUID = _build_base_cmd_string('annotation group', network, base_url)  # a good start

    if names is None:
        raise CyError(f'Must provide the UUID (or list of UUIDs) to group')

    if isinstance(names, list):  # If it's a list, make a string out of it
        names = ', '.join(names)

    res = commands.commands_post(f'{cmd_string} annotationlist="{names}"', base_url=base_url)

    if len(res) == 0:
        raise CyError(f'Error while grouping {names}')
    return res

@cy_log
def ungroup_annotation(names=None, network=None, base_url=DEFAULT_BASE_URL):
    """Ungroup Annotation group

    Ungroup annotation group from the network view in Cytoscape

    Args:
        names (UUID or str or list): Single UUID or str, or list of UUIDs or str
        network (SUID or str or None): Name or SUID of the network. Default is the "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        None

    Raises:
        CyError: if invalid name list
        requests.exceptions.HTTPError: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> ungroup_annotation(['016a4af1-69bc-4b99-8183-d6f118847f96', '016a4af1-69bc-4b99-8183-d6f118847f97'])
        >>> ungroup_annotation('016a4af1-69bc-4b99-8183-d6f118847f96', network='galFiltered.sif')
        >>> ungroup_annotation('016a4af1-69bc-4b99-8183-d6f118847f96', network=59945)
    """

    cmd_string, net_SUID = _build_base_cmd_string('annotation ungroup', network, base_url)  # a good start

    if names is None:
        raise CyError(f'Must provide the UUID (or list of UUIDs) to ungroup')

    if isinstance(names, str):  # If it's a string, force it into a list
        names = [names]

    for ann in names:
        commands.commands_post(f'{cmd_string} uuidOrName="{ann}"', base_url=base_url)

#-------------------------------------------------------------------

def _build_base_cmd_string(base_command, network, base_url):
    net_SUID = networks.get_network_suid(network, base_url=base_url)
    view_SUID = network_views.get_network_view_suid(net_SUID, base_url=base_url)

    # add view
    base_command += f' view="SUID:{view_SUID}"'

    return base_command, net_SUID

def _get_x_y_pos_cmd_string(x_pos, y_pos, net_SUID, base_url):
    if x_pos is None:
        x_pos = style_values.get_network_center(net_SUID, base_url=base_url)['x']
    if y_pos is None:
        y_pos = style_values.get_network_center(net_SUID, base_url=base_url)['y']
    return f' x="{x_pos}" y="{y_pos}"'

def _get_type_cmd_string(type):
    if type is None:
        return ''
    else:
        type = type.upper()
        if type not in styles.get_node_shapes():
            raise CyError(f'{type} is invalid. Choose a shape from get_node_shapes()')
        if type == 'ROUND_RECTANGLE':
            type = 'Rounded Rectangle'
        elif type == 'VEE':
            type = 'V'
        return f' type="{type}"'

def _get_z_order_cmd_string(z_order):
    if z_order is None:
        return ''
    else:
        if not (isinstance(z_order, float) or isinstance(z_order, int)):
            raise CyError(f'{z_order} is invalid. Z order must be a number.')
        return f' z="{z_order}"'

def _get_canvas_cmd_string(canvas):
    if canvas is None:
        return ''
    else:
        verify_canvas(canvas)
        return f' canvas="{canvas}"'

def _get_name_cmd_string(name, network, base_url):
    if name is None:
        return ''
    else:
        all_annotations = get_annotation_list(network, base_url=base_url)
        all_names = [x['name'] for x in all_annotations]
        verify_unique(name, all_names)
        return f' newName="{name}"'

def _get_height_width_cmd_string(height, width):
    if height is None:
        height_cmd = ''
    else:
        verify_positive(height)
        height_cmd = f' height="{height}"'

    if width is None:
        width_cmd = ''
    else:
        verify_positive(width)
        width_cmd = f' width="{width}"'

    return height_cmd + width_cmd

def _get_border_cmd_string(border_thickness, border_color, border_opacity):
    if border_thickness is None:
        border_thickness_cmd = ''
    else:
        verify_non_negative(border_thickness)
        border_thickness_cmd = f' borderThickness="{border_thickness}"'

    if border_color is None:
        border_color_cmd = ''
    else:
        verify_hex_color(border_color)
        border_color_cmd = f' borderColor="{border_color}"'

    if border_opacity is None:
        border_opacity_cmd = ''
    else:
        verify_opacity(border_opacity)
        border_opacity_cmd = f' borderOpacity="{border_opacity}"'

    return border_thickness_cmd + border_color_cmd + border_opacity_cmd

def _get_opacity_cmd_string(opacity):
    if opacity is None:
        return ''
    else:
        verify_opacity(opacity)
        return f' opacity="{opacity}"'

def _get_fill_color_cmd_string(fill_color):
    if fill_color is None:
        return ''
    else:
        verify_hex_color(fill_color)
        return f' fillColor="{fill_color}"'

def _get_angle_cmd_string(angle):
    if angle is None:
        return ''
    else:
        rotation = normalize_rotation(angle)
        return f' angle="{rotation}"'

def _get_custom_shape_cmd_string(custom_shape):
    if custom_shape is None:
        return ''
    else:
        return f' customShape="{custom_shape}"'

def _get_brightness_contrast_cmd_string(brightness, contrast):
    if brightness is None:
        brightness_cmd = ''
    else:
        verify_brightness_contrast(brightness)
        brightness_cmd = f' brightness="{brightness}"'

    if contrast is None:
        contrast_cmd = ''
    else:
        verify_brightness_contrast(contrast)
        contrast_cmd = f' contrast="{contrast}"'

    return brightness_cmd + contrast_cmd

def _get_url_cmd_string(url):
    if url is None:
        raise CyError(f'URL or path to image file must be provided.')
    if re.search('^http[s]*://', url) == None:
        url = sandbox.get_abs_sandbox_path(url)
    return f' url="{url}"'

def _get_font_cmd_string(font_size, font_family, font_style):
    if font_size is None:
        font_size_cmd = ''
    else:
        verify_positive(font_size)
        font_size_cmd = f' fontSize="{font_size}"'

    if font_family is None:
        font_family_cmd = ''
    else:
        font_family_cmd = f' fontFamily="{font_family}"'

    if font_style is None:
        font_style_cmd = ''
    else:
        verify_font_style(font_style)
        font_style_cmd = f' fontStyle="{font_style}"'

    return font_size_cmd + font_family_cmd + font_style_cmd

def _get_color_cmd_string(color):
    if color is None:
        return ''
    else:
        verify_hex_color(color)
        return f' color="{color}"'

def _get_text_cmd_string(text):
    if text is None:
        raise CyError("Must provide the text string to add.")
    return f' text="{text}"'