# -*- coding:utf-8 -*-

""" Interface for Py4Cytoscape.
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

from .networks import *
from .session import *
from .layouts import *
from .network_selection import *
from .tables import *
from .commands import *
from .cytoscape_system import *
from .apps import *
from .collections import *
from .filters import *
from .groups import *
from .tools import *
from .user_interface import *
from .network_views import *
from .styles import *
from .style_mappings import *
from .style_auto_mappings import *
from .style_defaults import *
from .style_values import *
from .style_dependencies import *
from .style_bypasses import *
from .py4cytoscape_utils import *
from .cy_ndex import *
from .decorators import *
from .py4cytoscape_notebook import get_browser_client_js, get_browser_client_channel, get_jupyter_bridge_url, get_notebook_is_running, set_notebook_is_running
from .py4cytoscape_logger import set_summary_logger
from .sandbox import *
from .py4cytoscape_sandbox import *
from .py4cytoscape_tuning import set_catchup_filter_secs, set_catchup_network_secs, set_model_propagation_secs
from ._version import __version__
from .notebook import *

# Note that we have tried to enforce documentation standards for modules and private functions per:
# https://www.python.org/dev/peps/pep-0257/ and https://www.python.org/dev/peps/pep-0008/#comments
# https://google.github.io/styleguide/pyguide.html

# TODO: Remember to set __all__ to enumerate what modules are exported from this package. Do this at the module level, too, for functions ... consider using a decorator to fill the __all__ per https://stackoverflow.com/questions/44834/can-someone-explain-all-in-python
# TODO: Add type hints per https://www.python.org/dev/peps/pep-0484/ for all functions

# TODO: Remember to execute pylint: https://stackoverflow.com/questions/38134086/how-to-run-pylint-with-pycharm

# Note that use of "import" statement project wide per advice of:
# https://stackoverflow.com/questions/44834/can-someone-explain-all-in-python
# http://effbot.org/zone/import-confusion.htm

