# -*- coding: utf-8 -*-

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
import requests
import json
import os
import uuid


# Internal module convenience imports
from .py4cytoscape_logger import log_http_result, log_http_request, detail_logger

# print(f'Starting {__name__} module')


# Call CyREST as a remote service via Jupyter-bridge
import chardet
class SpoofResponse:

    def __init__(self, url, status_code, reason, text):
        self.url = url
        self.status_code = status_code
        self.reason = reason
        self.text = text

    def __repr__(self):
        return '<SpoofResponse [%s]>' % (self.status_code)

    def json(self):
        return json.loads(self.text)

    def raise_for_status(self):
        """Raises stored :class:`HTTPError`, if one occurred."""

        if 400 <= self.status_code < 500:
            raise requests.exceptions.HTTPError(
                u'%s Client Error: %s for url: %s' % (self.status_code, self.reason, self.url), response=self)

        elif 500 <= self.status_code < 600:
            raise requests.exceptions.HTTPError(
                u'%s Server Error: %s for url: %s' % (self.status_code, self.reason, self.url), response=self)

# Create a unique channel that identifies this process so other processes don't mix up messages
_CHANNEL = None

# Get the name of the Jupyter-bridge server
_JUPYTER_BRIDGE_URL = os.environ.get('JUPYTER_BRIDGE_URL', 'https://jupyter-bridge.cytoscape.org')
_CYREST_URL_V1 = 'http://127.0.0.1:1234/v1' # Don't use 'localhost' here because Google Colab will hijack it

def get_browser_client_channel():
    return _CHANNEL


def get_jupyter_bridge_url():
    return _JUPYTER_BRIDGE_URL

def do_request_remote(method, url, **kwargs):
    log_http_request(method, url, **kwargs)

    if 'json' in kwargs:
        data = kwargs['json']
    elif 'data' in kwargs:
        data = kwargs['data'].decode('utf-8')
    else:
        data = None

    http_request = {'command': method,
                    'url': url,
                    'params': kwargs['params'] if 'params' in kwargs else None,
                    'data': data,
                    'headers': kwargs['headers'] if 'headers' in kwargs else None
                    }

    # Call Jupyter-bridge to request a Cytoscape operation. Jupyter-bridge will put the request into a queue, and
    # the local browser will pick it out, use it to call Cytoscape, and then queue a reply.
    try:
        r = requests.request('POST', f'{_JUPYTER_BRIDGE_URL}/queue_request?channel={_CHANNEL}',
                             headers={'Content-Type': 'application/json'}, json=http_request)
        r.raise_for_status()
    except Exception as e:
        raise requests.exceptions.HTTPError(f'Error posting to Jupyter-bridge: {_error_content(e)}')

    # Call Juptyer-bridge to pick up a reply queued by the local browser, which called Cytoscape to execute an operation
    # and return a reply.
    try:
        while True:
            r = requests.request('GET', f'{_JUPYTER_BRIDGE_URL}/dequeue_reply?channel={_CHANNEL}')
            if r.status_code != 408: break  # keep waiting for a result as long as we keep getting connection timeouts
        r.raise_for_status()
    except Exception as e:
        raise requests.exceptions.HTTPError(f'Error receiving from Jupyter-bridge: {_error_content(e)}')

    # We really need a JSON message coming from Jupyter-bridge. It will contain the Cytoscape HTTP response in a dict.
    # If the dict is bad, we can't continue. I have seen this happen, but as a consequence of questionable networking.
    # Specifically, I use tcpdump to monitor a message sent from Jupyter-bridge, and the message has an HTTP status,
    # headers, and JSON payload. However, on the receiver side, I use WireShark to see just the HTTP status and no
    # headers or JSON payload. The smoking gun appears to be that the headers and JSON payload are contained in the
    # TCP [FIN] packet, and never make it to the receiver side. Of course, this is bad form for TCP, but it is
    # happening. To mitigate this, I changed Jupyter-bridge to add 1500 bytes to the end of the payload. For normal-size
    # TCP packets (i.e., MTU=1500), this forces the headers and JSON payload to *not* be in the TCP [FIN] packet. This
    # seems to work, tacky as it may be. If it fails, we'll see that 'encoding' ends up being None, and the str() will
    # fail.
    try:
        content = r.content
        encoding = chardet.detect(content)['encoding']
        message = str(content, encoding, errors='replace')
        cy_reply = json.loads(message)
    except:
        content = content or 'None'
        raise requests.exceptions.HTTPError(u'Undeciperable message received from Jupyter-bridge: %s' % (str(content)))

    r = SpoofResponse(url, cy_reply['status'], cy_reply['reason'], cy_reply['text'])
    if cy_reply['status'] == 0:
        raise requests.exceptions.HTTPError(u'Could not contact url: %s' % (url), response=r)

    log_http_result(r)
    return r

def _error_content(e):
    return f'{e}' if e.response is None or e.response.text is None or e.response.text == '' else e.response.text

"""Determine whether a notebook is running. This matters because if none is running, we're going to have to
   connect to Cytoscape only via a local socket. If a notebook is running, there will be an option to connect
   via either a local socket (preferred) or Jupyter-Bridge (sufficient)."""

_notebook_is_running = None
def set_notebook_is_running(new_state=None):
    global _notebook_is_running
    old_state = _notebook_is_running
    _notebook_is_running = new_state
    return old_state

def get_notebook_is_running():
    return _notebook_is_running

def _check_notebook_is_running():
    if get_notebook_is_running() is None:
        try: # from https://exceptionshub.com/how-can-i-check-if-code-is-executed-in-the-ipython-notebook.html
            shell_class = get_ipython().__class__
            if shell_class.__name__ == 'ZMQInteractiveShell' or 'google.colab._shell' in str(shell_class):
                set_notebook_is_running(True)  # Jupyter notebook or qtconsole
            elif shell_class.__name__ == 'TerminalInteractiveShell':
                set_notebook_is_running(False)  # Terminal running IPython
            else:
                set_notebook_is_running(False)  # Other type (?)
        except NameError:
            set_notebook_is_running(False)  # Probably standard Python interpreter
        except:
            set_notebook_is_running(False)  # Safety check ... shouldn't ever happen
            detail_logger.debug('Warning: _notebook_is_running check failed')

_check_notebook_is_running()

"""Determine whether we're running locally or on a remote server. If locally (either via raw Python or via a
   locally installed Notebook), we prefer to connect to Cytoscape over a local socket. If remote, we have to
   connect over Jupyter-Bridge. Either way, we can determine which by whether Cytoscape answers to a version
   check. If Cytoscape doesn't answer, we have no information ... and we have to wait until Cytoscape is
   started and becomes reachable before we can determine local vs remote."""

_running_remote = None # None means "Don't know whether Cytoscape is local or remote yet"
def running_remote(new_state=None):
    global _running_remote
    old_state = _running_remote
    if not new_state is None:
        _running_remote = new_state
    return old_state

def check_running_remote():
    global _running_remote
    if get_notebook_is_running():
        if _running_remote is None:
            try:
                # Try connecting to a local Cytoscape, first, in case Notebook is on same machine as Cytoscape
                detail_logger.debug(f'Attempting to connect to local Cytoscape')
                r = requests.request('GET', _CYREST_URL_V1, headers={'Content-Type': 'application/json'})
                r.raise_for_status()
                _running_remote = False
                detail_logger.debug(f'Detected local Cytoscape')
            except:
                # Local Cytoscape doesn't appear to be reachable, so try reaching a remote Cytoscape via Jupyter-bridge
                try:
                    detail_logger.debug(f'Attempting to connect to remote Cytoscape')
                    do_request_remote('GET', _CYREST_URL_V1, headers={'Content-Type': 'application/json'})
                    _running_remote = True
                    detail_logger.debug(f'Detected remote Cytoscape')
                except Exception as e:
                    # Couldn't reach a local or remote Cytoscape ... use probably didn't start a Cytoscape, so assume he will eventually
                    detail_logger.debug(f'Error initially contacting Jupyter-bridge: {_error_content(e)}')
                    _running_remote = None
    else:
        _running_remote = False
    return _running_remote

def get_browser_client_js(debug_bridge=False):
    global _CHANNEL
    _CHANNEL = uuid.uuid4() # Get a new channel here ... each new browser client works on a fresh channel
    try:
        # Prepend channel number of client Javascript so it can communicate with this process via Jupyter-bridge
        r = requests.get(
            'https://raw.githubusercontent.com/cytoscape/jupyter-bridge/master/client/javascript_bridge.js')
        r.raise_for_status()
        inject_code = f'var Channel = "{_CHANNEL}"; \n\n' \
                      f'var JupyterBridge = "{_JUPYTER_BRIDGE_URL}"; \n\n' \
                      f' {r.text}'
        if debug_bridge:
            inject_code = f'var showDebug = true; \n\n' + inject_code
        return inject_code
    except Exception as e:
        raise requests.exceptions.HTTPError(f'Error creating Jupyter-bridge browser client for channel {_CHANNEL}: {_error_content(e)}')








