# -*- coding: utf-8 -*-

"""Functions for performing file operations within a sandbox.
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
import base64
import os

# Internal module imports
from . import commands

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_sandbox import *
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log


@cy_log
def sandbox_set(sandbox_name, copy_samples=True, reinitialize=True, base_url=DEFAULT_BASE_URL):
    """Apply edge bundling to the network specified.

    Edge bundling is executed with default parameters; optional parameters are not supported.

    Args:
        network (SUID or str or None): Name or SUID of the network; default is "current" network.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'message': 'Edge bundling success.'}

    Raises:
        CyError: if layout_name is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> bundle_edges() # Bundle edges in current network
        {'message': 'Edge bundling success.'}
        >>> bundle_edges('yeastHighQuality.sif') # Bundle edges in named network
        {'message': 'Edge bundling success.'}
    """
    sandbox_path, sandbox_name = commands.do_set_sandbox({'sandboxName': sandbox_name, 'copySamples': copy_samples, 'reinitialize': reinitialize}, base_url=base_url)
    return sandbox_path

def sandbox_remove(sandbox_name=None, base_url=DEFAULT_BASE_URL):
    return _sandbox_op(f'filetransfer removeSandbox', sandbox_name, base_url)

def sandbox_get_file_info(file_name, sandbox_name=None, base_url=DEFAULT_BASE_URL):
    return _sandbox_op(f'filetransfer getFileInfo fileName="{file_name}"', sandbox_name, base_url)

def sandbox_send_to(source_file, dest_file=None, overwrite=True, sandbox_name = None, base_url=DEFAULT_BASE_URL):
    with open(source_file, mode='rb') as file:
        file_content = file.read()
    file_content64 = base64.b64encode(file_content).decode('utf-8')

    return _sandbox_op(f'filetransfer toSandbox fileBase64="{file_content64}" fileByteCount={len(file_content)} fileName="{dest_file}" overwrite={overwrite}', sandbox_name, base_url=base_url)

def sandbox_get_from(source_file, dest_file=None, overwrite=True, sandbox_name = None, base_url=DEFAULT_BASE_URL):
    if not overwrite and os.path.exists(dest_file):
        raise CyError(f'File "{dest_file}" already exists')

    res = _sandbox_op(f'filetransfer fromSandbox fileName="{source_file}"', sandbox_name, base_url)

    file_content = base64.b64decode(res['fileBase64'], validate=True)
    with open(dest_file, mode='wb') as file:
        file.write(file_content)

    del res['fileBase64']
    return res

def sandbox_remove_file(file_name, sandbox_name=None, base_url=DEFAULT_BASE_URL):
    return _sandbox_op(f'filetransfer removeFile fileName="{file_name}"', sandbox_name, base_url)

def _sandbox_op(command, sandbox_name, base_url):
    if not sandbox_name:
        sandbox_path, sandbox_name = commands.do_initialize_sandbox(base_url=base_url)
    sandbox_param = f' sandboxName={sandbox_name or ""}'
    res = commands.commands_post(command + sandbox_param, base_url=base_url)
    return res
