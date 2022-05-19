# -*- coding: utf-8 -*-

""" Test functions in py4cytoscape_utils.py.
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
from test_utils import *

class Py4cytoscapeUtilsTests(unittest.TestCase):

    def setUp(self):
        try:
            close_session(False)
#            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    @print_entry_exit
    def test_build_url(self):
        self.assertEqual(build_url(DEFAULT_BASE_URL), DEFAULT_BASE_URL)
        self.assertEqual(build_url(DEFAULT_BASE_URL, 'command test'), DEFAULT_BASE_URL + '/command%20test')

    @print_entry_exit
    def test_node_suid_to_node_name(self):
        # Initialization
        load_test_session()

        suid_name_map = get_table_columns().loc[:, 'name']
        index = list(suid_name_map.index)
        values = list(suid_name_map.values)
        node_names = ['YBR043C', 'YPR145W', 'YDR277C']
        suids = [index[values.index(x)] for x in node_names]
        suids_with_name = suids.copy()
        suids_with_name.append('YBR043C')
        suids_with_none = suids.copy()
        suids_with_none.append(None)

        self.assertEqual(node_suid_to_node_name(None), None)

        # Verify that list of node names is translated to the same list
        self.assertEqual(node_suid_to_node_name(node_names), node_names)

        # Verify that string list of node names is translated to the same list
        self.assertEqual(node_suid_to_node_name(', '.join(node_names)), node_names)

        # Verify that single node name string is translated to itself
        self.assertEqual(node_suid_to_node_name(node_names[0]), [node_names[0]])

        # Verify that list of SUIDs is translated to right node names
        self.assertEqual(node_suid_to_node_name(suids), node_names)

        # Verify that string list of SUIDs is translated to right node names
        self.assertEqual(node_suid_to_node_name(str(suids)[1:-1]), node_names)

        # Verify that single SUID is translated to right node name
        self.assertEqual(node_suid_to_node_name(suids[0]), [node_names[0]])

        self.assertRaises(CyError, node_suid_to_node_name, ['YBR043C', 'junk', 'YDR277C'])
        self.assertRaises(CyError, node_suid_to_node_name, suids_with_name)
        self.assertRaises(CyError, node_suid_to_node_name, suids_with_none)

    @print_entry_exit
    def test_node_name_to_node_suid(self):
        # Initialization
        load_test_session()

        # Get list of all SUIDs and all node names
        suid_name_map = get_table_columns(table='node').loc[:, 'name']
        index = list(suid_name_map.index)
        values = list(suid_name_map.values)
        # Get list of interesting node names
        node_names = ['YBR043C', 'YPR145W', 'YDR277C']
        # Get list of SUIDs for those node names (e.g., [832759, 832761, 832757])
        suids = [index[values.index(x)] for x in node_names]
        # Get the string version of the SUID list (e.g., '832759, 832761, 832757')
        suids_str = str(suids)[1:-1]
        # Get a list of SUIDs followed by a node name (e.g., [832759, 832761, 832757, 'YBR043C'])
        suids_with_name = suids.copy()
        suids_with_name.append('YBR043C')
        # Get a list of names followed by a bad name None (e.g., ['YBR043C', 'YPR145W', 'YDR277C', None])
        names_with_none = node_names.copy()
        names_with_none.append(None)

        self.assertEqual(node_name_to_node_suid(None), None)
        self.assertEqual(node_name_to_node_suid(node_names), suids) # try list of node names
        self.assertEqual(node_name_to_node_suid(', '.join(node_names)), suids) # try string list of node names
        self.assertEqual(node_name_to_node_suid(node_names[0]), [suids[0]]) # try just a single node name
        self.assertRaises(CyError, node_name_to_node_suid, ['YBR043C', 'junk', 'YDR277C']) # try bad node name
        self.assertRaises(CyError, node_name_to_node_suid, ['YBR043C', 'junk', 'YDR277C'], unique_list=True) # try bad node name
        self.assertRaises(CyError, node_name_to_node_suid, suids_with_name) # try comparing to known-incorrect list
        self.assertEqual(node_name_to_node_suid(suids), suids) # try list of node SUIDs
        self.assertRaises(CyError, node_name_to_node_suid, names_with_none) # try bad node SUID
        self.assertEqual(node_name_to_node_suid(suids_str), suids) # try string list of node SUIDs
        self.assertEqual(node_name_to_node_suid(suids[0]), [suids[0]]) # try just a single node SUID

        # Verify that when there are two of the same-named nodes, one of their SUIDs is returned if one node is queried
        suid_orig = index[values.index('YGR009C')]
        suid_dup = add_cy_nodes(['YGR009C'], skip_duplicate_names=False)[0]['SUID']
        res = node_name_to_node_suid(['YGR009C'], unique_list=True)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        self.assertIn(res[0], {suid_orig, suid_dup})

        # Verify that when there are two of the same-named nodes, both of their SUIDs are returned if both nodes are queried
        res = node_name_to_node_suid(['YGR009C', 'YGR009C'], unique_list=True)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 2)
        self.assertSetEqual(set(res), {suid_orig, suid_dup})

        # Verify that when there are two of the same-named nodes, an error occurs if we ask for three nodes
        self.assertRaises(CyError, node_name_to_node_suid, ['YGR009C', 'YGR009C', 'YGR009C'], unique_list=True)

        # Verify that when there are two of the same-named nodes and node list is declared non-unique, a list of all same-named nodes is returned
        res = node_name_to_node_suid(['YGR009C', 'YGR009C', 'YGR009C'], unique_list=False)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 3)
        for suid_list in res:
            self.assertIsInstance(suid_list, list)
            self.assertEqual(len(suid_list), 2)
            self.assertSetEqual(set(suid_list), {suid_orig, suid_dup})

        self.assertEqual(node_name_to_node_suid(node_names[0], unique_list=False), [suids[0]]) # try just a single node name, list declared non-unique


    @print_entry_exit
    def test_edge_suid_to_edge_name(self):
        # Initialization
        load_test_session()

        suid_name_map = get_table_columns().loc[:, 'name']
        index = list(suid_name_map.index)
        values = list(suid_name_map.values)
        node_names = ['YBR043C', 'YPR145W', 'YDR277C']
        suids = [index[values.index(x)] for x in node_names]
        suids_with_name = suids.copy()
        suids_with_name.append('YBR043C')
        suids_with_none = suids.copy()
        suids_with_none.append(None)

        suid_name_map = get_table_columns(table='edge').loc[:, 'name']
        index = list(suid_name_map.index)
        values = list(suid_name_map.values)
        edge_name_str = 'YDR277C (pp) YDL194W, YDR277C (pp) YJR022W, YPR145W (pp) YMR117C'
        edge_names = str.split(edge_name_str, ', ')
        suids = [index[values.index(x)] for x in edge_names]
        suids_with_name = suids.copy()
        suids_with_name.append('YER054C (pp) YBR045C')
        names_with_none = edge_names.copy()
        names_with_none.append(None)

        self.assertEqual(edge_suid_to_edge_name(None), None)

        # Verify that list of edge names is translated to the same list
        self.assertEqual(edge_suid_to_edge_name(edge_names), edge_names)

        # Verify that string list of edge names is translated to the same list
        self.assertEqual(edge_suid_to_edge_name(', '.join(edge_names)), edge_names)

        # Verify that single edge name string is translated to itself
        self.assertEqual(edge_suid_to_edge_name(edge_names[0]), [edge_names[0]])

        # Verify that list of SUIDs is translated to right edge names
        self.assertEqual(edge_suid_to_edge_name(suids), edge_names)

        # Verify that string list of SUIDs is translated to right edge names
        self.assertEqual(edge_suid_to_edge_name(str(suids)[1:-1]), edge_names)

        # Verify that single SUID is translated to right edge name
        self.assertEqual(edge_suid_to_edge_name(suids[0]), [edge_names[0]])

        self.assertRaises(CyError, edge_suid_to_edge_name, ['YBR043C', 'junk', 'YDR277C'])
        self.assertRaises(CyError, edge_suid_to_edge_name, suids_with_name)
        self.assertRaises(CyError, edge_suid_to_edge_name, suids_with_none)

    @print_entry_exit
    def test_edge_name_to_edge_suid(self):
        # Initialization
        load_test_session()

        # Get list of all SUIDs and all edge names
        suid_name_map = get_table_columns(table='edge').loc[:, 'name']
        index = list(suid_name_map.index)
        values = list(suid_name_map.values)
        # Get list of interesting edge names
        edge_name_str = 'YDR277C (pp) YDL194W, YDR277C (pp) YJR022W, YPR145W (pp) YMR117C'
        edge_names = str.split(edge_name_str, ', ')
        # Get list of SUIDs for those edge names (e.g., [879268, 879270, 879272])
        suids = [index[values.index(x)] for x in edge_names]
        # Get the string version of the SUID list (e.g., '879268, 879270, 879272')
        suids_str = str(suids)[1:-1]
        # Get a list of SUIDs followed by a edge name (e.g., [879268, 879270, 879272, 'YER054C (pp) YBR045C'])
        suids_with_name = suids.copy()
        suids_with_name.append('YER054C (pp) YBR045C')
        # Get a list of names followed by a bad name None (e.g., ['YDR277C (pp) YDL194W', 'YDR277C (pp) YJR022W', 'YPR145W (pp) YMR117C', None])
        names_with_none = edge_names.copy()
        names_with_none.append(None)

        self.assertEqual(edge_name_to_edge_suid(None), None)

        # Verify that list of edge names is translated to SUIDs
        self.assertEqual(edge_name_to_edge_suid(edge_names), suids)

        # Verify that string list of edge names is translated to SUIDS
        self.assertEqual(edge_name_to_edge_suid(', '.join(edge_names)), suids)

        # Verify that single edge name is translated to its SUID
        self.assertEqual(edge_name_to_edge_suid(edge_names[0]), [suids[0]])

        # Verify that a bad edge name is caught
        self.assertRaises(CyError, edge_name_to_edge_suid,
                          ['YDR277C (pp) YDL194W', 'junk', 'YPR145W (pp) YMR117C'])
        self.assertRaises(CyError, edge_name_to_edge_suid,
                          ['YDR277C (pp) YDL194W', 'junk', 'YPR145W (pp) YMR117C'], unique_list=False)

        # Verify that a known-incorrect list (i.e., mix of SUIDs and names) is caught
        self.assertRaises(CyError, edge_name_to_edge_suid, suids_with_name)

        # Verify that list of edge SUIDs is translated to same SUIDs
        self.assertEqual(edge_name_to_edge_suid(suids), suids)

        # Verify that list of edge names and None is caught
        self.assertRaises(CyError, edge_name_to_edge_suid, names_with_none)

        # Verify that string list of edge SUIDs is translated to SUIDS
        self.assertEqual(edge_name_to_edge_suid(suids_str), suids)

        # Verify that single edge SUID is translated to its SUID
        self.assertEqual(edge_name_to_edge_suid(suids[0]), [suids[0]])

        # Verify that when there are two of the same-named edges, one of their SUIDs is returned if one edge is queried
        suid_orig = index[values.index('YER054C (pp) YBR045C')]
        suid_dup = add_cy_edges(['YER054C', 'YBR045C'], edge_type='pp')[0]['SUID']
        res = edge_name_to_edge_suid(['YER054C (pp) YBR045C'], unique_list=True)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        self.assertIn(res[0], {suid_orig, suid_dup})

        # Verify that when there are two of the same-named edges, both of their SUIDs are returned if both edges are queried
        res = edge_name_to_edge_suid(['YER054C (pp) YBR045C', 'YER054C (pp) YBR045C'], unique_list=True)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 2)
        self.assertSetEqual(set(res), {suid_orig, suid_dup})

        # Verify that when there are two of the same-named edges, an error occurs if we ask for three edges
        self.assertRaises(CyError, edge_name_to_edge_suid, ['YER054C (pp) YBR045C', 'YER054C (pp) YBR045C', 'YER054C (pp) YBR045C'], unique_list=True)

        # Verify that when there are two of the same-named nodes and node list is declared non-unique, a list of all same-named nodes is returned
        res = edge_name_to_edge_suid(['YER054C (pp) YBR045C', 'YER054C (pp) YBR045C', 'YER054C (pp) YBR045C'], unique_list=False)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 3)
        for suid_list in res:
            self.assertIsInstance(suid_list, list)
            self.assertEqual(len(suid_list), 2)
            self.assertSetEqual(set(suid_list), {suid_orig, suid_dup})

        self.assertEqual(edge_name_to_edge_suid(edge_names[0], unique_list=False), [suids[0]]) # try just a single node name, list declared non-unique



    @print_entry_exit
    def test_verify_supported_versions(self):
        verify_supported_versions() # Function shouldn't have thrown an exception
        self.assertRaises(CyError, verify_supported_versions, cyrest=2)
        verify_supported_versions(cytoscape=3.7)
        verify_supported_versions(cytoscape='3.7')
        self.assertRaises(CyError, verify_supported_versions, cytoscape='3.200')
        verify_supported_versions(cytoscape='2.7')
        self.assertRaises(CyError, verify_supported_versions, cytoscape='4.0')
        self.assertRaises(AttributeError, verify_supported_versions, cytoscape='complete trash')

if __name__ == '__main__':
    unittest.main()
