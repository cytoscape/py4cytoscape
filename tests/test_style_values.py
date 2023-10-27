# -*- coding: utf-8 -*-

""" Test functions in styles_values.py.
"""

"""License:
    Copyright 2020-2022 The Cytoscape Consortium

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


class StyleValuesTests(unittest.TestCase):
    def setUp(self):
        try:
            close_session(False)
#            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    _TEST_STYLE = 'galFiltered Style'

    @print_entry_exit
    def test_get_node_property(self):
        # Initialization
        load_test_session()

        self._check_get_property(get_node_property, 'node_names', 'node', 'NODE_LABEL', 'COMMON', 'YER112W', 'LSM4')

    @print_entry_exit
    def test_get_edge_property(self):
        # Initialization
        load_test_session()
        update_style_mapping(style_name=self._TEST_STYLE, mapping=map_visual_property(visual_prop='EDGE_LABEL', table_column='interaction', mapping_type='p'))

        self._check_get_property(get_edge_property, 'edge_names', 'edge', 'EDGE_LABEL', 'interaction', 'YDR277C (pp) YJR022W', 'pp')

    @print_entry_exit
    def test_get_network_property(self):
        # Initialization
        load_test_session()

        scale_prop = get_network_property('NETWORK_SCALE_FACTOR')
        self.assertIsInstance(scale_prop, float)

        self.assertRaises(CyError, get_network_property, None)
        self.assertRaises(CyError, get_network_property, 'BogusProperty')
        self.assertRaises(CyError, get_network_property, 'NETWORK_SCALE_FACTOR', network='BogusNetwork')

    @print_entry_exit
    def test_get_node_color(self):
        # Initialization
        load_test_session()

        self._check_get_property(get_node_color, 'node_names', 'node', None, None, 'YER112W', '#FFFFE7')

    @print_entry_exit
    def test_get_node_size(self):
        # Initialization
        load_test_session()

        self._check_get_property(get_node_size, 'node_names', 'node', None, None, 'YER112W', 46.470588235294116)

    @print_entry_exit
    def test_get_node_width(self):
        # Initialization
        load_test_session()

        self._check_get_property(get_node_width, 'node_names', 'node', None, None, 'YER112W', 46.470588235294116)

    @print_entry_exit
    def test_get_node_height(self):
        # Initialization
        load_test_session()

        self._check_get_property(get_node_height, 'node_names', 'node', None, None, 'YER112W', 46.470588235294116)

    @print_entry_exit
    def test_get_node_position(self):
        # Initialization
        load_test_session()
        all_node_names = get_table_columns(columns=['name'])

        def check_position_table(position_df, node_id_set):
            # Verify that all nodes are present
            self.assertSetEqual(set(position_df.index), node_id_set)
            # Verify that the table has exactly the 'x' and 'y' columns
            self.assertSetEqual(set(position_df), {'x', 'y'})

       # Verify that getting positions for all nodes works
        check_position_table(get_node_position(), set(all_node_names['name']))

        # Verify that getting positions for all nodes works when nodes are named
        check_position_table(get_node_position(list(all_node_names['name'])), set(all_node_names['name']))

        # Verify that getting positions for all nodes works when identified by SUIDs
        check_position_table(get_node_position(list(all_node_names.index)), set(all_node_names.index))

        # Verify that getting positions for all nodes works when identified by SUIDs
        check_position_table(get_node_position('YER112W'), {'YER112W'})

        # Verify that bad property, node/edge name or network is caught
        self.assertRaises(CyError, get_node_position, ['bogusName'])
        self.assertRaises(CyError, get_node_position, network='BogusNetwork')


    @print_entry_exit
    def test_get_set_node_label_position(self):
        # Yes, this tests set_node_label_position_bypass(), too ... normally, we would do this in test_style_bypass.py,
        # but it's very convenient to do it in conjunction with get_node_label_position()
        ORIG_VALUE = 'C,C,c,0.00,0.00'
        TEST_NODE_A = 'YDL194W'
        NEW_VALUE_0 = 'N,E,l,100.00,-200.00'
        NEW_VALUE_1 = 'W,N,r,-100.00,200.00'

        # Initialization
        load_test_session()
        test_node_A_suid = node_name_to_node_suid(TEST_NODE_A)[0]
        all_node_names_suids = get_table_columns(columns=['name'])
        all_node_names = list(all_node_names_suids['name'])
        all_node_suids = list(all_node_names_suids.index)
        orig_node_values = {node: ORIG_VALUE  for node in all_node_names}
        new_node_values_0 = {node: NEW_VALUE_0  for node in all_node_names}
        new_suid_values_1 = {node: NEW_VALUE_1  for node in all_node_suids}

        def check_position_table(node_list, expected_nodes):
            # Verify that all nodes are present
            self.assertSetEqual(set(node_list), set(expected_nodes))

            # Verify that each position is as expected
            for name in node_list:
                self.assertEqual(node_list[name], expected_nodes[name])

        # Verify that fetching node label position for all nodes works
        check_position_table(get_node_label_position(), orig_node_values)

        # Verify that setting/fetching node label position for single node (by name) works
        set_node_label_position_bypass(TEST_NODE_A, NEW_VALUE_0)
        check_position_table(get_node_label_position(TEST_NODE_A), {TEST_NODE_A: NEW_VALUE_0})

        # Verify that no other label positions are updated
        orig_node_values_0 = orig_node_values.copy()
        orig_node_values_0[TEST_NODE_A] = NEW_VALUE_0
        check_position_table(get_node_label_position(), orig_node_values_0)

        # Verify that fetching node label position for single node (by suid) works
        set_node_label_position_bypass(test_node_A_suid, NEW_VALUE_1)
        check_position_table(get_node_label_position(test_node_A_suid), {test_node_A_suid: NEW_VALUE_1})

        # Verify that setting/fetching node label position for list of nodes (by name) works
        set_node_label_position_bypass(all_node_names, NEW_VALUE_0)
        check_position_table(get_node_label_position(all_node_names), new_node_values_0)

        # Verify that setting/fetching node label position for list of nodes (by suid) works
        set_node_label_position_bypass(all_node_suids, NEW_VALUE_1)
        check_position_table(get_node_label_position(all_node_suids), new_suid_values_1)

        # Verify that bad node name or network is caught
        self.assertRaises(CyError, get_node_label_position, 'bogusName')
        self.assertRaises(CyError, get_node_label_position, network='BogusNetwork')


    @print_entry_exit
    def test_get_edge_line_width(self):
        # Initialization
        load_test_session()

        self._check_get_property(get_edge_line_width, 'edge_names', 'edge', None, None, 'YOR355W (pp) YNL091W', 2.0)

    @print_entry_exit
    def test_get_edge_color(self):
        # Initialization
        load_test_session()

        self._check_get_property(get_edge_color, 'edge_names', 'edge', None, None, 'YOR355W (pp) YNL091W', '#808080')

    @print_entry_exit
    def test_get_edge_line_style(self):
        # Initialization
        load_test_session()

        self._check_get_property(get_edge_line_style, 'edge_names', 'edge', None, None, 'YOR355W (pp) YNL091W', 'SOLID')

    @print_entry_exit
    def test_get_edge_target_arrow(self):
        # Initialization
        load_test_session()

        self._check_get_property(get_edge_target_arrow_shape, 'edge_names', 'edge', None, None, 'YOR355W (pp) YNL091W', 'NONE')

    @print_entry_exit
    def test_get_network_center(self):
        # Initialization
        load_test_session()

        # Verify that the proper dict is returned
        res = get_network_center()
        self.assertIsInstance(res, dict)
        self.assertEqual(len(res), 2)
        self.assertIn('x', res)
        self.assertIsInstance(res['x'], float)
        self.assertIn('y', res)
        self.assertIsInstance(res['y'], float)

        # Verify that a bad network is caught
        self.assertRaises(CyError, get_network_center, network='BogusNetwork')

    @print_entry_exit
    def test_get_network_zoom(self):
        # Initialization
        load_test_session()

        # Verify that the proper type is returned
        res = get_network_zoom()
        self.assertIsInstance(res, float)

        # Verify that a bad network is caught
        self.assertRaises(CyError, get_network_zoom, network='BogusNetwork')

    def _check_get_property(self, getter_func, names_param, table, visual_property, data_column, single_name, single_value):
        # Create various flavors of parameter lists for getter_func, including lists and string lists of names and suids
        if data_column is None:
            all_names = get_table_columns(columns=['name'], table=table)
        else:
            all_names = get_table_columns(columns=['name', data_column], table=table)
        prop_param = {} if visual_property is None else {'visual_property': visual_property}
        all_names_param = {names_param: list(all_names['name'])}
        all_names_str_param = {names_param: ','.join(list(all_names['name']))}
        all_suids_param = {names_param: list(all_names.index)}
        all_suids_str_param = {names_param: str(list(all_names.index))[1:-1]}
        prop_names_params = all_names_param.copy()
        prop_names_params.update(prop_param)
        prop_names_str_params = all_names_str_param.copy()
        prop_names_str_params.update(prop_param)
        prop_suids_params = all_suids_param.copy()
        prop_suids_params.update(prop_param)
        prop_suids_str_params = all_suids_str_param.copy()
        prop_suids_str_params.update(prop_param)
        single_name_params = {names_param: single_name}
        single_name_params.update(prop_param)

        # Verify that visual properties can be returned for all nodes/edges
        name_value_dict = getter_func(**prop_param)
        self.assertIsInstance(name_value_dict, dict)
        self.assertEqual(len(name_value_dict), len(all_names.index))
        if data_column is not None:
            name_found = [name in name_value_dict and value == name_value_dict[name]     for name, value in zip(all_names['name'], all_names[data_column])]
            self.assertFalse(False in name_found)

        # Verify that the same visual properties are returned when the nodes/edges are identified by name list
        by_name_dict = getter_func(**prop_names_params)
        self.assertDictEqual(by_name_dict, name_value_dict)

        # Verify that the same visual properties are returned when the nodes/edges are identified by string name list
        by_name_dict = getter_func(**prop_names_str_params)
        self.assertDictEqual(by_name_dict, name_value_dict)

        # Verify that the same visual properties are returned when nodes/edges are identified by SUID
        # This means looking the SUID up in the all_names table, getting the name, and then using prior test's result
        by_suid_dict = getter_func(**prop_suids_params)
        suid_found = [by_suid_dict[suid] == name_value_dict[all_names['name'][suid]]   for suid in by_suid_dict]
        self.assertFalse(False in suid_found)

        # Verify that the same visual properties are returned when nodes/edges are identified by string SUID list
        # This means looking the SUID up in the all_names table, getting the name, and then using prior test's result
        by_suid_dict = getter_func(**prop_suids_str_params)
        suid_found = [by_suid_dict[suid] == name_value_dict[all_names['name'][suid]]   for suid in by_suid_dict]
        self.assertFalse(False in suid_found)

        # Verify that the right node and visual property are returned when nodes/edges name is a string
        by_str_dict = getter_func(**single_name_params)
        self.assertDictEqual(by_str_dict, {single_name: single_value})

        # Verify that bad property, node/edge name or network is caught
        if visual_property is not None:
            self.assertRaises(CyError, getter_func, **{names_param: single_name})
            self.assertRaises(CyError, getter_func, visual_property=visual_property, **{names_param: 'bogusName'})
            self.assertRaises(CyError, getter_func, visual_property='BogusProperty', **{names_param: single_name})
        self.assertRaises(CyError, getter_func, **{names_param: single_name}, network='BogusNetwork')



if __name__ == '__main__':
    unittest.main()
