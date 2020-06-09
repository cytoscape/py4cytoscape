# -*- coding: utf-8 -*-

""" Test functions in style_mappings.py.
"""

"""License:
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
import time

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

    @unittest.skip('NODE_LABEL doesnt seem to exist ... maybe because of a timing race condition??')
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

        ### Failed ... NODE_LABEL doesn't seem to exist ... maybe because of a timing race condition??

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
        self._check_set_node_property({'prop_func': set_node_border_color_mapping,
                                       'prop_name': 'NODE_BORDER_PAINT',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       'cont_test_params': {'colors': ['#FBE723', '#440256']},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       'cont_bad_map_params': {'colors': ['#FBE72', '#440256']},
                                       'cont_short_map_params': {'colors': ['#440256']},
                                       'disc_test_params': {'colors': ['#FFFF00', '#00FF00'], 'mapping_type': 'd'},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_color': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_node_border_opacity_mapping(self):
        _NEW_DEFAULT = 225
        _PASSTHRU_VAL = 250
        self._check_set_node_property({'prop_func': set_node_border_opacity_mapping,
                                       'prop_name': 'NODE_BORDER_TRANSPARENCY',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       'cont_test_params': {'opacities': [50, 100]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       'cont_bad_map_params': {'opacities': [550, 100]},
                                       'cont_short_map_params': {'opacities': [50]},
                                       'disc_test_params': {'opacities': [50, 100], 'mapping_type': 'd'},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_opacity': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_node_border_width_mapping(self):
        _NEW_DEFAULT = 4
        _PASSTHRU_VAL = 3
        self._check_set_node_property({'prop_func': set_node_border_width_mapping,
                                       'prop_name': 'NODE_BORDER_WIDTH',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       'cont_test_params': {'widths': [5, 10]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       # 'cont_bad_map_params': {'width': [550, 100]}, ... no bounds checking for this property
                                       'cont_short_map_params': {'widths': [5]},
                                       'disc_test_params': {'widths': [5, 10], 'mapping_type': 'd'},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_width': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_node_color_mapping(self):
        _NEW_DEFAULT = '#654321'
        _PASSTHRU_VAL = '#123456'
        self._check_set_node_property({'prop_func': set_node_color_mapping,
                                       'prop_name': 'NODE_FILL_COLOR',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       'cont_test_params': {'colors': ['#FBE723', '#440256']},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       'cont_bad_map_params': {'colors': ['#FBE72', '#440256']},
                                       'cont_short_map_params': {'colors': ['#440256']},
                                       'disc_test_params': {'colors': ['#FFFF00', '#00FF00'], 'mapping_type': 'd'},
                                       # 'disc_invalid_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_color': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_invalid_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_node_combo_opacity_mapping(self):
        _NEW_DEFAULT = 225
        _PASSTHRU_VAL = 250
        self._check_set_node_property({'prop_func': set_node_combo_opacity_mapping,
                                       'prop_name': ['NODE_TRANSPARENCY', 'NODE_BORDER_TRANSPARENCY',
                                                     'NODE_LABEL_TRANSPARENCY'],
                                       'new_default': _NEW_DEFAULT,
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       'set_default': 'p',
                                       'cont_test_params': {'opacities': [50, 100]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       'cont_bad_map_params': {'opacities': [550, 100]},
                                       'cont_short_map_params': {'opacities': [50]},
                                       'disc_test_params': {'opacities': [50, 100], 'mapping_type': 'd'},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_opacity': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_node_fill_opacity_mapping(self):
        _NEW_DEFAULT = 225
        _PASSTHRU_VAL = 250
        self._check_set_node_property({'prop_func': set_node_fill_opacity_mapping,
                                       'prop_name': 'NODE_TRANSPARENCY',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       'cont_test_params': {'opacities': [50, 100]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       'cont_bad_map_params': {'opacities': [550, 100]},
                                       'cont_short_map_params': {'opacities': [50]},
                                       'disc_test_params': {'opacities': [50, 100], 'mapping_type': 'd'},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_opacity': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_node_font_face_mapping(self):
        _NEW_DEFAULT = 'Dialog.bold,bold,12'
        _PASSTHRU_VAL = 'Dialog.italic,plain,12'
        self._check_set_node_property({'prop_func': set_node_font_face_mapping,
                                       'prop_name': 'NODE_LABEL_FONT_FACE',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       # 'cont_test_params': {'fonts': ['Arial,plain,12', 'Arial Bold,bold,12']},
                                       'cont_no_map_params': {'mapping_type': 'c'},
                                       # 'cont_bad_map_params': {'fonts': ['Arial bogus,plain,12', 'Arial Bold,bold,12']},
                                       # 'cont_short_map_params': {'fonts': ['Arial,plain,12']},
                                       'disc_test_params': {'fonts': ['Arial,plain,12', 'Arial Bold,bold,12'],
                                                            'mapping_type': 'd'},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_font': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_node_font_size_mapping(self):
        _NEW_DEFAULT = 20
        _PASSTHRU_VAL = 40
        self._check_set_node_property({'prop_func': set_node_font_size_mapping,
                                       'prop_name': 'NODE_LABEL_FONT_SIZE',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       'cont_test_params': {'sizes': [20, 80]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       # 'cont_bad_map_params': {'sizes': [20, 80]},
                                       'cont_short_map_params': {'sizes': [20]},
                                       'disc_test_params': {'sizes': [40, 90], 'mapping_type': 'd'},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_size': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_node_height_mapping(self):
        _NEW_DEFAULT = 120
        _PASSTHRU_VAL = 140
        self._check_set_node_property({'prop_func': set_node_height_mapping,
                                       'prop_name': 'NODE_HEIGHT',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       'compare_tolerance_percent': 2,
                                       'cont_test_params': {'heights': [120, 180]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       # 'cont_bad_map_params': {'heights': [120, 180]},
                                       'cont_short_map_params': {'heights': [120]},
                                       'disc_test_params': {'heights': [140, 190], 'mapping_type': 'd'},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_height': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_node_label_mapping(self):
        # _NEW_DEFAULT = 'Test'
        _PASSTHRU_VAL = 'name'
        self._check_set_node_property({'prop_func': set_node_label_mapping,
                                       'prop_name': 'NODE_LABEL',
                                       # 'new_default': _NEW_DEFAULT,
                                       # 'set_default' : 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       # 'cont_test_params': {'heights': [120, 180]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       # 'cont_bad_map_params': {'heights': [120, 180]},
                                       # 'cont_short_map_params': {'heights': [120]},
                                       # 'disc_test_params': {'heights': [140, 190]},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       # 'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {},
                                       })

    @print_entry_exit
    def test_set_node_label_color_mapping(self):
        _NEW_DEFAULT = '#654321'
        _PASSTHRU_VAL = '#123456'
        self._check_set_node_property({'prop_func': set_node_label_color_mapping,
                                       'prop_name': 'NODE_LABEL_COLOR',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       'cont_test_params': {'colors': ['#FBE723', '#440256']},
                                       # 'cont_invalid_map_params': {'mapping_type': 'c'},
                                       'cont_bad_map_params': {'colors': ['#FBE72', '#440256']},
                                       'cont_short_map_params': {'colors': ['#440256']},
                                       'disc_test_params': {'colors': ['#FFFF00', '#00FF00'], 'mapping_type': 'd'},
                                       # 'disc_invalid_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_color': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_invalid_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_node_label_opacity_mapping(self):
        _NEW_DEFAULT = 225
        _PASSTHRU_VAL = 250
        self._check_set_node_property({'prop_func': set_node_label_opacity_mapping,
                                       'prop_name': 'NODE_LABEL_TRANSPARENCY',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       'cont_test_params': {'opacities': [50, 100]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       'cont_bad_map_params': {'opacities': [550, 100]},
                                       'cont_short_map_params': {'opacities': [50]},
                                       'disc_test_params': {'opacities': [50, 100], 'mapping_type': 'd'},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_opacity': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_node_shape_mapping(self):
        _NEW_DEFAULT = 'PARALLELOGRAM'
        # _PASSTHRU_VAL = 250
        self._check_set_node_property({'prop_func': set_node_shape_mapping,
                                       'prop_name': 'NODE_SHAPE',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'd',
                                       # 'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       # 'cont_test_params': {'opacities': [50, 100]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       # 'cont_bad_map_params': {'opacities': [550, 100]},
                                       # 'cont_short_map_params': {'opacities': [50]},
                                       'disc_test_params': {'shapes': ['OCTAGON', 'TRIANGLE'],
                                                            'default_shape': _NEW_DEFAULT},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       # 'pass_test_params': {'default_opacity': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       # 'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {},
                                       })

    @unittest.skip('Fetching NODE_SIZE always returns the default node size instead of the current node size')
    @print_entry_exit
    def test_set_node_size_mapping(self):
        _NEW_DEFAULT = 80
        _PASSTHRU_VAL = 20
        self._check_set_node_property({'prop_func': set_node_size_mapping,
                                       'prop_name': 'NODE_SIZE',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       'cont_test_params': {'sizes': [60, 100]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       # 'cont_bad_map_params': {'sizes': [120, 180]},
                                       'cont_short_map_params': {'sizes': [120]},
                                       'disc_test_params': {'sizes': [60, 80], 'mapping_type': 'd'},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_size': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_node_tooltip_mapping(self):
        # _NEW_DEFAULT = 'Test'
        _PASSTHRU_VAL = 'tooltip text'
        # TODO: This fails because of a race condition when reading the tooltip immediately after setting it
        self._check_set_node_property({'prop_func': set_node_tooltip_mapping,
                                       'prop_name': 'NODE_TOOLTIP',
                                       # 'new_default': _NEW_DEFAULT,
                                       # 'set_default' : 'p',
                                       # 'compare_tolerance_percent': 0,
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       # 'cont_test_params': {'heights': [120, 180]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       # 'cont_bad_map_params': {'heights': [120, 180]},
                                       # 'cont_short_map_params': {'heights': [120]},
                                       # 'disc_test_params': {'heights': [140, 190]},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       # 'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {},
                                       })

    @print_entry_exit
    def test_set_node_width_mapping(self):
        _NEW_DEFAULT = 120
        _PASSTHRU_VAL = 140
        self._check_set_node_property({'prop_func': set_node_width_mapping,
                                       'prop_name': 'NODE_WIDTH',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'c',
                                       'passthru_val': _PASSTHRU_VAL,
                                       'compare_tolerance_percent': 20,
                                       'cont_test_params': {'widths': [120, 180]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       # 'cont_bad_map_params': {'widths': [120, 180]},
                                       'cont_short_map_params': {'widths': [120]},
                                       'disc_test_params': {'widths': [140, 190], 'mapping_type': 'd'},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_width': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @unittest.skip('Unknown interaction between the two properties and the "Edge color to arrows" check box')
    @print_entry_exit
    def test_set_edge_color_mapping(self):
        _NEW_DEFAULT = '#654321'
        _PASSTHRU_VAL = '#123456'
        self._check_set_edge_property({'prop_func': set_edge_color_mapping,
                                       'prop_name': ['EDGE_UNSELECTED_PAINT', 'EDGE_STROKE_UNSELECTED_PAINT'],
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       'cont_test_params': {'colors': ['#FBE723', '#440256']},
                                       # 'cont_invalid_map_params': {'mapping_type': 'c'},
                                       'cont_bad_map_params': {'colors': ['#FBE72', '#440256']},
                                       'cont_short_map_params': {'colors': ['#440256']},
                                       'disc_test_params': {'colors': ['#FFFF00', '#00FF00'], 'mapping_type': 'd'},
                                       # 'disc_invalid_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_color': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_invalid_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_edge_font_face_mapping(self):
        _NEW_DEFAULT = 'Dialog.bold,bold,12'
        _PASSTHRU_VAL = 'Dialog.italic,plain,12'
        self._check_set_edge_property({'prop_func': set_edge_font_face_mapping,
                                       'prop_name': 'EDGE_LABEL_FONT_FACE',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       # 'cont_test_params': {'fonts': ['Arial,plain,12', 'Arial Bold,bold,12']},
                                       'cont_no_map_params': {'mapping_type': 'c'},
                                       # 'cont_bad_map_params': {'fonts': ['Arial bogus,plain,12', 'Arial Bold,bold,12']},
                                       # 'cont_short_map_params': {'fonts': ['Arial,plain,12']},
                                       'disc_test_params': {'fonts': ['Arial,plain,12', 'Arial Bold,bold,12'],
                                                            'mapping_type': 'd'},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_font': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_edge_font_size_mapping(self):
        _NEW_DEFAULT = 20
        _PASSTHRU_VAL = 40
        self._check_set_edge_property({'prop_func': set_edge_font_size_mapping,
                                       'prop_name': 'EDGE_LABEL_FONT_SIZE',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       'cont_test_params': {'sizes': [20, 80]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       # 'cont_bad_map_params': {'sizes': [20, 80]},
                                       'cont_short_map_params': {'sizes': [20]},
                                       'disc_test_params': {'sizes': [40, 90], 'mapping_type': 'd'},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_size': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_edge_label_mapping(self):
        # _NEW_DEFAULT = 'Test'
        _PASSTHRU_VAL = 'name'
        self._check_set_edge_property({'prop_func': set_edge_label_mapping,
                                       'prop_name': 'EDGE_LABEL',
                                       # 'new_default': _NEW_DEFAULT,
                                       # 'set_default' : 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       # 'cont_test_params': {'heights': [120, 180]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       # 'cont_bad_map_params': {'heights': [120, 180]},
                                       # 'cont_short_map_params': {'heights': [120]},
                                       # 'disc_test_params': {'heights': [140, 190]},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       # 'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {},
                                       })

    @print_entry_exit
    def test_set_edge_label_color_mapping(self):
        _NEW_DEFAULT = '#654321'
        _PASSTHRU_VAL = '#123456'
        self._check_set_edge_property({'prop_func': set_edge_label_color_mapping,
                                       'prop_name': 'EDGE_LABEL_COLOR',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       'cont_test_params': {'colors': ['#FBE723', '#440256']},
                                       # 'cont_invalid_map_params': {'mapping_type': 'c'},
                                       'cont_bad_map_params': {'colors': ['#FBE72', '#440256']},
                                       'cont_short_map_params': {'colors': ['#440256']},
                                       'disc_test_params': {'colors': ['#FFFF00', '#00FF00'], 'mapping_type': 'd'},
                                       # 'disc_invalid_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_color': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_invalid_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_edge_label_opacity_mapping(self):
        _NEW_DEFAULT = 225
        _PASSTHRU_VAL = 250
        self._check_set_edge_property({'prop_func': set_edge_label_opacity_mapping,
                                       'prop_name': 'EDGE_LABEL_TRANSPARENCY',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       'cont_test_params': {'opacities': [50, 100]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       'cont_bad_map_params': {'opacities': [550, 100]},
                                       'cont_short_map_params': {'opacities': [50]},
                                       'disc_test_params': {'opacities': [150, 200], 'mapping_type': 'd'},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_opacity': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_edge_line_style_mapping(self):
        _NEW_DEFAULT = 'EQUAL_DASH'
        # _PASSTHRU_VAL = 250
        self._check_set_edge_property({'prop_func': set_edge_line_style_mapping,
                                       'prop_name': 'EDGE_LINE_TYPE',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'd',
                                       # 'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       # 'cont_test_params': {'opacities': [50, 100]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       # 'cont_bad_map_params': {'opacities': [550, 100]},
                                       # 'cont_short_map_params': {'opacities': [50]},
                                       'disc_test_params': {'line_styles': ['ZIGZAG', 'SINEWAVE'],
                                                            'default_line_style': _NEW_DEFAULT},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       # 'pass_test_params': {'default_opacity': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       # 'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {},
                                       })

    @print_entry_exit
    def test_set_edge_line_width_mapping(self):
        _NEW_DEFAULT = 20
        _PASSTHRU_VAL = 40
        self._check_set_edge_property({'prop_func': set_edge_line_width_mapping,
                                       'prop_name': 'EDGE_WIDTH',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       'cont_test_params': {'widths': [5, 10]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       # 'cont_bad_map_params': {'width': [550, 100]}, ... no bounds checking for this property
                                       'cont_short_map_params': {'widths': [5]},
                                       'disc_test_params': {'widths': [5, 10], 'mapping_type': 'd'},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_width': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_edge_opacity_mapping(self):
        _NEW_DEFAULT = 225
        _PASSTHRU_VAL = 250
        self._check_set_edge_property({'prop_func': set_edge_opacity_mapping,
                                       'prop_name': 'EDGE_TRANSPARENCY',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       'cont_test_params': {'opacities': [50, 100]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       'cont_bad_map_params': {'opacities': [550, 100]},
                                       'cont_short_map_params': {'opacities': [50]},
                                       'disc_test_params': {'opacities': [75, 100], 'mapping_type': 'd'},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_opacity': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_edge_target_arrow_mapping(self):
        _NEW_DEFAULT = 'CIRCLE'
        # _PASSTHRU_VAL = 250
        self._check_set_edge_property({'prop_func': set_edge_target_arrow_maping,
                                       'prop_name': 'EDGE_TARGET_ARROW_SHAPE',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'd',
                                       # 'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       # 'cont_test_params': {'opacities': [50, 100]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       # 'cont_bad_map_params': {'opacities': [550, 100]},
                                       # 'cont_short_map_params': {'opacities': [50]},
                                       'disc_test_params': {'shapes': ['DIAMOND', 'CIRCLE'],
                                                            'default_shape': _NEW_DEFAULT},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       # 'pass_test_params': {'default_opacity': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       # 'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {},
                                       })

    @print_entry_exit
    def test_set_edge_source_arrow_mapping(self):
        _NEW_DEFAULT = 'CIRCLE'
        # _PASSTHRU_VAL = 250
        self._check_set_edge_property({'prop_func': set_edge_source_arrow_mapping,
                                       'prop_name': 'EDGE_SOURCE_ARROW_SHAPE',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'd',
                                       # 'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       # 'cont_test_params': {'opacities': [50, 100]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       # 'cont_bad_map_params': {'opacities': [550, 100]},
                                       # 'cont_short_map_params': {'opacities': [50]},
                                       'disc_test_params': {'shapes': ['DIAMOND', 'CIRCLE'],
                                                            'default_shape': _NEW_DEFAULT},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       # 'pass_test_params': {'default_opacity': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       # 'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {},
                                       })

    @print_entry_exit
    def test_set_edge_target_arrow_color_mapping(self):
        _NEW_DEFAULT = '#654321'
        _PASSTHRU_VAL = '#123456'
        self._check_set_edge_property({'prop_func': set_edge_target_arrow_color_mapping,
                                       'prop_name': 'EDGE_TARGET_ARROW_UNSELECTED_PAINT',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       'cont_test_params': {'colors': ['#FBE723', '#440256']},
                                       # 'cont_invalid_map_params': {'mapping_type': 'c'},
                                       'cont_bad_map_params': {'colors': ['#FBE72', '#440256']},
                                       'cont_short_map_params': {'colors': ['#440256']},
                                       'disc_test_params': {'colors': ['#FFFF00', '#00FF00'], 'mapping_type': 'd'},
                                       # 'disc_invalid_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_color': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_invalid_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_edge_source_arrow_color_mapping(self):
        _NEW_DEFAULT = '#654321'
        _PASSTHRU_VAL = '#123456'
        self._check_set_edge_property({'prop_func': set_edge_source_arrow_color_mapping,
                                       'prop_name': 'EDGE_SOURCE_ARROW_UNSELECTED_PAINT',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       'cont_test_params': {'colors': ['#FBE723', '#440256']},
                                       # 'cont_invalid_map_params': {'mapping_type': 'c'},
                                       'cont_bad_map_params': {'colors': ['#FBE72', '#440256']},
                                       'cont_short_map_params': {'colors': ['#440256']},
                                       'disc_test_params': {'colors': ['#FFFF00', '#00FF00'], 'mapping_type': 'd'},
                                       # 'disc_invalid_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_color': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_invalid_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_edge_target_arrow_color_mapping(self):
        _NEW_DEFAULT = '#654321'
        _PASSTHRU_VAL = '#123456'
        self._check_set_edge_property({'prop_func': set_edge_target_arrow_color_mapping,
                                       'prop_name': 'EDGE_TARGET_ARROW_UNSELECTED_PAINT',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'p',
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       'cont_test_params': {'colors': ['#FBE723', '#440256']},
                                       # 'cont_invalid_map_params': {'mapping_type': 'c'},
                                       'cont_bad_map_params': {'colors': ['#FBE72', '#440256']},
                                       'cont_short_map_params': {'colors': ['#440256']},
                                       'disc_test_params': {'colors': ['#FFFF00', '#00FF00'], 'mapping_type': 'd'},
                                       # 'disc_invalid_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {'default_color': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_invalid_map_params': {'mapping_type': 'p'},
                                       'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {'mapping_type': 'p'},
                                       })

    @print_entry_exit
    def test_set_edge_tooltip_mapping(self):
        # _NEW_DEFAULT = 'Test'
        _PASSTHRU_VAL = 'tooltip text'
        # TODO: This fails because of a race condition when reading the tooltip immediately after setting it
        self._check_set_edge_property({'prop_func': set_edge_tooltip_mapping,
                                       'prop_name': 'EDGE_TOOLTIP',
                                       # 'new_default': _NEW_DEFAULT,
                                       # 'set_default' : 'p',
                                       # 'compare_tolerance_percent': 0,
                                       'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       # 'cont_test_params': {'heights': [120, 180]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       # 'cont_bad_map_params': {'heights': [120, 180]},
                                       # 'cont_short_map_params': {'heights': [120]},
                                       # 'disc_test_params': {'heights': [140, 190]},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       'pass_test_params': {},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       # 'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {},
                                       })

    @print_entry_exit
    def test_set_edge_target_arrow_shape_mapping(self):
        _NEW_DEFAULT = 'CIRCLE'
        # _PASSTHRU_VAL = 250
        self._check_set_edge_property({'prop_func': set_edge_target_arrow_shape_mapping,
                                       'prop_name': 'EDGE_TARGET_ARROW_SHAPE',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'd',
                                       # 'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       # 'cont_test_params': {'opacities': [50, 100]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       # 'cont_bad_map_params': {'opacities': [550, 100]},
                                       # 'cont_short_map_params': {'opacities': [50]},
                                       'disc_test_params': {'shapes': ['DIAMOND', 'CIRCLE'],
                                                            'default_shape': _NEW_DEFAULT},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       # 'pass_test_params': {'default_opacity': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       # 'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {},
                                       })

    @print_entry_exit
    def test_set_edge_source_arrow_shape_mapping(self):
        _NEW_DEFAULT = 'CIRCLE'
        # _PASSTHRU_VAL = 250
        self._check_set_edge_property({'prop_func': set_edge_source_arrow_shape_mapping,
                                       'prop_name': 'EDGE_SOURCE_ARROW_SHAPE',
                                       'new_default': _NEW_DEFAULT,
                                       'set_default': 'd',
                                       # 'passthru_val': _PASSTHRU_VAL,
                                       # 'compare_tolerance_percent': 0,
                                       # 'cont_test_params': {'opacities': [50, 100]},
                                       # 'cont_no_map_params': {'mapping_type': 'c'},
                                       # 'cont_bad_map_params': {'opacities': [550, 100]},
                                       # 'cont_short_map_params': {'opacities': [50]},
                                       'disc_test_params': {'shapes': ['DIAMOND', 'CIRCLE'],
                                                            'default_shape': _NEW_DEFAULT},
                                       # 'disc_no_map_params': {'mapping_type': 'd'},
                                       # 'pass_test_params': {'default_opacity': _NEW_DEFAULT, 'mapping_type': 'p'},
                                       # 'pass_no_map_params': {'mapping_type': 'p'},
                                       # 'invalid_map_params': {'mapping_type': 'X'},
                                       'exception_check_params': {},
                                       })


    # Verify that current and default versions of visual property for a node can be set, and that the expected
    # errors are returned
    #
    # For explanation of 'profile' parameter, see _check_node_set_property()
    #
    def _check_set_edge_property(self, profile):
        # Initialization
        load_test_session()
        _TEST_EDGE = 'YER110C (pp) YML007W'
        _NOT_TEST_EDGE = 'YPR113W (pd) YMR043W'
        _TEST_STYLE = 'galFiltered Style'
        _CONT_COL = 'EdgeBetweenness'  # Guaranteed to exist
        _CONT_VAL_RANGE = [2.0, 20000.00]
        _DESC_COL = 'interaction'  # Guaranteed to exist
        _DESC_VAL_RANGE = ['pp', 'px']
        _PASS_COL = 'PassthruCol'  # Created for passthru test

        prop_func = profile['prop_func']
        prop_name_list = profile['prop_name'] if isinstance(profile['prop_name'], list) else [profile['prop_name']]
        orig_value_list = [get_edge_property(edge_names=[_TEST_EDGE], visual_property=prop_name)[_TEST_EDGE]
                           for prop_name in prop_name_list]

        def check_default():
            def_value_list = [get_edge_property(visual_property=prop_name)[_NOT_TEST_EDGE] for prop_name in
                              prop_name_list]
            for def_value in def_value_list:
                self._assert_equal(profile, def_value, profile['new_default'], msg='Check edge property equals default')

        # Verify that applying a continuous mapping functions
        if 'cont_test_params' in profile:
            self.assertEqual(
                prop_func(style_name=_TEST_STYLE, table_column=_CONT_COL, table_column_values=_CONT_VAL_RANGE,
                          **profile['cont_test_params']), '', msg='Check continuous mapping succeeded')
            cont_value_list = [get_edge_property(visual_property=prop_name)[_TEST_EDGE] for prop_name in prop_name_list]
            for cont_value, orig_value in zip(cont_value_list, orig_value_list):
                self.assertNotEqual(cont_value, orig_value,
                                    msg='Check continuous mapping not equal to original mapping')
            if 'set_default' in profile and profile['set_default'] == 'c': check_default()
        else:
            cont_value_list = []
            if 'cont_no_map_params' in profile:
                self.assertRaises(CyError, prop_func, style_name=_TEST_STYLE, table_column=_CONT_COL,
                                  **profile['cont_no_map_params'])

        # Verify that applying a discrete mapping functions
        if 'disc_test_params' in profile:
            self.assertEqual(
                prop_func(style_name=_TEST_STYLE, table_column=_DESC_COL, table_column_values=_DESC_VAL_RANGE,
                          **profile['disc_test_params']), '', msg='Check discrete mapping succeeded')
            disc_value_list = [get_edge_property(visual_property=prop_name)[_TEST_EDGE] for prop_name in prop_name_list]
            for disc_value, orig_value in zip(disc_value_list, orig_value_list):
                self.assertNotEqual(disc_value, orig_value, msg='Check discrete mapping not equal to original mapping')
            for disc_value, cont_value in zip(disc_value_list, cont_value_list):
                self.assertNotEqual(disc_value, cont_value,
                                    msg='Check discrete mapping not equal to continuous mapping')
            if 'set_default' in profile and profile['set_default'] == 'd': check_default()
        elif 'disc_no_map_params' in profile:
            self.assertRaises(CyError, prop_func, style_name=_TEST_STYLE, table_column=_DESC_COL,
                              **profile['disc_no_map_params'])

        # Create a column containing values, then verify that a passthru mapping causes a new value and new default value
        if 'pass_test_params' in profile:
            data = df.DataFrame(data={'id': [_TEST_EDGE], _PASS_COL: [profile['passthru_val']]})
            load_table_data(data, data_key_column='id', table='edge', table_key_column='name')
            self.assertEqual(prop_func(style_name=_TEST_STYLE, table_column=_PASS_COL, **profile['pass_test_params']),
                             '', msg='Check passthru mapping succeeded')
            pass_value_list = [get_edge_property(visual_property=prop_name)[_TEST_EDGE] for prop_name in prop_name_list]
            for pass_value in pass_value_list:
                self.assertEqual(pass_value, profile['passthru_val'], msg='Check node property equals passthru mapping')
            if 'set_default' in profile and profile['set_default'] == 'p': check_default()
        elif 'pass_no_map_params' in profile:
            self.assertRaises(CyError, prop_func, style_name=_TEST_STYLE, table_column=_CONT_COL,
                              **profile['pass_no_map_params'])

        # Verify that a bad value is caught
        if 'cont_bad_map_params' in profile:
            self.assertIsNone(
                prop_func(style_name=_TEST_STYLE, table_column=_CONT_COL, table_column_values=_CONT_VAL_RANGE,
                          **profile['cont_bad_map_params']), msg='Check bad continuous value')

        # Verify that a bad mapping type is caught
        if 'invalid_map_params' in profile:
            self.assertIsNone(
                prop_func(style_name=_TEST_STYLE, table_column=_PASS_COL, **profile['invalid_map_params']),
                msg='Check bad mapping type')

        # Verify that a bad column name is caught
        self.assertRaises(CyError, prop_func, style_name=_TEST_STYLE, table_column='Bogus Col',
                          **profile['exception_check_params'])

        # Verify that a bad style name is caught
        self.assertRaises(CyError, prop_func, style_name='Bogus Style', table_column=_PASS_COL,
                          **profile['exception_check_params'])

        # Verify that that a short mapping is caught
        if 'cont_short_map_params' in profile:
            self.assertRaises(CyError, prop_func, style_name=_TEST_STYLE, table_column=_CONT_COL,
                              table_column_values=_CONT_VAL_RANGE, **profile['cont_short_map_params'])

        # Verify that a bad network is caught
        self.assertRaises(CyError, prop_func, style_name=_TEST_STYLE, table_column=_PASS_COL,
                          **profile['exception_check_params'], network='bogus network')

    # Verify that current and default versions of visual property for a node can be set, and that the expected
    # errors are returned
    #
    # profile is a dict that drives the test. Field values:
    # {
    # 'prop_func': name of function that sets node visual property
    # 'prop_name': name of visual property to set
    # 'new_default': value to set as new default ... type matches visual property
    # 'set_default': type of mapping to use for testing that default is set properly (e.g., 'c', 'd', or 'p)
    # 'passthru_val': for a passthru mapping, the value to put into the passthru column ... type matches property
    # 'compare_tolerance_percent': for numeric properties that Cytoscape calculates,
    #       tolerance for Cytoscape's value matching expected 'new_default'
    # 'cont_test_params': parameter to pass for a 'c' mapping when 'c' is available ... usually includes the range
    #       of mapped values. e.g., {'colors': ['#FBE723', '#440256']}
    # 'cont_no_map_params': parameter to pass for verifying that 'c' is unavailable and trying to map 'c' should
    #       result in an error. e.g., {'mapping_type': 'c'}
    # 'cont_bad_map_params': parameter to pass for verifying that parameter values are checked when 'c' is available.
    #       Should result in an error. e.g., {'colors': ['#FBE72', '#440256']},
    # 'cont_short_map_params': parameter to pass for verifying that parameter values are checked when 'c' is available.
    #       Should result in an error. e.g., {'colors': ['#440256']} when two table_column_values are provided.
    # 'disc_test_params': parameter to pass for a 'd' mapping when 'd' is available ... usually includes the list
    #       of mapped values. e.g., {'colors': ['#FFFF00', '#00FF00'], 'mapping_type': 'd'},
    # 'disc_no_map_params': parameter to pass for verifying that 'd' is unavailable and trying to map 'd' should
    #       result in an error. e.g., {'mapping_type': 'd'},
    # 'pass_test_params': parameter to pass for a 'p' mapping when 'p' is available ... usually includes the default
    #       value when the default can be set. e.g., {'default_color': _NEW_DEFAULT, 'mapping_type': 'p'},
    # 'pass_no_map_params': parameter to pass for verifying that 'p' is unavailable and trying to map 'p' should
    #       result in an error. e.g., {'mapping_type': 'p'},
    # 'invalid_map_params': parameter to pass to verify that an invalid mapping is caught. e.g., {'mapping_type': 'X'},
    # 'exception_check_params': parameter to pass when checking for various kinds of exceptions. e.g., {'mapping_type': 'p'},
    # }
    def _check_set_node_property(self, profile):
        # Initialization
        load_test_session()
        _TEST_NODE = 'YML007W'
        _NOT_TEST_NODE = 'YGL035C'
        _TEST_STYLE = 'galFiltered Style'
        _CONT_COL = 'AverageShortestPathLength'  # Guaranteed to exist
        _CONT_VAL_RANGE = [1.0, 16.36]
        _DESC_COL = 'Degree'  # Guaranteed to exist
        _DESC_VAL_RANGE = ['1', '2']
        _PASS_COL = 'PassthruCol'  # Created for passthru test

        prop_func = profile['prop_func']
        prop_name_list = profile['prop_name'] if isinstance(profile['prop_name'], list) else [profile['prop_name']]
        orig_value_list = [get_node_property(node_names=[_TEST_NODE], visual_property=prop_name)[_TEST_NODE]
                           for prop_name in prop_name_list]

        def check_default():
            def_value_list = [get_node_property(visual_property=prop_name)[_NOT_TEST_NODE] for prop_name in
                              prop_name_list]
            for def_value in def_value_list:
                self._assert_equal(profile, def_value, profile['new_default'], msg='Check node property equals default')

        # Verify that applying a continuous mapping functions
        if 'cont_test_params' in profile:
            self.assertEqual(
                prop_func(style_name=_TEST_STYLE, table_column=_CONT_COL, table_column_values=_CONT_VAL_RANGE,
                          **profile['cont_test_params']), '',
                msg='Check continuous mapping succeeded')
            cont_value_list = [get_node_property(visual_property=prop_name)[_TEST_NODE] for prop_name in prop_name_list]
            for cont_value, orig_value in zip(cont_value_list, orig_value_list):
                self.assertNotEqual(cont_value, orig_value,
                                    msg='Check continuous mapping not equal to original mapping')
            if 'set_default' in profile and profile['set_default'] == 'c': check_default()
        else:
            cont_value_list = []
            if 'cont_no_map_params' in profile:
                self.assertRaises(CyError, prop_func, style_name=_TEST_STYLE, table_column=_CONT_COL,
                                  **profile['cont_no_map_params'])

        # Verify that applying a discrete mapping functions
        if 'disc_test_params' in profile:
            self.assertEqual(
                prop_func(style_name=_TEST_STYLE, table_column=_DESC_COL, table_column_values=_DESC_VAL_RANGE,
                          **profile['disc_test_params']), '', msg='Check discrete mapping succeeded')
            disc_value_list = [get_node_property(visual_property=prop_name)[_TEST_NODE] for prop_name in prop_name_list]
            for disc_value, orig_value in zip(disc_value_list, orig_value_list):
                self.assertNotEqual(disc_value, orig_value, msg='Check discrete mapping not equal to original mapping')
            for disc_value, cont_value in zip(disc_value_list, cont_value_list):
                self.assertNotEqual(disc_value, cont_value,
                                    msg='Check discrete mapping not equal to continuous mapping')
            if 'set_default' in profile and profile['set_default'] == 'd': check_default()
        elif 'disc_no_map_params' in profile:
            self.assertRaises(CyError, prop_func, style_name=_TEST_STYLE, table_column=_DESC_COL,
                              **profile['disc_no_map_params'])

        # Create a column containing values, then verify that a passthru mapping causes a new value and new default value
        if 'pass_test_params' in profile:
            data = df.DataFrame(data={'id': [_TEST_NODE], _PASS_COL: [profile['passthru_val']]})
            load_table_data(data, data_key_column='id', table='node', table_key_column='name')
            self.assertEqual(prop_func(style_name=_TEST_STYLE, table_column=_PASS_COL, **profile['pass_test_params']),
                             '',
                             msg='Check passthru mapping succeeded')
            pass_value_list = [get_node_property(visual_property=prop_name)[_TEST_NODE] for prop_name in prop_name_list]
            for pass_value in pass_value_list:
                self.assertEqual(pass_value, profile['passthru_val'], msg='Check node property equals passthru mapping')
            if 'set_default' in profile and profile['set_default'] == 'p': check_default()
        elif 'pass_no_map_params' in profile:
            self.assertRaises(CyError, prop_func, style_name=_TEST_STYLE, table_column=_CONT_COL,
                              **profile['pass_no_map_params'])

        # Verify that a bad value is caught
        if 'cont_bad_map_params' in profile:
            self.assertIsNone(
                prop_func(style_name=_TEST_STYLE, table_column=_CONT_COL, table_column_values=_CONT_VAL_RANGE,
                          **profile['cont_bad_map_params']),
                msg='Check bad continuous value')

        # Verify that a bad mapping type is caught
        if 'invalid_map_params' in profile:
            self.assertIsNone(
                prop_func(style_name=_TEST_STYLE, table_column=_PASS_COL, **profile['invalid_map_params']),
                msg='Check bad mapping type')

        # Verify that a bad column name is caught
        self.assertRaises(CyError, prop_func, style_name=_TEST_STYLE, table_column='Bogus Col',
                          **profile['exception_check_params'])

        # Verify that a bad style name is caught
        self.assertRaises(CyError, prop_func, style_name='Bogus Style', table_column=_PASS_COL,
                          **profile['exception_check_params'])

        # Verify that that a short mapping is caught
        if 'cont_short_map_params' in profile:
            self.assertRaises(CyError, prop_func, style_name=_TEST_STYLE, table_column=_CONT_COL,
                              table_column_values=_CONT_VAL_RANGE, **profile['cont_short_map_params'])

        # Verify that a bad network is caught
        self.assertRaises(CyError, prop_func, style_name=_TEST_STYLE, table_column=_PASS_COL,
                          **profile['exception_check_params'], network='bogus network')

    def _assert_equal(self, profile, def_value, expected_value, msg):
        if 'compare_tolerance_percent' in profile:
            tolerance = float(profile['compare_tolerance_percent']) / 100
            self.assertGreaterEqual(def_value, expected_value * (1 - tolerance), msg=msg)
            self.assertLessEqual(def_value, expected_value * (1 + tolerance), msg=msg)
        else:
            self.assertEqual(def_value, expected_value, msg=msg)

    # Verify that a visual property map is constructed as expected.
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
