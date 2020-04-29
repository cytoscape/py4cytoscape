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
from requests import RequestException

from test_utils import *


class StylesTests(unittest.TestCase):
    def setUp(self):
        try:
            py4cytoscape.delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    #    @py4cytoscape.skip
    @py4cytoscape.print_entry_exit
    def test_copy_visual_style(self):
        # Initialization
        load_test_session()

        # Verify that a new style can be added
        original_style_list = py4cytoscape.get_visual_style_names()
        res = py4cytoscape.copy_visual_style('Solid', 'SolidCopy')
        self.assertIsInstance(res, str)
        self.assertEqual(res, '')
        self.assertSetEqual(set(original_style_list) | {'SolidCopy'}, set(py4cytoscape.get_visual_style_names()))

        # Verify that the new style is the same as the old style
        original_style_props = py4cytoscape.get_style_all_mappings('Solid')
        new_style_props = py4cytoscape.get_style_all_mappings('Solid')
        self.assertListEqual(original_style_props, new_style_props)
        # TODO: Remember to compare defaults and dependencies, too

        # Verify that an invalid style name is caught
        self.assertRaises(py4cytoscape.CyError, py4cytoscape.copy_visual_style, 'bogusStyle', 'bogusStyleCopy')
        self.assertRaises(RequestException, py4cytoscape.copy_visual_style, 'Solid', '')


    #    @py4cytoscape.skip
    @py4cytoscape.print_entry_exit
    def test_create_visual_style(self):
        # Initialization
        load_test_session()

        def check_new_style(style_name):
            new_style_props = py4cytoscape.get_style_all_mappings(style_name)
            indexed_properties = {prop['visualProperty']: prop for prop in new_style_props}
            self._check_property(indexed_properties['NODE_LABEL'], 'NODE_LABEL', 'COMMON', 'String', 'passthrough')
            self._check_property(indexed_properties['NODE_FILL_COLOR'], 'NODE_FILL_COLOR', 'Degree', 'Integer', 'discrete', [{'key': '1', 'value': '#FF9900'}, {'key': '2', 'value': '#66AAAA'}])
            self._check_property(indexed_properties['EDGE_TARGET_ARROW_SHAPE'], 'EDGE_TARGET_ARROW_SHAPE', 'interaction', 'String', 'discrete', [{'key': 'pp', 'value': 'ARROW'}, {'key': 'pd', 'value': 'T'}])
            self._check_property(indexed_properties['EDGE_WIDTH'], 'EDGE_WIDTH', 'EdgeBetweenness', 'Double', 'passthrough')


        # Verify that creating a new style reports success
        defaults = {'NODE_SHAPE': 'diamond', 'NODE_SIZE': 30, 'EDGE_TRANSPARENCY': 120, 'NODE_LABEL_POSITION': 'W,E,c,0.00,0.00'}
        node_labels = py4cytoscape.map_visual_property('node label', 'COMMON', 'p')
        node_fills = py4cytoscape.map_visual_property('node fill color', 'Degree', 'd', ['1', '2'], ['#FF9900', '#66AAAA'])
        arrow_shapes = py4cytoscape.map_visual_property('Edge Target Arrow Shape', 'interaction', 'd', ['pp', 'pd'], ['Arrow', 'T'])
        edge_width = py4cytoscape.map_visual_property('edge width', 'EdgeBetweenness', 'p')
        res = py4cytoscape.create_visual_style('NewStyle', defaults=defaults, mappings=[node_labels, node_fills, arrow_shapes, edge_width])
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {'title': 'NewStyle'})

        # Verify that the properties are correct
        check_new_style('NewStyle')

        # Verify that creating the same style again gives the same results, except a different name
        res = py4cytoscape.create_visual_style('NewStyle', defaults=defaults, mappings=[node_labels, node_fills, arrow_shapes, edge_width])
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {'title': 'NewStyle_0'})
        check_new_style('NewStyle_0')

        # Create another style that has no defaults
        res = py4cytoscape.create_visual_style('NewStyleNoDefaults', mappings=[node_labels, node_fills, arrow_shapes, edge_width])
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {'title': 'NewStyleNoDefaults'})
        check_new_style('NewStyleNoDefaults')

        # Create another style that has no defaults or mappings
        res = py4cytoscape.create_visual_style('NewStyleEmpty')
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {'title': 'NewStyleEmpty'})
        self.assertListEqual(py4cytoscape.get_style_all_mappings('NewStyleEmpty'), [])

        # Verify that creating an invalid style returns an error
        node_fills = py4cytoscape.map_visual_property('node fill color', 'Degree', 'd', [1, 2], ['#FF9900', '#66AAAA'])
        self.assertRaises(py4cytoscape.CyError, py4cytoscape.create_visual_style, 'BogusStyle', defaults=defaults, mappings=[node_labels, node_fills, arrow_shapes, edge_width])


    def _check_property(self, cy_property, expected_property, expected_column, expected_column_type, expected_type, expected_cargo = None):
        self.assertIsInstance(cy_property, dict)
        self.assertEqual(cy_property['mappingType'], expected_type)
        self.assertEqual(cy_property['mappingColumn'], expected_column)
        self.assertEqual(cy_property['mappingColumnType'], expected_column_type)
        self.assertEqual(cy_property['visualProperty'], expected_property)
        if expected_type == 'discrete':
            self.assertIsInstance(cy_property['map'], type(expected_cargo))
            self.assertListEqual(cy_property['map'], expected_cargo)
        elif expected_type == 'continuous':
            self.assertIsInstance(cy_property['points'], type(expected_cargo))
            self.assertListEqual(cy_property['points'], expected_cargo)
        else:
            self.assertEqual(len(cy_property), 4) # passthrough or unknown


if __name__ == '__main__':
    unittest.main()
