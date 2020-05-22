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

    @print_entry_exit
    def test_set_network_property_bypass(self):
        # Initialization
        load_test_session()

        # Verify that a valid property can be set properly
        orig_scale = get_network_property('NETWORK_SCALE_FACTOR')
        self.assertEqual(set_network_property_bypass(orig_scale / 2, 'NETWORK_SCALE_FACTOR'), '')
        self.assertEqual(get_network_property('NETWORK_SCALE_FACTOR'), orig_scale / 2)

        # Verify that bad property name is caught
        self.assertRaises(CyError, set_network_property_bypass, 1, None)
        self.assertEqual(set_network_property_bypass(1, 'BogusProperty'), '')

        # Verify that invalid network is caught
        self.assertRaises(CyError, set_network_property_bypass, 1, 'NETWORK_SCALE_FACTOR', network='BogusNetwork')


    @print_entry_exit
    def test_clear_network_property_bypass(self):
        # Initialization
        load_test_session()

        # Verify that a valid property can be set properly and then cleared
        orig_scale = get_network_property('NETWORK_SCALE_FACTOR')
        self.assertEqual(set_network_property_bypass(orig_scale / 2, 'NETWORK_SCALE_FACTOR'), '')
        self.assertEqual(get_network_property('NETWORK_SCALE_FACTOR'), orig_scale / 2)
        self.assertDictEqual(clear_network_property_bypass('NETWORK_SCALE_FACTOR'), {'data': {}, 'errors': []})
        self.assertEqual(get_network_property('NETWORK_SCALE_FACTOR'), orig_scale)

        # Verify that bad property name is caught
        self.assertRaises(CyError, clear_network_property_bypass, None)
        self.assertRaises(CyError, clear_network_property_bypass, 'BogusProperty')

        # Verify that invalid network is caught
        self.assertRaises(CyError, clear_network_property_bypass, 'NETWORK_SCALE_FACTOR', network='BogusNetwork')

    @print_entry_exit
    def test_unhide_all(self):
        # Initialization
        load_test_session()
        # TODO: Organize documentation better ... I didn't realize they exist even though I coded them myself!
        all_node_names = get_all_nodes()
        all_edge_names = get_all_edges()

        # Verify that edges start as visible, and when they're made invisible, they're actually invisible
        orig_visible_edges = get_edge_property(edge_names=all_edge_names, visual_property='EDGE_VISIBLE')
        self.assertEqual(len(orig_visible_edges), len(all_edge_names))
        self.assertFalse(False in [orig_visible_edges[edge]    for edge in orig_visible_edges])
        self.assertEqual(set_edge_property_bypass(all_edge_names, False, visual_property='EDGE_VISIBLE'), '')
        invisible_edges = get_edge_property(edge_names=all_edge_names, visual_property='EDGE_VISIBLE')
        self.assertEqual(len(invisible_edges), len(all_edge_names))
        self.assertFalse(True in [invisible_edges[edge]    for edge in orig_visible_edges])

        # Verify that nodes start as visible, and when they're made invisible, they're actually invisible
        orig_visible_nodes = get_node_property(node_names=all_node_names, visual_property='NODE_VISIBLE')
        self.assertEqual(len(orig_visible_nodes), len(all_node_names))
        self.assertFalse(False in [orig_visible_nodes[node]    for node in orig_visible_nodes])
        self.assertEqual(set_node_property_bypass(all_node_names, False, visual_property='NODE_VISIBLE'), '')
        invisible_nodes = get_node_property(node_names=all_node_names, visual_property='NODE_VISIBLE')
        self.assertEqual(len(invisible_nodes), len(all_node_names))
        self.assertFalse(True in [invisible_nodes[node]    for node in orig_visible_nodes])

        # Unhide everything
        self.assertEqual(unhide_all(), '')

        # Verify that all nodes and edges appear to be visible as before
        visible_nodes = get_node_property(node_names=all_node_names, visual_property='NODE_VISIBLE')
        self.assertDictEqual(visible_nodes, orig_visible_nodes)
        visible_edges = get_edge_property(edge_names=all_edge_names, visual_property='EDGE_VISIBLE')
        self.assertDictEqual(visible_edges, orig_visible_edges)

        # Verify that invalid network is caught
        self.assertRaises(CyError, unhide_all, network='BogusNetwork')

    @print_entry_exit
    def test_set_node_color_bypass(self):

        self._check_node_bypass(set_node_color_bypass, '#800000', '#800080', 'BogusColor', 'NODE_FILL_COLOR')

    @print_entry_exit
    def test_set_node_size_bypass(self):

        self._check_node_bypass(set_node_size_bypass, 50, 75.5, 'BogusSize', 'NODE_SIZE')

    @print_entry_exit
    def test_set_node_tooltip_bypass(self):

        self._check_node_bypass(set_node_tooltip_bypass, 'testtip 1', 'testtip 2', None, 'NODE_TOOLTIP')

    @print_entry_exit
    def test_set_node_width_bypass(self):

        self._check_node_bypass(set_node_width_bypass, 80, 125.5, 'BogusWidth', 'NODE_WIDTH')

    @print_entry_exit
    def test_set_node_height_bypass(self):

        self._check_node_bypass(set_node_height_bypass, 80, 125.5, 'BogusWidth', 'NODE_HEIGHT')

    @print_entry_exit
    def test_set_node_label_bypass(self):

        self._check_node_bypass(set_node_label_bypass, 'label 1', 'label 2', None, 'NODE_LABEL')


    @print_entry_exit
    def test_set_node_font_face_bypass(self):

        self._check_node_bypass(set_node_font_face_bypass, 'Dialog.italic,plain,20', 'Dialog.bold,bold,10', None, 'NODE_LABEL_FONT_FACE')

    @print_entry_exit
    def test_set_node_font_size_bypass(self):

        self._check_node_bypass(set_node_font_size_bypass, 50, 100, 'BogusSize', 'NODE_LABEL_FONT_SIZE')

    @print_entry_exit
    def test_set_node_label_color_bypass(self):

        self._check_node_bypass(set_node_label_color_bypass, '#FF00FF', '#FFFF00', 'BogusColor', 'NODE_LABEL_COLOR')

    @print_entry_exit
    def test_set_node_shape_bypass(self):

        self._check_node_bypass(set_node_shape_bypass, 'ROUND_RECTANGLE', 'OCTAGON', 'BogusShape', 'NODE_SHAPE')

        # Verify that old shapes are translated to new shapes
        load_test_session()
        nodes = get_all_nodes()[0:2] # Get 2 nodes
        self.assertEqual(set_node_shape_bypass(nodes, ['round_rect', 'rect']), '')
        xlate = get_node_property(node_names = nodes, visual_property='NODE_SHAPE')
        self.assertEqual(xlate[nodes[0]], 'ROUND_RECTANGLE')
        self.assertEqual(xlate[nodes[1]], 'RECTANGLE')

        # Verify that count of shapes matches count of nodes
        self.assertIsNone(set_node_shape_bypass(nodes, ['round_rect', 'rect', 'OCTAGON']))

    @print_entry_exit
    def test_set_node_border_width_bypass(self):

        self._check_node_bypass(set_node_border_width_bypass, 5, 10.5, 'BogusWidth', 'NODE_BORDER_WIDTH')

    @print_entry_exit
    def test_set_node_border_color_bypass(self):

        self._check_node_bypass(set_node_border_color_bypass, '#FF00FF', '#FFFF00', 'BogusColor', 'NODE_BORDER_PAINT')

    @print_entry_exit
    def test_set_node_opacity_bypass(self):

        self._check_node_bypass(set_node_opacity_bypass, 128, 192, 300, 'NODE_TRANSPARENCY')
        self._check_node_bypass(set_node_opacity_bypass, 128, 192, 300, 'NODE_BORDER_TRANSPARENCY')
        self._check_node_bypass(set_node_opacity_bypass, 128, 192, 300, 'NODE_LABEL_TRANSPARENCY')

    @print_entry_exit
    def test_clear_node_opacity_bypass(self):
        # Initialization
        load_test_session()
        nodes = get_all_nodes()[0:2] # Get 2 nodes

        # Verify that setting a bypass and then clearing it reverts to the original opacity value
        orig_node_transparency = get_node_property(nodes, 'NODE_TRANSPARENCY')
        orig_node_border_transparency = get_node_property(nodes, 'NODE_BORDER_TRANSPARENCY')
        orig_node_label_transparency = get_node_property(nodes, 'NODE_LABEL_TRANSPARENCY')
        self.assertEqual(set_node_opacity_bypass(nodes, [127, 200]), '')
        self._dict_changed(get_node_property(nodes, 'NODE_TRANSPARENCY'), orig_node_transparency)
        self._dict_changed(get_node_property(nodes, 'NODE_BORDER_TRANSPARENCY'), orig_node_border_transparency)
        self._dict_changed(get_node_property(nodes, 'NODE_LABEL_TRANSPARENCY'), orig_node_label_transparency)

        self.assertDictEqual(clear_node_opacity_bypass(nodes), {'data': {}, 'errors': []})
        self.assertDictEqual(get_node_property(nodes, 'NODE_TRANSPARENCY'), orig_node_transparency)
        self.assertDictEqual(get_node_property(nodes, 'NODE_BORDER_TRANSPARENCY'), orig_node_border_transparency)
        self.assertDictEqual(get_node_property(nodes, 'NODE_LABEL_TRANSPARENCY'), orig_node_label_transparency)

        # Verify that a bad network is caught
        self.assertRaises(CyError, clear_node_opacity_bypass, nodes, network='BogusNetwork')

    @print_entry_exit
    def test_set_node_fill_opacity_bypass(self):

        self._check_node_bypass(set_node_fill_opacity_bypass, 128, 200, 300, 'NODE_TRANSPARENCY')

    @print_entry_exit
    def test_set_node_border_opacity_bypass(self):

        self._check_node_bypass(set_node_border_opacity_bypass, 128, 200, 300, 'NODE_BORDER_TRANSPARENCY')

    @print_entry_exit
    def test_set_node_label_opacity_bypass(self):

        self._check_node_bypass(set_node_label_opacity_bypass, 128, 200, 300, 'NODE_LABEL_TRANSPARENCY')

    @print_entry_exit
    def test_hide_selected_nodes(self):
        # Initialization
        load_test_session()
        nodes = get_all_nodes()[0:2] # Get 2 nodes

        # Verify that nodes that are selected and hidden are actually hidden
        select_nodes(nodes, by_col='name')
        orig_visible = get_node_property(nodes, 'NODE_VISIBLE')
        self.assertEqual(hide_selected_nodes(), '')
        new_visible = get_node_property(nodes, 'NODE_VISIBLE')
        self._dict_changed(orig_visible, new_visible)

        # Verify that a bad network is caught
        self.assertRaises(CyError, hide_selected_nodes, network='BogusNetwork')

    @print_entry_exit
    def test_hide_nodes(self):
        # Initialization
        load_test_session()
        # TODO: Organize documentation better ... I didn't realize they exist even though I coded them myself!
        test_node_names = get_all_nodes()[0:2]

        self._check_hide(hide_nodes, get_node_property, 'NODE_VISIBLE', test_node_names)

    @print_entry_exit
    def test_unhide_nodes(self):
        # Initialization
        load_test_session()
        # TODO: Organize documentation better ... I didn't realize they exist even though I coded them myself!
        test_node_names = get_all_nodes()[0:2]

        self._check_unhide(unhide_nodes, hide_nodes, get_node_property, 'NODE_VISIBLE', test_node_names)

    @print_entry_exit
    def test_set_edge_opacity_bypass(self):

        self._check_edge_bypass(set_edge_opacity_bypass, 128, 192, 300, None, 'EDGE_LABEL_TRANSPARENCY')
        self._check_edge_bypass(set_edge_opacity_bypass, 128, 192, 300, None, 'EDGE_TRANSPARENCY')

    @print_entry_exit
    def test_set_edge_color_bypass(self):

        self._check_edge_bypass(set_edge_color_bypass, '#FF00FF', '#FFFF00', 'BogusColor', None, 'EDGE_STROKE_UNSELECTED_PAINT')
        self._check_edge_bypass(set_edge_color_bypass, '#FF00FF', '#FFFF00', 'BogusColor', None, 'EDGE_UNSELECTED_PAINT')

    @print_entry_exit
    def test_set_edge_label_bypass(self):

        self._check_edge_bypass(set_edge_label_bypass, 'label 1', 'label 2', None, None, 'EDGE_LABEL')

    @print_entry_exit
    def test_set_edge_font_face_bypass(self):

        self._check_edge_bypass(set_edge_font_face_bypass, 'Dialog.italic,plain,20', 'Dialog.bold,bold,10', None, None, 'EDGE_LABEL_FONT_FACE')

    @print_entry_exit
    def test_set_edge_font_size_bypass(self):

        self._check_edge_bypass(set_edge_font_size_bypass, 50, 100, 'BogusSize', None, 'EDGE_LABEL_FONT_SIZE')

    @print_entry_exit
    def test_set_edge_label_color_bypass(self):

        self._check_edge_bypass(set_edge_label_color_bypass, '#FF00FF', '#FFFF00', 'BogusColor', None, 'EDGE_LABEL_COLOR')

    @print_entry_exit
    def test_set_edge_tooltip_bypass(self):

        self._check_edge_bypass(set_edge_tooltip_bypass, 'testtip 1', 'testtip 2', None, None, 'EDGE_TOOLTIP')

    @print_entry_exit
    def test_set_edge_line_width_bypass(self):

        self._check_edge_bypass(set_edge_line_width_bypass, 80, 125.5, 'BogusWidth', None, 'EDGE_WIDTH')

    @print_entry_exit
    def test_set_edge_line_style_bypass(self):

        self._check_edge_bypass(set_edge_line_style_bypass, 'SINEWAVE', 'ZIGZAG', 'BogusStyle', False, 'EDGE_LINE_TYPE')

    @print_entry_exit
    def test_set_edge_source_arrow_shape_bypass(self):

        self._check_edge_bypass(set_edge_source_arrow_shape_bypass, 'DIAMOND', 'CIRCLE', 'BogusShape', False, 'EDGE_SOURCE_ARROW_SHAPE')

    @print_entry_exit
    def test_set_edge_target_arrow_shape_bypass(self):

        self._check_edge_bypass(set_edge_target_arrow_shape_bypass, 'DIAMOND', 'CIRCLE', 'BogusShape', False, 'EDGE_TARGET_ARROW_SHAPE')

    @print_entry_exit
    def test_set_edge_source_arrow_color_bypass(self):

        self._check_edge_bypass(set_edge_source_arrow_color_bypass, '#FF00FF', '#FFFF00', 'BogusColor', None, 'EDGE_SOURCE_ARROW_UNSELECTED_PAINT')

    @print_entry_exit
    def test_set_edge_target_arrow_color_bypass(self):

        self._check_edge_bypass(set_edge_target_arrow_color_bypass, '#FF00FF', '#FFFF00', 'BogusColor', None, 'EDGE_TARGET_ARROW_UNSELECTED_PAINT')

    @print_entry_exit
    def test_set_edge_label_opacity_bypass(self):

        self._check_edge_bypass(set_edge_label_opacity_bypass, 128, 200, 300, False, 'EDGE_LABEL_TRANSPARENCY')

    @print_entry_exit
    def test_hide_selected_edges(self):
        # Initialization
        load_test_session()
        edges = get_all_edges()[0:2] # Get 2 edges

        # Verify that edges that are selected and hidden are actually hidden
        select_edges(edges, by_col='name')
        orig_visible = get_edge_property(edges, 'EDGE_VISIBLE')
        self.assertEqual(hide_selected_edges(), '')
        new_visible = get_edge_property(edges, 'EDGE_VISIBLE')
        self._dict_changed(orig_visible, new_visible)

        # Verify that a bad network is caught
        self.assertRaises(CyError, hide_selected_edges, network='BogusNetwork')

    @print_entry_exit
    def test_hide_edges(self):
        # Initialization
        load_test_session()
        # TODO: Organize documentation better ... I didn't realize they exist even though I coded them myself!
        test_edge_names = get_all_edges()[0:2]

        self._check_hide(hide_edges, get_edge_property, 'EDGE_VISIBLE', test_edge_names)

    @print_entry_exit
    def test_unhide_edges(self):
        # Initialization
        load_test_session()
        # TODO: Organize documentation better ... I didn't realize they exist even though I coded them myself!
        test_edge_names = get_all_edges()[0:2]

        self._check_unhide(unhide_edges, hide_edges, get_edge_property, 'EDGE_VISIBLE', test_edge_names)

    @print_entry_exit
    def test_set_clear_network_zoom_bypass(self):
        # Initialization
        load_test_session()

        # Verify that a valid property can be set properly and then cleared
        orig_scale = get_network_zoom()
        self.assertEqual(set_network_zoom_bypass(orig_scale / 2, bypass=True), '')
        self.assertEqual(get_network_zoom(), orig_scale / 2)
        self.assertDictEqual(clear_network_zoom_bypass(), {'data': {}, 'errors': []})

        self.assertEqual(get_network_zoom(), orig_scale)

        # Verify that invalid network is caught
        self.assertRaises(CyError, clear_network_zoom_bypass, network='BogusNetwork')
        self.assertRaises(CyError, set_network_zoom_bypass, orig_scale, network='BogusNetwork')

    @print_entry_exit
    def test_set_clear_network_center_bypass(self):
        # Initialization
        load_test_session()

        # Verify that a valid property can be set properly and then cleared
        orig_center = get_network_center()
        self.assertEqual(set_network_center_bypass(orig_center['x'] / 2, orig_center['y'] / 2, bypass=True), '')
        self.assertDictEqual(get_network_center(), {'x': orig_center['x'] / 2, 'y': orig_center['y'] / 2})
        self.assertDictEqual(clear_network_center_bypass(), {'data': {}, 'errors': []})

        self.assertDictEqual(get_network_center(), orig_center)

        # Verify that invalid network is caught
        self.assertRaises(CyError, clear_network_center_bypass, network='BogusNetwork')
        self.assertRaises(CyError, set_network_center_bypass, 1, 1, network='BogusNetwork')

    def _check_hide(self, hide_func, getter_func, visual_property, names):
        # Verify that nodes/edges start as visible, and when they're hidden, they're actually invisible
        orig_visible = getter_func(names, visual_property=visual_property)
        self.assertEqual(len(orig_visible), len(names))
        self.assertFalse(False in [orig_visible[name]    for name in names])
        self.assertEqual(hide_func(names), '')
        invisible = getter_func(names, visual_property=visual_property)
        self.assertEqual(len(invisible), len(names))
        self.assertFalse(True in [invisible[name]    for name in orig_visible])

        # Verify that hiding no nodes actually does nothing
        cur_visible_nodes = getter_func(visual_property=visual_property)
        self.assertEqual(hide_func([]), '')
        self.assertDictEqual(getter_func(visual_property=visual_property), cur_visible_nodes)

        # Verify that invalid network is caught
        self.assertRaises(CyError, hide_nodes, names, network='BogusNetwork')

    def _check_unhide(self, unhide_func, hide_func, getter_func, visual_property, names):
        # Verify that nodes/edges start as hidden, and when they're unhidden, they're actually visible
        self.assertEqual(hide_func(names), '')
        orig_hidden = getter_func(names, visual_property=visual_property)
        self.assertEqual(len(orig_hidden), len(names))
        self.assertFalse(True in [orig_hidden[name]    for name in names])
        self.assertDictEqual(unhide_func(names), {'data': {}, 'errors': []})
        visible = getter_func(names, visual_property=visual_property)
        self.assertEqual(len(visible), len(names))
        self.assertFalse(False in [visible[name]    for name in orig_hidden])

        # Verify that unhiding no nodes actually does nothing
        cur_visible_nodes = getter_func(visual_property=visual_property)
        self.assertDictEqual(unhide_func([]), {'data': {}, 'errors': []})
        self.assertDictEqual(getter_func(visual_property=visual_property), cur_visible_nodes)

        # Verify that invalid network is caught
        self.assertRaises(CyError, unhide_nodes, names, network='BogusNetwork')


    def _check_node_bypass(self, node_func, bypass_1, bypass_2, bogus_bypass, visual_property):
        # Initialization
        load_test_session()
        all_node_names = get_all_nodes()

        # Verify that all nodes get the bypass value when it's passed as a scalar
        self.assertEqual(node_func(all_node_names, bypass_1), '')
        new_vals = get_node_property(node_names=all_node_names, visual_property=visual_property)
        self.assertFalse(False in [new_vals[node] == bypass_1 for node in all_node_names])

        # Verify that all nodes get the bypass value when it's passed as a list
        load_test_session()
        self.assertEqual(node_func(all_node_names[0:2], [bypass_1, bypass_2]), '')
        new_vals = get_node_property(node_names=all_node_names[0:2], visual_property=visual_property)
        self.assertFalse(False in [new_vals[node] == val for node, val in zip(all_node_names[0:2], [bypass_1, bypass_2])])

        # Verify that bad values, bad node lists and bad networks are caught
        if bogus_bypass is not None: self.assertIsNone(node_func(all_node_names, bogus_bypass))
        #        self.assertIsNone(set_node_color_bypass(None, bypass_1)) # TODO: In many functions, a null column list means all columns
        self.assertRaises(CyError, node_func, ['BogusNode'], bypass_1)
        self.assertRaises(CyError, node_func, all_node_names, bypass_1, network='BogusNetwork')

    def _check_edge_bypass(self, edge_func, bypass_1, bypass_2, bogus_bypass, bogus_return, visual_property):
        # Initialization
        load_test_session()
        all_edge_names = get_all_edges()

        # Verify that all edges get the bypass value when it's passed as a scalar
        self.assertEqual(edge_func(all_edge_names, bypass_1), '')
        new_vals = get_edge_property(edge_names=all_edge_names, visual_property=visual_property)
        self.assertFalse(False in [new_vals[node] == bypass_1 for node in all_edge_names])

        # Verify that all nodes get the bypass value when it's passed as a list
        load_test_session()
        self.assertEqual(edge_func(all_edge_names[0:2], [bypass_1, bypass_2]), '')
        new_vals = get_edge_property(edge_names=all_edge_names[0:2], visual_property=visual_property)
        self.assertFalse(False in [new_vals[node] == val for node, val in zip(all_edge_names[0:2], [bypass_1, bypass_2])])

        # Verify that bad values, bad node lists and bad networks are caught
        if bogus_bypass is not None: self.assertEqual(edge_func(all_edge_names, bogus_bypass), bogus_return)
        #        self.assertIsNone(set_edge_color_bypass(None, bypass_1)) # TODO: In many functions, a null column list means all columns
        self.assertRaises(CyError, edge_func, ['BogusEdge'], bypass_1)
        self.assertRaises(CyError, edge_func, all_edge_names, bypass_1, network='BogusNetwork')

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
        self.assertDictEqual(getter_func(visual_property=visual_property), orig_colors)

        # Verify that nothing happens when an empty list is passed in
        self.assertDictEqual(clear_func([], visual_property), {'data': {}, 'errors': []})
        self.assertDictEqual(getter_func(visual_property=visual_property), orig_colors)

        # Verify that supplying a null node list is caught
        self.assertRaises(TypeError, clear_func, None, visual_property)

        # Verify that bad node list is caught
        self.assertRaises(CyError, clear_func, 'all', visual_property)
        self.assertRaises(CyError, clear_func, ['BogusNode'], visual_property)

        # Verify that bad property name is caught
        self.assertRaises(CyError, clear_func, list(all_names['name']), None)
        self.assertRaises(CyError, clear_func, list(all_names['name']), 'BogusProperty')

        # Verify that invalid network is caught
        self.assertRaises(CyError, clear_func, list(all_names['name']), visual_property, network='BogusNetwork')

    def _dict_changed(self, new_dict, base_dict):
        self.assertIsInstance(new_dict, dict)
        self.assertEqual(len(new_dict), 2)
        self.assertIsInstance(base_dict, dict)
        self.assertEqual(len(base_dict), 2)
        self.assertFalse(True in [new_dict[node] == base_dict[node] for node in base_dict])


if __name__ == '__main__':
    unittest.main()
