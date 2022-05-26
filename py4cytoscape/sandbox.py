# -*- coding: utf-8 -*-

"""Functions for performing file operations within a sandbox.

A sandbox is a directory on the Cytoscape workstation that is guaranteed writeable and is guaranteed to be isolated
from the whole file system. All Python and Cytoscape file operations are carried out relative to the "current sandbox".
Sandboxes primarily address file access issues when running workflows on a remote server (and accessing Cytoscape
running on the workstation via Jupyter-Bridge).

When running a workflow on the Cytoscape workstation (i.e., locally, not remotely), the entire workstation's file
system would be directly accessible to the workflow, and sandboxing isn't an issue. Essentially, this
acknowledges that the user has rightful and safe access to the file system (subject to normal file system
permissions).

When running a workflow on a remote server, accessing files local to the workflow's Python kernel isn't helpful
because they're on a server that the workstation's Cytoscape can't reach. Additionaly, it's problematic to allow
the Python kernel to access workstation files anyway because 1) errant notebooks could compromise workstation
security, and 2) notebooks can't easily account for differences in various workstation file systems (e.g.,
naming files in a Mac is different than in Windows).

Sandboxing solves this by creating a workstation directory that's guaranteed to exist. The notebook can create and
access files within the sandbox (by using the sandbox_* functions in this module), and Cytoscape can do the same.
When a workflow runs remotely, py4cytoscape automatically creates a default sandbox for this data flow.

While workflows running on a Cytoscape workstation have access to the entire workstation file system, they can opt
to use a sandbox instead. This allows workflows to be developed on a workstation, then moved to a remote server and
executed there. (See the sandbox_set() function.)

It's possible for a workflow to use the default sandbox or (instead) create a custom sandbox for the exclusive use
of a workflow or family of workflows.

    See Also:
        `Sandboxing <https://py4cytoscape.readthedocs.io/en/latest/concepts.html#sandboxing>`_ in the Concepts section in the py4cytoscape User Manual.
"""
# from sphinx.addnodes import desc

"""Note that there is more detailed commentary and lower level functions in py4cytsocape_sandbox.py."""

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

    A sandbox is the root for the file system used for all file operations. When running a workflow
    from a command line or notebook on the same workstation as Cytoscape, the default sandbox is the
    entire workstation file system, and the current directory is the same as the Python kernel's
    default directory. When running a workflow on a remote server, the default sandbox is the
    'default_sandbox' created automatically under the under the ``filetransfer`` directory in the
    CytoscapeConfiguration directory. Naming a custom sandbox with this sandbox_set() function
    creates a new sub-directory as a sibling to 'default_sandbox' and uses it for subsequent
    file operations. Setting a None sandbox reverts to the workstation's file system when the
    workflow is running on the Cytoscape workstation, and 'default_sandbox' when the workflow is
    running remotely.

    Sandboxes are highly recommended as an aid to creating workflows that can be shared with
    others.

    Args:
        sandbox_name (str): Name of new default sandbox. None means to use the original default
            sandbox (e.g., the whole file system for local execution, or 'default_sandbox' for
            remote execution). If new sandbox doesn't exist, it is created.
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
        >>> sandbox_set(None) # When running on the Cytoscape workstation
        'C:\\Users\\CyDeveloper\\PycharmProjects\\py4cytoscape\\tests\\scratchpad'
        >>> sandbox_set(None) # When running on on a remote server
        'C:\\Users\\CyDeveloper\\CytoscapeConfiguration\\filetransfer\\default_sandbox'
        >>> sandbox_set('mySand', copy_samples=False, reinitialize=False) # Keep prior sandbox contents
        'C:\\Users\\CyDeveloper\\CytoscapeConfiguration\\filetransfer\\mySand'

    See Also:
        `Sandboxing <https://py4cytoscape.readthedocs.io/en/latest/concepts.html#sandboxing>`_ in the Concepts section in the py4cytoscape User Manual.
    """
    if sandbox_name: sandbox_name = sandbox_name.strip()

    # If the sandbox_name is null, it means set to the default sandbox, which depends on the runtime configuration.
    # If we're running on the Cytoscape workstation, null means to use the whole Cytoscape file system. If we're
    # running remotely, it's the default sandbox name. Any runtime configuration is allowed to set a non-null
    # sandbox, and if it doesn't exist, it'll be created. Note that the copySamples and reinitialize parameters are
    # used only when the sandbox isn't the whole Cytoscape file system.
    sandbox_name, sandbox_path = commands.do_set_sandbox({'sandboxName': sandbox_name, 'copySamples': copy_samples, 'reinitialize': reinitialize}, base_url=base_url)
    return sandbox_path

@cy_log
def sandbox_remove(sandbox_name=None, base_url=DEFAULT_BASE_URL):
    """Delete sandbox contents and remove its directory.

    If the current sandbox is the entire file system on a Cytoscape workstation, trying to delete it
    is an error. Otherwise, deleting the current sandbox results in the default sandbox becoming the
    new current sandbox. When running on the same workstation as Cytoscape, the default
    sandbox is the entire file system on the Cytoscape workstation. When running in a remote server,
    the default sandbox is the 'default_sandbox' created automatically under the
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
        into account when choosing a cloud service for your files.

        When you capture a URL in the clipboard, you should copy it into your program for use with ``sandbox_url_to()``.

    This function is most useful for Notebooks executing on a remote server. For Notebooks running on the
    local Cytoscape workstation, consider using the import_file_from_url() function if the Notebook is not
    intended to ever run on a remote server.

    Args:
        source_url (str): URL addressing cloud file to download
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
        # really is being used. This would be appropriate if we're running in on the Cytoscape workstation. A
        # Cytoscape workstation environment is still free to operate in a sandbox if it wants.
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
        # Either running remotely or a sandbox has been defined for local execution. Either way,
        # use the sandbox and interpret the file_name as relative to the sandbox directory. This
        # works well when file_name is a relative name. If it's absolute, it'll be appended to the
        # sandbox directory name, which will create something unintelligible that will be trapped
        # by the FileTransfer app.
        command += f' sandboxName="{sandbox_name}"'
    elif file_name:
        # Running locally with no sandbox defined ... essentially passing through to the whole workstation
        # file system. If the caller supplies an absolute path, use it ... otherwise, make it relative to
        # the current sandbox (or kernel current working directory).
        if os.path.isabs(file_name):
            pass
        else:
            file_name = os.path.join(sandbox_path, file_name)
    if file_name: command += f' fileName="{file_name}"'

    res = commands.commands_post(command, base_url=base_url)
    return res
