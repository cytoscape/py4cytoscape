# -*- coding: utf-8 -*-

import unittest
from test_utils import *
from PyCy3 import *
from PyCy3.pycy3_utils import DEFAULT_BASE_URL, build_url, node_suid_to_node_name, node_name_to_node_suid, edge_name_to_edge_suid
from PyCy3.decorators import *

class PyCy3Tests(unittest.TestCase):

    def setUp(self):
        try:
            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    @print_entry_exit
    def test_build_url(self):
        self.assertEqual(build_url(DEFAULT_BASE_URL), DEFAULT_BASE_URL)
        self.assertEqual(build_url(DEFAULT_BASE_URL,'command test'), DEFAULT_BASE_URL + '/command%20test')

    @print_entry_exit
    def test_node_suid_to_node_name(self):
        # Initialization
        load_test_session()

        suid_name_map = tables.get_table_columns().loc[:, 'name']
        index = list(suid_name_map.index)
        values = list(suid_name_map.values)
        node_names = ['YBR043C', 'YPR145W', 'YDR277C']
        suids = [index[values.index(x)] for x in node_names]
        suids_with_name = suids.copy()
        suids_with_name.append('YBR043C')
        suids_with_none = suids.copy()
        suids_with_none.append(None)

        self.assertEqual(node_suid_to_node_name(None), None)
        self.assertEqual(node_suid_to_node_name(node_names), node_names)
        self.assertRaises(CyError, node_suid_to_node_name, ['YBR043C', 'junk', 'YDR277C'])
        self.assertRaises(CyError, node_suid_to_node_name, suids_with_name)
        self.assertEqual(node_suid_to_node_name(suids), node_names)
        self.assertRaises(CyError, node_suid_to_node_name, suids_with_none)

    @print_entry_exit
    def test_node_name_to_node_suid(self):
        # Initialization
        load_test_session()

        suid_name_map = tables.get_table_columns(table='node').loc[:, 'name']
        index = list(suid_name_map.index)
        values = list(suid_name_map.values)
        node_names = ['YBR043C', 'YPR145W', 'YDR277C']
        suids = [index[values.index(x)] for x in node_names]
        suids_with_name = suids.copy()
        suids_with_name.append('YBR043C')
        names_with_none = node_names.copy()
        names_with_none.append(None)

        self.assertEqual(node_name_to_node_suid(None), None)
        self.assertEqual(node_name_to_node_suid(node_names), suids)
        self.assertRaises(CyError, node_name_to_node_suid, ['YBR043C', 'junk', 'YDR277C'])
        self.assertRaises(CyError, node_name_to_node_suid, suids_with_name)
        self.assertEqual(node_name_to_node_suid(suids), suids)
        self.assertRaises(CyError, node_name_to_node_suid, names_with_none)

        suid_dup = add_cy_nodes(['YGR009C'], skip_duplicate_names=False) #SUID 188
        res = node_name_to_node_suid(['YGR009C'])
        self.assertIsInstance(res[0], list)
        self.assertEqual(len(res), 1)
        self.assertGreaterEqual(len(res[0]), 2)
        self.assertIn(suid_dup[0]['SUID'], res[0])

    @print_entry_exit
    def test_edge_name_to_edge_suid(self):
        # Initialization
        load_test_session()

        suid_name_map = tables.get_table_columns(table='edge').loc[:, 'name']
        index = list(suid_name_map.index)
        values = list(suid_name_map.values)
        edge_names = ['YDR277C (pp) YDL194W', 'YDR277C (pp) YJR022W', 'YPR145W (pp) YMR117C']
        suids = [index[values.index(x)] for x in edge_names]
        suids_with_name = suids.copy()
        suids_with_name.append('YER054C (pp) YBR045C')
        names_with_none = edge_names.copy()
        names_with_none.append(None)

        self.assertEqual(edge_name_to_edge_suid(None), None)
        self.assertEqual(edge_name_to_edge_suid(edge_names), suids)
        self.assertRaises(CyError, edge_name_to_edge_suid, ['YDR277C (pp) YDL194W', 'junk', 'YPR145W (pp) YMR117C'])
        self.assertRaises(CyError, edge_name_to_edge_suid, suids_with_name)
        self.assertEqual(edge_name_to_edge_suid(suids), suids)
        self.assertRaises(CyError, edge_name_to_edge_suid, names_with_none)

if __name__ == '__main__':
    unittest.main()


