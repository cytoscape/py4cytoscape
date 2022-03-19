# -*- coding: utf-8 -*-

"""Low level sandbox functions and state broken out into this file to avoid circular module usage.
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
import os

# Internal module imports

# Internal module convenience imports

# print(f'Starting {__name__} module')


_default_sandbox = {} # Once a sandbox is explicitly defined, it'll override this default
_default_sandbox_path = None
PREDEFINED_SANDBOX_NAME = 'default_sandbox'
_current_sandbox_name = None
_current_sandbox_path = None # Resolve this by explicitly setting it or when first Cytoscape command is issued
_sandbox_reinitialize = True


_SANDBOX_TEMPLATE = {'sandboxName': None, 'copySamples': True, 'reinitialize': True}
def sandbox_initializer(**new_sandbox):
    # Start with a sandbox template and update properties using whatever is found in the new_sandbox
    if len(new_sandbox) == 1 and 'init' in new_sandbox:
        params = new_sandbox['init']
    else:
        params = new_sandbox
    sandbox = dict(_SANDBOX_TEMPLATE)
    for key, val in params.items():
        if key in sandbox:
            sandbox[key] = val
        else:
            raise Exception(f'Invalid key {key} in sandbox parameter list')
    return sandbox

def set_default_sandbox(**new_sandbox):
    # Set and return the sandbox properties to be used as a default, probably based on whether running remote
    global _default_sandbox
    _default_sandbox = sandbox_initializer(init=new_sandbox)
    return _default_sandbox

def get_default_sandbox():
    # Return whatever is the current default sandbox properties
    return _default_sandbox

def set_default_sandbox_path(newPath):
    # Set and return the default path, which isn't one of the properties tracked in the default_sandbox
    global _default_sandbox_path
    _default_sandbox_path = newPath
    return _default_sandbox_path

def get_default_sandbox_path():
    # Return the default path, which isn't one of the properties tracked in the default_sandbox
    return _default_sandbox_path

def get_current_sandbox_name():
    # Return the current sandbox name
    return _current_sandbox_name

def get_current_sandbox_path():
    # Return the current sandbox path
    return _current_sandbox_path

def get_current_sandbox():
    # Return both the current sandbox name and path
    return _current_sandbox_name, _current_sandbox_path

def set_current_sandbox(sandbox_name, sandbox_path):
    # Set and return the current sandbox name and path
    global _current_sandbox_name, _current_sandbox_path
    _current_sandbox_name = sandbox_name
    _current_sandbox_path = sandbox_path
    return get_current_sandbox()

def set_sandbox_reinitialize(do_reinitialize=True):
    # Set and return flag indicating that next command should reinitialize the sandbox according to the default_sandbox
    global _sandbox_reinitialize
    _sandbox_reinitialize = do_reinitialize
    return _sandbox_reinitialize

def get_sandbox_reinitialize():
    # Return flag indicating that next command should reinitialize the sandbox according to the default_sandbox
    return _sandbox_reinitialize

def get_abs_sandbox_path(file_location):
    sandbox_name, sandbox_path = get_current_sandbox()
    if not sandbox_name:
        return os.path.abspath(file_location)
    elif sandbox_name and sandbox_path:
        return f'{sandbox_path}/{file_location}'
    else:
        return file_location

def reset_default_sandbox():
    # Reset the entire state of the sandbox system
    global _default_sandbox, _default_sandbox_path , _sandbox_reinitialize
    _default_sandbox = {}
    _default_sandbox_path = None
    set_current_sandbox(None, None)
    _sandbox_reinitialize = True


reset_default_sandbox() # Create a clean slate


"""There are four cases: {Raw Python, Notebook Python} x {Local Execution, Remote Execution}. We have
 to draw these distinctions because there may be a difference between the file system seen by the Python
 script as distinct from Cytoscape. For example, when running standalone Python on the same workstation as
 Cytoscape, both Python and Cytoscape see the same file system. When running Python in a Notebook on a remote
 Notebook server, Python sees the server's file system, while Cytoscape sees the workstation's file system.
 
 The four cases affect how/whether a sandbox is used. If no sandbox is used, we assume that file names/paths 
 used in py4cytoscape identify files/paths on the Cytoscape workstation. If a sandbox is used, all 
 file names/paths are relative to the sandbox. Here is a discussion of each case:
  
 (Raw Python, Local Execution) - The common case would be "no sandbox", though it is reasonable that a sandbox 
     would be desirable, especially if the workflow is expected to execute remotely (with Notebook), too. IMPLEMENTATION:
     Use no sandbox, but allow workflow author to easily opt for a sandbox early in the workflow. By default,
     non-absolute paths are evaluated relative to the Python kernel's current directory ... this is consistent with
     pre-sandbox behaviors of py4cytoscape functions. 
     
 (Raw Python, Remote Execution) - This means execution without a Notebook system. This case is unknown to us, so
     handling it won't be prioritized. IMPLEMENTATION: Same as (Notebook Python, Remote Execution).
     
 (Notebook Python, Local Execution) - The common case would be "no sandbox", the same as (Raw Python, Local Execution).
     This is especially important for casual users and students running notebooks. For users that intend to develop
     notebooks and execute them remotely, a sandbox can be manually created easily at the beginning of the workflow.
     IMPLEMENTATION: same as (Raw Python, Local Execution). 
   
 (Notebook Python, Remote Execution) - The common case would be "sandbox", though it is plausible (but unlikely) 
     that running without a sandbox would be useful (as would be the case where direct access to the Cytoscape
     workstation file system is preferred, and the Python workflow integrates with other Python workflows/libraries).
     IMPLEMENTATION: Create a default sandbox and use it. Worry about the direct file system access case if it ever
     comes up.
  
  As a practical matter, the following default sandbox logic would apply:
  
  if remote_execution:
      set up pre-defined sandbox
  else # Local Execution
      don't use sandbox ... use kernel's CWD instead ... but allow workflow to create sandbox

  This logic would apply immediately before the first Cytoscape command (i.e., when py4Cytoscape determines whether
  remote_execution). It can be pre-empted by explicitly declaring a sandbox (or no sandbox) at any
  time before or after the first Cytoscape command, and an explicit sandbox declaration overrules the default.
  
  Note that one would think that py4cytoscape should set up the sandbox as part of its module initialization. 
  Similarly, one would think that at that time, a determination of whether a Notebook is running on 
  a remote server should be possible. It's not possible to determine remote-or-not because that determination 
  relies on Cytoscape having been started on the workstation. (If it has been started, then accessing it 
  directly 127.0.0.1 or via Jupyter-Bridge is possible and necessary.) Because we allow the user to start 
  Cytoscape after module initialization, the remote-or-not decision is deferred, too, and so is creation of 
  the default sandbox (which relies on a Cytoscape connection).
  
  So, the remote-or-not and sandbox initialization are carried out lazily upon execution of the first Cytoscape
  command. And it's also possible that the first Cytoscape command could be a sandbox_set() that changes the sandbox
  to be different than the default.
  
  Finally, while we intend that the user will have installed the FileTransfer app into Cytoscape (and that it will be
  core at some point), we have to allow for the FileTransfer app to be missing in the case of (Raw Python, Local 
  Execution) -- other cases really do need sandboxes, so the absence of FileTransfer would be an error. In that
  situation, the sandbox should be considered to be the kernel's CWD.    
  """

