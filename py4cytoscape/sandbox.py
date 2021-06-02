# -*- coding: utf-8 -*-

"""Functions for performing file operations within a sandbox.

A sandbox is a directory on the Cytoscape workstation that is guaranteed writeable and is guaranteed to be isolated
from the whole file system. All file operations are carried out relative to the "current sandbox". Generally, a
Notebook-based workflow doesn't have to do anything to set up a sandbox ... the default sandbox is automatically
set up as part of py4cytoscape startup. However, the workflow can set different sandboxes, and can even switch between
them. A sandbox can contain both files and directories, and the user can transfer files between a sandbox and the
workflow's native file system (e.g., a remote Notebook's server).

If a sandbox is defined, all Cytoscape functions read and write files to it by default.

Thus, is it possible to build workflows that don't depend on the structure of the Cytoscape workstation's file system.
Such workflows can store workflow data files along with other workflow files on a remote Notebook server, then transfer
them to a sandbox only when Cytoscape will need them. Conversely, when Cytoscape creates a file in a sandbox (e.g.,
exporting an image), the workflow can transfer the file to workflow storage.

A special case is when py4cytoscape is running on the same workstation as Cytoscape. The default sandbox is considered
to be directory that's current for the Python kernel. Alternatively, the workflow could also define a sandbox, and
then move files in and out of it just as a remote Notebook would.

    See Also:
        `Sandboxing <https://py4cytoscape.readthedocs.io/en/latest/concepts.html#sandboxing>`_ in the Concepts section in the py4cytoscape User Manual.
"""
# from sphinx.addnodes import desc

"""Note that there is more detailed commentary and lower level functions in py4cytsocape_sandbox.py."""

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
import time

# Internal module imports
from . import commands

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_sandbox import *
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log


@cy_log
def sandbox_set(sandbox_name, copy_samples=True, reinitialize=True, base_url=DEFAULT_BASE_URL):
    """Set a new default sandbox, creating it if necessary.

    A sandbox is the root for the file system used for all file operations. When running standalone
    on the same workstation as Cytoscape, the default sandbox is the directory that's current for
    the Python kernel. When running in a Notebook or remote server, the default sandbox is the
    'default_sandbox' created automatically under the under the ``filetransfer`` directory in the
    CytoscapeConfiguration directory. Naming a sandbox with this function creates a new
    sub-directory as a sibling to 'default_sandbox' and uses it for subsequent file operations.
    Setting a None sandbox uses the default sandbox instead.

    Sandboxes are highly recommended as an aid to creating workflows that can be shared with
    others.

    Args:
        sandbox_name (str): Name of new default sandbox. None means to use the original default
            sandbox (e.g., the whole file system for local execution, or 'default_sandbox' for
            Notebook and remote execution). If new sandbox doesn't exist, it is created.
        copy_samples (bool): True to copy the Cytoscape sampleData into the sandbox
        reinitialize (bool): True to delete sandbox contents (if any) if sandbox already exists
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: sandbox path in Cytoscape workstation's file system

    Raises:
        CyError: if sandbox_name is invalid or sandbox can't be created
        requests.exceptions.HTTPError: if can't connect to Cytoscape, Cytoscape returns an error, or sandbox can't be created

    Examples:
        >>> sandbox_set(None) # When running standalone on the Cytoscape workstation
        'C:\\Program Files\\Cytoscape_v3.8.1'
        >>> sandbox_set(None) # When running in a Notebook
        'C:\\Users\\CyDeveloper\\CytoscapeConfiguration\\filetransfer\\default_sandbox'
        >>> sandbox_set('mySand', copy_samples=False, reinitialize=False) # Keep prior sandbox contents
        'C:\\Users\\CyDeveloper\\CytoscapeConfiguration\\filetransfer\\mySand'

    See Also:
        `Sandboxing <https://py4cytoscape.readthedocs.io/en/latest/concepts.html#sandboxing>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    if sandbox_name: sandbox_name = sandbox_name.strip()

    # If the sandbox_name is null, it means set to the default sandbox, which depends on the runtime configuration.
    # If we're running standalone Python, null means to use the whole Cytoscape file system. If we're on a notebook
    # or running remotely, it's the default sandbox name. Any runtime configuration is allowed to set a non-null
    # sandbox, and if it doesn't exist, it'll be created. Note that the copySamples and reinitialize parameters are
    # used only when the sandbox isn't the whole Cytoscape file system.
    sandbox_name, sandbox_path = commands.do_set_sandbox({'sandboxName': sandbox_name, 'copySamples': copy_samples, 'reinitialize': reinitialize}, base_url=base_url)
    return sandbox_path

@cy_log
def sandbox_remove(sandbox_name=None, base_url=DEFAULT_BASE_URL):
    """Delete sandbox contents and remove its directory.

    If the current sandbox is the entire file system on a Cytoscape workstation, trying to delete it
    is an error. Otherwise, deleting the current sandbox results in the default sandbox becoming the
    new current sandbox. When running standalone on the same workstation as Cytoscape, the default
    sandbox is the entire file system on the Cytoscape workstation. When running in a Notebook or
    remote server, the default sandbox is the 'default_sandbox' created automatically under the
    under the ``filetransfer`` directory in the CytoscapeConfiguration directory. If that sandbox is
    deleted, it will be re-created so that subsequent file operations can complete successfully.

    Args:
        sandbox_name (str): Name of sandbox to delete. None means to delete the current
            sandbox. If that sandbox is the default sandbox, it is automatically re-created.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'sandboxPath': <directory on Cytoscape workstation>, 'existed': <True if sandbox existed>}

    Raises:
        requests.exceptions.HTTPError: if can't connect to Cytoscape, Cytoscape returns an error, or sandbox is invalid

    Examples:
        >>> sandbox_remove() # Valid only when running in Notebook or remotely or when explicitly set sandbox is current
        {'sandboxPath': 'C:\\Users\\CyDeveloper\\CytoscapeConfiguration\\filetransfer\\default_sandbox', 'existed': True}
        >>> sandbox_set('mySand')
        {'sandboxPath': 'C:\\Users\\CyDeveloper\\CytoscapeConfiguration\\filetransfer\\mySand', 'existed': True}

    See Also:
        `Sandboxing <https://py4cytoscape.readthedocs.io/en/latest/concepts.html#sandboxing>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    if sandbox_name: sandbox_name = sandbox_name.strip()

    # If the sandbox exists, remove it. Note that the _sandbox_op call may have the side effect of creating the sandbox
    # if the sandbox system hasn't been initialized yet. There are a few cases here. If the sandbox_name is None, the
    # removal should be of the current sandbox (set in sandbox_set or as the default startup sandbox). If there is no
    # default startup sandbox (because we're running as standalone Python instead of remotely or as a notebook), this
    # removal is essentially an error because it's very bad to remove the whole Cytoscape file system.
    default_sandbox_name = get_default_sandbox()['sandboxName']
    current_sandbox_before_remove = get_current_sandbox_name()

    res = _sandbox_op(f'filetransfer removeSandbox', sandbox_name, base_url=base_url)
    if sandbox_name is None or sandbox_name == current_sandbox_before_remove:
        set_current_sandbox(default_sandbox_name, get_default_sandbox_path()) # There is no more current sandbox ... wipe out name of sandbox
        sandbox_name = current_sandbox_before_remove

    # At this point, the sandbox has been deleted. If it was the current sandbox, there is no more current sandbox.
    # A null current sandbox means that the Cytoscape native file system should be used. This is not OK if we're
    # executing from a notebook or remotely. To remedy this, we revert to the default sandbox as the new current
    # sandbox. If that was the sandbox we just deleted, we need to re-initialize so it gets re-created.

    if sandbox_name == default_sandbox_name and default_sandbox_name == current_sandbox_before_remove:
        set_sandbox_reinitialize() # Recreate the default sandbox before the next command executes
    elif sandbox_name == current_sandbox_before_remove:
        # A user-created sandbox was removed, so fall back to the making the default sandbox current ...
        # be sure not to wipe out any work that's already there
        commands.do_set_sandbox({'sandboxName': default_sandbox_name, 'copySamples': False, 'reinitialize': False})
    return res

@cy_log
def sandbox_get_file_info(file_name, sandbox_name=None, base_url=DEFAULT_BASE_URL):
    """Get metadata on file in sandbox (or entire sandbox).

    If the current sandbox is the entire file system on a Cytoscape workstation, trying to delete it
    is an error. Otherwise, deleting the current sandbox results in the default sandbox becoming the
    new current sandbox. When running standalone on the same workstation as Cytoscape, the default
    sandbox is the entire file system on the Cytoscape workstation. When running in a Notebook or
    remote server, the default sandbox is the 'default_sandbox' created automatically under the
    under the ``filetransfer`` directory in the CytoscapeConfiguration directory. If that sandbox is
    deleted, it will be re-created so that subsequent file operations can complete successfully.

    Note that this function can be used to query either a file or a directory.

    Args:
        file_name (str): Name of file whose metadata to return ... can be sandbox-relative path ... ``.`` returns
            metadata on sandbox itself
        sandbox_name (str): Name of sandbox containing file. None means "the current sandbox".
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'filePath': <full path on Cytoscape workstation>, 'modifiedTime': <last changed time, '' if file doesn't exist>, 'isFile': <True if file, False if directory>}

    Raises:
        CyError: if file name is invalid
        requests.exceptions.HTTPError: if can't connect to Cytoscape, Cytoscape returns an error, or sandbox is invalid

    Examples:
        >>> sandbox_get_file_info('.')
        {'filePath': 'C:\\Users\\CyDeveloper\\CytoscapeConfiguration\\filetransfer\\default_sandbox', 'modifiedTime': '2020-09-24 14:10:08.0560', 'isFile': False}
        >>> sandbox_get_file_info('test.png')
        {'filePath': 'C:\\Users\\CyDeveloper\\CytoscapeConfiguration\\filetransfer\\default_sandbox\\test.png', 'modifiedTime': '2020-09-24 14:10:08.0560', 'isFile': True}
        >>> sandbox_get_file_info('test.png', sandbox_name='mySand')
        {'filePath': 'C:\\Users\\CyDeveloper\\CytoscapeConfiguration\\filetransfer\\mySand\\test.png', 'modifiedTime': '2020-09-24 14:10:08.0560', 'isFile': True}

    See Also:
        `Sandboxing <https://py4cytoscape.readthedocs.io/en/latest/concepts.html#sandboxing>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    try:
        return _sandbox_op(f'filetransfer getFileInfo', sandbox_name, file_name=file_name, base_url=base_url)
    except Exception as e:
        # This is a nasty case ... there isn't much way for getFileInfo to fail as long as the FileTransfer app
        # is installed. We'll assume failure means it isn't installed. And if that's so, it must mean that we're
        # running on the Cytoscape workstation. If so, get the file metadata the old fashioned way. This way,
        # callers don't have to know or care about the case of the uninstalled FileTransfer app.
        if not sandbox_name and not get_current_sandbox_name() and file_name and file_name.strip():
            file_path = os.path.abspath(file_name)
            if os.path.exists(file_path):
                is_file = os.path.isfile(file_name)
                modifiedTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(file_name)))
            else:
                is_file = False
                modifiedTime = ''
            return {'filePath': file_path, 'modifiedTime': modifiedTime, 'isFile': is_file}
        else:
            raise e

@cy_log
def sandbox_send_to(source_file, dest_file=None, overwrite=True, sandbox_name = None, base_url=DEFAULT_BASE_URL):
    """Transfer a file to a sandbox.

    The source file is transferred to the named (or current) sandbox, overwriting an existing file if one
    already exists. The ``dest_file`` can be an absolute path if the sandbox is the entire file system (i.e., for
    standalone Python execution) or a path relative to the sandbox (i.e., for Notebook or remote execution or if a
    sandbox was explicitly created).

    Note that there is no function that transfers an entire directory. Note, though, that when using ``sandbox_set()``
    to make a sandbox current, it is possible to copy the Cytoscape sample data directories into to the sandbox at the
    same time.

    Args:
        source_file (str): Name of file in the Python workflow's file system
        dest_file (str): Name of file to write (as absolute path or sandbox-relative path) ... if None, use file name in source_file
        overwrite (bool): False causes error if dest_file already exists; True replaces it if it exists
        sandbox_name (str): Name of sandbox containing file. None means "the current sandbox".
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'filePath': <new file's absolute path in Cytoscape workstation>}

    Raises:
        CyError: if file name is invalid
        requests.exceptions.HTTPError: if can't connect to Cytoscape, Cytoscape returns an error, or sandbox is invalid

    Examples:
        >>> sandbox_send_to('myData.csv')
        {'filePath': 'C:\\Users\\CyDeveloper\\CytoscapeConfiguration\\filetransfer\\default_sandbox\\myData.csv'}
        >>> sandbox_send_to('myData01.csv', 'myData.csv', overwrite=True)
        {'filePath': 'C:\\Users\\CyDeveloper\\CytoscapeConfiguration\\filetransfer\\default_sandbox\\myData.csv'}
        >>> sandbox_send_to('myData01.csv', 'myData.csv', sandbox_name='mySand')
        {'filePath': 'C:\\Users\\CyDeveloper\\CytoscapeConfiguration\\filetransfer\\mySand\\myData.csv'}

    See Also:
        `Sandboxing <https://py4cytoscape.readthedocs.io/en/latest/concepts.html#sandboxing>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    try:
        with open(source_file, mode='rb') as file:
            file_content = file.read()
        file_content64 = base64.b64encode(file_content).decode('utf-8')
    except Exception as e:
        raise CyError(f'Could not read file "{source_file}": {e}')

    if not dest_file or not dest_file.strip():
        head, dest_file = os.path.split(source_file)

    return _sandbox_op(f'filetransfer toSandbox fileByteCount={len(file_content)} overwrite={overwrite} fileBase64="{file_content64}"', sandbox_name, file_name=dest_file, base_url=base_url)

@cy_log
def sandbox_url_to(source_url, dest_file, overwrite=True, sandbox_name = None, base_url=DEFAULT_BASE_URL):
    """Transfer a cloud-based file to a sandbox.

    The source URL identifies a file to be transferred to the named (or current) sandbox, overwriting an existing
    file if one already exists. The ``dest_file`` can be an absolute path if the sandbox is the entire file
    system (i.e., for standalone Python execution), or it can be a path relative to the sandbox (i.e., for Notebook or
    remote execution or if a sandbox was explicitly created).

    Supported URLs include:
        **Raw URL**: URL directly references the file to download (e.g., http://tpsoft.com/museum_images/IBM%20PC.JPG

        **Dropbox**: Use the standard Dropbox ``Get Link`` feature to create the ``source_url`` link in the clipboard (e.g., https://www.dropbox.com/s/r15azh0xb53smu1/GDS112_full.soft?dl=0)

        **GDrive**: Use the standard Google Drive ``Get Link`` feature to create the ``source_url`` link in the clipboard (e.g., https://drive.google.com/file/d/12sJaKQQbesF10xsrbgiNtUcqCQYY1YI3/view?usp=sharing)

        **OneDrive**: Use the OneDrive web site to right click on the file, choose the ``Embed`` menu option, then copy the URL in the iframe's ``src`` parameter into the clipboard (e.g., https://onedrive.live.com/embed?cid=C357475E90DD89C4&resid=C357475E90DD89C4%217207&authkey=ACEU5LrVtI_jWTU)

        **GitHub**: Use the GitHub web site to show the file or a link to it, and capture the URL in the clipboard (e.g., https://github.com/cytoscape/file-transfer-app/blob/master/test_data/GDS112_full.soft)

        Note that GitHub enforces a limit on the size of a file that can be stored there. We advise that you take this
        into account when choosing a cloud service for your files

        When you capture a URL in the clipboard, you should copy it into your program for use with ``sandbox_url_to()``.

    Args:
        source_url (str): URL addressing cloud file to download )
        dest_file (str): Name of file to write (as absolute path or sandbox-relative path)
        overwrite (bool): False causes error if dest_file already exists; True replaces it if it exists
        sandbox_name (str): Name of sandbox containing file. None means "the current sandbox".
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'filePath': <new file's absolute path in Cytoscape workstation>, 'fileByteCount': number of bytes read}

    Raises:
        CyError: if file name or URL is invalid
        requests.exceptions.HTTPError: if can't connect to Cytoscape, Cytoscape returns an error, or sandbox is invalid

    Examples:
        >>> sandbox_url_to('https://www.dropbox.com/s/r15azh0xb53smu1/GDS112_full.soft?dl=0', 'test file')
        {'filePath': 'C:\\Users\\CyDeveloper\\CytoscapeConfiguration\\filetransfer\\default_sandbox\\test file', 'fileByteCount': 5536880}
        >>> sandbox_url_to('https://www.dropbox.com/s/r15azh0xb53smu1/GDS112_full.soft?dl=0', 'test file', overwrite=True)
        {'filePath': 'C:\\Users\\CyDeveloper\\CytoscapeConfiguration\\filetransfer\\default_sandbox\\test file', 'fileByteCount': 5536880}
        >>> sandbox_url_to('https://www.dropbox.com/s/r15azh0xb53smu1/GDS112_full.soft?dl=0', 'test file', sandbox_name='mySand')
        {'filePath': 'C:\\Users\\CyDeveloper\\CytoscapeConfiguration\\filetransfer\\mysand\\test file', 'fileByteCount': 5536880}

    See Also:
        `Sandboxing <https://py4cytoscape.readthedocs.io/en/latest/concepts.html#sandboxing>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    if not source_url:
        raise CyError(f'Source URL cannot be null')
    if not dest_file:
        raise CyError(f'Destination file cannot be null')

    return _sandbox_op(f'filetransfer urlToSandbox overwrite={overwrite} sourceURL={source_url}', sandbox_name, file_name=dest_file, base_url=base_url)

@cy_log
def sandbox_get_from(source_file, dest_file=None, overwrite=True, sandbox_name = None, base_url=DEFAULT_BASE_URL):
    """Transfer a file from a sandbox.

    The source file is transferred from the named (or current) sandbox to the Python workflow's file system,
    overwriting an existing file if one already exists. The ``source_file`` can be an absolute path if the sandbox is
    the entire file system (i.e., for standalone Python execution) or a path relative to the sandbox
    (i.e., for Notebook or remote execution or if a sandbox was explicitly created).

    Note that there is no function that transfers an entire directory.

    Args:
        source_file (str): Name of file to read (as absolute path or sandbox-relative path)
        dest_file (str): Name of file in the Python workflow's file system ... if None, use file name in source_file
        sandbox_name (str): Name of sandbox containing file. None means "the current sandbox".
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'filePath': <source file's absolute path in Cytoscape workstation>}

    Raises:
        CyError: if file name is invalid
        requests.exceptions.HTTPError: if can't connect to Cytoscape, Cytoscape returns an error, or sandbox is invalid

    Examples:
        >>> sandbox_get_from('test.png', 'C:\\Users\\CyDeveloper\\Cytofiles\\test.png', overwrite=True)
        {'filePath': 'C:\\Users\\CyDeveloper\\Cytofiles\\test.png'}
        >>> sandbox_get_from('mySamples/workspace.cys', 'C:\\Users\\CyDeveloper\\Cytofiles\\workspace.cys', sandbox_name='mySand')
        {'filePath': 'C:\\Users\\CyDeveloper\\Cytofiles\\workspace.cys'}

    See Also:
        `Sandboxing <https://py4cytoscape.readthedocs.io/en/latest/concepts.html#sandboxing>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    source_file = source_file.strip() if source_file else ''
    if not dest_file or not dest_file.strip():
        head, dest_file = os.path.split(source_file)

    if not overwrite and os.path.exists(dest_file):
        raise CyError(f'File "{dest_file}" already exists')

    res = _sandbox_op(f'filetransfer fromSandbox', sandbox_name, file_name=source_file, base_url=base_url)

    file_content = base64.b64decode(res['fileBase64'], validate=True)
    try:
        with open(dest_file, mode='wb') as file:
            file.write(file_content)
    except Exception as e:
        raise CyError(f'Could not write to file "{dest_file}": {e}')

    del res['fileBase64']
    return res

@cy_log
def sandbox_remove_file(file_name, sandbox_name=None, base_url=DEFAULT_BASE_URL):
    """Remove a file from a sandbox.

    The named file is removed from the named sandbox. If the sandbox is the entire file system (i.e., for standalone
    Python execution), the file name can be an absolute path. Otherwise, it is a path relative to the named sandbox.

    Note that there is no function that deletes a directory, except for ``sandbox_remove()``, which deletes a sandbox
    and all of its contents.

    Args:
        file_name (str): Name of file to delete (as absolute path or sandbox-relative path)
        sandbox_name (str): Name of sandbox containing file. None means "the current sandbox".
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'filePath': <file's absolute path in Cytoscape workstation>, 'existed': True if file existed before being deleted}

    Raises:
        CyError: if file name is invalid
        requests.exceptions.HTTPError: if can't connect to Cytoscape, Cytoscape returns an error, or sandbox is invalid

    Examples:
        >>> sandbox_remove_file('test.png')
        {'filePath': 'C:\\Users\\CyDeveloper\\default_sandbox\\test.png', 'existed': True}
        >>> sandbox_remove_file('mySamples/workspace.cys', sandbox_name='mySand')
        {'filePath': 'C:\\Users\\CyDeveloper\\mySand\\mySamples\\workspace.cys', 'existed': False}

    See Also:
        `Sandboxing <https://py4cytoscape.readthedocs.io/en/latest/concepts.html#sandboxing>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    return _sandbox_op(f'filetransfer removeFile', sandbox_name, file_name=file_name, base_url=base_url)

def _sandbox_op(command, sandbox_name, file_name=None, base_url=DEFAULT_BASE_URL):
    if file_name: file_name = file_name.strip()
    if sandbox_name:
        sandbox_name = sandbox_name.strip()
        sandbox_path = get_current_sandbox_path()
    else:
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

    if sandbox_name:
        command += f' sandboxName="{sandbox_name}"'
    elif file_name:
        file_name = os.path.join(sandbox_path, file_name)
    if file_name: command += f' fileName="{file_name}"'

    res = commands.commands_post(command, base_url=base_url)
    return res
