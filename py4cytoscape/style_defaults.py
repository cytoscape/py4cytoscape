# -*- coding: utf-8 -*-

"""Functions for getting and setting DEFAULT values for visual properties, organized into sections:

I. General functions for setting node, edge and network defaults
II. Specific functions for setting particular node, edge and network defaults

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
import time

# Internal module imports
from . import networks
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

def set_visual_property_default(style_string, style_name='default', base_url=DEFAULT_BASE_URL):
    res = commands.cyrest_put('styles/' + style_name + '/defaults', body=[style_string], base_url=base_url, require_json=False)
    time.sleep(MODEL_PROPAGATION_SECS) # wait for attributes to be applied ... it looks like Cytoscape returns before this is complete [BUG]
    return res


def set_node_border_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
    if is_not_hex_color(new_color):
        return None

    style = {'visualProperty': 'NODE_BORDER_PAINT', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


def set_node_border_width_default(new_width, style_name='default', base_url=DEFAULT_BASE_URL):
    style = {'visualProperty': 'NODE_BORDER_WIDTH', 'value': new_width}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res


def set_node_color_default(new_color, style_name='default', base_url=DEFAULT_BASE_URL):
    if is_not_hex_color(new_color):
        return None

    style = {'visualProperty': 'NODE_FILL_COLOR', 'value': new_color}
    res = set_visual_property_default(style, style_name, base_url=base_url)
    return res
