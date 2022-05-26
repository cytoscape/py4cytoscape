# -*- coding: utf-8 -*-

"""Functions related to TOOLS found in the Tools Menu in Cytoscape.
"""

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

# External library imports
import sys

# Internal module imports
from . import commands
from . import sandbox

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log


@cy_log
def analyze_network(directed=False, base_url=DEFAULT_BASE_URL):
    """Calculate various network statistics.

    The results are added to the Node and Edge tables and the Results Panel.
    The summary statistics in the Results Panel are also returned by the function
    as a list of named values.

    Args:
        directed (bool): If True, the network is considered a directed graph. Default is False.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: Named list of summary statistics

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> analyze_network()
        {'networkTitle': 'galFiltered.sif (undirected)', 'nodeCount': '330', 'edgeCount': '359', 'avNeighbors': '2.379032258064516', 'diameter': '27', 'radius': '14', 'avSpl': '9.127660963823953', 'cc': '0.06959203036053131', 'density': '0.009631709546819902', 'heterogeneity': '0.8534500004035027', 'centralization': '0.06375695335900727', 'ncc': '26'}
        >>> analyze_network(True)
        {'networkTitle': 'galFiltered.sif (directed)', 'nodeCount': '330', 'edgeCount': '359', 'avNeighbors': '2.16969696969697', 'diameter': '10', 'radius': '1', 'avSpl': '3.4919830756382395', 'cc': '0.03544266191325015', 'density': '0.003297411808050106', 'ncc': '26', 'mnp': '1', 'nsl': '0'}
    """
    res = commands.commands_post(f'analyzer analyze directed={directed}', base_url=base_url)
    return res


@cy_log
def cybrowser_close(id=None, base_url=DEFAULT_BASE_URL):
    """Cybrowser Close.

    Close an internal web browser and remove all content. Provide an id for the browser you want to close.

    Args:
        id (str): The identifier for the browser window to close
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {}

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cybrowser_close('CyGame')
        {}
    """
    id_str = f' id="{id}"' if id is not None else ''

    res = commands.commands_post(f'cybrowser close{id_str}', base_url=base_url)
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
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

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
    id_str = f' id="{id}"' if id else ''
    text_str = f' text="{text}"' if text else ''
    title_str = f' title="{title}"' if title else ''
    url_str = f' url="{url}"' if url else ''

    res = commands.commands_post(f'cybrowser dialog{id_str}{text_str}{title_str}{url_str}', base_url=base_url)
    return res


@cy_log
def cybrowser_hide(id=None, base_url=DEFAULT_BASE_URL):
    """Cybrowser Hide.

    Hide an existing browser, whether it's in the Results panel or a separate window.

    Args:
        id (str): The identifier for the browser window to hide
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

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
    id_str = f' id="{id}"' if id else ''

    res = commands.commands_post(f'cybrowser hide{id_str}', base_url=base_url)
    return res


@cy_log
def cybrowser_list(base_url=DEFAULT_BASE_URL):
    """Cybrowser List.

    List all browsers that are currently open, whether as a dialog or in the results panel.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: [{'id': id, 'title': title, 'url': current url}]

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cybrowser_list()
        [{'id': 'CytoManual ID', 'title': 'CytoManual Page', 'url': 'http://manual.cytoscape.org/en/stable/'}, {'id': ...} ...]

    Note:
        In the return value, there is a dict for each browser window,
        and the ``id`` and ``title`` were provided in the ``cybrowser_show()`` call, and the ``url`` is for the page currently
        loaded in the browser window
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
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'browserId': id, 'result': result}

    Raises:
        CyError: if the browser could not execute the command
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cybrowser_send(id='Test Window', script='navigator.userAgent')
        {'browserId': 'Test Window', 'result': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/608.1 (KHTML, like Gecko) JavaFX/13 Safari/608.1 CyBrowser/1.2.0'}
        >>> cybrowser_send(id='CytoWindow', script="window.location='http://google.com'")
        {'browserId': 'CytoWindow', 'result': 'http://google.com'}

    Note:
        In the return result, ``id`` is the one provided as a parameter to this function and
        ``result`` is the string returned as a result of executing the script

    See Also:
        :meth:`cybrowser_show`, :meth:`cybrowser_hide`, :meth:`cybrowser_dialog`
    """
    id_str = f' id="{id}"' if id else ''

    res = commands.commands_post(f'cybrowser send{id_str} script="{script}"', base_url=base_url)
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
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

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
    id_str = f' id="{id}"' if id else ''
    text_str = f' text="{text}"' if text else ''
    title_str = f' title="{title}"' if title else ''
    url_str = f' url="{url}"' if url else ''

    res = commands.commands_post(f'cybrowser show{id_str}{text_str}{title_str}{url_str}', base_url=base_url)
    return res


@cy_log
def cybrowser_version(base_url=DEFAULT_BASE_URL):
    """Display the version of the CyBrowser app.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

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
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

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
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'heatColumn': 'diffusion_output_heat', 'rankColumn': 'diffusion_output_rank'} where ``heatColumn`` is the name of the node table column containing each node's calculated heat and ``rankColumn`` is the name of the node table column containing the node's (0-based) rank

    Raises:
        CyError: if an invalid parameter is passed
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> diffusion_advanced(heat_column_name='diffusion_output_heat', time=0.1)
        {'heatColumn': 'diffusion_output_1_heat', 'rankColumn': 'diffusion_output_1_rank'}
    """
    heat_str = f' heatColumnName="{heat_column_name}"' if heat_column_name else ''
    time_str = f' time="{time}"' if time else ''

    res = commands.commands_post(f'diffusion diffuse_advanced{heat_str}{time_str}', base_url=base_url)
    return res


@cy_log
def merge_networks(sources=None,
                   title=None,
                   operation="union",
                   node_keys=None,
                   node_merge_map=None,
                   nodes_only=False,
                   edge_keys=None,
                   edge_merge_map=None,
                   network_merge_map=None,
                   in_network_merge=True,
                   base_url=DEFAULT_BASE_URL):
    """Merge Networks.

    Combine networks via union, intersection, or difference operations. Lots of optional parameters choose from!

    Args:
        sources (list): List of network names to be merged.
        title (str): Title of the resulting merged network. Default is a concatentation of operation and source network titles.
        operation (str): Type of merge: union (default), intersection or difference.
        node_keys (list): An order-dependent list of columns to match nodes across source networks. Default is "name"
            column for all sources.
        node_merge_map (list): A list of column merge records specifying how to merge node table data. Each record should
            be of the form: ["network1 column", "network2 column", "merged column", "type"], where column names are
            provided and type is String, Integer, Double or List.
        nodes_only (bool): If True, this will merge the node tables and ignore edge and network table data. Default is False.
        edge_keys (list): An order-dependent list of columns to match edges across source networks. Default is "name"
            column for all sources.
        edge_merge_map (list): A list of column merge records specifying how to merge edge table data. Each record should
            be of the form: ["network1 column", "network2 column", "merged column", "type"], where column names are
            provided and type is String, Integer, Double or List.
        network_merge_map (list): A list of column merge records specifying how to merge network table data. Each record
            should be of the form: ["network1 column", "network2 column", "merged column", "type"], where column names
            are provided and type is String, Integer, Double or List.
        in_network_merge (bool) If True (default), nodes and edges with matching attributes in the same network will be
            merged.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        int: SUID of merged network

    Raises:
        CyError: if an invalid parameter is passed
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> merge_networks(['Network_0', 'Network_1'])
        366343
        >>> merge_networks(['Network_0', 'Network_1'], title='nodes mapped')
        366343
        >>> merge_networks(['Network_0', 'Network_1'], node_merge_map=[['given name', 'first name', 'called', 'String'], ['score', 'age', 'score_m', 'Integer']], title='nodes mapped')
        366343
    """
    cmd_string = 'network merge'  # a good start

    # Sources must be supplied
    if sources is None:
        raise CyError('Missing sources!')

    # Create mandatory args
    cmd_string += f' sources="{",".join(sources)}" operation={operation} nodesOnly={nodes_only} inNetworkMerge={in_network_merge}'

    # Add optional args
    if not title is None:
        cmd_string += f' netName="{title}"'
    if not node_keys is None:
        cmd_string += f' nodeKeys="{",".join(node_keys)}"'
    if not edge_keys is None:
        cmd_string += f' edgeKeys="{",".join(edge_keys)}"'
    if not node_merge_map is None:
        record_list = [f'{{{",".join(rec)}}}' for rec in node_merge_map]
        cmd_string += f' nodeMergeMap="{",".join(record_list)}"'
    if not edge_merge_map is None:
        record_list = [f'{{{",".join(rec)}}}' for rec in edge_merge_map]
        cmd_string += f' edgeMergeMap="{",".join(record_list)}"'
    if not network_merge_map is None:
        record_list = [f'{{{",".join(rec)}}}' for rec in network_merge_map]
        cmd_string += f' networkMergeMap="{",".join(record_list)}"'

    res = commands.commands_post(cmd_string, base_url=base_url)

    return res['SUID'] if 'SUID' in res else res

@cy_log
def import_file_from_url(source_url, dest_file, overwrite=True, base_url=DEFAULT_BASE_URL):
    """Transfer a cloud-based file to the current Cytoscape directory.

    The source URL identifies a file to be transferred from a cloud resource to either the
    to the current Cytoscape directory (if executing on the Cytoscape workstation) or sandbox (if
    executing on a remote server or a sandbox was explicitly created). If the destination file already
    exists, it is overwritten. The ``dest_file`` can be an absolute path if the workflow is
    executing on the local Cytoscape workstation.

    Supported URLs include:
        **Raw URL**: URL directly references the file to download (e.g., http://tpsoft.com/museum_images/IBM%20PC.JPG

        **Dropbox**: Use the standard Dropbox ``Get Link`` feature to create the ``source_url`` link in the clipboard (e.g., https://www.dropbox.com/s/r15azh0xb53smu1/GDS112_full.soft?dl=0)

        **GDrive**: Use the standard Google Drive ``Get Link`` feature to create the ``source_url`` link in the clipboard (e.g., https://drive.google.com/file/d/12sJaKQQbesF10xsrbgiNtUcqCQYY1YI3/view?usp=sharing)

        **OneDrive**: Use the OneDrive web site to right click on the file, choose the ``Embed`` menu option, then copy the URL in the iframe's ``src`` parameter into the clipboard (e.g., https://onedrive.live.com/embed?cid=C357475E90DD89C4&resid=C357475E90DD89C4%217207&authkey=ACEU5LrVtI_jWTU)

        **GitHub**: Use the GitHub web site to show the file or a link to it, and capture the URL in the clipboard (e.g., https://github.com/cytoscape/file-transfer-app/blob/master/test_data/GDS112_full.soft)

        Note that GitHub enforces a limit on the size of a file that can be stored there. We advise that you take this
        into account when choosing a cloud service for your files.

        When you capture a URL in the clipboard, you should copy it into your program for use with this function.

    This function is most useful for Notebooks running on the local Cytoscape workstation. For Notebooks
    that could run on a remote server, consider using sandbox_url_to() and related sandbox functions.

    Args:
        source_url (str): URL addressing cloud file to download
        dest_file (str): Name of file to write (as Cytoscape-relative path, absolute file system path or sandbox-relative path)
        overwrite (bool): False causes error if dest_file already exists; True replaces it if it exists
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'filePath': <new file's absolute path in Cytoscape workstation>, 'fileByteCount': number of bytes read}

    Raises:
        CyError: if file name or URL is invalid
        requests.exceptions.HTTPError: if can't connect to Cytoscape, Cytoscape returns an error, or sandbox is invalid

    Examples:
        >>> import_file_from_url('https://www.dropbox.com/s/r15azh0xb53smu1/GDS112_full.soft?dl=0', 'test file')
        {'filePath': 'C:\\Users\\CyDeveloper\\CytoscapeConfiguration\\filetransfer\\default_sandbox\\test file', 'fileByteCount': 5536880}
        >>> import_file_from_url('https://www.dropbox.com/s/r15azh0xb53smu1/GDS112_full.soft?dl=0', 'test file', overwrite=True)
        {'filePath': 'C:\\Users\\CyDeveloper\\CytoscapeConfiguration\\filetransfer\\default_sandbox\\test file', 'fileByteCount': 5536880}

    See Also:
        `Sandboxing <https://py4cytoscape.readthedocs.io/en/latest/concepts.html#sandboxing>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    return sandbox.sandbox_url_to(source_url, dest_file, overwrite=overwrite, sandbox_name=None, base_url=base_url)
