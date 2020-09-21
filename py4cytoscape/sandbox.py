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
    # If the sandbox_name is null, it means set to the default sandbox, which depends on the runtime configuration.
    # If we're running standalone Python, null means to use the whole Cytoscape file system. If we're on a notebook
    # or running remotely, it's the default sandbox name. Any runtime configuration is allowed to set a non-null
    # sandbox, and if it doesn't exist, it'll be created. Note that the copySamples and reinitialize parameters are
    # used only when the sandbox isn't the whole Cytoscape file system.
    sandbox_name, sandbox_path = commands.do_set_sandbox({'sandboxName': sandbox_name, 'copySamples': copy_samples, 'reinitialize': reinitialize}, base_url=base_url)
    return sandbox_path

def sandbox_remove(sandbox_name=None, base_url=DEFAULT_BASE_URL):
    # If the sandbox exists, remove it. Note that the _sandbox_op call may have the side effect of creating the sandbox
    # if the sandbox system hasn't been initialized yet. There are a few cases here. If the sandbox_name is None, the
    # removal should be of the current sandbox (set in sandbox_set or as the default startup sandbox). If there is no
    # default startup sandbox (because we're running as standalone Python instead of remotely or as a notebook), this
    # removal is essentially an error because it's very bad to remove the whole Cytoscape file system.
    default_sandbox_name = get_default_sandbox()['sandboxName']
    current_sandbox_before_remove = get_current_sandbox_name()
    res = _sandbox_op(f'filetransfer removeSandbox', sandbox_name, base_url)
    if not sandbox_name or sandbox_name == current_sandbox_before_remove:
        set_current_sandbox(default_sandbox_name, get_default_sandbox_path()) # There is no more current sandbox ... wipe out name of sandbox

    # At this point, the sandbox has been deleted. If it was the current sandbox, there is no more current sandbox.
    # A null current sandbox means that the Cytoscape native file system should be used. This is not OK if we're
    # executing from a notebook or remotely. To remedy this, we revert to the default sandbox as the new current
    # sandbox. If that was the sandbox we just deleted, we need to re-initialize so it gets re-created.

    if sandbox_name == default_sandbox_name:
        set_sandbox_reinitialize() # Recreate the default sandbox before the next command executes
    elif sandbox_name == current_sandbox_before_remove:
        # Make the default sandbox current ... be sure not to wipe out any work that's already there
        commands.do_set_sandbox({'sandboxName': default_sandbox_name, 'copySamples': False, 'reinitialize': False})
    return res

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
        # An empty sandbox name (either None or "") means to use the currently set sandbox (from sandbox_set).
        # Fetch the current sandbox name and use it. After that, the sandbox name could still be None ... meaning
        # that either there is no sandbox set yet, or the entire raw Cytoscape file system is being used as a sandbox.
        # To resolve this, get the default sandbox, which is what the sandbox will be set to after it's initialized.
        # Even after all of that, the sandbox name could still be None, which means that the raw Cytoscape file system
        # really is being used. This would be appropriate if we're running in a standalone Python environment instead
        # of a remote execution or a local notebook. A standalone Python environment is still free to operate in a
        # sandbox if it wants.
        #
        # Note that if the sandbox hasn't been initialized yet, it'll need to be created. This could happen because
        # the sandbox is *lazily* initialized. This gives the user the choice of starting Cytoscape before or after
        # starting the Python workflow. Forcing an initialization at this point is appropriate if it hasn't already
        # happened.
        #
        # Given all of this, we let the do_initialize_sandbox figure out whether an initialization is needed, and
        # beyond that, what the current sandbox name is.
        sandbox_name, sandbox_path = commands.do_initialize_sandbox(base_url=base_url)
    sandbox_param = f' sandboxName={sandbox_name or ""}'
    res = commands.commands_post(command + sandbox_param, base_url=base_url)
    return res
