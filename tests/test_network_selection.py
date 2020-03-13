# -*- coding: utf-8 -*-

import unittest
from PyCy3 import *
from PyCy3.decorators import *


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
        self._load_test_session()

        input('select a bunch of nodes and edges')
        clear_selection()

        input('select a bunch of nodes and edges')
        clear_selection('nodes')

        input('select a bunch of nodes and edges')
        clear_selection('edges')

        clear_selection(network='bogus')

    @skip
    @print_entry_exit
    def test_select_first_neigbors(self):
        # Initialization
        self._load_test_session()
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

    @skip
    @print_entry_exit
    def test_select_nodes(self):
        # Initialization
        self._load_test_session()
        df_all_nodes = tables.get_table_columns(columns='COMMON')
        all_suids = set(df_all_nodes.index)
        suid_RAP1 = df_all_nodes[df_all_nodes['COMMON'] == 'RAP1'].index[0]
        suid_GCR1 = df_all_nodes[df_all_nodes['COMMON'] == 'GCR1'].index[0]
        suid_PDC1 = df_all_nodes[df_all_nodes['COMMON'] == 'PDC1'].index[0]
        suid_PEP12 = df_all_nodes[df_all_nodes['COMMON'] == 'PEP12'].index[0]

        # Verify that all nodes are reported as selected
        all_selected = select_nodes(None)['nodes']
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

    @skip
    @print_entry_exit
    def test_select_all_nodes(self):
        # Initialization
        self._load_test_session()
        all_suids = set(tables.get_table_columns().index)

        # Verify that selector reports all nodes and that Cytoscape thinks all nodes are selected
        self.assertTrue(set(select_all_nodes()), all_suids)
        self.assertTrue(set(get_selected_nodes(node_suids=True)), all_suids)

        self.assertRaises(CyError, select_all_nodes, network='bogus')

    @skip
    @print_entry_exit
    def test_get_selected_node_count(self):
        # Initialization
        self._load_test_session()
        all_suids = set(tables.get_table_columns().index)

        # Verify that zero selections is counted
        node_count = get_selected_node_count()
        self.assertEqual(node_count, 0)

        # Verify that all selections is counted
        select_all_nodes()
        node_count = get_selected_node_count()
        self.assertEqual(node_count, len(all_suids))

        self.assertRaises(CyError, get_selected_node_count, network='bogus')

    @skip
    @print_entry_exit
    def test_get_selected_nodes(self):
        # Initialization
        self._load_test_session()

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

    @skip
    @print_entry_exit
    def test_invert_node_selection(self):
        # Initialization
        self._load_test_session()
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

    @skip
    @print_entry_exit
    def test_delete_selected_nodes(self):
        # Initialization
        self._load_test_session()
        all_node_suids = set(tables.get_table_columns().index)
        # TODO: Get all edge SUIDs and make sure they're returned by delete_selected_nodes, too

        # Verify that deleting no selected nodes actually deletes no nodes
        self.assertDictEqual(delete_selected_nodes(), {})

        # Verify that deleting all nodes deletes all nodes
        invert_node_selection()
        self.assertSetEqual(set(delete_selected_nodes()['nodes']), all_node_suids)
        self.assertEqual(get_node_count(), 0)

        self.assertRaises(CyError, get_selected_nodes, network='bogus')

    def _load_test_session(self, session_filename=None):
        open_session(session_filename)



"""
    @skip
    @print_entry_exit
    def test_get_selected_node_count(self):
        # Initialization
        input('Load galFiltered.sif')

        res = get_selected_node_count()
        print(res)

    @skip
    @print_entry_exit
    def test_get_selected_nodes(self):
        # Initialization
        input('Load galFiltered.sif')

        res = get_selected_nodes(False)
        print(res)

        res = get_selected_nodes(True)
        print(res)
"""


if __name__ == '__main__':
    unittest.main()


