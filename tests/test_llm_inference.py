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


def _make_fake_lms(models=None, respond_return='response text', stream_fragments=None):
    """Build a fake ``lmstudio`` module whose Client is a context manager.

    Returns a tuple of (fake_lms, fake_model) so tests can assert on call args.
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

    fake_lms = mock.MagicMock(name='lmstudio')
    fake_lms.Client.return_value = fake_client
    return fake_lms, fake_model, fake_client


class LLMInferenceTests(unittest.TestCase):

    def test_public_api_exported(self):
        # Verify the module-level functions are present
        for name in ('llm_infer', 'llm_infer_stream', 'list_llm_models',
                     'llm_server_reachable', 'DEFAULT_LLM_HOST'):
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


if __name__ == '__main__':
    unittest.main()
