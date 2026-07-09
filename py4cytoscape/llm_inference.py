# -*- coding: utf-8 -*-

"""Functions for running local LLM inference via the LM Studio Python SDK.

These helpers provide a thin, optional wrapper around the ``lmstudio`` package
so that py4cytoscape workflows can send prompts to a locally running LM Studio
server (for example, to summarize a network, explain results, or draft
annotations) without depending on any cloud service.

The ``lmstudio`` package is an *optional* dependency. It is imported lazily so
that py4cytoscape continues to work when the package is not installed; the LLM
functions raise a helpful :class:`CyError` in that case. Install it with::

    pip install lmstudio

and ensure the LM Studio server is running (``lms server start``).
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

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_logger import cy_log

# Default host:port for the LM Studio local server (distinct from Cytoscape's CyREST).
DEFAULT_LLM_HOST = 'localhost:1234'


def _import_lmstudio(caller):
    """Import the optional ``lmstudio`` package or raise a helpful CyError."""
    try:
        import lmstudio  # noqa: F401  (imported for availability check)
        return lmstudio
    except ImportError:
        raise CyError(
            "The 'lmstudio' package is required for LLM inference but is not installed. "
            "Install it with 'pip install lmstudio' and start the LM Studio server "
            "with 'lms server start'.",
            caller=caller)


@cy_log
def llm_server_reachable(host=DEFAULT_LLM_HOST):
    """Check whether a local LM Studio server is reachable.

    Args:
        host (str): Host and port of the LM Studio server. Default is ``localhost:1234``.

    Returns:
        bool: True if the server responds, False otherwise.

    Raises:
        CyError: if the ``lmstudio`` package is not installed

    Examples:
        >>> llm_server_reachable()
        True
    """
    lms = _import_lmstudio(sys._getframe().f_code.co_name)
    try:
        with lms.Client(api_host=host) as client:
            client.list_downloaded_models()
        return True
    except Exception:
        return False


@cy_log
def list_llm_models(host=DEFAULT_LLM_HOST):
    """List the LLM models downloaded in the local LM Studio installation.

    Args:
        host (str): Host and port of the LM Studio server. Default is ``localhost:1234``.

    Returns:
        list: list of model key strings (e.g. ``['mistralai/mistral-7b-instruct-v0.3']``)

    Raises:
        CyError: if the ``lmstudio`` package is not installed or the server can't be reached

    Examples:
        >>> list_llm_models()
        ['mistralai/mistral-7b-instruct-v0.3', 'text-embedding-nomic-embed-text-v1.5']
    """
    caller = sys._getframe().f_code.co_name
    lms = _import_lmstudio(caller)
    try:
        with lms.Client(api_host=host) as client:
            models = client.list_downloaded_models()
    except Exception as e:
        raise CyError(f"Could not reach LM Studio server at '{host}': {e}", caller=caller)

    keys = []
    for m in models:
        keys.append(getattr(m, 'model_key', None) or getattr(m, 'path', None) or str(m))
    return keys


@cy_log
def llm_infer(prompt, model_key=None, host=DEFAULT_LLM_HOST, config=None):
    """Run a single-shot LLM completion against the local LM Studio server.

    Args:
        prompt (str): The text prompt to send to the model.
        model_key (str): Key of the model to use (e.g. ``mistralai/mistral-7b-instruct-v0.3``).
            If None, the currently loaded/default model is used.
        host (str): Host and port of the LM Studio server. Default is ``localhost:1234``.
        config (dict): Optional inference parameters passed through to the SDK,
            e.g. ``{'temperature': 0.7, 'maxTokens': 256}``.

    Returns:
        str: The model's response text.

    Raises:
        CyError: if the ``lmstudio`` package is not installed, the server can't be
            reached, or inference fails

    Examples:
        >>> llm_infer('Summarize what a protein-protein interaction network is.')
        'A protein-protein interaction network represents ...'
        >>> llm_infer('Say hello', model_key='mistralai/mistral-7b-instruct-v0.3', config={'temperature': 0.2})
        'Hello! How can I help you today?'
    """
    caller = sys._getframe().f_code.co_name
    if prompt is None or str(prompt).strip() == '':
        raise CyError('prompt must be a non-empty string', caller=caller)
    lms = _import_lmstudio(caller)
    try:
        with lms.Client(api_host=host) as client:
            model = client.llm.model(model_key) if model_key else client.llm.model()
            result = model.respond(prompt, config=config) if config else model.respond(prompt)
            return str(result)
    except CyError:
        raise
    except Exception as e:
        raise CyError(f"LLM inference failed on host '{host}': {e}", caller=caller)


@cy_log
def llm_infer_stream(prompt, model_key=None, host=DEFAULT_LLM_HOST, config=None):
    """Run a streaming LLM completion, yielding response text fragments.

    This is useful for displaying tokens as they are produced. The LM Studio
    connection remains open until the returned generator is exhausted.

    Args:
        prompt (str): The text prompt to send to the model.
        model_key (str): Key of the model to use. If None, the currently loaded/default model is used.
        host (str): Host and port of the LM Studio server. Default is ``localhost:1234``.
        config (dict): Optional inference parameters passed through to the SDK,
            e.g. ``{'temperature': 0.7, 'maxTokens': 256}``.

    Returns:
        Iterator[str]: an iterator of response text fragments

    Raises:
        CyError: if the ``lmstudio`` package is not installed, the server can't be
            reached, or inference fails

    Examples:
        >>> for fragment in llm_infer_stream('List three graph layout algorithms.'):
        ...     print(fragment, end='')
    """
    caller = sys._getframe().f_code.co_name
    if prompt is None or str(prompt).strip() == '':
        raise CyError('prompt must be a non-empty string', caller=caller)
    lms = _import_lmstudio(caller)

    def _generate():
        try:
            with lms.Client(api_host=host) as client:
                model = client.llm.model(model_key) if model_key else client.llm.model()
                stream = model.respond_stream(prompt, config=config) if config else model.respond_stream(prompt)
                for fragment in stream:
                    yield getattr(fragment, 'content', str(fragment))
        except Exception as e:
            raise CyError(f"LLM streaming inference failed on host '{host}': {e}", caller=caller)

    return _generate()


@cy_log
def llm_list_loaded_models(host=DEFAULT_LLM_HOST):
    """List the LLM model identifiers currently loaded in memory in LM Studio.

    Args:
        host (str): Host and port of the LM Studio server. Default is ``localhost:1234``.

    Returns:
        list: list of identifier strings for each loaded model
            (e.g. ``['mistralai/mistral-7b-instruct-v0.3']``)

    Raises:
        CyError: if the ``lmstudio`` package is not installed or the server can't be reached

    Examples:
        >>> llm_list_loaded_models()
        ['mistralai/mistral-7b-instruct-v0.3']
    """
    caller = sys._getframe().f_code.co_name
    lms = _import_lmstudio(caller)
    try:
        with lms.Client(api_host=host) as client:
            handles = client.llm.list_loaded()
    except Exception as e:
        raise CyError(f"Could not reach LM Studio server at '{host}': {e}", caller=caller)
    return [getattr(h, 'identifier', str(h)) for h in handles]


@cy_log
def llm_load_model(model_key, identifier=None, ttl=3600, config=None, host=DEFAULT_LLM_HOST):
    """Load a model into memory in the local LM Studio server.

    If the model is already loaded, no additional instance is created and the
    existing model identifier is returned.

    Args:
        model_key (str): Model key to load (e.g. ``mistralai/mistral-7b-instruct-v0.3``).
            Must correspond to a downloaded model.
        identifier (str): Optional custom identifier for this instance. If None,
            the server assigns one (usually the same as ``model_key``).
        ttl (int): Time-to-live in seconds before the server auto-unloads the model
            when idle. Default is 3600 (1 hour). Pass None to disable auto-unload.
        config (dict): Optional model load parameters (e.g. context length, GPU layers).
        host (str): Host and port of the LM Studio server. Default is ``localhost:1234``.

    Returns:
        str: The identifier of the loaded model instance.

    Raises:
        CyError: if the ``lmstudio`` package is not installed, ``model_key`` is empty,
            the model is not downloaded, or the server can't be reached

    Examples:
        >>> llm_load_model('mistralai/mistral-7b-instruct-v0.3')
        'mistralai/mistral-7b-instruct-v0.3'
        >>> llm_load_model('mistralai/mistral-7b-instruct-v0.3', ttl=None)
        'mistralai/mistral-7b-instruct-v0.3'
    """
    caller = sys._getframe().f_code.co_name
    if not model_key or str(model_key).strip() == '':
        raise CyError('model_key must be a non-empty string', caller=caller)
    lms = _import_lmstudio(caller)
    try:
        with lms.Client(api_host=host) as client:
            # Avoid loading a duplicate instance if already present
            handles = client.llm.list_loaded()
            for h in handles:
                if getattr(h, 'identifier', None) == model_key:
                    return model_key
            kwargs = {'ttl': ttl}
            if identifier is not None:
                kwargs['instance_identifier'] = identifier
            if config is not None:
                kwargs['config'] = config
            handle = client.llm.load_new_instance(model_key, **kwargs)
            return getattr(handle, 'identifier', model_key)
    except CyError:
        raise
    except Exception as e:
        raise CyError(f"Failed to load model '{model_key}' on host '{host}': {e}", caller=caller)


@cy_log
def llm_unload_model(model_key, host=DEFAULT_LLM_HOST):
    """Unload a model from memory in the local LM Studio server.

    If the model is not currently loaded, the call is a no-op and returns False.

    Args:
        model_key (str): Identifier of the loaded model to unload.
        host (str): Host and port of the LM Studio server. Default is ``localhost:1234``.

    Returns:
        bool: True if the model was unloaded, False if it was not loaded.

    Raises:
        CyError: if the ``lmstudio`` package is not installed, ``model_key`` is empty,
            or the server can't be reached

    Examples:
        >>> llm_unload_model('mistralai/mistral-7b-instruct-v0.3')
        True
        >>> llm_unload_model('model/not-loaded')
        False
    """
    caller = sys._getframe().f_code.co_name
    if not model_key or str(model_key).strip() == '':
        raise CyError('model_key must be a non-empty string', caller=caller)
    lms = _import_lmstudio(caller)
    try:
        with lms.Client(api_host=host) as client:
            handles = client.llm.list_loaded()
            loaded_ids = [getattr(h, 'identifier', None) for h in handles]
            if model_key not in loaded_ids:
                return False
            client.llm.unload(model_key)
            return True
    except CyError:
        raise
    except Exception as e:
        raise CyError(f"Failed to unload model '{model_key}' on host '{host}': {e}", caller=caller)


@cy_log
def llm_ensure_model_loaded(model_key, ttl=3600, config=None, host=DEFAULT_LLM_HOST):
    """Ensure a model is loaded, loading it first if necessary.

    This is the recommended helper to call before running inference: it avoids
    loading a redundant instance when the model is already in memory.

    Args:
        model_key (str): Model key to ensure is loaded.
        ttl (int): Time-to-live in seconds passed to :func:`llm_load_model` when
            the model needs to be loaded. Default is 3600 (1 hour).
        config (dict): Optional load configuration passed to :func:`llm_load_model`.
        host (str): Host and port of the LM Studio server. Default is ``localhost:1234``.

    Returns:
        bool: True if the model was already loaded, False if it had to be loaded now.

    Raises:
        CyError: if the ``lmstudio`` package is not installed, the model is not
            downloaded, or the server can't be reached

    Examples:
        >>> llm_ensure_model_loaded('mistralai/mistral-7b-instruct-v0.3')  # already in memory
        True
        >>> llm_ensure_model_loaded('mistralai/mistral-7b-instruct-v0.3')  # was not loaded
        False
    """
    caller = sys._getframe().f_code.co_name
    if not model_key or str(model_key).strip() == '':
        raise CyError('model_key must be a non-empty string', caller=caller)
    lms = _import_lmstudio(caller)
    try:
        with lms.Client(api_host=host) as client:
            handles = client.llm.list_loaded()
            already_loaded = any(getattr(h, 'identifier', None) == model_key for h in handles)
            if already_loaded:
                return True
            kwargs = {'ttl': ttl}
            if config is not None:
                kwargs['config'] = config
            client.llm.load_new_instance(model_key, **kwargs)
            return False
    except CyError:
        raise
    except Exception as e:
        raise CyError(f"Failed to ensure model '{model_key}' is loaded on host '{host}': {e}", caller=caller)
