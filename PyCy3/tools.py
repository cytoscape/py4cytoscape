# -*- coding: utf-8 -*-

"""Functions related to TOOLS found in the Tools Menu in Cytoscape.
"""

import sys

from . import commands
from .exceptions import CyError
from .pycy3_utils import *
from .pycy3_logger import *

@cy_log
def cybrowser_close(id=None, base_url=DEFAULT_BASE_URL):
    """Cybrowser Close.

    Close an internal web browser and remove all content. Provide an id for the browser you want to close.

    Args:
        id (str): The identifier for the browser window to close
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        dict: {}

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cybrowser_close('CyGame')
        {}
    """
    id_str = ' id="' + str(id) + '"' if id is not None else ''

    res = commands.commands_post('cybrowser close' + id_str, base_url=base_url)
    return res

@cy_log
def cybrowser_dialog(id=None, text=None, title=None, url=None, base_url=DEFAULT_BASE_URL):
    """Launch Cytoscape's internal web browser in a separate window

    Provide an id for the window if you want subsequent control of the window e.g., via cybrowser hide.

    Args:
        id (str): The identifier for the new browser window
        text (str): HTML text to initially load into the browser
        title (str): Text to be shown in the title bar of the browser window
        url (str): The URL the browser should load
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        dict: {'id': id} where ``id`` is the one provided as a parameter to this function

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cybrowser_dialog(id='Test Window', title='Hello Africa', text='<HTML><HEAD><TITLE>Hello</TITLE></HEAD><BODY>Hello, world!</BODY></HTML>')
        {'id': 'Test Window'}
        >>> cybrowser_dialog(id='CytoWindow', title='Cytoscape Home Page', url='http://www.cytoscape.org')
        {'id': 'CytoWindow'}

    See Also:
        :meth:`cybrowser_show`, :meth:`cybrowser_hide`
    """
    id_str = ' id="' + str(id) + '"' if id else ''
    text_str = ' text="' + str(text) + '"' if text else ''
    title_str = ' title="' + str(title) + '"' if title else ''
    url_str = ' url="' + str(url) + '"' if url else ''

    res = commands.commands_post('cybrowser dialog' + id_str + text_str + title_str + url_str, base_url=base_url)
    return res

@cy_log
def cybrowser_hide(id=None, base_url=DEFAULT_BASE_URL):
    """Cybrowser Hide.

    Hide an existing browser, whether it's in the Results panel or a separate window.

    Args:
        id (str): The identifier for the browser window to hide
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        dict: {}

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cybrowser_hide('CyGame')
        {}

    See Also:
        :meth:`cybrowser_show`, :meth:`cybrowser_dialog`
    """
    id_str = ' id="' + str(id) + '"' if id else ''

    res = commands.commands_post('cybrowser hide' + id_str, base_url=base_url)
    return res

@cy_log
def cybrowser_list(base_url=DEFAULT_BASE_URL):
    """Cybrowser List.

    List all browsers that are currently open, whether as a dialog or in the results panel.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        list: [{'id': id, 'title': title, 'url': current url}] where there is a dict for each browser window,
            and the ``id`` and ``title`` were provided in the ``cybrowser_show()`` call, and the ``url`` is for the page currently
            loaded in the browser window

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cybrowser_list()
        [{'id': 'CytoManual ID', 'title': 'CytoManual Page', 'url': 'http://manual.cytoscape.org/en/stable/'}, {'id': ...} ...]
    """
    res = commands.commands_post('cybrowser list', base_url=base_url)
    return res

@cy_log
def cybrowser_send(id=None, script='', base_url=DEFAULT_BASE_URL):
    """Cybrowser Send.

    Send the text to the browser indicated by the id and return the response, if any. Note that the JSON result
    field could either be a bare string or JSON formatted text.

    Args:
        id (str): The identifier for the new browser window
        script (str) A string that represents a JavaScript variable, script, or call to be executed in the browser.
            Note that only string results are returned.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        dict: {'browserId': id, 'result': result} where ``id`` is the one provided as a parameter to this function and
            ``result`` is the string returned as a result of executing the script

    Raises:
        CyError: if the browser could not execute the command
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cybrowser_send(id='Test Window', script='navigator.userAgent')
        {'browserId': 'Test Window', 'result': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/608.1 (KHTML, like Gecko) JavaFX/13 Safari/608.1 CyBrowser/1.2.0'}
        >>> cybrowser_send(id='CytoWindow', script="window.location='http://google.com'")
        {'browserId': 'CytoWindow', 'result': 'http://google.com'}

    See Also:
        :meth:`cybrowser_show`, :meth:`cybrowser_hide`, :meth:`cybrowser_dialog`
    """
    id_str = ' id="' + str(id) + '"' if id else ''

    res = commands.commands_post('cybrowser send' + id_str + ' script="' + script + '"', base_url=base_url)
    return res

@cy_log
def cybrowser_show(id=None, text=None, title=None, url=None, base_url=DEFAULT_BASE_URL):
    """Cybrowser Show.

    Launch Cytoscape's internal web browser in a pane in the Result Panel. Provide an id for the window
    if you want subsequent control of the window via cybrowser hide.

    Args:
        id (str): The identifier for the new browser window
        text (str): HTML text to initially load into the browser
        title (str): Text to be shown in the title bar of the browser window
        url (str): The URL the browser should load
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        dict: {'id': id} where ``id`` is the one provided as a parameter to this function

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cybrowser_show(id='Test Window', title='Hello Africa', text='<HTML><HEAD><TITLE>Hello</TITLE></HEAD><BODY>Hello, world!</BODY></HTML>')
        {'id': 'Test Window'}
        >>> cybrowser_show(id='CytoWindow', title='Cytoscape Home Page', url='http://www.cytoscape.org')
        {'id': 'CytoWindow'}

    See Also:
        :meth:`cybrowser_dialog`, :meth:`cybrowser_hide`
    """
    id_str = ' id="' + str(id) + '"' if id else ''
    text_str = ' text="' + str(text) + '"' if text else ''
    title_str = ' title="' + str(title) + '"' if title else ''
    url_str = ' url="' + str(url) + '"' if url else ''

    res = commands.commands_post('cybrowser show' + id_str + text_str + title_str + url_str, base_url=base_url)
    return res

@cy_log
def cybrowser_version(base_url=DEFAULT_BASE_URL):
    """Display the version of the CyBrowser app.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        dict: {'version': app version} where app version is the CyBrowser app version

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cybrowser_version()
        {'version': '1.2.0'}
    """
    res = commands.commands_post('cybrowser version', base_url=base_url)
    return res

@cy_log
def diffusion_basic(base_url=DEFAULT_BASE_URL):
    """Diffusion Basic.

    Diffusion will send the selected network view and its selected nodes to a web-based REST service to calculate
    network propagation. Results are returned and represented by columns in the node table.

    Columns are created for each execution of Diffusion and their names are returned in the response. The nodes
    you would like to use as input should be selected. This will be used to generate the contents of the
    ``diffusion_input`` column, which represents the query vector and corresponds to h in the diffusion equation.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        dict: {'heatColumn': 'diffusion_output_heat', 'rankColumn': 'diffusion_output_rank'} where ``heatColumn`` is the name of the node table column containing each node's calculated heat and ``rankColumn`` is the name of the node table column containing the node's (0-based) rank

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> diffusion_basic()
        {'heatColumn': 'diffusion_output_heat', 'rankColumn': 'diffusion_output_rank'}
    """
    res = commands.commands_post('diffusion diffuse', base_url=base_url)
    return res

@cy_log
def diffusion_advanced(heat_column_name=None, time=None, base_url=DEFAULT_BASE_URL):
    """Diffusion Advanced.

    Diffusion will send the selected network view and its selected nodes to a web-based REST service to calculate
    network propagation. Results are returned and represented by columns in the node table. Advanced operation supports
    parameters.

    Columns are created for each execution of Diffusion and their names are returned in the response. The nodes
    you would like to use as input should be selected. This will be used to generate the contents of the
    ``diffusion_input`` column, which represents the query vector and corresponds to h in the diffusion equation.

    Args:
        heat_column_name (str): A node column name intended to override the default table column ``diffusion_input``.
            This represents the query vector and corresponds to h in the diffusion equation.
        time (str): The extent of spread over the network. This corresponds to t in the diffusion equation.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of PyCy3.

    Returns:
        dict: {'heatColumn': 'diffusion_output_heat', 'rankColumn': 'diffusion_output_rank'} where ``heatColumn`` is the name of the node table column containing each node's calculated heat and ``rankColumn`` is the name of the node table column containing the node's (0-based) rank

    Raises:
        CyError: if an invalid parameter is passed
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> diffusion_advanced(heat_column_name='diffusion_output_heat', time=0.1)
        {'heatColumn': 'diffusion_output_1_heat', 'rankColumn': 'diffusion_output_1_rank'}
    """
    heat_str = ' heatColumnName="' + str(heat_column_name) + '"' if heat_column_name else ''
    time_str = ' time="' + str(time) + '"' if time else ''

    res = commands.commands_post('diffusion diffuse_advanced' + heat_str + time_str, base_url=base_url)
    return res
