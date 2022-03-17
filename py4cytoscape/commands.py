# -*- coding: utf-8 -*-

"""Functions for constructing any arbitrary CyREST API or Commands API method via
standard GET, PUT, POST and DELETE protocols. These functions handle marshalling
and unmarshalling of urls, parameters and returns so that higher-level functions
can work with Python-friendly arguments and returns.

I. CyREST API functions
II. Commands API functions
III. Internal functions
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
import requests
import urllib.parse
import json
import webbrowser
import sys
import os

# Internal module convenience imports
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log, log_http_result, log_http_request, show_error
from .py4cytoscape_notebook import running_remote, do_request_remote, check_running_remote, get_notebook_is_running
from .py4cytoscape_sandbox import *
from .exceptions import CyError


def __init__(self):
    pass

# ==============================================================================
# I. CyREST API functions
# ------------------------------------------------------------------------------

@cy_log
def cyrest_api(base_url=DEFAULT_BASE_URL):
    """Open Swagger docs for CyREST API.

    Opens Swagger docs in default browser for a live instance of CyREST operations.

    Note that to open a Swagger window, you may need to configure your browser to allow pop-up windows.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        bool: True

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cyrest_api() # loads Swagger CyREST API into browser
        True
    """
    res = _do_browser_open(f'{base_url}/swaggerUI/swagger-ui/index.html?url={base_url}/swagger.json#/')
    return res


@cy_log
def cyrest_delete(operation=None, parameters=None, base_url=DEFAULT_BASE_URL, require_json=True):
    """Construct a query, make DELETE call and process the result.

    Args:
        operation (str): A string to be converted to the REST query namespace
        parameters (dict): A named list of values to be converted to REST query parameters
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.
        require_json (bool): True if only JSON is accepted as a response; otherwise, return non-JSON if response is non-JSON

    Returns:
        str or dict: a dict if result was JSON; otherwise a string

    Raises:
        ValueError: if JSON is expected and response is not JSON
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cyrest_delete('networks/51/views', require_json=False) # deletes views for network 51
        ''
        >>> cyrest_delete('session') # deletes the current session
        {'message': 'New session created.'}
    """
    try:
        url = build_url(base_url, operation)
        r = _do_request('DELETE', url, params=parameters, base_url=base_url)
        r.raise_for_status()
        try:
            return r.json()
        except ValueError as e:
            if require_json:
                raise
            else:
                return r.text
    except requests.exceptions.RequestException as e:
        _handle_error(e)


@cy_log
def cyrest_get(operation=None, parameters=None, base_url=DEFAULT_BASE_URL, require_json=True):
    """Construct a query, make GET call and process the result.

    Args:
        operation (str): A string to be converted to the REST query namespace
        parameters (dict): A named list of values to be converted to REST query parameters
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.
        require_json (bool): True if only JSON is accepted as a response; otherwise, return non-JSON if response is non-JSON

    Returns:
        str or dict: a dict if result was JSON; otherwise a string

    Raises:
        ValueError: if JSON is expected and response is not JSON
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cyrest_get('gc', require_json=False) # starts Cytoscape garbage collection
        ''
        >>> cyrest_get('version') # fetches CyREST version
        {'apiVersion': 'v1', 'cytoscapeVersion': '3.8.0'}
    """
    try:
        url = build_url(base_url, operation)
        r = _do_request('GET', url, params=parameters, base_url=base_url)
        r.raise_for_status()
        try:
            return r.json()
        except ValueError as e:
            if require_json:
                raise
            else:
                return r.text
    except requests.exceptions.RequestException as e:
        _handle_error(e)


@cy_log
def cyrest_post(operation=None, parameters=None, body=None, base_url=DEFAULT_BASE_URL, require_json=True):
    """Construct a query and body, make POST call and process the result.

    Args:
        operation (str): A string to be converted to the REST query namespace
        parameters (dict): A named list of values to be converted to REST query parameters
        body (dict): A named list of values to be converted to JSON
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.
        require_json (bool): True if only JSON is accepted as a response; otherwise, return non-JSON if response is non-JSON

    Returns:
        str or dict: a dict if result was JSON; otherwise a string

    Raises:
        ValueError: if JSON is expected and response is not JSON
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cyrest_post('networks/51/views') # Add a view to a network
        {'networkViewSUID': '52'}
        >>> cyrest_post('commands/command/echo', body={'message': 'Hi there'}) # echo a message
        {'data': ['Hi there'], 'errors': '[]}
    """
    try:
        url = build_url(base_url, operation)
        r = _do_request('POST', url, params=parameters, json=body, headers = {'Content-Type': 'application/json'}, base_url=base_url)
        r.raise_for_status()
        try:
            return r.json()
        except ValueError as e:
            if require_json:
                raise
            else:
                return r.text
    except requests.exceptions.RequestException as e:
        _handle_error(e)


@cy_log
def cyrest_put(operation=None, parameters=None, body=None, base_url=DEFAULT_BASE_URL, require_json=True):
    """Construct a query and body, make PUT call and process the result.

    Args:
        operation (str): A string to be converted to the REST query namespace
        parameters (dict): A named list of values to be converted to REST query parameters
        body (dict): A named list of values to be converted to JSON
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.
        require_json (bool): True if only JSON is accepted as a response; otherwise, return non-JSON if response is non-JSON

    Returns:
        str or dict: a dict if result was JSON; otherwise a string

    Raises:
        ValueError: if JSON is expected and response is not JSON
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> cyrest_put('networks/views/currentNetworkView', body={'networkViewSUID': view}) # Make a view the current view
        {'data': {}, 'errors': '[]}
    """
    try:
        url = build_url(base_url, operation)
        r = _do_request('PUT', url, params=parameters, json=body, headers = {'Content-Type': 'application/json'}, base_url=base_url)
        r.raise_for_status()
        try:
            return r.json()
        except ValueError as e:
            if require_json:
                raise
            else:
                return r.text
    except requests.exceptions.RequestException as e:
        _handle_error(e)


# ==============================================================================
# II. Commands API functions
# ------------------------------------------------------------------------------

@cy_log
def commands_api(base_url=DEFAULT_BASE_URL):
    """Open Swagger docs for CyREST Commands API.

    Opens Swagger docs in default browser for a live instance of Commands available via CyREST.

    Note that to open a Swagger window, you may need to configure your browser to allow pop-up windows.

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        bool: True

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> commands_api() # loads Swagger CyREST Commands API into browser
        True
    """
    res = _do_browser_open(f'{base_url}/swaggerUI/swagger-ui/index.html?url={base_url}/commands/swagger.json#/')
    return res

# TODO: Make sure this works the same as in R
@cy_log
def commands_get(cmd_string, base_url=DEFAULT_BASE_URL):
    """Commands GET.

    Using the same syntax as Cytoscape's Command Line Dialog, this function converts a command string into a
    CyREST query URL, executes a GET request, and parses the result content into a list object.

    Args:
        cmd_string (str): command
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: a list of lines in the command result (omitting the "Finished" line at the end)

    Raises:
        CyError: if command has an error
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> commands_get('command sleep duration=5')
        []
        >>> commands_get('apps status app="Network Merge"')
        ['app: Network Merge, status: Installed']
        >>> commands_get('view')
        ["Available commands for 'view':", 'create', 'destroy', 'export', 'fit content', 'fit selected', ...]
    """
    try:
        get_url, parameters = _command_2_get_query(cmd_string, base_url=base_url)
        r = _do_request('GET', get_url, params=parameters, headers={'Accept': 'text/plain'}, base_url=base_url)
        r.raise_for_status()

        # Break response into a list of lines and return it
        res_list = re.split('\n\\s*', r.text)
        res_list = [line for line in res_list if line != 'Finished']
        if len(res_list) and res_list[-1] == '': del res_list[
            -1]  # deal with artifact of .split() leaving last line blank
        return res_list
    except requests.exceptions.RequestException as e:
        _handle_error(e, force_cy_error=True)


# TODO: Make sure this works the same as in R
@cy_log
def commands_help(cmd_string='help', base_url=DEFAULT_BASE_URL):
    """Commands Help.

    Using the same syntax as Cytoscape's Command Line Dialog, this function returns a list of available commands or args.
    Works with or without 'help' command prefix. Note that if you ask about a command that doesn't have any arguments,
    this function will run the command!

    Args:
        cmd_string (str): command
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: a list of lines in the command result (omitting the "Finished" line at the end)

    Raises:
        CyError: if command has an error
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> commands_help('apps')
        ['disable', 'enable', 'information', 'install', 'list available', 'list disabled', ...]
    """
    try:
        cmd_string = re.sub(r'help *', '', cmd_string)  # remove 'help ' if it's already in the request
        get_url, parameters = _command_2_get_query(cmd_string, base_url=base_url)
        r = _do_request('GET', get_url, params=parameters, headers={'Accept': 'text/plain'}, base_url=base_url)
        r.raise_for_status()

        # Break response into a list of lines and return it
        res_list = re.split('\n\\s*', r.text)[1:]  # create a list of command options, and leave off the header
        res_list = [line.strip() for line in res_list]
        if len(res_list) and res_list[-1] == '':
            del res_list[-1]  # deal with artifact of .split() leaving last line blank
        return res_list
    except requests.exceptions.RequestException as e:
        _handle_error(e, force_cy_error=True)


@cy_log
def commands_post(cmd, base_url=DEFAULT_BASE_URL):
    """Commands POST.

    Using the same syntax as Cytoscape's Command Line Dialog, this function converts a command string into a CyREST
    query URL, executes a POST request, and parses the result content into a dict object.

    Args:
        cmd_string (str): command
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict or list: a structured command reply

    Raises:
        CyError: if command has an error
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> commands_post('apps status app="Network Merge"')
        {'appName': 'Network Merge', 'status': 'Installed'}
        >>> commands_post('apps list available')
        [{appName: 'CHAT', 'description': 'Identify contextually relevant hubs in biological networks', 'details': ''},
         {'appName': 'AgilentLiteratureSearch', 'description': 'Mines scientific literature to ... ', 'details': ''} ...]
    """

    try:
        post_url = _command_2_post_query_url(cmd, base_url=base_url)
        post_body = _command_2_post_query_body(cmd)
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = _do_request('POST', post_url, json=post_body, headers=headers, base_url=base_url)
        r.raise_for_status()
        res = json.loads(r.text)
        if len(res['errors']):
            raise CyError(str(res['errors'][0]))
        return res['data']
    except requests.exceptions.RequestException as e:
        _handle_error(e)


@cy_log
def commands_run(cmd_string, base_url=DEFAULT_BASE_URL):
    """Run a Command.

    Using the same syntax as Cytoscape's Command Line Dialog, this function converts a command string into a CyREST
    query URL, executes a GET request, and parses the result content into a list object. Same as commandsGET.

    Args:
        cmd_string (str): command
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: a list of lines in the command result (omitting the "Finished" line at the end)

    Raises:
        CyError: if command has an error
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> commands_run('session new destroyCurrentSession=true')
        []
    """
    return commands_get(cmd_string, base_url=base_url)


# TODO: Take another look at the R version ... it seems to be passing in the wrong parameter name. Comments seem wrong.
@cy_log
def command_echo(variable_name='*', base_url=DEFAULT_BASE_URL):
    """Command Echo.

    The echo command will display the value of the variable specified by the variableName argument, or all
    variables if variableName is not provided.

    Args:
        variable_name (str): The name of the variable to display. Default is to display all variable values using "*".
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: a list containing as single string containing the ``variable_name`` value

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> command_echo('Hi there')
        ['Hi there']
        >>> command_echo()
        ['*']
    """
    return commands_post(f'command echo message="{variable_name}"', base_url=base_url)


# TODO: It doesn't look like the command space supports open ... does the R version work?
@cy_log
def command_open_dialog(base_url=DEFAULT_BASE_URL):
    """Command Open Dialog.

    The command line dialog provides a field to enter commands and view results. It also provides the help command
    to display namespaces, commands, and arguments

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        None

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> command_open_dialog()
    """
    return commands_post('command open dialog', base_url=base_url)


@cy_log
def command_pause(message='', base_url=DEFAULT_BASE_URL):
    """Command Pause.

    The pause command displays a dialog with the text provided in the message argument and waits for the user to click OK.

    Args:
        message (str): Text to display in pause dialog
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {}

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> command_pause()
        {}
    """
    return commands_post(f'command pause message="{message}"', base_url=base_url)


@cy_log
def command_quit(base_url=DEFAULT_BASE_URL):
    """Command Quit.

    This command causes Cytoscape to exit. It is typically used at the end of a script file

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {}

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> command_quit()
        {}
    """
    return commands_post('command quit', base_url=base_url)


# TODO: Consider whether absolute path should happen in R, too
@cy_log
def command_run_file(file, args=None, base_url=DEFAULT_BASE_URL):
    """Command Run File.

    The run command will execute a command script from the file pointed to by the file argument, which should contain
    Cytoscape commands, one per line. Arguments to the script are provided by the args argument

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {}

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> command_run_file('data/CommandScript.txt')
        {}
    """
    args_str = f' args="{args}"' if args else ''
    file = get_abs_sandbox_path(file)

    return commands_post(f'command run{args_str} file="{file}"', base_url=base_url)


@cy_log
def command_sleep(duration=None, base_url=DEFAULT_BASE_URL):
    """Command Sleep.

    The sleep command will pause processing for a period of time as specified by duration seconds. It is typically used
    as part of a command script.

    Args:
        duration (float): The time in seconds to sleep
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {}

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> command_sleep(6)
        {}
    """
    dur_str = f' duration="{duration}"' if duration else ''

    return commands_post(f'command sleep{dur_str}', base_url=base_url)


def _command_2_get_query(cmd_string, base_url=DEFAULT_BASE_URL):
    # Wipe out parameters so we can focus just on the Cytoscape command
    # For example, 'network get attribute network="test" namespace="default" columnList="SUID"'
    # becomes 'network get attributeXXXXXXnetwork="test"XXXXXXnamespace="default"XXXXXXcolumnList="SUID"'
    cmd_mark_params = re.sub(r' ([A-Za-z0-9_-]*=)', 'XXXXXX\\1', cmd_string)

    # Separate Cytoscape command and parameters. Using the above:
    # 'network get attribute', 'network="test"', 'namespace="default"', 'columnList="SUID"'
    split_cmd = cmd_mark_params.split('XXXXXX')

    # Assemble just the cy_cmd as a CyREST command URL
    cy_cmd = split_cmd[0] or ''
    url = base_url + urllib.parse.quote('/commands/' + re.sub(' ', '/', cy_cmd, count=1))

    # Create a dict of parameter names/values
    args = ' '.join(split_cmd[1:])
    if args:
        args = re.sub(r'"', '', args)  # Get rid of all " (presumably surrounding command argument values)
        name_list = re.findall('[A-Za-z0-9_-]+=', args)  # Find all parameter names (e.g., 'abc=')
        name_list = [re.sub(r'=', '', name) for name in name_list]  # Get rid of all '=' at the end of parameter names
        val_list = re.split(' *[A-Za-z0-9_-]+=', args)[
                   1:]  # Find all parameter values (.e.g., the '123' part of 'abc=123')
        arg_dict = {key: val for key, val in
                    zip(name_list, val_list)}  # Create dictionary out of param names and values
    else:
        arg_dict = None

    return url, arg_dict


def _command_2_post_query_url(cmd, base_url=DEFAULT_BASE_URL):
    """ Construct complete command URL from base URL and Cytoscape command """

    # Wipe out parameters so we can focus just on the Cytoscape command
    # For example, 'network get attribute network="test" namespace="default" columnList="SUID"'
    # becomes 'network get attributeXXXXXXnetwork="test"XXXXXXnamespace="default"XXXXXXcolumnList="SUID"'
    cmd_mark_params = re.sub(r' ([A-Za-z0-9_-]*=)', 'XXXXXX\\1', cmd)

    # Separate Cytoscape command and parameters. Using the above:
    # 'network get attribute', 'network="test"', 'namespace="default"', 'columnList="SUID"'
    split_cmd = cmd_mark_params.split('XXXXXX')

    # Assemble just the cy_cmd as a CyREST command URL
    cy_cmd = split_cmd[0] or ''
    url = base_url + urllib.parse.quote('/commands/' + re.sub(' ', '/', cy_cmd, count=1))

    return url


def _command_2_post_query_body(cmd):
    """ Construct body of POST as JSON representing inline parameters """

    # Set markers 'XXXXXX" on each parameter so we can see where they are.
    # For example, 'network get attribute network="test" namespace="default" columnList="SUID"'
    # becomes 'network get attributeXXXXXXnetwork="test"XXXXXXnetwork="default"XXXXXXcolumnList="SUID"'
    cmd_mark_params = re.sub(r' ([A-Za-z0-9_-]*=)', 'XXXXXX\\1', cmd)
    split_cmd = cmd_mark_params.split("XXXXXX")

    # Extract just the parameters ... if there are none, invent one
    params = split_cmd[1:]
    if params is None: params = ['atLeastOneArg=required']

    # Create a dictionary containing params as key-value, squeezing out quotes
    param_dict = {}
    for x in params:
        p = re.sub('"', '', x).split('=', 1)
        if p[0] is None: raise CyError('Missing parameter name in "{x}"')
        param_dict[p[0]] = p[1]

    return param_dict

def sub_versions(base_url=DEFAULT_BASE_URL, **kwargs):
    # If we're running through Jupyter-Bridge, get the versions of components along the way
    if _find_remote_cytoscape():
        return do_request_remote('version', None, **kwargs).json()
    else:
        return {}

def _handle_error(e, force_cy_error=False):
    # An exception occurred ... figure out the most sensible thing to return as the exception text
    caller = sys._getframe(1).f_code.co_name
    if e.response is None or e.response.text is None or e.response.text == '':
        show_error(f'In {caller}: {e}') # Was: narrate(f'In {caller}: {e}')
        raise
    else:
        content = e.response.text
        try:
            content = json.loads(content)['errors'][0]['message']
# now written to stderrr by CyError constructor:            narrate(f'In {caller}: {e}\n{content}')
            e = CyError(content, caller=caller)
        except:
# now written to stderrr by CyError constructor:            narrate(f'In {caller}: {e}\n{content}')
            if force_cy_error:
                e = CyError(content, caller=caller)
            else:
                show_error(f'In {caller}: {e}\n{content}')
        raise e


def _do_request_local(method, url, **kwargs):
    # Call CyREST via a local URL
    log_http_request(method, url, **kwargs)
    r = requests.request(method, url, **kwargs)
    log_http_result(r)
    return r

def _do_request(method, url, base_url=DEFAULT_BASE_URL, **kwargs):
    # Determine whether actual call is local or remote
    requester = _get_requester()

    do_initialize_sandbox(requester, base_url=base_url) # make sure there's a sandbox before executing a command

    return requester(method, url, **kwargs)

def do_initialize_sandbox(requester=None, base_url=DEFAULT_BASE_URL):
    # If re-initialize has been requested, reset sandbox to environment's default (i.e., None or default_sandbox)
    if get_sandbox_reinitialize():
        return do_set_sandbox(_get_default_sandbox(), requester, base_url=base_url)
    else:
        return get_current_sandbox()

def do_set_sandbox(sandbox_to_set, requester=None, base_url=DEFAULT_BASE_URL):
    # Set the sandbox to whatever is passed in. Note that sandbox_to_set is a dictionary not a string.
    requester = requester or _get_requester()
    if not sandbox_to_set['sandboxName']:
        # A null name means that the default sandbox should be used, but honoring the copySamples and reinitialize
        # settings passed in by the caller.
        sandbox_to_set['sandboxName'] = _get_default_sandbox()['sandboxName']
    sandbox_name = sandbox_to_set['sandboxName']
    if sandbox_name:
        # A named sandbox name means to create one if it doesn't already exist ... otherwise, preserve it and apply
        # copySamples or reinitialize if true
        try:
            r = requester('POST', f'{base_url}/commands/filetransfer/setSandbox',
                          json=sandbox_to_set,
                          headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
            r.raise_for_status()
            new_sandbox = set_current_sandbox(sandbox_name, r.json()['data']['sandboxPath'])
        except Exception as e:
            message = r.text
            caller = sys._getframe(1).f_code.co_name
            try:
                message = r.json()['errors'][0]['message']
            except Exception as e0:
                raise CyError(message, caller=caller)
            if message.startswith('Failed to find command namespace'):
                raise CyError(f'Error: FileTransfer app must be installed in Cytoscape', caller=caller)
            else:
                raise CyError(message, caller=caller)
    else:
        # A null name really means to use the whole Cytoscape file system. If the default sandbox is set up right,
        # we should never get here if we're running a remote configuration.
        #
        # But if we are running remotely, we find out what sandbox is running.
        #
        # If we are running on the Cytoscape workstation, we want to find out whether a sandbox is defined, and if so,
        # what it is. If no sandbox is defined, the entire workstation file system is the sandbox. If a sandbox is
        # defined, the caller will consider the file name to be relative to it.
        default_sandbox_path = get_default_sandbox_path()
        if default_sandbox_path is None:
            if running_remote():
                try:
                    r = requester('POST', f'{base_url}/commands/filetransfer/getFileInfo',
                                  json={'sandboxName': None, 'fileName': '.'},
                                  headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
                    r.raise_for_status()
                    default_sandbox_path = set_default_sandbox_path(json.loads(r.text)['data']['filePath'])
                except Exception as e:
                    # This is a nasty case ... it's hard for getFileInfo to fail unless FileTransfer isn't installed.
                    # We'll assume that's so, and assume that means we're running on the Cytoscape workstation. So,
                    # coerce the paths to be consistent with that situation. Sandbox functions will fail, but
                    # functions that depend only on calculating paths should do fine.
                    default_sandbox_path = None
                    narrate('Warning: FileTransfer app is not available, so sandbox operations will fail')
            else:
                default_sandbox_path = os.getcwd() # Running on the Cytoscape workstation

        new_sandbox = set_current_sandbox(None, default_sandbox_path)

    set_sandbox_reinitialize(False) # No need to initialize again immediately before the next command is issued
    return new_sandbox

def _get_default_sandbox():
    # Figure out what the default sandbox should be, depending on whether we're running remote or on the Cytoscape workstation
    default = get_default_sandbox()
    if len(default) == 0:
        # There hasn't been a default sandbox calculated yet ... create a new default to reflect whether remote
        # execution. This determination is deferred until now (instead of occurring when Python execution first starts)
        # so as to give the user some flexibility regarding when Cytoscape needs to be started ... this allows
        # Cytoscape to be started only before the user issues the first command.
        if running_remote():
            default = sandbox_initializer(sandboxName=PREDEFINED_SANDBOX_NAME)
        else:
            default = sandbox_initializer(sandboxName=None)  # for execution on Cytoscape workstation
        set_default_sandbox(**default)
    return default

def _get_requester():
    # Figure out whether CyREST is local or remote ... if remote, we'll want to go through Jupyter-Bridge
    return do_request_remote if _find_remote_cytoscape() else _do_request_local

def _do_browser_open(url, **kwargs):
    # Figure out whether CyREST is local or remote ... if remote, issue a browser command through Jupyter-Bridge
    if _find_remote_cytoscape():
        return do_request_remote('webbrowser', url, **kwargs)
    else:
        return webbrowser.open(url, new=2, autoraise=True)

def _find_remote_cytoscape():
    if check_running_remote() is None:
        raise requests.exceptions.RequestException('Cannot find local or remote Cytoscape. Start Cytoscape and then proceed.')
    return running_remote()