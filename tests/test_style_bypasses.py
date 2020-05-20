# -*- coding: utf-8 -*-

""" Test functions in styles_bypasses.py.

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


class StyleBypassesTests(unittest.TestCase):
    def setUp(self):
        try:
            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    _TEST_STYLE = 'galFiltered Style'

    @print_entry_exit
    def test_set_node_property_bypass(self):

        self._set_property_bypass(set_node_property_bypass, get_node_property, 'node', 'NODE_FILL_COLOR')

    @print_entry_exit
    def test_clear_node_property_bypass(self):

        self._clear_property_bypass(clear_node_property_bypass, set_node_property_bypass, get_node_property, 'node', 'NODE_FILL_COLOR')

    @print_entry_exit
    def test_set_edge_property_bypass(self):

        self._set_property_bypass(set_edge_property_bypass, get_edge_property, 'edge', 'EDGE_UNSELECTED_PAINT')

    @print_entry_exit
    def test_clear_edge_property_bypass(self):

        self._clear_property_bypass(clear_edge_property_bypass, set_edge_property_bypass, get_edge_property, 'edge', 'EDGE_UNSELECTED_PAINT')




    def _set_property_bypass(self, bypass_func, getter_func, table, visual_property):
        # Initialization
        load_test_session()
        all_names = get_table_columns(columns='name', table=table)

        def check_bypass(res, set_color):
            self.assertIsInstance(res, str)
            self.assertEqual(res, '')
            cur_colors = getter_func(visual_property=visual_property)
            self.assertEqual(len(cur_colors), len(all_names.index))
            color_check = [name in cur_colors and cur_colors[name] == set_color     for cur, name in zip(cur_colors, all_names['name'])]
            self.assertFalse(False in color_check)

        res = bypass_func(list(all_names['name']), ['#FF0000'], visual_property)
        check_bypass(res, '#FF0000')

        res = bypass_func(list(all_names['name']), '#FF00FF', visual_property)
        check_bypass(res, '#FF00FF')

        res = bypass_func(list(all_names['name']), ['#0000FF'] * len(all_names.index), visual_property)
        check_bypass(res, '#0000FF')

        res = bypass_func(list(all_names.index), ['#00FF00'], visual_property)
        check_bypass(res, '#00FF00')

        # TODO: Figure out what this should return ... with None for node list
        # self.assertEqual(set_node_property_bypass(None, ['#FF0000'], visual_property), '')

        # Verify that bad node list is caught
        self.assertRaises(CyError, bypass_func, ['BogusNode'], ['#FF0000'], visual_property)

        # Verify that bad property name is caught
        self.assertRaises(CyError, bypass_func, list(all_names['name']), ['#FF0000'], None)
        self.assertEqual(bypass_func(list(all_names['name']), ['#FF0000'], 'BogusProperty'), '')

        # Verify that mismatch of count of nodes to properties is caught
        self.assertRaises(CyError, bypass_func(list(all_names['name']), ['#FF0000', '#FF00FF'], visual_property))

        # Verify that invalid network is caught
        self.assertRaises(CyError, bypass_func, list(all_names['name']), ['#FF0000'], visual_property, network='BogusNetwork')

    def _clear_property_bypass(self, clear_func, bypass_func, getter_func, table, visual_property):
        # Initialization
        load_test_session()
        all_names = get_table_columns(columns='name', table=table)
        orig_colors = getter_func(visual_property=visual_property)

        def check_bypass(res, set_color):
            self.assertIsInstance(res, str)
            self.assertEqual(res, '')
            cur_colors = getter_func(visual_property=visual_property)
            self.assertEqual(len(cur_colors), len(all_names.index))
            color_check = [name in cur_colors and cur_colors[name] == set_color     for cur, name in zip(cur_colors, all_names['name'])]
            self.assertFalse(False in color_check)

        # Verify that when all nodes have colors, supplying node names clears them all
        res = bypass_func(list(all_names['name']), ['#FF0000'], visual_property)
        check_bypass(res, '#FF0000')
        self.assertDictEqual(clear_func(list(all_names['name']), visual_property), {'data': {}, 'errors': []})
        reset_colors = getter_func(visual_property=visual_property)
        self.assertDictEqual(reset_colors, orig_colors)

        # Verify that when all nodes have colors, supplying node SUIDs clears them all
        res = bypass_func(list(all_names['name']), ['#FF00CC'], visual_property)
        check_bypass(res, '#FF00CC')
        self.assertDictEqual(clear_func(list(all_names.index), visual_property),
                             {'data': {}, 'errors': []})
        reset_colors = getter_func(visual_property=visual_property)
        self.assertDictEqual(reset_colors, orig_colors)

        # Verify that supplying an empty node list is caught
        self.assertRaises(TypeError, clear_func, None, visual_property)

        # Verify that bad node list is caught
        self.assertRaises(CyError, clear_func, 'all', visual_property)
        self.assertRaises(CyError, clear_func, ['BogusNode'], visual_property)

        # Verify that bad property name is caught
        self.assertRaises(CyError, clear_func, list(all_names['name']), None)
        self.assertRaises(CyError, clear_func, list(all_names['name']), 'BogusProperty')

        # Verify that invalid network is caught
        self.assertRaises(CyError, clear_func, list(all_names['name']), visual_property, network='BogusNetwork')


if __name__ == '__main__':
    unittest.main()
