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
import json
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

        self.assertEqual(set_visual_property_default({'visualProperty': 'EDGE_UNSELECTED_PAINT', 'value': '#654321'},
                                                     style_name=self._TEST_STYLE), '')
        self.assertEqual(
            set_visual_property_default({'visualProperty': 'EDGE_WIDTH', 'value': '50.0'}, style_name=self._TEST_STYLE),
            '')
        self.assertEqual(set_visual_property_default({'visualProperty': 'NODE_SHAPE', 'value': 'OCTAGON'},
                                                     style_name=self._TEST_STYLE), '')
        self.assertEqual(set_visual_property_default({'visualProperty': 'EDGE_TARGET_ARROW_SHAPE', 'value': 'CIRCLE'},
                                                     style_name=self._TEST_STYLE), '')
        self.assertEqual(set_visual_property_default({'visualProperty': 'EDGE_LINE_TYPE', 'value': 'ZIGZAG'},
                                                     style_name=self._TEST_STYLE), '')

        self._check_getter_value_default('EDGE_UNSELECTED_PAINT', orig_edge_unselected_paint, '#654321')
        self._check_getter_value_default('EDGE_WIDTH', orig_edge_width, 50.0)
        self._check_getter_value_default('NODE_SHAPE', orig_node_shape, 'OCTAGON')
        self._check_getter_value_default('EDGE_TARGET_ARROW_SHAPE', orig_edge_target_arrow, 'CIRCLE')
        self._check_getter_value_default('EDGE_LINE_TYPE', orig_edge_line_style, 'ZIGZAG')

        # Verify that an invalid style name is caught
        self.assertRaises(CyError, get_visual_property_default, 'EDGE_UNSELECTED_PAINT', style_name='bogusStyle')
        self.assertRaises(CyError, set_visual_property_default,
                          {'visualProperty': 'EDGE_UNSELECTED_PAINT', 'value': '#654321'}, style_name='bogusStyle')
        self.assertRaises(CyError, get_visual_property_default, 'bogusProperty', style_name=self._TEST_STYLE)
        self.assertEqual(set_visual_property_default({'visualProperty': 'bogusProperty', 'value': '#654321'},
                                                     style_name=self._TEST_STYLE), '')
        self.assertEqual(set_visual_property_default({'visualProperty': 'EDGE_UNSELECTED_PAINT', 'value': 'bogusValue'},
                                                     style_name=self._TEST_STYLE), '')
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

    @print_entry_exit
    def test_set_node_custom_bar_chart(self):
        # Initialization
        load_test_session()
        chart_params = {'style_name': self._TEST_STYLE}
        chart_profile = {}
        chart_cols = ['AverageShortestPathLength', 'BetweennessCentrality']

        # Verify that specifying no columns results in no properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_bar_chart, [], chart_params, {},
                                                              chart_profile, {})

        # Verify that specifying valid columns results in valid default properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_bar_chart, chart_cols, chart_params,
                                                              {}, chart_profile,
                                                              {'cy_range': [0.0, 16.35887097],
                                                               'cy_showRangeAxis': False, 'cy_axisLabelFontSize': 1,
                                                               'cy_colorScheme': 'CUSTOM',
                                                               'cy_showRangeZeroBaseline': False,
                                                               'cy_colors': ['#E41A1C', '#377EB8', '#4DAF4A',
                                                                             '#984EA3', '#FF7F00', '#FFFF33',
                                                                             '#A65628', '#F781BF', '#999999',
                                                                             '#E41A1C', '#377EB8', '#4DAF4A',
                                                                             '#984EA3', '#FF7F00', '#FFFF33',
                                                                             '#A65628', '#F781BF', '#999999'],
                                                               'cy_showDomainAxis': False, 'cy_axisColor': '#000000',
                                                               'cy_axisWidth': 0.25, 'cy_orientation': 'VERTICAL',
                                                               'cy_type': 'GROUPED',
                                                               'cy_dataColumns': ['AverageShortestPathLength',
                                                                                  'BetweennessCentrality'],
                                                               'cy_separation': 0.0})

        # Verify that specifying a valid type results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_bar_chart, chart_cols, chart_params,
                                                              {'type': 'GROUPED'}, chart_profile,
                                                              {'cy_type': 'GROUPED'})

        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_bar_chart, chart_cols, chart_params,
                                                              {'type': 'STACKED'}, chart_profile,
                                                              {'cy_type': 'STACKED'})

        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_bar_chart, chart_cols, chart_params,
                                                              {'type': 'HEAT_STRIPS'}, chart_profile,
                                                              {'cy_type': 'HEAT_STRIPS',
                                                               'cy_colors': ["#B2182B", "#F7F7F7", "#2166AC"]})

        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_bar_chart, chart_cols, chart_params,
                                                              {'type': 'UP_DOWN'}, chart_profile,
                                                              {'cy_type': 'UP_DOWN',
                                                               'cy_colors': ["#B2182B", "#2166AC"]})

        # Verify that specifying display colors results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_bar_chart, chart_cols, chart_params,
                                                              {'type': 'GROUPED', 'colors': ['#FF00FF', '#00FF00']},
                                                              chart_profile, {'cy_type': 'GROUPED',
                                                                              'cy_colors': ['#FF00FF', '#00FF00']})

        # Verify that specifying an axis range results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_bar_chart, chart_cols, chart_params,
                                                              {'range': [0, 50]}, chart_profile,
                                                              {'cy_range': [0.0, 50.0]})

        # Verify that specifying an orientation results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_bar_chart, chart_cols, chart_params,
                                                              {'orientation': 'HORIZONTAL'}, chart_profile,
                                                              {'cy_orientation': 'HORIZONTAL'})

        # Verify that enabling a domain axis results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_bar_chart, chart_cols, chart_params,
                                                              {'col_axis': True}, chart_profile,
                                                              {'cy_showDomainAxis': True})

        # Verify that enabling a domain axis results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_bar_chart, chart_cols, chart_params,
                                                              {'range_axis': True}, chart_profile,
                                                              {'cy_showRangeAxis': True})

        # Verify that enabling a baseline axis results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_bar_chart, chart_cols, chart_params,
                                                              {'zero_line': True}, chart_profile,
                                                              {'cy_showRangeZeroBaseline': True})

        # Verify that specifying an axis width results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_bar_chart, chart_cols, chart_params,
                                                              {'axis_width': 0.50}, chart_profile,
                                                              {'cy_axisWidth': 0.5})

        # # Verify that specifying an axis color results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_bar_chart, chart_cols, chart_params,
                                                              {'axis_color': '#FFFFFF'}, chart_profile,
                                                              {'cy_axisColor': '#FFFFFF'})

        # Verify that specifying an axis font size results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_bar_chart, chart_cols, chart_params,
                                                              {'axis_font_size': 5}, chart_profile,
                                                              {'cy_axisLabelFontSize': 5})

        # Verify that specifying a bar separation results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_bar_chart, chart_cols, chart_params,
                                                              {'separation': 0.5}, chart_profile,
                                                              {'cy_separation': 0.5})

        # Verify that specifying a different slot results in valid properties
        self._check_chart_attrs(set_node_custom_bar_chart, chart_cols, chart_params, {'slot': 9}, chart_profile, {})

        # Verify that error is thrown when type is invalid
        self.assertRaises(CyError, set_node_custom_bar_chart, chart_cols, type='BogusType')

        # Verify that error is thrown when slot is invalid
        self.assertRaises(CyError, set_node_custom_bar_chart, chart_cols, slot=10, **chart_params)
        self.assertRaises(CyError, set_node_custom_bar_chart, chart_cols, slot=0, **chart_params)

    @print_entry_exit
    def test_set_node_custom_box_chart(self):
        # Initialization
        load_test_session()
        chart_params = {'style_name': self._TEST_STYLE}
        chart_profile = {}
        chart_cols = ['AverageShortestPathLength', 'BetweennessCentrality']

        # Verify that specifying no columns results in no properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_box_chart, [], chart_params, {},
                                                              chart_profile, {})

        # Verify that specifying valid columns results in valid default properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_box_chart, chart_cols, chart_params,
                                                              {}, chart_profile,
                                                              {'cy_axisWidth': 0.25, 'cy_range': [0.0, 16.35887097],
                                                               'cy_showRangeAxis': False, 'cy_orientation': 'VERTICAL',
                                                               'cy_axisLabelFontSize': 1, 'cy_colorScheme': 'CUSTOM',
                                                               'cy_showRangeZeroBaseline': False,
                                                               'cy_colors': ['#67001F', '#B2182B', '#D6604D',
                                                                             '#F4A582', '#FDDBC7', '#F7F7F7',
                                                                             '#D1E5F0', '#92C5DE', '#4393C3',
                                                                             '#2166AC', '#053061', '#67001F',
                                                                             '#B2182B', '#D6604D', '#F4A582',
                                                                             '#FDDBC7', '#F7F7F7', '#D1E5F0',
                                                                             '#92C5DE', '#4393C3', '#2166AC',
                                                                             '#053061'],
                                                               'cy_dataColumns': ['AverageShortestPathLength',
                                                                                  'BetweennessCentrality'],
                                                               'cy_axisColor': '#000000'})

        # Verify that specifying display colors results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_box_chart, chart_cols, chart_params,
                                                              {'colors': ['#FF00FF', '#00FF00']}, chart_profile,
                                                              {'cy_colors': ['#FF00FF', '#00FF00']})

        # Verify that specifying an axis range results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_box_chart, chart_cols, chart_params,
                                                              {'range': [0, 50]}, chart_profile,
                                                              {'cy_range': [0.0, 50.0]})

        # Verify that specifying an orientation results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_box_chart, chart_cols, chart_params,
                                                              {'orientation': 'HORIZONTAL'}, chart_profile,
                                                              {'cy_orientation': 'HORIZONTAL'})

        # Verify that enabling a domain axis results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_box_chart, chart_cols, chart_params,
                                                              {'range_axis': True}, chart_profile,
                                                              {'cy_showRangeAxis': True})

        # Verify that enabling a baseline axis results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_box_chart, chart_cols, chart_params,
                                                              {'zero_line': True}, chart_profile,
                                                              {'cy_showRangeZeroBaseline': True})

        # Verify that specifying an axis width results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_box_chart, chart_cols, chart_params,
                                                              {'axis_width': 0.50}, chart_profile,
                                                              {'cy_axisWidth': 0.5})

        # Verify that specifying an axis color results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_box_chart, chart_cols, chart_params,
                                                              {'axis_color': '#FFFFFF'}, chart_profile,
                                                              {'cy_axisColor': '#FFFFFF'})

        # Verify that specifying an axis font size results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_box_chart, chart_cols, chart_params,
                                                              {'axis_font_size': 5}, chart_profile,
                                                              {'cy_axisLabelFontSize': 5})

        # Verify that specifying a different slot results in valid properties
        self._check_chart_attrs(set_node_custom_box_chart, chart_cols, chart_params, {'slot': 9}, chart_profile, {})

        # Verify that error is thrown when slot is invalid
        self.assertRaises(CyError, set_node_custom_box_chart, chart_cols, slot=10, **chart_params)
        self.assertRaises(CyError, set_node_custom_box_chart, chart_cols, slot=0, **chart_params)

    @print_entry_exit
    def test_set_node_custom_heat_map_chart(self):
        # Initialization
        load_test_session()
        chart_params = {'style_name': self._TEST_STYLE}
        chart_profile = {}
        chart_cols = ['AverageShortestPathLength', 'BetweennessCentrality']

        # Verify that specifying no columns results in no properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_heat_map_chart, [], chart_params, {},
                                                              chart_profile, {})

        # Verify that specifying valid columns results in valid default properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_heat_map_chart, chart_cols, chart_params,
                                                              {}, chart_profile,
                                                              {'cy_axisWidth': 0.25, 'cy_range': [0.0, 16.35887097],
                                                               'cy_showRangeAxis': False,
                                                               'cy_orientation': 'HORIZONTAL',
                                                               'cy_axisLabelFontSize': 1, 'cy_colorScheme': 'CUSTOM',
                                                               'cy_showRangeZeroBaseline': False,
                                                               'cy_colors': ['#D6604D', '#D1E5F0', '#053061',
                                                                             '#888888'],
                                                               'cy_dataColumns': ['BetweennessCentrality',
                                                                                  'AverageShortestPathLength'],
                                                               'cy_axisColor': '#000000'})

        # Verify that specifying display colors results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_heat_map_chart, chart_cols, chart_params,
                                                              {'colors': ['#123456', '#654321', '#112233', '#888888']},
                                                              chart_profile,
                                                              {'cy_colors': ['#123456', '#654321', '#112233',
                                                                             '#888888']})

        # Verify that specifying an axis range results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_heat_map_chart, chart_cols, chart_params,
                                                              {'range': [0, 50]}, chart_profile,
                                                              {'cy_range': [0.0, 50.0]})

        # Verify that specifying an orientation results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_heat_map_chart, chart_cols, chart_params,
                                                              {'orientation': 'VERTICAL'}, chart_profile,
                                                              {'cy_orientation': 'VERTICAL'})

        # Verify that enabling a domain axis results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_heat_map_chart, chart_cols, chart_params,
                                                              {'range_axis': True}, chart_profile,
                                                              {'cy_showRangeAxis': True})

        # Verify that enabling a baseline axis results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_heat_map_chart, chart_cols, chart_params,
                                                              {'zero_line': True}, chart_profile,
                                                              {'cy_showRangeZeroBaseline': True})

        # Verify that specifying an axis width results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_heat_map_chart, chart_cols, chart_params,
                                                              {'axis_width': 0.50}, chart_profile,
                                                              {'cy_axisWidth': 0.5})

        # Verify that specifying an axis color results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_heat_map_chart, chart_cols, chart_params,
                                                              {'axis_color': '#FFFFFF'}, chart_profile,
                                                              {'cy_axisColor': '#FFFFFF'})

        # Verify that specifying an axis font size results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_heat_map_chart, chart_cols, chart_params,
                                                              {'axis_font_size': 5}, chart_profile,
                                                              {'cy_axisLabelFontSize': 5})

        # Verify that specifying a different slot results in valid properties
        self._check_chart_attrs(set_node_custom_heat_map_chart, chart_cols, chart_params, {'slot': 9}, chart_profile,
                                {})

        # Verify that error is thrown when slot is invalid
        self.assertRaises(CyError, set_node_custom_heat_map_chart, chart_cols, slot=10, **chart_params)
        self.assertRaises(CyError, set_node_custom_heat_map_chart, chart_cols, slot=0, **chart_params)

    @print_entry_exit
    def test_set_node_custom_line_chart(self):
        # Initialization
        load_test_session()
        chart_params = {'style_name': self._TEST_STYLE}
        chart_profile = {}
        chart_cols = ['AverageShortestPathLength', 'BetweennessCentrality']

        # Verify that specifying no columns results in no properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_line_chart, [], chart_params, {},
                                                              chart_profile, {})

        # Verify that specifying valid columns results in valid default properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_line_chart, chart_cols, chart_params,
                                                              {}, chart_profile,
                                                              {'cy_lineWidth': 1.0, 'cy_axisWidth': 0.25,
                                                               'cy_range': [0.0, 16.35887097],
                                                               'cy_showRangeAxis': False, 'cy_axisLabelFontSize': 1,
                                                               'cy_colorScheme': 'CUSTOM',
                                                               'cy_showRangeZeroBaseline': False,
                                                               'cy_colors': ['#E41A1C', '#377EB8', '#4DAF4A',
                                                                             '#984EA3', '#FF7F00', '#FFFF33',
                                                                             '#A65628', '#F781BF', '#999999',
                                                                             '#E41A1C', '#377EB8', '#4DAF4A',
                                                                             '#984EA3', '#FF7F00', '#FFFF33',
                                                                             '#A65628', '#F781BF', '#999999'],
                                                               'cy_dataColumns': ['AverageShortestPathLength',
                                                                                  'BetweennessCentrality'],
                                                               'cy_axisColor': '#000000'})

        # Verify that specifying display colors results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_line_chart, chart_cols, chart_params,
                                                              {'colors': ['#FF00FF', '#00FF00']}, chart_profile,
                                                              {'cy_colors': ['#FF00FF', '#00FF00']})

        # Verify that specifying an axis range results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_line_chart, chart_cols, chart_params,
                                                              {'range': [0, 50]}, chart_profile,
                                                              {'cy_range': [0.0, 50.0]})

        # Verify that specifying an orientation results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_line_chart, chart_cols, chart_params,
                                                              {'line_width': 5.0}, chart_profile,
                                                              {'cy_lineWidth': 5.0})

        # Verify that enabling a domain axis results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_line_chart, chart_cols, chart_params,
                                                              {'range_axis': True}, chart_profile,
                                                              {'cy_showRangeAxis': True})

        # Verify that enabling a baseline axis results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_line_chart, chart_cols, chart_params,
                                                              {'zero_line': True}, chart_profile,
                                                              {'cy_showRangeZeroBaseline': True})

        # Verify that specifying an axis width results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_line_chart, chart_cols, chart_params,
                                                              {'axis_width': 0.50}, chart_profile,
                                                              {'cy_axisWidth': 0.5})

        # Verify that specifying an axis color results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_line_chart, chart_cols, chart_params,
                                                              {'axis_color': '#FFFFFF'}, chart_profile,
                                                              {'cy_axisColor': '#FFFFFF'})

        # Verify that specifying an axis font size results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_line_chart, chart_cols, chart_params,
                                                              {'axis_font_size': 5}, chart_profile,
                                                              {'cy_axisLabelFontSize': 5})

        # Verify that specifying a different slot results in valid properties
        self._check_chart_attrs(set_node_custom_line_chart, chart_cols, chart_params, {'slot': 9}, chart_profile,
                                {})

        # Verify that error is thrown when slot is invalid
        self.assertRaises(CyError, set_node_custom_line_chart, chart_cols, slot=10, **chart_params)
        self.assertRaises(CyError, set_node_custom_line_chart, chart_cols, slot=0, **chart_params)

    @print_entry_exit
    def test_set_node_custom_pie_chart(self):
        # Initialization
        load_test_session()
        chart_params = {'style_name': self._TEST_STYLE}
        chart_profile = {}
        chart_cols = ['AverageShortestPathLength', 'BetweennessCentrality']

        # Verify that specifying no columns results in default properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_pie_chart, [], chart_params, {},
                                                              chart_profile,
                                                              {'cy_colorScheme': 'CUSTOM', 'cy_startAngle': 0.0,
                                                               'cy_colors': [], 'cy_dataColumns': []})

        # Verify that specifying valid columns results in valid default properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_pie_chart, chart_cols, chart_params,
                                                              {}, chart_profile,
                                                              {'cy_colorScheme': 'CUSTOM', 'cy_startAngle': 0.0,
                                                               'cy_colors': ['#E41A1C', '#377EB8', '#4DAF4A',
                                                                             '#984EA3', '#FF7F00', '#FFFF33',
                                                                             '#A65628', '#F781BF', '#999999',
                                                                             '#E41A1C', '#377EB8', '#4DAF4A',
                                                                             '#984EA3', '#FF7F00', '#FFFF33',
                                                                             '#A65628', '#F781BF', '#999999'],
                                                               'cy_dataColumns': ['AverageShortestPathLength',
                                                                                  'BetweennessCentrality']})

        # Verify that specifying display colors results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_pie_chart, chart_cols, chart_params,
                                                              {'colors': ['#FF00FF', '#00FF00']}, chart_profile,
                                                              {'cy_colors': ['#FF00FF', '#00FF00']})

        # Verify that specifying start angle results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_pie_chart, chart_cols, chart_params,
                                                              {'start_angle': 90.0}, chart_profile,
                                                              {'cy_startAngle': 90.0})

        # Verify that specifying a different slot results in valid properties
        self._check_chart_attrs(set_node_custom_pie_chart, chart_cols, chart_params, {'slot': 9}, chart_profile,
                                {})

        # Verify that error is thrown when slot is invalid
        self.assertRaises(CyError, set_node_custom_pie_chart, chart_cols, slot=10, **chart_params)
        self.assertRaises(CyError, set_node_custom_pie_chart, chart_cols, slot=0, **chart_params)

    @print_entry_exit
    def test_set_node_custom_ring_chart(self):
        # Initialization
        load_test_session()
        chart_params = {'style_name': self._TEST_STYLE}
        chart_profile = {}
        chart_cols = ['AverageShortestPathLength', 'BetweennessCentrality']

        # Verify that specifying no columns results in default properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_ring_chart, [], chart_params, {},
                                                              chart_profile,
                                                              {'cy_holeSize': 0.5, 'cy_colorScheme': 'CUSTOM',
                                                               'cy_startAngle': 0.0, 'cy_colors': [],
                                                               'cy_dataColumns': []})

        # Verify that specifying valid columns results in valid default properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_ring_chart, chart_cols, chart_params,
                                                              {}, chart_profile,
                                                              {'cy_holeSize': 0.5, 'cy_colorScheme': 'CUSTOM',
                                                               'cy_startAngle': 0.0,
                                                               'cy_colors': ['#E41A1C', '#377EB8', '#4DAF4A',
                                                                             '#984EA3', '#FF7F00', '#FFFF33',
                                                                             '#A65628', '#F781BF', '#999999',
                                                                             '#E41A1C', '#377EB8', '#4DAF4A',
                                                                             '#984EA3', '#FF7F00', '#FFFF33',
                                                                             '#A65628', '#F781BF', '#999999'],
                                                               'cy_dataColumns': ['AverageShortestPathLength',
                                                                                  'BetweennessCentrality']})

        # Verify that specifying display colors results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_ring_chart, chart_cols, chart_params,
                                                              {'colors': ['#FF00FF', '#00FF00']}, chart_profile,
                                                              {'cy_colors': ['#FF00FF', '#00FF00']})

        # Verify that specifying start angle results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_ring_chart, chart_cols, chart_params,
                                                              {'start_angle': 90.0}, chart_profile,
                                                              {'cy_startAngle': 90.0})

        # Verify that specifying hole size results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_ring_chart, chart_cols, chart_params,
                                                              {'hole_size': 2.0}, chart_profile,
                                                              {'cy_holeSize': 2.0})

        # Verify that specifying a different slot results in valid properties
        self._check_chart_attrs(set_node_custom_ring_chart, chart_cols, chart_params, {'slot': 9}, chart_profile,
                                {})

        # Verify that error is thrown when slot is invalid
        self.assertRaises(CyError, set_node_custom_ring_chart, chart_cols, slot=10, **chart_params)
        self.assertRaises(CyError, set_node_custom_ring_chart, chart_cols, slot=0, **chart_params)

    @print_entry_exit
    def test_set_node_custom_linear_gradient(self):
        # Initialization
        load_test_session()
        chart_params = {'style_name': self._TEST_STYLE}
        chart_profile = {}

        # Verify that specifying no columns results in default properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_linear_gradient, None, chart_params, {},
                                                              chart_profile,
                                                              {'cy_angle': 0.0, 'cy_gradientFractions': [0.0, 1.0],
                                                               'cy_gradientColors': ['#DDDDDD', '#888888']})

        # Verify that specifying display colors results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_linear_gradient, None, chart_params,
                                                              {'colors': ['#FF00FF', '#00FF00']}, chart_profile,
                                                              {'cy_gradientColors': ['#FF00FF', '#00FF00']})

        # Verify that specifying anchor colors results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_linear_gradient, None, chart_params,
                                                              {'anchors': [1.0, 2.0]}, chart_profile,
                                                              {'cy_gradientFractions': [1.0, 2.0]})

        # Verify that specifying hole size results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_linear_gradient, None, chart_params,
                                                              {'angle': 90.0}, chart_profile,
                                                              {'cy_angle': 90.0})

        # Verify that specifying a different slot results in valid properties
        self._check_chart_attrs(set_node_custom_linear_gradient, None, chart_params, {'slot': 9}, chart_profile,
                                {})

        # Verify that error is thrown when slot is invalid
        self.assertRaises(CyError, set_node_custom_linear_gradient, slot=10, **chart_params)
        self.assertRaises(CyError, set_node_custom_linear_gradient, slot=0, **chart_params)

    @print_entry_exit
    def test_set_node_custom_radial_gradient(self):
        # Initialization
        load_test_session()
        chart_params = {'style_name': self._TEST_STYLE}
        chart_profile = {}

        # Verify that specifying no columns results in default properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_radial_gradient, None, chart_params, {},
                                                              chart_profile,
                                                              {'cy_gradientFractions': [0.0, 1.0],
                                                               'cy_gradientColors': ['#DDDDDD', '#888888'],
                                                               'cy_center': {'x': 0.5, 'y': 0.5}})

        # Verify that specifying display colors results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_radial_gradient, None, chart_params,
                                                              {'colors': ['#FF00FF', '#00FF00']}, chart_profile,
                                                              {'cy_gradientColors': ['#FF00FF', '#00FF00']})

        # Verify that specifying anchor colors results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_radial_gradient, None, chart_params,
                                                              {'anchors': [1.0, 2.0]}, chart_profile,
                                                              {'cy_gradientFractions': [1.0, 2.0]})

        # Verify that specifying hole size results in valid properties
        chart_params, chart_profile = self._check_chart_attrs(set_node_custom_radial_gradient, None, chart_params,
                                                              {'x_center': 1.0, 'y_center': 1.5}, chart_profile,
                                                              {'cy_center': {'x': 1.0, 'y': 1.5}})

        # Verify that specifying a different slot results in valid properties
        self._check_chart_attrs(set_node_custom_radial_gradient, None, chart_params, {'slot': 9}, chart_profile,
                                {})

        # Verify that error is thrown when slot is invalid
        self.assertRaises(CyError, set_node_custom_radial_gradient, slot=10, **chart_params)
        self.assertRaises(CyError, set_node_custom_radial_gradient, slot=0, **chart_params)

    @print_entry_exit
    def test_set_node_custom_position(self):
        # Initialization
        load_test_session()

        def check_custom_position(slot):
            # Verify that setting default parameters results in getting default parameters back
            orig_prop = get_visual_property_default('NODE_CUSTOMGRAPHICS_POSITION_' + str(slot),
                                                    style_name=self._TEST_STYLE)
            self.assertEqual(set_node_custom_position(style_name=self._TEST_STYLE, slot=slot), '')
            self.assertEqual(
                get_visual_property_default('NODE_CUSTOMGRAPHICS_POSITION_' + str(slot), style_name=self._TEST_STYLE),
                orig_prop)

            # Verify that setting new parameters results in getting new parameters back
            self.assertEqual(
                set_node_custom_position(node_anchor='W', graphic_anchor='E', justification='l', x_offset=-10.0,
                                         y_offset=15.0, style_name=self._TEST_STYLE, slot=slot), '')
            self.assertEqual(
                get_visual_property_default('NODE_CUSTOMGRAPHICS_POSITION_' + str(slot), style_name=self._TEST_STYLE),
                'W,E,l,-10.00,15.00')

        # Verify that valid parameters in valid slots work properly
        check_custom_position(1)
        check_custom_position(9)

        # Verify that error is thrown when slot is invalid
        self.assertRaises(CyError, set_node_custom_position, slot=10)
        self.assertRaises(CyError, set_node_custom_position, slot=0)

    @print_entry_exit
    def test_remove_node_custom_graphics(self):
        # Initialization
        load_test_session()

        def check_remove_graphics(slot):
            # Verify that setting default parameters results in getting default parameters back
            orig_prop = get_visual_property_default('NODE_CUSTOMGRAPHICS_' + str(slot),
                                                    style_name=self._TEST_STYLE)
            self.assertEqual(set_node_custom_linear_gradient(colors=['#FF00FF', '#00FF00'], anchors=[-2.0, 2.0], angle=90.0, slot=slot, style_name=self._TEST_STYLE), '')
            gradient_prop = get_visual_property_default('NODE_CUSTOMGRAPHICS_' + str(slot),
                                                    style_name=self._TEST_STYLE)
            self.assertEqual(remove_node_custom_graphics(slot=slot, style_name=self._TEST_STYLE), '')
            removed_prop = get_visual_property_default('NODE_CUSTOMGRAPHICS_' + str(slot),
                                                    style_name=self._TEST_STYLE)
            self.assertEqual(orig_prop, removed_prop)

        # Verify that valid parameters in valid slots work properly
        check_remove_graphics(1)
        check_remove_graphics(9)

        # Verify that error is thrown when slot is invalid
        self.assertRaises(CyError, remove_node_custom_graphics, slot=10)
        self.assertRaises(CyError, remove_node_custom_graphics, slot=0)


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
        # Initialization
        load_test_session()

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
        self._check_setter_default(set_edge_label_color_default, 'EDGE_LABEL_COLOR', '#FF00FF', 'bogusColor',
                                   exception_scenario='exception')

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

    @print_entry_exit
    def test_get_edge_selection_color_default(self):
        # Initialization
        load_test_session()

        self._check_getter_default(get_edge_selection_color_default, 'EDGE_STROKE_SELECTED_PAINT', '#FF00FF')

        # Initialization
        load_test_session()

        style_dependencies.set_style_dependencies(style_name=self._TEST_STYLE,
                                                  dependencies={'arrowColorMatchesEdge': True})
        self._check_getter_default(get_edge_selection_color_default, 'EDGE_SELECTED_PAINT', '#FFFF00')

    @print_entry_exit
    def test_set_edge_selection_color_default(self):
        self._check_setter_default(set_edge_selection_color_default, 'EDGE_SELECTED_PAINT', '#FF00FF', 'bogusColor',
                                   exception_scenario='exception')
        self._check_setter_default(set_edge_selection_color_default, 'EDGE_STROKE_SELECTED_PAINT', '#FFFF00',
                                   'bogusColor', exception_scenario='exception')

    @print_entry_exit
    def test_set_edge_source_arrow_color_default(self):
        self._check_setter_default(set_edge_source_arrow_color_default, 'EDGE_SOURCE_ARROW_UNSELECTED_PAINT', '#FF00FF',
                                   'bogusColor', exception_scenario='exception')

    @print_entry_exit
    def test_set_edge_target_arrow_color_default(self):
        self._check_setter_default(set_edge_target_arrow_color_default, 'EDGE_TARGET_ARROW_UNSELECTED_PAINT', '#FF00FF',
                                   'bogusColor', exception_scenario='exception')

    @print_entry_exit
    def test_set_edge_source_arrow_shape_default(self):
        self._check_setter_default(set_edge_source_arrow_shape_default, 'EDGE_SOURCE_ARROW_SHAPE', 'CIRCLE',
                                   'BogusShape', exception_scenario='no effect')

    @print_entry_exit
    def test_set_edge_target_arrow_shape_default(self):
        self._check_setter_default(set_edge_target_arrow_shape_default, 'EDGE_TARGET_ARROW_SHAPE', 'CIRCLE',
                                   'BogusShape', exception_scenario='no effect')

    @print_entry_exit
    def test_set_edge_tooltip_default(self):
        self._check_setter_default(set_edge_tooltip_default, 'EDGE_TOOLTIP', 'test tooltip')

    @print_entry_exit
    def test_get_background_color_default(self):
        # Initialization
        load_test_session()

        self._check_getter_default(get_background_color_default, 'NETWORK_BACKGROUND_PAINT', '#654321')

    @print_entry_exit
    def test_set_background_color_default(self):
        self._check_setter_default(set_background_color_default, 'NETWORK_BACKGROUND_PAINT', '#FF00FF', 'bogusColor')

    def _check_getter_default(self, getter_func, prop_name, new_value):
        # Verify that the node selection color can be fetched and looks different after it's set
        orig_default = get_visual_property_default(prop_name, style_name=self._TEST_STYLE)
        self.assertEqual(
            set_visual_property_default({'visualProperty': prop_name, 'value': new_value}, style_name=self._TEST_STYLE),
            '')
        self._check_getter_value_default(prop_name, orig_default, new_value)
        self.assertEqual(getter_func(style_name=self._TEST_STYLE), new_value)

        # Verify that an invalid style name is caught
        self.assertRaises(TypeError, getter_func,
                          style_name='bogusStyle')  # TODO: Really should be CyError, but for get_style_dependencies() returning null instead of CyError

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

    def _check_chart_attrs(self, chart_func, col_list, base_params, new_params, base_attrs, new_attrs, slot=1):
        # Call the chart function with updated parameters
        chart_params = base_params.copy()
        chart_params.update(new_params)
        if col_list is None:
            self.assertEqual(chart_func(**chart_params), '')
        else:
            self.assertEqual(chart_func(col_list, **chart_params), '')

        # Verify the new property value
        expected_attrs = base_attrs.copy()
        expected_attrs.update(new_attrs)
        whole_prop = get_visual_property_default('NODE_CUSTOMGRAPHICS_' + str(slot), style_name=self._TEST_STYLE)
        chart_dict = json.loads(re.split(':', whole_prop, 1)[1])
        self.assertDictEqual(chart_dict, expected_attrs)
        return chart_params, expected_attrs


if __name__ == '__main__':
    unittest.main()
