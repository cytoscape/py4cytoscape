# -*- coding: utf-8 -*-

import unittest

from test_utils import *

class NetworkSelectionTests(unittest.TestCase):

    def setUp(self):
        try:
            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

#    @skip
    @print_entry_exit
    def test_clear_selection(self):
        # Initialization
        load_test_session()
        COMMON_NODES = ['RAP1', 'PDC1', 'MIG1', 'SUC2']
        SELECTED_NODES = ['YGL035C', 'YLR044C', 'YNL216W', 'YIL162W']
        SELECTED_EDGES = ['YGL035C (pd) YIL162W', 'YGL035C (pd) YLR044C', 'YNL216W (pd) YLR044C']

        # Select some nodes and edges, then verify that all selections are cleared
        select_nodes(COMMON_NODES, by_col='COMMON')
        selected_nodes = get_selected_nodes()
        select_edges_connecting_selected_nodes()
        selected_edges = get_selected_edges()
        clear_selection()
        self.assertSetEqual(set(selected_nodes), set(SELECTED_NODES))
        self.assertSetEqual(set(selected_edges), set(SELECTED_EDGES))
        self.assertEqual(get_selected_nodes(), None)
        self.assertEqual(get_selected_edges(), None)

        # Select some nodes and edges, then verify that only nodes are cleared
        select_nodes(COMMON_NODES, by_col='COMMON')
        selected_nodes = get_selected_nodes()
        select_edges_connecting_selected_nodes()
        selected_edges = get_selected_edges()
        clear_selection('nodes')
        self.assertSetEqual(set(selected_nodes), set(SELECTED_NODES))
        self.assertSetEqual(set(selected_edges), set(SELECTED_EDGES))
        self.assertEqual(get_selected_nodes(), None)
        self.assertSetEqual(set(get_selected_edges()), set(selected_edges))
        clear_selection()

        # Select some nodes and edges, then verify that only edges are cleared
        select_nodes(COMMON_NODES, by_col='COMMON')
        selected_nodes = get_selected_nodes()
        select_edges_connecting_selected_nodes()
        selected_edges = get_selected_edges()
        clear_selection('edges')
        self.assertSetEqual(set(selected_nodes), set(SELECTED_NODES))
        self.assertSetEqual(set(selected_edges), set(SELECTED_EDGES))
        self.assertSetEqual(set(get_selected_nodes()), set(selected_nodes))
        self.assertEqual(get_selected_edges(), None)

        self.assertRaises(CyError, clear_selection, network='bogus')

#    @skip
    @print_entry_exit
    def test_select_first_neigbors(self):
        # Initialization
        load_test_session()
        df_all_nodes = tables.get_table_columns(columns='COMMON')

        def _test_first_neighbors(direction, expected_selection):
            clear_selection()
            select_nodes(['RAP1'], by_col='COMMON')
            first_neighbor_nodes = select_first_neighbors(direction=direction)['nodes'] if direction else select_first_neighbors()['nodes']
            first_names = set(df_all_nodes[df_all_nodes.index.isin(first_neighbor_nodes)]['COMMON'])
            self.assertSetEqual(first_names, expected_selection)

        # Verify that nodes around RAP1 are selected properly, depending on edge direction requested
        _test_first_neighbors(None, {'RPS24A', 'PDC1', 'RAP1', 'ADH1', 'HIS4', 'RPS24B', 'RPL18B', 'ENO2', 'TPI1', 'CDC19', 'HSP42', 'PGK1', 'RPL25', 'RPS17A', 'PHO5', 'RPL16A', 'ENO1', 'RPL18A'})
        _test_first_neighbors('any', {'RPS24A', 'PDC1', 'RAP1', 'ADH1', 'HIS4', 'RPS24B', 'RPL18B', 'ENO2', 'TPI1', 'CDC19', 'HSP42', 'PGK1', 'RPL25', 'RPS17A', 'PHO5', 'RPL16A', 'ENO1', 'RPL18A'})
        _test_first_neighbors('incoming', {'RPS17A', 'RAP1'})
        _test_first_neighbors('outgoing', {'RPS24A', 'PDC1', 'RAP1', 'ADH1', 'HIS4', 'RPS24B', 'RPL18B', 'ENO2', 'TPI1', 'CDC19', 'HSP42', 'PGK1', 'RPL25', 'PHO5', 'RPL16A', 'ENO1', 'RPL18A'})
        _test_first_neighbors('undirected', {'RAP1'})

        clear_selection()
        select_nodes(['RAP1'], by_col='COMMON')
        self.assertDictEqual(select_first_neighbors(direction='bogus'), {})

        self.assertRaises(CyError, select_first_neighbors, network='bogus')

#    @skip
    @print_entry_exit
    def test_select_nodes(self):
        # Initialization
        load_test_session()
        df_all_nodes = tables.get_table_columns(columns='COMMON')
        all_suids = set(df_all_nodes.index)
        suid_RAP1 = df_all_nodes[df_all_nodes['COMMON'] == 'RAP1'].index[0]
        suid_GCR1 = df_all_nodes[df_all_nodes['COMMON'] == 'GCR1'].index[0]
        suid_PDC1 = df_all_nodes[df_all_nodes['COMMON'] == 'PDC1'].index[0]
        suid_PEP12 = df_all_nodes[df_all_nodes['COMMON'] == 'PEP12'].index[0]

        # Verify that selecting no nodes reports that no nodes were selected
        self.assertDictEqual(select_nodes(None), {})

        # Verify that all nodes are reported as selected
        all_selected = select_nodes(list(all_suids))['nodes']
        self.assertSetEqual(all_suids, set(all_selected))

        # Verify that only RAP1 is reported selected
        clear_selection()
        nodes_selected = select_nodes(['RAP1'], by_col='COMMON')['nodes']
        self.assertSetEqual(set(nodes_selected), set([suid_RAP1]))

        # Verify that only RAP1 and GCR1 are reported selected
        clear_selection()
        nodes_selected = select_nodes(['RAP1', 'GCR1'], by_col='COMMON')['nodes']
        self.assertSetEqual(set(nodes_selected), set([suid_RAP1, suid_GCR1]))

        # Verify that adding PDC1 is reported selected and that RAP1 and GCR1 remain selected
        nodes_selected = select_nodes(['PDC1'], by_col='COMMON')['nodes']
        self.assertSetEqual(set(nodes_selected), set([suid_PDC1]))
        self.assertSetEqual(set(get_selected_nodes(node_suids=True)), set([suid_RAP1, suid_GCR1, suid_PDC1]))

        # Verify that selecting only PEP12 is reported selected and that other nodes don't remain selected
        nodes_selected = select_nodes(['PEP12'], by_col='COMMON', preserve_current_selection=False)['nodes']
        self.assertSetEqual(set(nodes_selected), set([suid_PEP12]))
        self.assertSetEqual(set(get_selected_nodes(node_suids=True)), set([suid_PEP12]))

        # verify that all nodes are reported selected
        clear_selection()
        nodes_selected = select_nodes(all_selected)['nodes']
        self.assertSetEqual(set(nodes_selected), all_suids)
        self.assertSetEqual(set(get_selected_nodes(node_suids=True)), all_suids)

        # verify that bad nodes don't show up in the selected list
        clear_selection()
        nodes_selected = select_nodes(['RAP1x', 'GCR1'], by_col='COMMON')['nodes']
        self.assertSetEqual(set(nodes_selected), set([suid_GCR1]))

        self.assertRaises(CyError, select_nodes, [], network='bogus')

#    @skip
    @print_entry_exit
    def test_select_all_nodes(self):
        # Initialization
        load_test_session()
        all_suids = set(tables.get_table_columns().index)

        # Verify that selector reports all nodes and that Cytoscape thinks all nodes are selected
        self.assertTrue(set(select_all_nodes()), all_suids)
        self.assertTrue(set(get_selected_nodes(node_suids=True)), all_suids)

        self.assertRaises(CyError, select_all_nodes, network='bogus')

#    @skip
    @print_entry_exit
    def test_get_selected_node_count(self):
        # Initialization
        load_test_session()
        all_suids = set(tables.get_table_columns().index)

        # Verify that zero selections is counted
        node_count = get_selected_node_count()
        self.assertEqual(node_count, 0)

        # Verify that all selections is counted
        select_all_nodes()
        node_count = get_selected_node_count()
        self.assertEqual(node_count, len(all_suids))

        self.assertRaises(CyError, get_selected_node_count, network='bogus')

#    @skip
    @print_entry_exit
    def test_get_selected_nodes(self):
        # Initialization
        load_test_session()

        # Verify that no node selections is reported
        self.assertEqual(get_selected_nodes(), None)

        # Verify that nodes reported by SUID are correct
        nodes_selected = select_nodes(['YNL216W', 'YPL075W'], by_col='name')['nodes']
        nodes_reported = get_selected_nodes(node_suids=True)
        self.assertSetEqual(set(nodes_selected), set(nodes_reported))

        # Verify that nodes reported by name are correct
        nodes_reported = get_selected_nodes(node_suids=False)
        self.assertSetEqual({'YNL216W', 'YPL075W'}, set(nodes_reported))

        self.assertRaises(CyError, get_selected_nodes, network='bogus')

#    @skip
    @print_entry_exit
    def test_invert_node_selection(self):
        # Initialization
        load_test_session()
        all_suids = set(tables.get_table_columns().index)

        # Verify that inverting an unselected network reports all nodes selected
        self.assertSetEqual(set(invert_node_selection()['nodes']), all_suids)

        # Verify that selecting two nodes and inverting returns all nodes except the original two
        nodes_selected = set(select_nodes(['YNL216W', 'YPL075W'], by_col='name', preserve_current_selection=False)['nodes'])
        inverted_nodes = set(invert_node_selection()['nodes'])
        self.assertSetEqual(all_suids.difference(nodes_selected), inverted_nodes)

        # Verify that inverting again gives the original two nodes
        original_nodes = set(invert_node_selection()['nodes'])
        self.assertSetEqual(nodes_selected, original_nodes)

        self.assertRaises(CyError, get_selected_nodes, network='bogus')

#    @skip
    @print_entry_exit
    def test_delete_selected_nodes(self):
        # Initialization
        load_test_session()
        all_node_suids = set(tables.get_table_columns().index)
        # TODO: Get all edge SUIDs and make sure they're returned by delete_selected_nodes, too

        # Verify that deleting no selected nodes actually deletes no nodes
        self.assertDictEqual(delete_selected_nodes(), {})

        # Verify that deleting all nodes deletes all nodes
        invert_node_selection()
        self.assertSetEqual(set(delete_selected_nodes()['nodes']), all_node_suids)
        self.assertEqual(get_node_count(), 0)

        self.assertRaises(CyError, get_selected_nodes, network='bogus')

#    @skip
    @print_entry_exit
    def test_select_nodes_connected_by_selected_edges(self):
        # Initialization
        load_test_session()
        COMMON_NODES = ['RAP1', 'PDC1', 'MIG1', 'SUC2']
        SELECTED_EDGES = ['YGL035C (pd) YIL162W', 'YGL035C (pd) YLR044C', 'YNL216W (pd) YLR044C']

        # Select some nodes and verify that the expected edges are selected
        selected_nodes = select_nodes(COMMON_NODES, by_col='COMMON')['nodes']
        selected_edges = edge_name_to_edge_suid(SELECTED_EDGES) # expected edges
        selection = select_edges_connecting_selected_nodes()
        self.assertSetEqual(set(selected_nodes), set(selection['nodes']))
        self.assertSetEqual(set(selected_edges), set(selection['edges']))

        self.assertRaises(CyError, select_nodes_connected_by_selected_edges, network='bogus')


#    @skip
    @print_entry_exit
    def test_select_edges(self):
        # Initialization
        load_test_session()
        SINGLE_EDGE = ['YDR412W (pp) YPR119W']
        single_edge_suid = edge_name_to_edge_suid(SINGLE_EDGE) # expected edges
        EDGE_LIST = ['YGL035C (pd) YIL162W', 'YGL035C (pd) YLR044C', 'YNL216W (pd) YLR044C']
        edge_list_suids = edge_name_to_edge_suid(EDGE_LIST) # expected edges

        # Verify that selecting all edges works
        self.assertDictEqual(select_edges(None), {})

        # Verify that selecting a single edge works
        selection = select_edges(single_edge_suid, preserve_current_selection=False)
        self.assertSetEqual(set(single_edge_suid), set(selection['edges']))
        self.assertListEqual(selection['nodes'], [])

        # Verify that selecting multiple edge works, and that it adds to the previously selected edge
        selection = select_edges(EDGE_LIST, by_col='name', preserve_current_selection=True)
        self.assertSetEqual(set(edge_list_suids), set(selection['edges']))
        self.assertListEqual(selection['nodes'], [])
        expected_edges = single_edge_suid.copy()
        expected_edges.extend(edge_list_suids)
        selected_edges = get_selected_edges(edge_suids=True)
        self.assertSetEqual(set(expected_edges), set(selected_edges))

        self.assertRaises(CyError, select_edges, None, network='bogus')

#    @skip
    @print_entry_exit
    def test_select_all_edges(self):
        # Initialization
        load_test_session()

        # TODO: I seem to be converting between edge IDs and edge names a lot. Is there a way to avoid the explicit conversion?
        # Verify that all edges get selected
        all_edge_suids = edge_name_to_edge_suid(get_all_edges())
        self.assertSetEqual(set(all_edge_suids), set(select_all_edges()))

        self.assertRaises(CyError, select_all_edges, network='bogus')

#    @skip
    @print_entry_exit
    def test_invert_edge_selection(self):
        # Initialization
        load_test_session()
        all_edge_suids = edge_name_to_edge_suid(get_all_edges())

        # Verify that all edges get selected
        self.assertSetEqual(set(all_edge_suids), set(invert_edge_selection()['edges']))

        # Verify that all edges get deselected
        self.assertDictEqual(invert_edge_selection(), {})

        # Verify that all edges get selected
        self.assertSetEqual(set(all_edge_suids), set(invert_edge_selection()['edges']))

        self.assertRaises(CyError, invert_edge_selection, network='bogus')

#    @skip
    @print_entry_exit
    def test_delete_selected_edges(self):
        # Initialization
        load_test_session()
        all_edge_suids = edge_name_to_edge_suid(get_all_edges())

        # Verify that no edges are returned when there are no edges to delete
        self.assertDictEqual(delete_selected_edges(), {})

        # Verify that all edges get selected and are deleted
        self.assertSetEqual(set(all_edge_suids), set(invert_edge_selection()['edges']))
        self.assertSetEqual(set(all_edge_suids), set(delete_selected_edges()['edges']))
        self.assertIsNone(get_all_edges())

        self.assertRaises(CyError, delete_selected_edges, network='bogus')

#    @skip
    @print_entry_exit
    def test_get_selected_edge_count(self):
        # Initialization
        load_test_session()
        all_edge_suids = edge_name_to_edge_suid(get_all_edges())

        # Verify that when no edges are selected, the count is 0
        self.assertEqual(get_selected_edge_count(), 0)

        # Verify that all edges get selected and are counted
        self.assertSetEqual(set(all_edge_suids), set(invert_edge_selection()['edges']))
        self.assertEqual(get_selected_edge_count(), len(all_edge_suids))

        self.assertRaises(CyError, get_selected_edge_count, network='bogus')

#    @skip
    @print_entry_exit
    def test_get_selected_edges(self):
        # Initialization
        load_test_session()
        EDGE_LIST = ['YGL035C (pd) YIL162W', 'YGL035C (pd) YLR044C', 'YNL216W (pd) YLR044C']

        # Verify that when no edges are selected, the selected edge list is null
        self.assertIsNone(get_selected_edges())

        # Verify that when some edges are selected, they're returned in the list
        select_edges(EDGE_LIST, by_col='name')
        self.assertSetEqual(set(get_selected_edges(edge_suids=False)), set(EDGE_LIST))
        self.assertSetEqual(set(get_selected_edges(edge_suids=True)), set(edge_name_to_edge_suid(EDGE_LIST)))

        self.assertRaises(CyError, get_selected_edges, network='bogus')

#    @skip
    @print_entry_exit
    def test_select_edges_connecting_selected_nodes(self):
        # Initialization
        load_test_session()
        COMMON_NODES = ['RAP1', 'PDC1', 'MIG1', 'SUC2', 'PFK27', 'TAH18'] # PFK27 & TAH18 aren't connected to the other nodes
        self_edge_PFK27 = add_cy_edges(['YOL136C', 'YOL136C'], edge_type='pp')
        EXPECTED_EDGES = ['YGL035C (pd) YIL162W', 'YGL035C (pd) YLR044C', 'YNL216W (pd) YLR044C', 'YOL136C (pp) YOL136C']

        # Verify that when no edges are selected, no edges get selected
        self.assertIsNone(select_edges_connecting_selected_nodes())

        # Verify that when some nodes are selected, they're returned in the list along with edges that connect them
        selected_nodes = select_nodes(COMMON_NODES, by_col='COMMON')['nodes']
        selection = select_edges_connecting_selected_nodes()
        expected_edges = edge_name_to_edge_suid(EXPECTED_EDGES)  # expected edges
        self.assertSetEqual(set(selected_nodes), set(selection['nodes']))
        self.assertSetEqual(set(expected_edges), set(selection['edges']))

        self.assertRaises(CyError, select_edges_connecting_selected_nodes, network='bogus')

#    @skip
    @print_entry_exit
    def test_select_edges_adjacent_to_selected_nodes(self):
        # Initialization
        load_test_session()
        COMMON_NODES = ['PDC1', 'TAH18']
        EXPECTED_EDGES = ['YPR048W (pp) YDL215C', 'YER179W (pp) YLR044C', 'YGL035C (pd) YLR044C', 'YPR048W (pp) YOR355W', 'YNL216W (pd) YLR044C', 'YNL199C (pp) YPR048W']

        # Verify that when no edges are selected, no edges get selected
        self.assertDictEqual(select_edges_adjacent_to_selected_nodes(), {})

        # Verify that when some nodes are selected, they're returned in the list along with edges that connect them
        selected_nodes = select_nodes(COMMON_NODES, by_col='COMMON')['nodes']
        expected_edges = edge_name_to_edge_suid(EXPECTED_EDGES)  # expected edges
        selection = select_edges_adjacent_to_selected_nodes()
        self.assertSetEqual(set(selected_nodes), set(selection['nodes']))
        self.assertSetEqual(set(expected_edges), set(selection['edges']))

        self.assertRaises(CyError, select_edges_connecting_selected_nodes, network='bogus')

#    @skip
    @print_entry_exit
    def test_delete_duplicate_edges(self):
        # Initialization
        load_test_session()
        original_edge_count = get_edge_count()
        EDGE_TO_DUP = ['YNL216W (pd) YLR044C']
        original_edge_suid = get_edge_info([EDGE_TO_DUP])[0]['SUID']

        # Verify that when no edges are duplicated, no edges get deleted
        self.assertDictEqual(delete_duplicate_edges(), {})
        self.assertEqual(get_edge_count(), original_edge_count)

        # Verify that duplicating an edge then deleting one of the same-name edges results in the original network
        first_copy_edge_suid = add_cy_edges(['YNL216W', 'YLR044C'], edge_type='pd')[0]['SUID']
        edge_deleted_suids = delete_duplicate_edges()['edges']
        self.assertEqual(len(edge_deleted_suids), 1)
        self.assertTrue(set(edge_deleted_suids) < set([original_edge_suid, first_copy_edge_suid]))
        self.assertEqual(get_edge_count(), original_edge_count)

        # Verify that duplicating an edge twice then deleting one of the same-name edges results in the original network
        first_copy_edge_suid = add_cy_edges(['YNL216W', 'YLR044C'], edge_type='pd')[0]['SUID']
        second_copy_edge_suid = add_cy_edges(['YNL216W', 'YLR044C'], edge_type='pd')[0]['SUID']
        edge_deleted_suids = delete_duplicate_edges()['edges']
        self.assertEqual(len(edge_deleted_suids), 2)
        self.assertTrue(set(edge_deleted_suids) < set([original_edge_suid, first_copy_edge_suid, second_copy_edge_suid]))
        self.assertEqual(get_edge_count(), original_edge_count)

        self.assertRaises(CyError, delete_duplicate_edges, network='bogus')

#    @skip
    @print_entry_exit
    def test_delete_self_loops(self):
        # Initialization
        load_test_session()

        # Verify that when there are no self-edges, none get deleted
        original_edges = get_all_edges()
        self.assertEqual(delete_self_loops(), '')
        self.assertSetEqual(set(get_all_edges()), set(original_edges))

        # Add a few self-edges and make sure they get deleted
        self_edge_PFK27_1 = add_cy_edges(['YOL136C', 'YOL136C'], edge_type='pp')
        self_edge_PFK27_2 = add_cy_edges(['YOL136C', 'YOL136C'], edge_type='pp')
        self_edge_PDC1 = add_cy_edges(['YLR044C', 'YLR044C'], edge_type='pp')
        self.assertEqual(delete_self_loops(), '')
        self.assertSetEqual(set(get_all_edges()), set(original_edges))

        self.assertRaises(CyError, delete_self_loops, network='bogus')

if __name__ == '__main__':
    unittest.main()


