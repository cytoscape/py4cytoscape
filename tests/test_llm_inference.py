# -*- coding: utf-8 -*-

""" Test functions in llm_inference.py.

These are hermetic unit tests: the LM Studio SDK (``lmstudio``) and its server
are mocked, so the tests require neither the optional ``lmstudio`` package nor a
running LM Studio server.
"""

"""License:
    Copyright 2020-2022 The Cytoscape Consortium

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
    documentation files (the "Software"), to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
    and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions
    of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
    WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
    OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
    OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import sys
import unittest
from unittest import mock

from py4cytoscape import llm_inference as llm
from py4cytoscape.exceptions import CyError


def _make_handle(identifier):
    """Return a minimal fake model handle with an ``identifier`` attribute."""
    h = mock.MagicMock(name=f'handle:{identifier}')
    h.identifier = identifier
    return h


def _make_fake_lms(models=None, respond_return='response text', stream_fragments=None,
                   loaded_handles=None):
    """Build a fake ``lmstudio`` module whose Client is a context manager.

    Returns a tuple of (fake_lms, fake_model, fake_client) so tests can assert
    on call args.

    Args:
        loaded_handles: list of fake model handles returned by ``client.llm.list_loaded``.
            Defaults to an empty list.
    """
    fake_model = mock.MagicMock(name='model')
    fake_model.respond.return_value = respond_return

    if stream_fragments is not None:
        fake_model.respond_stream.return_value = iter(
            [mock.MagicMock(content=frag) for frag in stream_fragments])

    fake_client = mock.MagicMock(name='client')
    # Support "with lms.Client(...) as client:"
    fake_client.__enter__.return_value = fake_client
    fake_client.__exit__.return_value = False
    fake_client.llm.model.return_value = fake_model
    fake_client.list_downloaded_models.return_value = models or []
    fake_client.llm.list_loaded.return_value = loaded_handles if loaded_handles is not None else []
    # load_new_instance returns a handle with identifier = first arg by default
    fake_client.llm.load_new_instance.side_effect = lambda key, **_: _make_handle(key)

    fake_lms = mock.MagicMock(name='lmstudio')
    fake_lms.Client.return_value = fake_client
    return fake_lms, fake_model, fake_client


class LLMInferenceTests(unittest.TestCase):

    def test_public_api_exported(self):
        # Verify all module-level functions are present
        for name in ('llm_infer', 'llm_infer_stream', 'list_llm_models',
                     'llm_server_reachable', 'llm_load_model', 'llm_unload_model',
                     'llm_ensure_model_loaded', 'llm_list_loaded_models',
                     'DEFAULT_LLM_HOST'):
            self.assertTrue(hasattr(llm, name), f'missing {name}')
        self.assertEqual(llm.DEFAULT_LLM_HOST, 'localhost:1234')

    def test_import_lmstudio_missing_raises_cyerror(self):
        # Simulate the package being absent: a None entry in sys.modules makes
        # "import lmstudio" raise ImportError.
        original = sys.modules.get('lmstudio', mock.sentinel.absent)
        sys.modules['lmstudio'] = None
        try:
            with self.assertRaises(CyError):
                llm._import_lmstudio('test_caller')
        finally:
            if original is mock.sentinel.absent:
                del sys.modules['lmstudio']
            else:
                sys.modules['lmstudio'] = original

    def test_llm_infer_returns_text(self):
        fake_lms, fake_model, _ = _make_fake_lms(respond_return='hello world')
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            result = llm.llm_infer('Say hi', model_key='some/model')
        self.assertEqual(result, 'hello world')
        fake_model.respond.assert_called_once_with('Say hi')

    def test_llm_infer_passes_config(self):
        fake_lms, fake_model, _ = _make_fake_lms(respond_return='ok')
        cfg = {'temperature': 0.2, 'maxTokens': 16}
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            result = llm.llm_infer('prompt', model_key='m', config=cfg)
        self.assertEqual(result, 'ok')
        fake_model.respond.assert_called_once_with('prompt', config=cfg)

    def test_llm_infer_uses_host(self):
        fake_lms, _, _ = _make_fake_lms(respond_return='x')
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            llm.llm_infer('p', host='example:9999')
        fake_lms.Client.assert_called_once_with(api_host='example:9999')

    def test_llm_infer_empty_prompt_raises(self):
        fake_lms, _, _ = _make_fake_lms()
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            with self.assertRaises(CyError):
                llm.llm_infer('   ')
            with self.assertRaises(CyError):
                llm.llm_infer(None)

    def test_llm_infer_wraps_sdk_error(self):
        fake_lms, fake_model, _ = _make_fake_lms()
        fake_model.respond.side_effect = RuntimeError('boom')
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            with self.assertRaises(CyError):
                llm.llm_infer('p', model_key='m')

    def test_list_llm_models(self):
        m1 = mock.MagicMock(model_key='org/model-a')
        m2 = mock.MagicMock(model_key='org/model-b')
        fake_lms, _, _ = _make_fake_lms(models=[m1, m2])
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            keys = llm.list_llm_models()
        self.assertEqual(keys, ['org/model-a', 'org/model-b'])

    def test_list_llm_models_connection_error_raises(self):
        fake_lms, _, fake_client = _make_fake_lms()
        fake_client.list_downloaded_models.side_effect = ConnectionError('down')
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            with self.assertRaises(CyError):
                llm.list_llm_models()

    def test_llm_server_reachable_true(self):
        fake_lms, _, _ = _make_fake_lms(models=[])
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            self.assertTrue(llm.llm_server_reachable())

    def test_llm_server_reachable_false(self):
        fake_lms, _, fake_client = _make_fake_lms()
        fake_client.list_downloaded_models.side_effect = ConnectionError('down')
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            self.assertFalse(llm.llm_server_reachable())

    def test_llm_infer_stream_yields_fragments(self):
        fake_lms, _, _ = _make_fake_lms(stream_fragments=['Hello', ', ', 'world'])
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            out = ''.join(llm.llm_infer_stream('prompt', model_key='m'))
        self.assertEqual(out, 'Hello, world')

    def test_llm_infer_stream_empty_prompt_raises(self):
        fake_lms, _, _ = _make_fake_lms(stream_fragments=[])
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            with self.assertRaises(CyError):
                llm.llm_infer_stream('')


class LLMModelManagementTests(unittest.TestCase):
    """Tests for llm_list_loaded_models, llm_load_model,
    llm_unload_model, and llm_ensure_model_loaded."""

    # ------------------------------------------------------------------
    # llm_list_loaded_models
    # ------------------------------------------------------------------

    def test_list_loaded_models_empty(self):
        fake_lms, _, _ = _make_fake_lms(loaded_handles=[])
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            self.assertEqual(llm.llm_list_loaded_models(), [])

    def test_list_loaded_models_returns_identifiers(self):
        handles = [_make_handle('org/model-a'), _make_handle('org/model-b')]
        fake_lms, _, _ = _make_fake_lms(loaded_handles=handles)
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            result = llm.llm_list_loaded_models()
        self.assertEqual(result, ['org/model-a', 'org/model-b'])

    def test_list_loaded_models_server_error_raises(self):
        fake_lms, _, fake_client = _make_fake_lms()
        fake_client.llm.list_loaded.side_effect = ConnectionError('down')
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            with self.assertRaises(CyError):
                llm.llm_list_loaded_models()

    # ------------------------------------------------------------------
    # llm_load_model
    # ------------------------------------------------------------------

    def test_load_model_calls_load_new_instance(self):
        fake_lms, _, fake_client = _make_fake_lms(loaded_handles=[])
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            result = llm.llm_load_model('org/model-x')
        fake_client.llm.load_new_instance.assert_called_once_with('org/model-x', ttl=3600)
        self.assertEqual(result, 'org/model-x')

    def test_load_model_idempotent_when_already_loaded(self):
        handles = [_make_handle('org/model-x')]
        fake_lms, _, fake_client = _make_fake_lms(loaded_handles=handles)
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            result = llm.llm_load_model('org/model-x')
        fake_client.llm.load_new_instance.assert_not_called()
        self.assertEqual(result, 'org/model-x')

    def test_load_model_passes_ttl_and_config(self):
        fake_lms, _, fake_client = _make_fake_lms(loaded_handles=[])
        cfg = {'contextLength': 4096}
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            llm.llm_load_model('org/m', ttl=None, config=cfg)
        fake_client.llm.load_new_instance.assert_called_once_with(
            'org/m', ttl=None, config=cfg)

    def test_load_model_passes_custom_identifier(self):
        fake_lms, _, fake_client = _make_fake_lms(loaded_handles=[])
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            llm.llm_load_model('org/m', identifier='my-instance')
        fake_client.llm.load_new_instance.assert_called_once_with(
            'org/m', ttl=3600, instance_identifier='my-instance')

    def test_load_model_empty_key_raises(self):
        fake_lms, _, _ = _make_fake_lms()
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            with self.assertRaises(CyError):
                llm.llm_load_model('')
            with self.assertRaises(CyError):
                llm.llm_load_model(None)

    def test_load_model_sdk_error_raises(self):
        fake_lms, _, fake_client = _make_fake_lms(loaded_handles=[])
        fake_client.llm.load_new_instance.side_effect = RuntimeError('no disk')
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            with self.assertRaises(CyError):
                llm.llm_load_model('org/m')

    # ------------------------------------------------------------------
    # llm_unload_model
    # ------------------------------------------------------------------

    def test_unload_model_loaded(self):
        handles = [_make_handle('org/model-x')]
        fake_lms, _, fake_client = _make_fake_lms(loaded_handles=handles)
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            result = llm.llm_unload_model('org/model-x')
        self.assertTrue(result)
        fake_client.llm.unload.assert_called_once_with('org/model-x')

    def test_unload_model_not_loaded_returns_false(self):
        fake_lms, _, fake_client = _make_fake_lms(loaded_handles=[])
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            result = llm.llm_unload_model('org/model-x')
        self.assertFalse(result)
        fake_client.llm.unload.assert_not_called()

    def test_unload_model_empty_key_raises(self):
        fake_lms, _, _ = _make_fake_lms()
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            with self.assertRaises(CyError):
                llm.llm_unload_model('')

    def test_unload_model_sdk_error_raises(self):
        handles = [_make_handle('org/m')]
        fake_lms, _, fake_client = _make_fake_lms(loaded_handles=handles)
        fake_client.llm.unload.side_effect = RuntimeError('fail')
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            with self.assertRaises(CyError):
                llm.llm_unload_model('org/m')

    # ------------------------------------------------------------------
    # llm_ensure_model_loaded
    # ------------------------------------------------------------------

    def test_ensure_model_loaded_already_loaded_returns_true(self):
        handles = [_make_handle('org/model-x')]
        fake_lms, _, fake_client = _make_fake_lms(loaded_handles=handles)
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            result = llm.llm_ensure_model_loaded('org/model-x')
        self.assertTrue(result)
        fake_client.llm.load_new_instance.assert_not_called()

    def test_ensure_model_loaded_not_loaded_loads_and_returns_false(self):
        fake_lms, _, fake_client = _make_fake_lms(loaded_handles=[])
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            result = llm.llm_ensure_model_loaded('org/model-x')
        self.assertFalse(result)
        fake_client.llm.load_new_instance.assert_called_once_with('org/model-x', ttl=3600)

    def test_ensure_model_loaded_passes_config(self):
        fake_lms, _, fake_client = _make_fake_lms(loaded_handles=[])
        cfg = {'contextLength': 2048}
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            llm.llm_ensure_model_loaded('org/m', ttl=600, config=cfg)
        fake_client.llm.load_new_instance.assert_called_once_with(
            'org/m', ttl=600, config=cfg)

    def test_ensure_model_loaded_empty_key_raises(self):
        fake_lms, _, _ = _make_fake_lms()
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            with self.assertRaises(CyError):
                llm.llm_ensure_model_loaded('')

    def test_ensure_model_loaded_sdk_error_raises(self):
        fake_lms, _, fake_client = _make_fake_lms(loaded_handles=[])
        fake_client.llm.load_new_instance.side_effect = RuntimeError('oom')
        with mock.patch.object(llm, '_import_lmstudio', return_value=fake_lms):
            with self.assertRaises(CyError):
                llm.llm_ensure_model_loaded('org/m')


if __name__ == '__main__':
    unittest.main()
