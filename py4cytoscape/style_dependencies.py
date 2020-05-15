# -*- coding: utf-8 -*-

"""# Functions for getting and setting style DEPEDENDENCIES, organized into sections:

I. General functions for getting and setting dependencies
II. Specific functions for setting particular dependencies

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

def set_style_dependencies(style_name='default', dependencies={}, base_url=DEFAULT_BASE_URL):
    # launch error if visual style name is missing
    if style_name not in styles.get_visual_style_names(base_url=base_url):
        error = 'Error in py4cytoscape:set_style_dependencies. No visual style named "' + style_name + '"'
        # TODO: R version of this error has the wrong text
        sys.stderr.write(error)
        return None # TODO: Is this what we want to return here?

    dep_list = [{'visualPropertyDependency': dep, 'enabled': val}    for dep, val in dependencies.items()]

    res = commands.cyrest_put('styles/' + style_name + '/dependencies', body=dep_list, base_url=base_url, require_json=False)
    res = commands.commands_post('vizmap apply styles="' + style_name + '"')
    # TODO: Do we really want to lose the first res value?
    return res

def get_style_dependencies(style_name='default', base_url=DEFAULT_BASE_URL):
    # launch error if visual style name is missing
    if style_name not in styles.get_visual_style_names(base_url=base_url):
        error = 'Error in py4cytoscape:get_style_dependencies. No visual style named "' + style_name + '"'
        # TODO: R version of this error has the wrong text
        sys.stderr.write(error)
        raise CyError(error)
#        return None
        # TODO: Is this what we want to return here?

    res = commands.cyrest_get('styles/' + style_name + '/dependencies', base_url=base_url)

    # make it a dict
    dep_list = {dep['visualPropertyDependency']: dep['enabled']  for dep in res}
    return dep_list


def lock_node_dimensions(new_state, style_name='default', base_url=DEFAULT_BASE_URL):
    toggle = 'true' if new_state else 'false'

    res = set_style_dependencies(style_name=style_name, dependencies={'nodeSizeLocked': toggle}, base_url=base_url)

    return res
