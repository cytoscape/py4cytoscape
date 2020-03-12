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

    @skip
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

        input('select a node')
        select_first_neighbors()

        input('select a node')
        select_first_neighbors(direction='any')

        input('select a node')
        select_first_neighbors(direction='incoming')

        input('select a node')
        select_first_neighbors(direction='outgoing')

        input('select a node')
        select_first_neighbors(direction='undirected')

        input('select a node')
        select_first_neighbors(direction='bogus')

        select_first_neighbors(network='bogus')

#    @skip
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

        self.assertRaises(CyError, select_nodes, [], network='bogus')

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


