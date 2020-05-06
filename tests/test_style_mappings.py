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
import pandas as df


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
        res = map_visual_property('node fill color', 'gal1RGexp', 'c', [-2.426, 0.0, 2.058],
                                  ['#0066CC', '#FFFFFF', '#FFFF00'])
        self._check_property(res, 'NODE_FILL_COLOR', 'gal1RGexp', 'Double', 'continuous',
                             [{'value': -2.426, 'lesser': '#0066CC', 'equal': '#0066CC', 'greater': '#0066CC'},
                              {'value': 0.0, 'lesser': '#FFFFFF', 'equal': '#FFFFFF', 'greater': '#FFFFFF'},
                              {'value': 2.058, 'lesser': '#FFFF00', 'equal': '#FFFF00', 'greater': '#FFFF00'}])

        # Verify continuous property with points list bracketed on either side by colors
        res = map_visual_property('node fill color', 'gal1RGexp', 'c', [-2.426, 0.0, 2.058],
                                  ['#000000', '#0066CC', '#FFFFFF', '#FFFF00', '#FFFFFF'])
        self._check_property(res, 'NODE_FILL_COLOR', 'gal1RGexp', 'Double', 'continuous',
                             [{'value': -2.426, 'lesser': '#000000', 'equal': '#0066CC', 'greater': '#0066CC'},
                              {'value': 0.0, 'lesser': '#FFFFFF', 'equal': '#FFFFFF', 'greater': '#FFFFFF'},
                              {'value': 2.058, 'lesser': '#FFFF00', 'equal': '#FFFF00', 'greater': '#FFFFFF'}])

        # Verify discrete mapping to two values
        res = map_visual_property('node shape', 'degree.layout', 'd', [1, 2], ['ellipse', 'rectangle'])
        self._check_property(res, 'NODE_SHAPE', 'degree.layout', 'Integer', 'discrete',
                             [{'key': 1, 'value': 'ellipse'}, {'key': 2, 'value': 'rectangle'}])

        # Verify passthru of node string value
        res = map_visual_property('node label', 'COMMON', 'p')
        self._check_property(res, 'NODE_LABEL', 'COMMON', 'String', 'passthrough')

        # Verify passthru of node integer value
        res = map_visual_property('node label', 'degree.layout', 'p')
        self._check_property(res, 'NODE_LABEL', 'degree.layout', 'Integer', 'passthrough')

        # Verify discrete mapping of edge string value
        res = map_visual_property('Edge Target Arrow Shape', 'interaction', 'd', ['pp', 'pd'], ['Arrow', 'T'])

        self._check_property(res, 'EDGE_TARGET_ARROW_SHAPE', 'interaction', 'String', 'discrete',
                             [{'key': 'pp', 'value': 'Arrow'}, {'key': 'pd', 'value': 'T'}])

        # Verify passthru mapping of edge double value
        res = map_visual_property('edge width', 'EdgeBetweenness', 'p')
        self._check_property(res, 'EDGE_WIDTH', 'EdgeBetweenness', 'Double', 'passthrough')

        # Verify that unknown type acts like passthru
        res = map_visual_property('edge width', 'EdgeBetweenness', 'junktype')
        self._check_property(res, 'EDGE_WIDTH', 'EdgeBetweenness', 'Double', 'junktype')

        # Verify that unknown property, column or bad continuous mapping are caught
        self.assertRaises(CyError, map_visual_property, 'bogus property', 'EdgeBetweenness', 'p')
        self.assertRaises(CyError, map_visual_property, 'edge width', 'bogus column', 'p')
        self.assertRaises(CyError, map_visual_property, 'node fill color', 'gal1RGexp', 'c',
                          [-10.0, -2.426, 0.0, 2.058], ['#0066CC', '#FFFFFF', '#FFFF00'])

    @print_entry_exit
    def test_get_style_all_mappings(self):
        # Initialization
        load_test_session()

        # Verify that a plausible style can be fetched (... in this case, discrete mapping isn't present)
        res = get_style_all_mappings(self._GAL_FILTERED_STYLE)
        indexed_properties = {prop['visualProperty']: prop for prop in res}
        self._check_property(indexed_properties['NODE_LABEL'], 'NODE_LABEL', 'COMMON', 'String', 'passthrough')
        self._check_property(indexed_properties['NODE_SIZE'], 'NODE_SIZE', 'degree.layout', 'Number', 'continuous',
                             [{'value': 1.0, 'lesser': '1.0', 'equal': '40.0', 'greater': '40.0'},
                              {'value': 18.0, 'lesser': '150.0', 'equal': '150.0', 'greater': '1.0'}])
        self._check_property(indexed_properties['NODE_FILL_COLOR'], 'NODE_FILL_COLOR', 'gal1RGexp', 'Number',
                             'continuous',
                             [{'value': -2.426, 'lesser': '#0066CC', 'equal': '#0066CC', 'greater': '#0066CC'},
                              {'value': 1.225471493171426e-07, 'lesser': '#FFFFFF', 'equal': '#FFFFFF',
                               'greater': '#FFFFFF'},
                              {'value': 2.058, 'lesser': '#FFFF00', 'equal': '#FFFF00', 'greater': '#FFFF00'}])
        self._check_property(indexed_properties['NODE_LABEL_FONT_SIZE'], 'NODE_LABEL_FONT_SIZE', 'Degree', 'Number',
                             'continuous', [{'value': 1.0, 'lesser': '1', 'equal': '10', 'greater': '10'},
                                            {'value': 18.0, 'lesser': '40', 'equal': '40', 'greater': '1'}])

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
            self._check_property(res, indexed_prop['visualProperty'], indexed_prop['mappingColumn'],
                                 indexed_prop['mappingColumnType'], indexed_prop['mappingType'], cargo)

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
        # WARNING: This update often fails silently, which causes the get_style_mapping to fail [Cytoscape BUG]
        self.assertEqual(update_style_mapping(self._GAL_FILTERED_STYLE, existing_prop), '')
        readded_prop = get_style_mapping(self._GAL_FILTERED_STYLE, 'NODE_LABEL')
        self._check_property(readded_prop, existing_prop['visualProperty'], existing_prop['mappingColumn'],
                             existing_prop['mappingColumnType'], existing_prop['mappingType'])

        # Verify that an invalid style or property is caught
        self.assertRaises(CyError, update_style_mapping, 'bogus style', new_prop)
        self.assertRaises(TypeError, update_style_mapping, self._GAL_FILTERED_STYLE, 'bogus property')

    @print_entry_exit
    def test_set_node_border_color_mapping(self):
        _NEW_DEFAULT = '#654321'
        _PASSTHRU_VAL = '#123456'
        self._check_set_property({'prop_func': set_node_border_color_mapping,
                                  'prop_name': 'NODE_BORDER_PAINT',
                                  'new_default': _NEW_DEFAULT,
                                  'passthru_val': _PASSTHRU_VAL,
                                  'cont_test_params': {'colors': ['#FBE723', '#440256']},
                                  'cont_bad_map_params': {'colors': ['#FBE72', '#440256']},
                                  'cont_short_map_params': {'colors': ['#440256']},
                                  'disc_test_params': {'colors': ['#FFFF00', '#00FF00']},
                                  'pass_test_params': {'default_color': _NEW_DEFAULT},
                                  })

    @print_entry_exit
    def test_set_node_border_opacity_mapping(self):
        _NEW_DEFAULT = 225
        _PASSTHRU_VAL = 250
        self._check_set_property({'prop_func': set_node_border_opacity_mapping,
                                  'prop_name': 'NODE_BORDER_TRANSPARENCY',
                                  'new_default': _NEW_DEFAULT,
                                  'passthru_val': _PASSTHRU_VAL,
                                  'cont_test_params': {'opacities': [50, 100]},
                                  'cont_bad_map_params': {'opacities': [550, 100]},
                                  'cont_short_map_params': {'opacities': [50]},
                                  'disc_test_params': {'opacities': [50, 100]},
                                  'pass_test_params': {'default_opacity': _NEW_DEFAULT},
                                  })

    @print_entry_exit
    def test_set_node_border_width_mapping(self):
        _NEW_DEFAULT = 4
        _PASSTHRU_VAL = 3
        self._check_set_property({'prop_func': set_node_border_width_mapping,
                                  'prop_name': 'NODE_BORDER_WIDTH',
                                  'new_default': _NEW_DEFAULT,
                                  'passthru_val': _PASSTHRU_VAL,
                                  'cont_test_params': {'widths': [5, 10]},
                                  # 'cont_bad_map_params': {'width': [550, 100]}, ... no bounds checking for this property
                                  'cont_short_map_params': {'widths': [5]},
                                  'disc_test_params': {'widths': [5, 10]},
                                  'pass_test_params': {'default_width': _NEW_DEFAULT},
                                  })

    @print_entry_exit
    def test_set_node_color_mapping(self):
        _NEW_DEFAULT = '#654321'
        _PASSTHRU_VAL = '#123456'
        self._check_set_property({'prop_func': set_node_color_mapping,
                                  'prop_name': 'NODE_FILL_COLOR',
                                  'new_default': _NEW_DEFAULT,
                                  'passthru_val': _PASSTHRU_VAL,
                                  'cont_test_params': {'colors': ['#FBE723', '#440256']},
                                  'cont_bad_map_params': {'colors': ['#FBE72', '#440256']},
                                  'cont_short_map_params': {'colors': ['#440256']},
                                  'disc_test_params': {'colors': ['#FFFF00', '#00FF00']},
                                  'pass_test_params': {'default_color': _NEW_DEFAULT},
                                  })

    @print_entry_exit
    def test_set_node_combo_opacity_mapping(self):
        _NEW_DEFAULT = 225
        _PASSTHRU_VAL = 250
        self._check_set_property({'prop_func': set_node_combo_opacity_mapping,
                                  'prop_name': ['NODE_TRANSPARENCY', 'NODE_BORDER_TRANSPARENCY', 'NODE_LABEL_TRANSPARENCY'],
                                  'new_default': _NEW_DEFAULT,
                                  'passthru_val': _PASSTHRU_VAL,
                                  'cont_test_params': {'opacities': [50, 100]},
                                  'cont_bad_map_params': {'opacities': [550, 100]},
                                  'cont_short_map_params': {'opacities': [50]},
                                  'disc_test_params': {'opacities': [50, 100]},
                                  'pass_test_params': {'default_opacity': _NEW_DEFAULT},
                                  })

    @print_entry_exit
    def test_set_node_fill_opacity_mapping(self):
        _NEW_DEFAULT = 225
        _PASSTHRU_VAL = 250
        self._check_set_property({'prop_func': set_node_fill_opacity_mapping,
                                  'prop_name': 'NODE_TRANSPARENCY',
                                  'new_default': _NEW_DEFAULT,
                                  'passthru_val': _PASSTHRU_VAL,
                                  'cont_test_params': {'opacities': [50, 100]},
                                  'cont_bad_map_params': {'opacities': [550, 100]},
                                  'cont_short_map_params': {'opacities': [50]},
                                  'disc_test_params': {'opacities': [50, 100]},
                                  'pass_test_params': {'default_opacity': _NEW_DEFAULT},
                                  })

    @print_entry_exit
    def test_set_node_font_face_mapping(self):
        _NEW_DEFAULT = 'Dialog.bold,bold,12'
        _PASSTHRU_VAL = 'Dialog.italic,plain,12'
        self._check_set_property({'prop_func': set_node_font_face_mapping,
                                  'prop_name': 'NODE_LABEL_FONT_FACE',
                                  'new_default': _NEW_DEFAULT,
                                  'passthru_val': _PASSTHRU_VAL,
                                  # 'cont_test_params': {'fonts': ['Arial,plain,12', 'Arial Bold,bold,12']},
                                  # 'cont_bad_map_params': {'fonts': ['Arial bogus,plain,12', 'Arial Bold,bold,12']},
                                  # 'cont_short_map_params': {'fonts': ['Arial,plain,12']},
                                  'disc_test_params': {'fonts': ['Arial,plain,12', 'Arial Bold,bold,12']},
                                  'pass_test_params': {'default_font': _NEW_DEFAULT},
                                  })
















    def _check_set_property(self, profile):
        # Initialization
        load_test_session()
        _TEST_NODE = 'YML007W'
        _NOT_TEST_NODE = 'YGL035C'
        _TEST_STYLE = 'galFiltered Style'
        prop_name_list = profile['prop_name'] if isinstance(profile['prop_name'], list) else [profile['prop_name']]
        orig_value_list = [get_node_property(node_names=[_TEST_NODE], visual_property=prop_name)[_TEST_NODE]
                           for prop_name in prop_name_list]

        # Verify that applying a continuous mapping functions
        if 'cont_test_params' in profile:
            self.assertEqual(profile['prop_func'](style_name=_TEST_STYLE, table_column='AverageShortestPathLength',
                                                  table_column_values=[1.0, 16.36], **profile['cont_test_params']), '')
            cont_value_list = [get_node_property(visual_property=prop_name)[_TEST_NODE]     for prop_name in prop_name_list]
            for cont_value, orig_value in zip(cont_value_list, orig_value_list):
                self.assertNotEqual(cont_value, orig_value)
        else:
            cont_value_list = []
            self.assertRaises(CyError, profile['prop_func'], style_name=_TEST_STYLE, table_column='AverageShortestPathLength', mapping_type='c')

        # Verify that applying a discrete mapping functions
        if 'disc_test_params' in profile:
            self.assertEqual(profile['prop_func'](style_name=_TEST_STYLE, table_column='Degree', mapping_type='d',
                                                  table_column_values=['1', '2'],
                                                  **profile['disc_test_params']), '')
            disc_value_list = [get_node_property(visual_property=prop_name)[_TEST_NODE]    for prop_name in prop_name_list]
            for disc_value, orig_value in zip(disc_value_list, orig_value_list):
                self.assertNotEqual(disc_value, orig_value)
            for disc_value, cont_value in zip(disc_value_list, cont_value_list):
                self.assertNotEqual(disc_value, cont_value)
        else:
            self.assertRaises(CyError, profile['prop_func'], style_name=_TEST_STYLE, table_column='Degree', mapping_type='d')

        # Create a column containing values, then verify that a passthru mapping causes a new value and new default value
        data = df.DataFrame(data={'id': [_TEST_NODE], 'PassthruCol': [profile['passthru_val']]})
        load_table_data(data, data_key_column='id', table='node', table_key_column='name')
        if 'pass_test_params' in profile:
            self.assertEqual(profile['prop_func'](style_name=_TEST_STYLE, table_column='PassthruCol', mapping_type='p',
                                                  **profile['pass_test_params']), '')
            pass_value_list = [get_node_property(visual_property=prop_name)[_TEST_NODE]    for prop_name in prop_name_list]
            for pass_value in pass_value_list:
                self.assertEqual(pass_value, profile['passthru_val'])
            def_value_list = [get_node_property(visual_property=prop_name)[_NOT_TEST_NODE]     for prop_name in prop_name_list]
            for def_value in def_value_list:
                self.assertEqual(def_value, profile['new_default'])
        else:
            self.assertRaises(CyError, profile['prop_func'], style_name=_TEST_STYLE, table_column='PassthruCol', mapping_type='p')

        # Verify that a bad value is caught
        if 'cont_bad_map_params' in profile:
            self.assertIsNone(profile['prop_func'](style_name=_TEST_STYLE, table_column='AverageShortestPathLength',
                                                   table_column_values=[1.0, 16.36], **profile['cont_bad_map_params']))

        # Verify that a bad mapping type is caught
        self.assertIsNone(profile['prop_func'](style_name=_TEST_STYLE, table_column='PassthruCol', mapping_type='X'))

        # Verify that a bad column name is caught
        self.assertRaises(CyError, profile['prop_func'], style_name=_TEST_STYLE, table_column='Bogus Col',
                          mapping_type='p')

        # Verify that a bad style name is caught
        self.assertRaises(CyError, profile['prop_func'], style_name='Bogus Style', table_column='PassthruCol',
                          mapping_type='p')

        # Verify that that a short mapping is caught
        if 'cont_short_map_params' in profile:
            self.assertRaises(CyError, profile['prop_func'], style_name=_TEST_STYLE,
                              table_column='AverageShortestPathLength', table_column_values=[1.0, 16.36],
                              **profile['cont_short_map_params'])

        # Verify that a bad network is caught
        self.assertRaises(CyError, profile['prop_func'], style_name=_TEST_STYLE, table_column='PassthruCol',
                          mapping_type='p', network='bogus network')

    def _check_property(self, cy_property, expected_property, expected_column, expected_column_type, expected_type,
                        expected_cargo=None):
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
            self.assertEqual(len(cy_property), 4)  # passthrough or unknown


if __name__ == '__main__':
    unittest.main()
