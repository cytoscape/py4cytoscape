# -*- coding:utf-8 -*-

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
from .style_defaults import *
from .style_values import *
from .decorators import *

# TODO: Enforce documentation standards for modules and private functions per:
# https://www.python.org/dev/peps/pep-0257/ and https://www.python.org/dev/peps/pep-0008/#comments
# https://google.github.io/styleguide/pyguide.html

# TODO: Remember to set __all__ to enumerate what modules are exported from this package. Do this at the module level, too, for functions ... consider using a decorator to fill the __all__ per https://stackoverflow.com/questions/44834/can-someone-explain-all-in-python
# TODO: Add type hints per https://www.python.org/dev/peps/pep-0484/ for all functions

# TODO: Remember to execute pylint: https://stackoverflow.com/questions/38134086/how-to-run-pylint-with-pycharm

# Note that use of "import" statement project wide per advice of:
# https://stackoverflow.com/questions/44834/can-someone-explain-all-in-python
# http://effbot.org/zone/import-confusion.htm

