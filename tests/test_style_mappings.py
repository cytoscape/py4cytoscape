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


class StyleMappingsTests(unittest.TestCase):
    def setUp(self):
        try:
            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    _GAL_FILTERED_STYLE = 'galFiltered Style'

    
    @print_entry_exit
    def test_map_visual_property(self):
        # Initialization
        load_test_session()

        # Verify continuous property with points list matching color list
        res = map_visual_property('node fill color', 'gal1RGexp', 'c', [-2.426, 0.0, 2.058], ['#0066CC', '#FFFFFF','#FFFF00']) # {'mappingType': 'continuous', 'mappingColumn': 'gal1RGexp', 'mappingColumnType': 'Double', 'visualProperty': 'NODE_FILL_COLOR', 'points': [{'value': -2.426, 'lesser': '#0066CC', 'equal': '#0066CC', 'greater': '#0066CC'}, {'value': 0.0, 'lesser': '#FFFFFF', 'equal': '#FFFFFF', 'greater': '#FFFFFF'}, {'value': 2.058, 'lesser': '#FFFF00', 'equal': '#FFFF00', 'greater': '#FFFF00'}]}
        self._check_property(res, 'NODE_FILL_COLOR', 'gal1RGexp', 'Double', 'continuous', [{'value': -2.426, 'lesser': '#0066CC', 'equal': '#0066CC', 'greater': '#0066CC'}, {'value': 0.0, 'lesser': '#FFFFFF', 'equal': '#FFFFFF', 'greater': '#FFFFFF'}, {'value': 2.058, 'lesser': '#FFFF00', 'equal': '#FFFF00', 'greater': '#FFFF00'}])

        # Verify continuous property with points list bracketed on either side by colors
        res = map_visual_property('node fill color', 'gal1RGexp', 'c', [-2.426, 0.0, 2.058], ['#000000', '#0066CC', '#FFFFFF','#FFFF00', '#FFFFFF']) # {'mappingType': 'continuous', 'mappingColumn': 'gal1RGexp', 'mappingColumnType': 'Double', 'visualProperty': 'NODE_FILL_COLOR', 'points': [{'value': -2.426, 'lesser': '#000000', 'equal': '#0066CC', 'greater': '#0066CC'}, {'value': 0.0, 'lesser': '#FFFFFF', 'equal': '#FFFFFF', 'greater': '#FFFFFF'}, {'value': 2.058, 'lesser': '#FFFF00', 'equal': '#FFFF00', 'greater': '#FFFFFF'}]}
        self._check_property(res, 'NODE_FILL_COLOR', 'gal1RGexp', 'Double', 'continuous', [{'value': -2.426, 'lesser': '#000000', 'equal': '#0066CC', 'greater': '#0066CC'}, {'value': 0.0, 'lesser': '#FFFFFF', 'equal': '#FFFFFF', 'greater': '#FFFFFF'}, {'value': 2.058, 'lesser': '#FFFF00', 'equal': '#FFFF00', 'greater': '#FFFFFF'}])

        # Verify discrete mapping to two values
        res = map_visual_property('node shape', 'degree.layout', 'd', [1, 2], ['ellipse', 'rectangle']) # {'mappingType': 'discrete', 'mappingColumn': 'degree.layout', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_SHAPE', 'map': [{'key': 1, 'value': 'ellipse'}, {'key': 2, 'value': 'rectangle'}]}
        self._check_property(res, 'NODE_SHAPE', 'degree.layout', 'Integer', 'discrete', [{'key': 1, 'value': 'ellipse'}, {'key': 2, 'value': 'rectangle'}])

        # Verify passthru of node string value
        res = map_visual_property('node label', 'COMMON', 'p') # {'mappingType': 'passthrough', 'mappingColumn': 'COMMON', 'mappingColumnType': 'String', 'visualProperty': 'NODE_LABEL'}
        self._check_property(res, 'NODE_LABEL', 'COMMON', 'String', 'passthrough')

        # Verify passthru of node integer value
        res = map_visual_property('node label', 'degree.layout', 'p') # {'mappingType': 'passthrough', 'mappingColumn': 'degree.layout', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_LABEL'}
        self._check_property(res, 'NODE_LABEL', 'degree.layout', 'Integer', 'passthrough')

        # Verify discrete mapping of edge string value
        res = map_visual_property('Edge Target Arrow Shape', 'interaction', 'd', ['pp','pd'], ['Arrow','T']) # {'mappingType': 'passthrough', 'mappingColumn': 'degree.layout', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_LABEL'}
        self._check_property(res, 'EDGE_TARGET_ARROW_SHAPE', 'interaction', 'String', 'discrete', [{'key': 'pp', 'value': 'Arrow'}, {'key': 'pd', 'value': 'T'}])

        # Verify passthru mapping of edge double value
        res = map_visual_property('edge width', 'EdgeBetweenness', 'p') # {'mappingType': 'passthrough', 'mappingColumn': 'EdgeBetweenness', 'mappingColumnType': 'Double', 'visualProperty': 'EDGE_WIDTH'}
        self._check_property(res, 'EDGE_WIDTH', 'EdgeBetweenness', 'Double', 'passthrough')

        # Verify that unknown type acts like passthru
        res = map_visual_property('edge width', 'EdgeBetweenness', 'junktype')
        self._check_property(res, 'EDGE_WIDTH', 'EdgeBetweenness', 'Double', 'junktype')

        # Verify that unknown property, column or bad continuous mapping are caught
        self.assertRaises(CyError, map_visual_property, 'bogus property', 'EdgeBetweenness', 'p')
        self.assertRaises(CyError, map_visual_property, 'edge width', 'bogus column', 'p')
        self.assertRaises(CyError, map_visual_property, 'node fill color', 'gal1RGexp', 'c', [-10.0, -2.426, 0.0, 2.058], ['#0066CC', '#FFFFFF','#FFFF00'])



    @print_entry_exit
    def test_get_style_all_mappings(self):
        # Initialization
        load_test_session()

        # Verify that a plausible style can be fetched (... in this case, discrete mapping isn't present)
        res = get_style_all_mappings(self._GAL_FILTERED_STYLE)
        indexed_properties = {prop['visualProperty']: prop    for prop in res}
        self._check_property(indexed_properties['NODE_LABEL'], 'NODE_LABEL', 'COMMON', 'String', 'passthrough')
        self._check_property(indexed_properties['NODE_SIZE'], 'NODE_SIZE', 'degree.layout', 'Number', 'continuous', [{'value': 1.0, 'lesser': '1.0', 'equal': '40.0', 'greater': '40.0'}, {'value': 18.0, 'lesser': '150.0', 'equal': '150.0', 'greater': '1.0'}])
        self._check_property(indexed_properties['NODE_FILL_COLOR'], 'NODE_FILL_COLOR', 'gal1RGexp', 'Number', 'continuous', [{'value': -2.426, 'lesser': '#0066CC', 'equal': '#0066CC', 'greater': '#0066CC'}, {'value': 1.225471493171426e-07, 'lesser': '#FFFFFF', 'equal': '#FFFFFF', 'greater': '#FFFFFF'}, {'value': 2.058, 'lesser': '#FFFF00', 'equal': '#FFFF00', 'greater': '#FFFF00'}])
        self._check_property(indexed_properties['NODE_LABEL_FONT_SIZE'], 'NODE_LABEL_FONT_SIZE', 'Degree', 'Number', 'continuous', [{'value': 1.0, 'lesser': '1', 'equal': '10', 'greater': '10'}, {'value': 18.0, 'lesser': '40', 'equal': '40', 'greater': '1'}])

        # Verify that an invalid style is caught
        self.assertRaises(CyError, get_style_all_mappings, 'bogus style')

    
    @print_entry_exit
    def test_get_style_mapping(self):
        # Initialization
        load_test_session()

        # Get all of the properties in a list
        res = get_style_all_mappings(self._GAL_FILTERED_STYLE)
        indexed_properties = {prop['visualProperty']: prop for prop in res}

        # Fetch each property and verify it matches the one in the list
        for prop_name in indexed_properties:
            res = get_style_mapping(self._GAL_FILTERED_STYLE, prop_name)
            indexed_prop = indexed_properties[prop_name]
            cargo = indexed_prop['map'] if 'map' in indexed_prop else \
                    indexed_prop['points'] if 'points' in indexed_prop else \
                    None
            self._check_property(res, indexed_prop['visualProperty'], indexed_prop['mappingColumn'], indexed_prop['mappingColumnType'], indexed_prop['mappingType'], cargo)

        # Verify that an invalid style or property is caught
        self.assertRaises(CyError, get_style_mapping, 'bogus style', 'NODE_SIZE')
        self.assertRaises(CyError, get_style_mapping, self._GAL_FILTERED_STYLE, 'bogus property')

    
    @print_entry_exit
    def test_delete_style_mapping(self):
        # Initialization
        load_test_session()

        # Get all of the properties in a list and delete the first one
        all_props = get_style_all_mappings(self._GAL_FILTERED_STYLE)
        prop_to_delete = all_props[0]['visualProperty']
        res = delete_style_mapping(self._GAL_FILTERED_STYLE, prop_to_delete)
        self.assertEqual(res, '')

        # Verify that after the delete, the style is no longer present
        remaining_props = get_style_all_mappings(self._GAL_FILTERED_STYLE)
        del all_props[0]
        self.assertListEqual(all_props, remaining_props)

        # Verify that an invalid style or property is caught
        self.assertRaises(CyError, delete_style_mapping, 'bogus style', prop_to_delete)
        self.assertIsNone(delete_style_mapping(self._GAL_FILTERED_STYLE, 'bogus property'))

    
    @print_entry_exit
    def test_update_style_mapping(self):
        # Initialization
        load_test_session()

        # Replace the existing NODE_LABEL property with a different one, and verify that it was replaced
        existing_prop = get_style_mapping(self._GAL_FILTERED_STYLE, 'NODE_LABEL')
        new_prop = map_visual_property('NODE_LABEL', 'name', 'p')
        self.assertEqual(update_style_mapping(self._GAL_FILTERED_STYLE, new_prop), '')
        replaced_prop = get_style_mapping(self._GAL_FILTERED_STYLE, 'NODE_LABEL')
        self._check_property(replaced_prop, 'NODE_LABEL', 'name', 'String', 'passthrough')

        # Remove the NODE_LABEL property, verify it's removed, then re-add the original property ane verify
        self.assertEqual(delete_style_mapping(self._GAL_FILTERED_STYLE, 'NODE_LABEL'), '')
        self.assertRaises(CyError, get_style_mapping, self._GAL_FILTERED_STYLE, 'NODE_LABEL')
        self.assertEqual(update_style_mapping(self._GAL_FILTERED_STYLE, existing_prop), '')
        readded_prop = get_style_mapping(self._GAL_FILTERED_STYLE, 'NODE_LABEL')
        self._check_property(readded_prop, existing_prop['visualProperty'], existing_prop['mappingColumn'], existing_prop['mappingColumnType'], existing_prop['mappingType'])

        # Verify that an invalid style or property is caught
        self.assertRaises(CyError, update_style_mapping, 'bogus style', new_prop)
        self.assertRaises(TypeError, update_style_mapping, self._GAL_FILTERED_STYLE, 'bogus property')


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
