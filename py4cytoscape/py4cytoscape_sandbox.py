# -*- coding: utf-8 -*-

"""Logging configuration values that can be set by a user.
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

# Internal module imports

# Internal module convenience imports

_default_sandbox = {} # If a sandbox is explicitly defined, it'll override the default
PREDEFINED_SANDBOX_NAME = 'default_sandbox'
_current_sandbox_name = None
_current_sandbox_path = None # Resolve this by explicitly setting it or when first Cytoscape command is issued
_sandbox_reinitialize = True


_SANDBOX_TEMPLATE = {'sandboxName': None, 'copySamples': True, 'reinitialize': True}
def sandbox_initializer(**new_sandbox):
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

def default_sandbox(**new_sandbox):
    global _default_sandbox
    old_default_sandbox = dict(_default_sandbox)
    if len(new_sandbox):
        _default_sandbox = sandbox_initializer(init=new_sandbox)
        sandbox_reinitialize(True)
    return old_default_sandbox

def get_current_sandbox_name():
    return _current_sandbox_name

def get_current_sandbox_path():
    return _current_sandbox_path

def get_current_sandbox():
    return _current_sandbox_path, _current_sandbox_name

def set_current_sandbox(sandbox_name, sandbox_path):
    global _current_sandbox_name, _current_sandbox_path
    _current_sandbox_name = sandbox_name
    _current_sandbox_path = sandbox_path
    return get_current_sandbox()

def sandbox_reinitialize(new_state=None):
    global _sandbox_reinitialize
    old_state = _sandbox_reinitialize
    if new_state is not None:
        _sandbox_reinitialize = new_state
    return old_state

_current_sandbox_name, _current_sandbox_path = set_current_sandbox(None, None)

"""There are four cases: {Raw Python, Notebook Python} x {Local Execution, Remote Execution}. They affect
 how/whether a sandbox is used. If no sandbox is used, we assume that file names/paths used in py4cytoscape
 identify files/paths on the Cytoscape workstation. If a sandbox is used, all file names/paths are relative
 to the sandbox. Here is a discussion of each case:
  
 (Raw Python, Local Execution) - The common case would be "no sandbox", though it is reasonable that a sandbox 
     would be desirable, especially if the workflow is expected to execute remotely (with Notebook), too. IMPLEMENTATION:
     Use no sandbox, but allow workflow author to easily opt for a sandbox early in the workflow. 
     
 (Raw Python, Remote Execution) - This means execution without a Notebook system. This case is unknown to us, so
     handling it won't be prioritized. IMPLEMENTATION: Same as (Notebook Python, Local Execution).
     
 (Notebook Python, Local Execution) - We assume that the workflow author intends that a Notebook be executable either
     on a local or remote Notebook. The common case would be a sandbox, which should be created by py4cytoscape by
     default. It's plausible that the workflow author would not intend portability to a remote Notebook, and would 
     prefer to access files/paths unfiltered by a sandbox. This should be an easy choice to implement. IMPLEMENTATION:
     Use default sandbox, but allow workflow author to easily opt for no sandbox early in the workflow.
     
 (Notebook Python, Remote Execution) - The common case would be "sandbox", though it is plausible (but unlikely) 
     that running without a sandbox would be useful (as would be the case where direct access to the Cytoscape
     workstation file system is preferred, and the Python workflow integrates with other Python workflows/libraries).
     IMPLEMENTATION: Same as (Notebook Python, Local Execution).
  
  It's important for both Notebook Python cases to share the same default behavior because development of a Notebook
  locally and then promoting it to remote execution enables the very important goal of shared or publishable workflows.
  
  As a practical matter, the following default sandbox logic would apply:
  
  if on_notebook or remote_execution:
      set up pre-defined sandbox
  else # Raw Python, Local Execution
      don't use sandbox

  This logic would apply immediately before the first Cytoscape command (i.e., when py4Cytoscape determines whether
  on_notebook and remote_execution. It can be pre-empted by explicitly declaring a sandbox (or no sandbox) at any
  time before or after the first Cytoscape command, and an explicit sandbox declaration overrules the default.
    
  """

