# -*- coding: utf-8 -*-

"""Functions for managing Cytoscape SESSIONS, including save, open and close.
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
import os

# Internal module imports
from . import commands

# Internal module convenience imports
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log
from .py4cytoscape_notebook import running_remote


def __init__(self):
    pass


@cy_log
def close_session(save_before_closing, filename=None, base_url=DEFAULT_BASE_URL):
    """Close the current session in Cytoscape, destroying all unsaved work.

    A boolean for whether to save before closing is required since you could lose data by closing without saving.

    Args:
        save_before_closing (bool): Whether to save before closing the current session. If False, then all
            unsaved work will be lost.
        filename (str): If ``save_before_closing`` is True and the session has not previously been saved,
            then the path and name of the session file to save should be provided.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {} empty

    Raises:
        CyError: if filename is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> close_session(False) # delete the current session without saving it first
        {}
        >>> close_session(True) # delete the current session after saving it to the file it came from
        {}
        >>> close_session(True, 'new') # delete the current session after saving it to 'new.cys'
        {}
    """
    if save_before_closing: save_session(filename, base_url=base_url)

    return commands.commands_post('session new', base_url=base_url)


@cy_log
def open_session(file_location=None, base_url=DEFAULT_BASE_URL):
    """Open Session File or URL.

    Open a session file or URL. This will clear all networks, tables and styles associated with current
    session. Be sure to ``saveSession`` first.

    Args:
        file_location (str): File path or URL (with 'http' or 'https' prefix). Default is a sample session file.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {} empty

    Raises:
        CyError: if filename is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> open_session() # load session from sample Yeast Perturbation.cys file
        {}
        >>> open_session('data/Affinity Purification.cys') # load session from a file
        {}
        >>> open_session('https://github.com/bdemchak/py4cytoscape/blob/master/tests/data/Affinity%20Purification.cys')
        {}

    See Also:
        :meth:`save_session`
    """
    type = 'file'
    if file_location is None:
        file_location = './sampleData/sessions/Yeast Perturbation.cys'
    elif str.startswith(file_location, 'http'):
        type = 'url'
    elif not running_remote():
        file_location = os.path.abspath(file_location)

    narrate('Opening ' + file_location + '...')
    return commands.commands_post(f'session open {type}="{file_location}"', base_url=base_url)


@cy_log
def save_session(filename=None, base_url=DEFAULT_BASE_URL):
    """Saves the current Cytoscape session as a CYS file.

    If no ``filename`` is provided, then it attempts to save to an existing CYS file associated with the session. If
    ``filename`` already exists, then it is overwritten.

    Args:
        filename (str): Full path or path relavtive to current working directory, in addition to the name
            of the file. The ``.cys`` extension is automatically added. Leave blank to update previously
            saved session file.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {} empty

    Raises:
        CyError: if filename is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> save_session('other') # Save current session as other.cys
        {}
        >>> save_session('other.cys') # Save current session as other.cys
        {}
        >>> save_session() # Save current session back to the same file it was loaded from
        {}
    """
    if filename is None:
        filename = commands.cyrest_get('session/name', base_url=base_url)
        if filename == '':
            raise CyError('Save failed. Provide a filename the first time you save a session.')
        return commands.commands_post('session save', base_url=base_url)
    else:
        # TODO: R uses '.cys$' here, but shouldn't the '.' be escaped??
        if re.search('.cys$', filename) is None: filename += '.cys'
        if not running_remote():
            filename = os.path.abspath(filename)
            if os.path.isfile(filename): narrate('This file has been overwritten.')
        return commands.commands_post(f'session save as file="{filename}"', base_url=base_url)
