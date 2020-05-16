# -*- coding: utf-8 -*-

""" Test functions in styles_dependencies.py.

License:
    Copyright 2020 The Cytoscape Consortium

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

import unittest
import re
import json
from requests import RequestException

from test_utils import *


class StyleDependenciesTests(unittest.TestCase):
    def setUp(self):
        try:
            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    _TEST_STYLE = 'galFiltered Style'

    @print_entry_exit
    def test_get_set_style_dependencies(self):
        # Initialization
        load_test_session()
        expected_def_orig = {'arrowColorMatchesEdge': False, 'nodeCustomGraphicsSizeSync': True, 'nodeSizeLocked': False}
        expected_gal_orig = {'arrowColorMatchesEdge': False, 'nodeCustomGraphicsSizeSync': True, 'nodeSizeLocked': True}

        # Verify that the initial dependencies are as expected for both styles
        self.assertDictEqual(get_style_dependencies(), expected_def_orig)
        self.assertDictEqual(get_style_dependencies(style_name=self._TEST_STYLE), expected_gal_orig)

        # Verify that setting a default style returns expected dict and sets expected properties
        set_res = set_style_dependencies(dependencies={'arrowColorMatchesEdge': True, 'nodeCustomGraphicsSizeSync': False})
        self._check_set_dependency(set_res)
        self.assertDictEqual(get_style_dependencies(),
                             {'arrowColorMatchesEdge': True, 'nodeCustomGraphicsSizeSync': False,
                              'nodeSizeLocked': False})
        self.assertDictEqual(set_style_dependencies(dependencies={'nodeSizeLocked': True}), set_res)
        self.assertDictEqual(get_style_dependencies(),
                             {'arrowColorMatchesEdge': True, 'nodeCustomGraphicsSizeSync': False,
                              'nodeSizeLocked': True})

        # Verify that the galFiltered style is unaffected, and that setting properties actually sets them
        self.assertDictEqual(get_style_dependencies(style_name=self._TEST_STYLE), expected_gal_orig)
        self.assertDictEqual(set_style_dependencies(style_name=self._TEST_STYLE, dependencies={'arrowColorMatchesEdge': True, 'nodeCustomGraphicsSizeSync': False, 'nodeSizeLocked': True}), set_res)
        self.assertDictEqual(get_style_dependencies(style_name=self._TEST_STYLE),
                             {'arrowColorMatchesEdge': True, 'nodeCustomGraphicsSizeSync': False,
                              'nodeSizeLocked': True})

        # Verify that setting no properties results in no changes
        self.assertDictEqual(set_style_dependencies(style_name=self._TEST_STYLE), set_res)
        self.assertDictEqual(get_style_dependencies(style_name=self._TEST_STYLE),
                             {'arrowColorMatchesEdge': True, 'nodeCustomGraphicsSizeSync': False,
                              'nodeSizeLocked': True})

        # Verify that addressing a bogus style is caught
        self.assertRaises(CyError, get_style_dependencies, style_name='bogusStyle')
        self.assertRaises(CyError, set_style_dependencies, style_name='bogusStyle')

    @print_entry_exit
    def test_match_arrow_color_to_edge(self):
        self._check_dependency(match_arrow_color_to_edge, 'arrowColorMatchesEdge')

    @print_entry_exit
    def test_lock_node_dimensions(self):
        self._check_dependency(lock_node_dimensions, 'nodeSizeLocked')

    @print_entry_exit
    def test_sync_node_custom_graphics_size(self):
        self._check_dependency(sync_node_custom_graphics_size, 'nodeCustomGraphicsSizeSync')


    def _check_dependency(self, setter_func, prop_name):
        # Initialization
        load_test_session()
        orig_state = get_style_dependencies(style_name=self._TEST_STYLE)[prop_name]

        # Verify that setting the same value on the same style doesn't change the property
        set_res = setter_func(orig_state, style_name=self._TEST_STYLE)
        self._check_set_dependency(set_res)
        self.assertEqual(get_style_dependencies(style_name=self._TEST_STYLE)[prop_name], orig_state)

        # Verify that setting the opposite value on the same style properly changes the property
        set_res = setter_func(not orig_state, style_name=self._TEST_STYLE)
        self._check_set_dependency(set_res)
        self.assertEqual(get_style_dependencies(style_name=self._TEST_STYLE)[prop_name], not orig_state)

        # Verify that setting the original value on the same style changes the property back
        set_res = setter_func(orig_state, style_name=self._TEST_STYLE)
        self._check_set_dependency(set_res)
        self.assertEqual(get_style_dependencies(style_name=self._TEST_STYLE)[prop_name], orig_state)

        # Verify that setting the opposite value on a different style doesn't change the original style's property
        set_res = setter_func(not orig_state)
        self._check_set_dependency(set_res)
        self.assertEqual(get_style_dependencies(style_name=self._TEST_STYLE)[prop_name], orig_state)
        self.assertEqual(get_style_dependencies()[prop_name], not orig_state)

        # Verify that addressing a bogus style is caught
        self.assertRaises(CyError, setter_func, True, style_name='bogusStyle')

    def _check_set_dependency(self, set_res):
        self.assertIsInstance(set_res, dict)
        self.assertEqual(len(set_res), 1)
        self.assertIn('views', set_res)
        self.assertIsInstance(set_res['views'], list)
        self.assertIsInstance(set_res['views'][0], int)
        return set_res

if __name__ == '__main__':
    unittest.main()
