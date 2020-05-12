# -*- coding: utf-8 -*-

""" Test functions in styles.py.

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
from requests import RequestException

from test_utils import *


class StyleDefaultsTests(unittest.TestCase):
    def setUp(self):
        try:
            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    _TEST_STYLE = 'galFiltered Style'


    @print_entry_exit
    def test_update_style_defaults(self):
        # Initialization
        load_test_session()

        orig_edge_unselected_paint = get_visual_property_default('EDGE_UNSELECTED_PAINT', style_name=self._TEST_STYLE)
        orig_edge_width = get_visual_property_default('EDGE_WIDTH', style_name=self._TEST_STYLE)
        orig_node_shape = get_visual_property_default('NODE_SHAPE', style_name=self._TEST_STYLE)
        orig_edge_target_arrow = get_visual_property_default('EDGE_TARGET_ARROW_SHAPE', style_name=self._TEST_STYLE)
        orig_edge_line_style = get_visual_property_default('EDGE_LINE_TYPE', style_name=self._TEST_STYLE)

        self.assertEqual(update_style_defaults(defaults={}, style_name=self._TEST_STYLE), '')
        self.assertEqual(update_style_defaults(defaults={'edge color': '#654321'}, style_name=self._TEST_STYLE), '')
        self.assertEqual(update_style_defaults(defaults={'edge width': '50.0',
                                                         'node shape': 'OCTAGON',
                                                         'EDGE_TARGET_ARROW_SHAPE': 'CIRCLE',
                                                         'EDGE_LINE_TYPE': 'ZIGZAG'},
                                               style_name=self._TEST_STYLE), '')

        self._check_getter_value_default('EDGE_UNSELECTED_PAINT', orig_edge_unselected_paint, '#654321')
        self._check_getter_value_default('EDGE_WIDTH', orig_edge_width, 50.0)
        self._check_getter_value_default('NODE_SHAPE', orig_node_shape, 'OCTAGON')
        self._check_getter_value_default('EDGE_TARGET_ARROW_SHAPE', orig_edge_target_arrow, 'CIRCLE')
        self._check_getter_value_default('EDGE_LINE_TYPE', orig_edge_line_style, 'ZIGZAG')

        # Verify that an invalid style name is caught
        self.assertRaises(CyError, update_style_defaults, defaults={}, style_name='bogusStyle')
        self.assertEqual(update_style_defaults(defaults={'bogusProperty': '0'}, style_name=self._TEST_STYLE), '')
        # TODO: Do we want a silent failure for bogus properties?

    @print_entry_exit
    def test_get_set_visual_property_default(self):
        # Initialization
        load_test_session()

        orig_edge_unselected_paint = get_visual_property_default('EDGE_UNSELECTED_PAINT', style_name=self._TEST_STYLE)
        orig_edge_width = get_visual_property_default('EDGE_WIDTH', style_name=self._TEST_STYLE)
        orig_node_shape = get_visual_property_default('NODE_SHAPE', style_name=self._TEST_STYLE)
        orig_edge_target_arrow = get_visual_property_default('EDGE_TARGET_ARROW_SHAPE', style_name=self._TEST_STYLE)
        orig_edge_line_style = get_visual_property_default('EDGE_LINE_TYPE', style_name=self._TEST_STYLE)

        self.assertEqual(set_visual_property_default({'visualProperty': 'EDGE_UNSELECTED_PAINT', 'value': '#654321'}, style_name=self._TEST_STYLE), '')
        self.assertEqual(set_visual_property_default({'visualProperty': 'EDGE_WIDTH', 'value': '50.0'}, style_name=self._TEST_STYLE), '')
        self.assertEqual(set_visual_property_default({'visualProperty': 'NODE_SHAPE', 'value': 'OCTAGON'}, style_name=self._TEST_STYLE), '')
        self.assertEqual(set_visual_property_default({'visualProperty': 'EDGE_TARGET_ARROW_SHAPE', 'value': 'CIRCLE'}, style_name=self._TEST_STYLE), '')
        self.assertEqual(set_visual_property_default({'visualProperty': 'EDGE_LINE_TYPE', 'value': 'ZIGZAG'}, style_name=self._TEST_STYLE), '')

        self._check_getter_value_default('EDGE_UNSELECTED_PAINT', orig_edge_unselected_paint, '#654321')
        self._check_getter_value_default('EDGE_WIDTH', orig_edge_width, 50.0)
        self._check_getter_value_default('NODE_SHAPE', orig_node_shape, 'OCTAGON')
        self._check_getter_value_default('EDGE_TARGET_ARROW_SHAPE', orig_edge_target_arrow, 'CIRCLE')
        self._check_getter_value_default('EDGE_LINE_TYPE', orig_edge_line_style, 'ZIGZAG')

        # Verify that an invalid style name is caught
        self.assertRaises(CyError, get_visual_property_default, 'EDGE_UNSELECTED_PAINT', style_name='bogusStyle')
        self.assertRaises(CyError, set_visual_property_default, {'visualProperty': 'EDGE_UNSELECTED_PAINT', 'value': '#654321'}, style_name='bogusStyle')
        self.assertRaises(CyError, get_visual_property_default, 'bogusProperty', style_name=self._TEST_STYLE)
        self.assertEqual(set_visual_property_default({'visualProperty': 'bogusProperty', 'value': '#654321'}, style_name=self._TEST_STYLE), '')
        self.assertEqual(set_visual_property_default({'visualProperty': 'EDGE_UNSELECTED_PAINT', 'value': 'bogusValue'}, style_name=self._TEST_STYLE), '')
        # TODO: Do we want a silent failure for bogus properties?

    @print_entry_exit
    def test_set_node_border_color_default(self):
        self._check_setter_default(set_node_border_color_default, 'NODE_BORDER_PAINT', '#FF00FF', 'bogusColor')

    @print_entry_exit
    def test_set_node_border_width_default(self):
        self._check_setter_default(set_node_border_width_default, 'NODE_BORDER_WIDTH', 20.0)

    @print_entry_exit
    def test_set_node_border_opacity_default(self):
        self._check_setter_default(set_node_border_opacity_default, 'NODE_BORDER_TRANSPARENCY', 150, 350)

    @print_entry_exit
    def test_set_node_color_default(self):
        self._check_setter_default(set_node_color_default, 'NODE_FILL_COLOR', '#FF00FF', 'bogusColor')

# FAIL
    @print_entry_exit
    def test_set_node_custom_bar_chart(self):
        raise CyError('Not implemented')

# FAIL
    @print_entry_exit
    def test_set_node_custom_box_chart(self):
        raise CyError('Not implemented')

# FAIL
    @print_entry_exit
    def test_set_node_custom_heat_map_chart(self):
        raise CyError('Not implemented')

# FAIL
    @print_entry_exit
    def test_set_node_custom_line_chart(self):
        raise CyError('Not implemented')

# FAIL
    @print_entry_exit
    def test_set_node_custom_pie_chart(self):
        raise CyError('Not implemented')

# FAIL
    @print_entry_exit
    def test_set_node_custom_ring_chart(self):
        raise CyError('Not implemented')

# FAIL
    @print_entry_exit
    def test_set_node_custom_linear_gradient(self):
        raise CyError('Not implemented')

# FAIL
    @print_entry_exit
    def test_set_node_custom_radial_gradient(self):
        raise CyError('Not implemented')

# FAIL
    @print_entry_exit
    def test_set_node_custom_position(self):
        raise CyError('Not implemented')

# FAIL
    @print_entry_exit
    def test_remove_node_custom_graphics(self):
        raise CyError('Not implemented')

    @print_entry_exit
    def test_set_node_fill_opacity_default(self):
        self._check_setter_default(set_node_fill_opacity_default, 'NODE_TRANSPARENCY', 150, 350)

    @print_entry_exit
    def test_set_node_font_face_default(self):
        self._check_setter_default(set_node_font_face_default, 'NODE_LABEL_FONT_FACE', 'Dialog.italic,plain,12')

    @print_entry_exit
    def test_set_node_font_size_default(self):
        self._check_setter_default(set_node_font_size_default, 'NODE_LABEL_FONT_SIZE', 20)

    @print_entry_exit
    def test_set_node_height_default(self):
        self._check_setter_default(set_node_height_default, 'NODE_HEIGHT', 150)

    @print_entry_exit
    def test_set_node_label_default(self):
        self._check_setter_default(set_node_label_default, 'NODE_LABEL', "Node Label")

    @print_entry_exit
    def test_set_node_label_color_default(self):
        self._check_setter_default(set_node_label_color_default, 'NODE_LABEL_COLOR', '#FF00FF', 'bogusColor')

    @print_entry_exit
    def test_set_node_label_opacity_default(self):
        self._check_setter_default(set_node_label_opacity_default, 'NODE_LABEL_TRANSPARENCY', 150, 350)

    @print_entry_exit
    def test_set_node_selection_color_default(self):
        self._check_setter_default(set_node_selection_color_default, 'NODE_SELECTED_PAINT', '#FF00FF', 'bogusColor')

    @print_entry_exit
    def test_get_node_selection_color_default(self):
        self._check_getter_default(get_node_selection_color_default, 'NODE_SELECTED_PAINT', '#654321')

    @print_entry_exit
    def test_set_node_shape_default(self):
        self._check_setter_default(set_node_shape_default, 'NODE_SHAPE', 'HEXAGON', 'bogusShape')

    @print_entry_exit
    def test_set_node_size_default(self):
        self._check_setter_default(set_node_size_default, 'NODE_SIZE', 150)

    @print_entry_exit
    def test_set_node_width_default(self):
        self._check_setter_default(set_node_width_default, 'NODE_WIDTH', 150)

    @print_entry_exit
    def test_set_node_tooltip_default(self):
        self._check_setter_default(set_node_tooltip_default, 'NODE_TOOLTIP', 'test tooltip')

    @print_entry_exit
    def test_set_edge_color_default(self):
        self._check_setter_default(set_edge_color_default, 'EDGE_UNSELECTED_PAINT', '#FF00FF', 'bogusColor')
        self._check_setter_default(set_edge_color_default, 'EDGE_STROKE_UNSELECTED_PAINT', '#FFFF00', 'bogusColor')

    @print_entry_exit
    def test_set_edge_font_face_default(self):
        self._check_setter_default(set_edge_font_face_default, 'EDGE_LABEL_FONT_FACE', 'Dialog.italic,plain,12')

    @print_entry_exit
    def test_set_edge_font_size_default(self):
        self._check_setter_default(set_edge_font_size_default, 'EDGE_LABEL_FONT_SIZE', 20)

    @print_entry_exit
    def test_set_edge_label_default(self):
        self._check_setter_default(set_edge_label_default, 'EDGE_LABEL', 'edge label')

    @print_entry_exit
    def test_set_edge_label_color_default(self):
        self._check_setter_default(set_edge_label_color_default, 'EDGE_LABEL_COLOR', '#FF00FF', 'bogusColor', exception_scenario='exception')

    @print_entry_exit
    def test_set_edge_label_opacity_default(self):
        self._check_setter_default(set_edge_label_opacity_default, 'EDGE_LABEL_TRANSPARENCY', 150, 350)

    @print_entry_exit
    def test_set_edge_line_width_default(self):
        self._check_setter_default(set_edge_line_width_default, 'EDGE_WIDTH', 20)

    @print_entry_exit
    def test_set_edge_line_style_default(self):
        self._check_setter_default(set_edge_line_style_default, 'EDGE_LINE_TYPE', 'ZIGZAG')

    @print_entry_exit
    def test_set_edge_opacity_default(self):
        self._check_setter_default(set_edge_opacity_default, 'EDGE_TRANSPARENCY', 150, 350)

# FAIL
    @print_entry_exit
    def test_get_edge_selection_color_default(self):
        raise CyError('Not implemented')

    @print_entry_exit
    def test_set_edge_selection_color_default(self):
        self._check_setter_default(set_edge_selection_color_default, 'EDGE_SELECTED_PAINT', '#FF00FF', 'bogusColor', exception_scenario='exception')
        self._check_setter_default(set_edge_selection_color_default, 'EDGE_STROKE_SELECTED_PAINT', '#FFFF00', 'bogusColor', exception_scenario='exception')

    @print_entry_exit
    def test_set_edge_source_arrow_color_default(self):
        self._check_setter_default(set_edge_source_arrow_color_default, 'EDGE_SOURCE_ARROW_UNSELECTED_PAINT', '#FF00FF', 'bogusColor', exception_scenario='exception')

    @print_entry_exit
    def test_set_edge_target_arrow_color_default(self):
        self._check_setter_default(set_edge_target_arrow_color_default, 'EDGE_TARGET_ARROW_UNSELECTED_PAINT', '#FF00FF', 'bogusColor', exception_scenario='exception')

    @print_entry_exit
    def test_set_edge_source_arrow_shape_default(self):
        self._check_setter_default(set_edge_source_arrow_shape_default, 'EDGE_SOURCE_ARROW_SHAPE', 'CIRCLE', 'BogusShape', exception_scenario='no effect')

    @print_entry_exit
    def test_set_edge_target_arrow_shape_default(self):
        self._check_setter_default(set_edge_target_arrow_shape_default, 'EDGE_TARGET_ARROW_SHAPE', 'CIRCLE', 'BogusShape', exception_scenario='no effect')

    @print_entry_exit
    def test_set_edge_tooltip_default(self):
        self._check_setter_default(set_edge_tooltip_default, 'EDGE_TOOLTIP', 'test tooltip')

    @print_entry_exit
    def test_get_background_color_default(self):
        self._check_getter_default(get_background_color_default, 'NETWORK_BACKGROUND_PAINT', '#654321')

    @print_entry_exit
    def test_set_background_color_default(self):
        self._check_setter_default(set_background_color_default, 'NETWORK_BACKGROUND_PAINT', '#FF00FF', 'bogusColor')


    def _check_getter_default(self, getter_func, prop_name, new_value):
        # Initialization
        load_test_session()

        # Verify that the node selection color can be fetched and looks different after it's set
        orig_default = get_visual_property_default(prop_name, style_name=self._TEST_STYLE)
        self.assertEqual(set_visual_property_default({'visualProperty': prop_name, 'value': new_value}, style_name=self._TEST_STYLE), '')
        self._check_getter_value_default(prop_name, orig_default, new_value)
        self.assertEqual(getter_func(style_name=self._TEST_STYLE), new_value)

        # Verify that an invalid style name is caught
        self.assertRaises(CyError, getter_func, style_name='bogusStyle')

    def _check_getter_value_default(self, prop_name, orig_val, expected_val):
        self.assertNotEqual(orig_val, expected_val)
        new_val = get_visual_property_default(prop_name, style_name=self._TEST_STYLE)
        self.assertEqual(new_val, expected_val)

    def _check_setter_default(self, setter_func, prop_name, good_value, bogus_value=None, exception_scenario=None):
        # Initialization
        load_test_session()

        # Verify that if there's a bogus value, it's caught
        orig_value = get_visual_property_default(prop_name, style_name=self._TEST_STYLE)
        self.assertNotEqual(orig_value, good_value)
        if bogus_value is not None:
            if exception_scenario == 'no effect':
                self.assertEqual(setter_func(bogus_value, style_name=self._TEST_STYLE), '')
                self.assertEqual(get_visual_property_default(prop_name, style_name=self._TEST_STYLE), orig_value)
            elif exception_scenario == 'exception':
                self.assertRaises(CyError, setter_func, bogus_value, style_name=self._TEST_STYLE)
            else:
                self.assertIsNone(setter_func(bogus_value, style_name=self._TEST_STYLE))
                self.assertEqual(get_visual_property_default(prop_name, style_name=self._TEST_STYLE), orig_value)

        # Verify that a good value can be set and that it applies to self._TEST_STYLE but not 'default' style
        self.assertEqual(setter_func(good_value, style_name=self._TEST_STYLE), '')
        self.assertEqual(get_visual_property_default(prop_name, style_name=self._TEST_STYLE), good_value)
        self.assertNotEqual(get_visual_property_default(prop_name), good_value)

if __name__ == '__main__':
    unittest.main()
