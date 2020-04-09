# -*- coding: utf-8 -*-

import unittest
from requests import HTTPError

from test_utils import *

class GroupsTests(unittest.TestCase):
    def setUp(self):
        try:
            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    @skip
    @print_entry_exit
    def test_create_group(self):
        # Initialization
        load_test_session()
        select_nodes(['GDS1', 'PFK27'], by_col='COMMON')
        selection = select_edges_adjacent_to_selected_nodes()
        clear_selection()

        def check_group(group_name, group_create_func):
            group = group_create_func(group_name)
            self.assertIsInstance(group, dict)
            self.assertIsInstance(group['group'], int)
            group_id = group['group']

            group_info = get_group_info(group_name)
            self.assertIsInstance(group_info, dict)
            self.assertEqual(group_info['group'], group_id)
            self.assertEqual(group_info['name'], group_name)
            self.assertSetEqual(set(group_info['nodes']), set(selection['nodes']))
            self.assertListEqual(group_info['internalEdges'], [])
            self.assertSetEqual(set(group_info['externalEdges']), set(selection['edges']))
            self.assertFalse(group_info['collapsed'])


        # Create a group out of just 2 selected nodes
        select_nodes(selection['nodes'])
        check_group('group 1', lambda x: create_group(x))

        # Create a group out of just 2 named nodes in a given column
        check_group('group 2', lambda x: create_group(x, nodes=['GDS1', 'PFK27'], nodes_by_col='COMMON'))

        # Create a group out of just 2 named nodes in a named column
        check_group('group 3', lambda x: create_group(x, nodes='COMMON:GDS1,COMMON:PFK27'))

    #    @skip
    @print_entry_exit
    def test_add_to_group(self):
        # Initialization
        load_test_session()
        select_nodes(['GDS1', 'PFK27'], by_col='COMMON')
        selection_2_nodes = select_edges_adjacent_to_selected_nodes()
        select_nodes(['PDC1'], by_col='COMMON')
        selection_3_nodes = select_edges_adjacent_to_selected_nodes()
        clear_selection()
        select_nodes(['PEP12'], by_col='COMMON')
        selection_PEP12_node = select_edges_adjacent_to_selected_nodes()
        clear_selection()
        select_nodes(['AHP1'], by_col='COMMON')
        selection_AHP1_node = select_edges_adjacent_to_selected_nodes()
        clear_selection()
        all_nodes = node_name_to_node_suid(get_all_nodes())
        all_edges = edge_name_to_edge_suid(get_all_edges())

        def check_group(group_name, group_add_func, expected_nodes, expected_internal_edges, expected_external_edges):
            self.assertDictEqual(group_add_func(group_name), {})
            group_info = get_group_info(group_name)
            self.assertSetEqual(set(group_info['nodes']), expected_nodes)
            self.assertSetEqual(set(group_info['internalEdges']), expected_internal_edges)
            self.assertSetEqual(set(group_info['externalEdges']), expected_external_edges)

        # Verify that all nodes and edges produces right nodes, internal edges and external edges
        group_0 = create_group('group 0')['group']
        check_group('group 0', lambda x: add_to_group(x, nodes='all', edges='all'), set(all_nodes) | {group_0}, set(all_edges), set())

        # Create a group out of just 2 selected nodes
        select_nodes(selection_2_nodes['nodes'])
        group = create_group('group 1')
        group_id = group['group']

        # Verify that adding a list of nodes by SUID produces right nodes, internal edges and external edges
        check_group('group 1', lambda x: add_to_group(x, list(set(selection_3_nodes['nodes']) - set(selection_2_nodes['nodes']))), set(selection_3_nodes['nodes']), set(), set(selection_3_nodes['edges']))

        # Verify that adding a list of edges by SUID produces right nodes, internal edges and external edges ... and doesn't allow selected nodes (PEP12) in
        edge_GDS1_PFK27 = add_cy_edges(['YOR355W', 'YOL136C'])[0]['SUID']
        edge_GDS1_PEP12 = add_cy_edges(['YOR355W', 'YOR036W'])[0]['SUID']
        select_nodes(['PEP12'], by_col='COMMON') # should not end up in group 1 ... verify to be sure
        check_group('group 1', lambda x: add_to_group(x, nodes=[], edges=[edge_GDS1_PFK27, edge_GDS1_PEP12]), set(selection_3_nodes['nodes']), {edge_GDS1_PFK27}, set(selection_3_nodes['edges']) | {edge_GDS1_PEP12})

        # Verify that adding a selected node (PEP12) produces right nodes, internal edges and external edges
        check_group('group 1', lambda x: add_to_group(x), set(selection_3_nodes['nodes']) | {selection_PEP12_node['nodes'][0]}, {edge_GDS1_PFK27, edge_GDS1_PEP12}, set(selection_3_nodes['edges']) | set(selection_3_nodes['edges']) | set(selection_PEP12_node['edges']))

        # Verify that adding nothing at all produces right nodes, internal edges and external edges
        select_all_nodes()
        select_all_edges()
        check_group('group 1', lambda x: add_to_group(x, nodes=[], edges=[]), set(selection_3_nodes['nodes']) | {selection_PEP12_node['nodes'][0]}, {edge_GDS1_PFK27, edge_GDS1_PEP12}, set(selection_3_nodes['edges']) | set(selection_3_nodes['edges']) | set(selection_PEP12_node['edges']))

        # Verify that adding a column by COMMON produces right nodes, internal edges and external edges
        check_group('group 1', lambda x: add_to_group(x, nodes='COMMON:AHP1'), set(selection_3_nodes['nodes']) | {selection_PEP12_node['nodes'][0]} | {selection_AHP1_node['nodes'][0]}, {edge_GDS1_PFK27, edge_GDS1_PEP12}, set(selection_3_nodes['edges']) | set(selection_3_nodes['edges']) | set(selection_PEP12_node['edges']) | set(selection_AHP1_node['edges']))

if __name__ == '__main__':
    unittest.main()