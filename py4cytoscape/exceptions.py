# -*- coding: utf-8 -*-

"""Error classes for py4cytoscape.
"""

# External library imports
import sys

# Internal module convenience imports
from .py4cytoscape_logger import show_error


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

class CyError(Exception):
    """Create an error describing a Cytoscape or py4cytoscape fault.

    Args:
        message_text (str): text describing error condition
        caller (str): name of function in which error is to be reported

    Returns:
         CyError: contains the text message and error location

    Raises:
        none

    Examples:
        >>> CyError('Invalid column name')
        'In commands_get(): Invalid column name'
        >>> CyError('slot must be an integer between 1 and 9', caller=sys._getframe(1).f_code.co_name)
        'In get_network_suid(): slot must be an integer between 1 and 9'
    """

    def __init__(self, message_text, caller=None):
        if caller is None: caller = sys._getframe(1).f_code.co_name
        whole_error = f'In {caller}(): {message_text}'
        super().__init__(whole_error)
        show_error(whole_error)     # was: print(whole_error, file=sys.stderr)


