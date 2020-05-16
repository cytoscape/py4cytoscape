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
        self.assertIsInstance(set_res, dict)
        self.assertEqual(len(set_res), 1)
        self.assertIn('views', set_res)
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








if __name__ == '__main__':
    unittest.main()
