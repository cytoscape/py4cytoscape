# -*- coding: utf-8 -*-

"""Functions for inspecting and managing apps for Cytoscape.
"""

import sys

from . import commands
from .exceptions import CyError
from .pycy3_utils import *

def disable_app(app, base_url=DEFAULT_BASE_URL):
    verify_supported_versions(1, 3.7, base_url=base_url)
    res = commands.commands_post('apps disable app="' + app + '"', base_url=base_url)
    return res
