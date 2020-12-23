# -*- coding: utf-8 -*-

""" Test functions in groups.py.
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

from requests import HTTPError

from test_utils import *


class GroupsTests(unittest.TestCase):
    def setUp(self):
        try:
            close_session(False)
#            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    
    @print_entry_exit
    def test_create_group(self):
        # Initialization
        load_test_session()
        select_nodes(['GDS1', 'PFK27'], by_col='COMMON')
        selection = select_edges_adjacent_to_selected_nodes()
        clear_selection()

        # Create a group out of just 2 selected nodes
        select_nodes(selection['nodes'])
        self._check_whole_group('group 1', lambda x: create_group(x), selection)

        # Create a group out of just 2 named nodes in a given column
        self._check_whole_group('group 2',
                                lambda x: create_group(x, nodes=['GDS1', 'PFK27'], nodes_by_col='COMMON'),
                                selection)

        # Create a group out of just 2 named nodes in a named column
        self._check_whole_group('group 3', lambda x: create_group(x, nodes='COMMON:GDS1,COMMON:PFK27'), selection)

        # Create a group with no name
        self._check_whole_group('', lambda x: create_group(x, nodes='COMMON:GDS1,COMMON:PFK27'), selection)

        self.assertRaises(CyError, create_group, 'group 4', nodes='COMMON:GDS1,COMMON:PFK27',
                          network='bogus')

    
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
        # TODO: Suggestion for new functionality ... edges_adjacent_to_nodes(['AHP1'], by_col='COMMON')
        select_nodes(['AHP1'], by_col='COMMON')
        selection_AHP1_node = select_edges_adjacent_to_selected_nodes()
        clear_selection()
        all_nodes = node_name_to_node_suid(get_all_nodes())
        # TODO: Suggestion for new functionality ... get_all_nodes('SUID' or 'name' or both) ... same with get_all_edges
        all_edges = edge_name_to_edge_suid(get_all_edges())

        def check_group(group_name, group_add_func, expected_nodes, expected_internal_edges, expected_external_edges):
            self.assertDictEqual(group_add_func(group_name), {})
            self._check_group_info(group_name, group_name, None, expected_nodes, expected_internal_edges,
                                   expected_external_edges)

        # Verify that all nodes and edges produces right nodes, internal edges and external edges
        group_0 = create_group('group 0')['group']
        check_group('group 0',
                    lambda x: add_to_group(x, nodes='all', edges='all'),
                    expected_nodes=set(all_nodes) | {group_0},
                    expected_internal_edges=set(all_edges),
                    expected_external_edges=set())

        # Create group1 out of just 2 selected nodes
        select_nodes(selection_2_nodes['nodes'])
        group = create_group('group 1')
        group_id = group['group']

        # Verify that adding a list of nodes (i.e., AHP1) by SUID produces right nodes, internal edges and external edges
        check_group('group 1',
                    lambda x: add_to_group(x, nodes = list(set(selection_3_nodes['nodes']) - set(selection_2_nodes['nodes']))),
                    expected_nodes=set(selection_3_nodes['nodes']), # GDS1 & PFK27 & AHP1
                    expected_internal_edges=set(),
                    expected_external_edges=set(selection_3_nodes['edges']))

        # Verify that adding a list of edges by SUID produces right nodes, internal edges and external edges
        edge_GDS1_PFK27 = add_cy_edges(['YOR355W', 'YOL136C'])[0]['SUID']
        edge_GDS1_PEP12 = add_cy_edges(['YOR355W', 'YOR036W'])[0]['SUID']
        select_nodes(['PEP12'], by_col='COMMON')  # should not end up in group 1 ... verify to be sure
        check_group('group 1',
                    lambda x: add_to_group(x, nodes=[], edges=[edge_GDS1_PFK27, edge_GDS1_PEP12]),
                    expected_nodes=set(selection_3_nodes['nodes']), # GDS1 & PFK27 & AHP
                    expected_internal_edges={edge_GDS1_PFK27},
                    expected_external_edges=set(selection_3_nodes['edges']) | {edge_GDS1_PEP12})

        # Verify that adding a selected node (PEP12) produces right nodes, internal edges and external edges
        check_group('group 1',
                    lambda x: add_to_group(x),
                    expected_nodes=set(selection_3_nodes['nodes']) | {selection_PEP12_node['nodes'][0]},
                    expected_internal_edges={edge_GDS1_PFK27, edge_GDS1_PEP12},
                    expected_external_edges=set(selection_3_nodes['edges']) | set(selection_PEP12_node['edges']))

        # Verify that adding nothing at all produces right nodes, internal edges and external edges
        select_all_nodes()
        select_all_edges()
        check_group('group 1',
                    lambda x: add_to_group(x, nodes=[], edges=[]),
                    expected_nodes=set(selection_3_nodes['nodes']) | {selection_PEP12_node['nodes'][0]},
                    expected_internal_edges={edge_GDS1_PFK27, edge_GDS1_PEP12},
                    expected_external_edges=set(selection_3_nodes['edges']) | set(selection_PEP12_node['edges']))

        # Verify that adding a column by COMMON produces right nodes, internal edges and external edges
        check_group('group 1',
                    lambda x: add_to_group(x, nodes='COMMON:AHP1'),
                    expected_nodes=set(selection_3_nodes['nodes']) | {selection_PEP12_node['nodes'][0]} | {selection_AHP1_node['nodes'][0]},
                    expected_internal_edges={edge_GDS1_PFK27, edge_GDS1_PEP12},
                    expected_external_edges=set(selection_3_nodes['edges']) | set(selection_PEP12_node['edges']) | set(selection_AHP1_node['edges']))

        self.assertRaises(CyError, add_to_group, 'group x', nodes='COMMON:AHP1', network='Bogus')

    
    @print_entry_exit
    def test_list_groups(self):
        # Initialization
        load_test_session()

        # Verify that when there are no groups, no groups are returned
        group_list = list_groups()
        self.assertIsInstance(group_list, dict)
        self.assertIsInstance(group_list['groups'], list)
        self.assertSetEqual(set(list_groups()['groups']), set())

        # Add a few groups and verify that they're in the list
        group_1_suid = create_group('Group 1', nodes=['GDS1', 'PFK27'], nodes_by_col='COMMON')['group']
        group_2_suid = create_group('Group 2', nodes=['PDC1', 'FBP1', 'CIN4'], nodes_by_col='COMMON')['group']
        self.assertSetEqual(set(list_groups()['groups']), {group_1_suid, group_2_suid})

        self.assertRaises(CyError, list_groups, network='Bogus')

    
    @print_entry_exit
    def test_get_group_info(self):
        # Initialization
        load_test_session()
        select_nodes(['GDS1', 'PFK27'], by_col='COMMON')
        selection_GDS1_PFK27 = select_edges_adjacent_to_selected_nodes()
        clear_selection()
        select_nodes(['PDC1', 'FBP1', 'CIN4'], by_col='COMMON')
        selection_PDC1_FBP1_CIN4 = select_edges_adjacent_to_selected_nodes()
        clear_selection()
        group_1_suid = create_group('Group 1', nodes=['GDS1', 'PFK27'], nodes_by_col='COMMON')['group']
        group_2_suid = create_group('', nodes=['PDC1', 'FBP1', 'CIN4'], nodes_by_col='COMMON')['group']

        # Verify that info for a real group accessed by group name is valid
        self._check_group_info('Group 1', 'Group 1', group_1_suid, set(selection_GDS1_PFK27['nodes']), set(),
                               set(selection_GDS1_PFK27['edges']))

        # Verify that info for a real group accessed by group name is valid
        self._check_group_info(group_1_suid, 'Group 1', group_1_suid, set(selection_GDS1_PFK27['nodes']), set(),
                               set(selection_GDS1_PFK27['edges']))

        # Verify that info for an unnamed group group is valid
        self._check_group_info('', '', group_2_suid, set(selection_PDC1_FBP1_CIN4['nodes']), set(),
                               set(selection_PDC1_FBP1_CIN4['edges']))

        self.assertRaises(CyError, get_group_info, -1)
        self.assertRaises(CyError, get_group_info, 'Bogus Group')
        self.assertRaises(CyError, get_group_info, 'Group 1', network='Bogus')

    
    @print_entry_exit
    def test_collapse_expand_group(self):
        # Initialization
        load_test_session()
        select_nodes(['GDS1', 'PFK27'], by_col='COMMON')
        clear_selection()
        select_nodes(['PDC1', 'FBP1', 'CIN4'], by_col='COMMON')
        clear_selection()
        group_1_suid = create_group('Group 1', nodes=['GDS1', 'PFK27'], nodes_by_col='COMMON')['group']
        group_2_suid = create_group('Group 2', nodes=['PDC1', 'FBP1', 'CIN4'], nodes_by_col='COMMON')['group']
        group_3_suid = create_group('Group 3', nodes=['PEP12', 'BAS1', 'MSL1'], nodes_by_col='COMMON')['group']

        def check_group_info(group, expected_collapse):
            group_info = get_group_info(group)
            self.assertEqual(group_info['collapsed'], expected_collapse)

        def verify(pre_conditioning, operation, op_res, post_state):
            pre_conditioning()
            res = operation()
            self.assertSetEqual(set(res['groups']), op_res)
            for x in post_state:
                check_group_info(x[0], x[1])

        # Verify expanding already-expanded groups has no effect
        check_group_info(group_1_suid, False)
        check_group_info(group_2_suid, False)
        check_group_info(group_3_suid, False)
        verify(pre_conditioning=lambda: None,
               operation=lambda: expand_group(),
               op_res=set(),
               post_state=[(group_1_suid, False), (group_2_suid, False), (group_3_suid, False)])

        # Verify collapsing all selected groups if none are selected
        verify(pre_conditioning=lambda: None,
               operation=lambda: collapse_group(),
               op_res=set(),
               post_state=[(group_1_suid, False), (group_2_suid, False), (group_3_suid, False)])

        # Verify collapsing a selected group doesn't affect others
        verify(pre_conditioning=lambda: select_nodes([group_2_suid]),
               operation=lambda: collapse_group(),
               op_res={group_2_suid},
               post_state=[(group_1_suid, False), (group_2_suid, True), (group_3_suid, False)])
        verify(pre_conditioning=lambda: select_nodes([group_3_suid]),
               operation=lambda: collapse_group(),
               op_res={group_2_suid, group_3_suid},
               post_state=[(group_1_suid, False), (group_2_suid, True), (group_3_suid, True)])

        # Verify collapsing an unselected group doesn't affect others
        verify(pre_conditioning=lambda: None,
               operation=lambda: collapse_group('unselected'),
               op_res={group_1_suid},
               post_state=[(group_1_suid, True), (group_2_suid, True), (group_3_suid, True)])

        # Verify that expanding selected groups doesn't affect others
        verify(pre_conditioning=lambda: None,
               operation=lambda: expand_group(),
               op_res={group_2_suid, group_3_suid},
               post_state=[(group_1_suid, True), (group_2_suid, False), (group_3_suid, False)])

        # Verify that expanding unselected groups doesn't affect others
        verify(pre_conditioning=lambda: None,
               operation=lambda: expand_group('unselected'),
               op_res={group_1_suid},
               post_state=[(group_1_suid, False), (group_2_suid, False), (group_3_suid, False)])

        # Verify collapsing two specific groups (in list) doesn't affect the third
        verify(pre_conditioning=lambda: None,
               operation=lambda: collapse_group(['Group 1', 'Group 2']),
               op_res={group_1_suid, group_2_suid},
               post_state=[(group_1_suid, True), (group_2_suid, True), (group_3_suid, False)])

        # Verify expanding two specific groups (in list) doesn't affect the third
        verify(pre_conditioning=lambda: None,
               operation=lambda: expand_group(['Group 1', 'Group 2']),
               op_res={group_1_suid, group_2_suid},
               post_state=[(group_1_suid, False), (group_2_suid, False), (group_3_suid, False)])

        # Verify collapsing two specific groups (in list) doesn't affect the third
        verify(pre_conditioning=lambda: None,
               operation=lambda: collapse_group(['SUID:' + str(group_1_suid), 'SUID:' + str(group_2_suid)]),
               op_res={group_1_suid, group_2_suid},
               post_state=[(group_1_suid, True), (group_2_suid, True), (group_3_suid, False)])

        # Verify expanding two specific groups (in list) doesn't affect the third
        verify(pre_conditioning=lambda: None,
               operation=lambda: expand_group(['SUID:' + str(group_1_suid), 'SUID:' + str(group_2_suid)]),
               op_res={group_1_suid, group_2_suid},
               post_state=[(group_1_suid, False), (group_2_suid, False), (group_3_suid, False)])

        # Verify collapsing two specific groups (in string) doesn't affect the third
        verify(pre_conditioning=lambda: None,
               operation=lambda: collapse_group('Group 1,Group 2'),
               op_res={group_1_suid, group_2_suid},
               post_state=[(group_1_suid, True), (group_2_suid, True), (group_3_suid, False)])

        # Verify expanding two specific groups (in string) doesn't affect the third
        verify(pre_conditioning=lambda: None,
               operation=lambda: expand_group('Group 1,Group 2'),
               op_res={group_1_suid, group_2_suid},
               post_state=[(group_1_suid, False), (group_2_suid, False), (group_3_suid, False)])

        # Verify collapsing all groups works
        verify(pre_conditioning=lambda: None,
               operation=lambda: collapse_group('all'),
               op_res={group_1_suid, group_2_suid, group_3_suid},
               post_state=[(group_1_suid, True), (group_2_suid, True), (group_3_suid, True)])

        # Verify expanding two specific groups (in string) doesn't affect the third
        verify(pre_conditioning=lambda: None,
               operation=lambda: expand_group('all'),
               op_res={group_1_suid, group_2_suid, group_3_suid},
               post_state=[(group_1_suid, False), (group_2_suid, False), (group_3_suid, False)])

        self.assertRaises(CyError, collapse_group, -1)
        self.assertRaises(CyError, expand_group, -1)
        self.assertRaises(CyError, collapse_group, 'Bogus Group')
        self.assertRaises(CyError, expand_group, 'Bogus Group')
        self.assertRaises(CyError, collapse_group, 'Group 1', network='Bogus')
        self.assertRaises(CyError, expand_group, 'Group 1', network='Bogus')

    
    @print_entry_exit
    def test_create_group_by_column(self):
        # Initialization
        load_test_session()
        # Create Cluster column and assign nodes to cluster identifiers
        all_nodes = list(get_table_columns(columns=['name'])['name'])
        all_nodes.sort()  # A cheap way of getting a consistent ordering from run to run
        test_data = df.DataFrame(data={'id': all_nodes, 'Cluster': '' * len(all_nodes)})
        res = load_table_data(test_data, data_key_column='id', table='node', table_key_column='name')
        self.assertEqual(res, 'Success: Data loaded in defaultnode table')
        # TODO: Suggestion for new functionality ... create_column(colname, default_val, [(rowID, newVal)]) or similar
        test_data = df.DataFrame(
            data={'id': ['GDS1', 'PFK27', 'PDC1', 'FBP1', 'CIN4'], 'Cluster': ['A', 'A', 'B', 'B', 'B']})
        res = load_table_data(test_data, data_key_column='id', table='node', table_key_column='COMMON')
        self.assertEqual(res, 'Success: Data loaded in defaultnode table')
        # For each cluster, figure out what the selected nodes and external edges should be
        select_nodes(['GDS1', 'PFK27'], by_col='COMMON')
        selection_GDS1_PFK27 = select_edges_adjacent_to_selected_nodes()
        select_nodes(['PDC1', 'FBP1', 'CIN4'], by_col='COMMON', preserve_current_selection=False)
        selection_PDC1_FBP1_CIN4 = select_edges_adjacent_to_selected_nodes()
        clear_selection()

        # Verify that cluster A goes into the right group
        group_a = create_group_by_column('Group A', 'Cluster', 'A')
        self._check_group_info('Group A', 'Group A', group_a['group'], set(selection_GDS1_PFK27['nodes']), set(),
                               set(selection_GDS1_PFK27['edges']))

        # Verify that cluster B goes into the right group
        group_b = create_group_by_column('Group B', 'Cluster', 'B')
        self._check_group_info('Group B', 'Group B', group_b['group'], set(selection_PDC1_FBP1_CIN4['nodes']), set(),
                               set(selection_PDC1_FBP1_CIN4['edges']))

        # Verify that when the value ('C') doesn't exist, an empty group is created
        group_c = create_group_by_column('Group C', 'Cluster', 'C')
        self._check_group_info('Group C', 'Group C', group_c['group'], set(), set(), set())

        # Verify that when the column ('bogus') doesn't exist, an empty group is created
        group_d = create_group_by_column('Group D', 'bogus', 'C')
        self._check_group_info('Group D', 'Group D', group_d['group'], set(), set(), set())

        self.assertRaises(CyError, create_group_by_column, 'Group 1', network='Bogus')

    
    @print_entry_exit
    def test_remove_from_group(self):
        # Initialization
        load_test_session()
        select_nodes(['GDS1', 'PFK27'], by_col='COMMON')
        selection_GDS1_PFK27 = select_edges_adjacent_to_selected_nodes()
        select_nodes(['GDS1'], by_col='COMMON', preserve_current_selection=False)
        selection_GDS1_node = select_edges_adjacent_to_selected_nodes()
        clear_selection()

        # Verify that test group has right nodes, internal edges and external edges
        group_0 = create_group('group 0', nodes=selection_GDS1_PFK27['nodes'])['group']
        self._check_group_info(group='group 0',
                               expected_name='group 0',
                               expected_suid=group_0,
                               expected_nodes=set(selection_GDS1_PFK27['nodes']),
                               expected_internal_edges=set(),
                               expected_external_edges=set(selection_GDS1_PFK27['edges']))

        # Verify that removing GDS1 and its edges results in only PFK27 and its edges
        self.assertDictEqual(remove_from_group('group 0', nodes=['GDS1'], nodes_by_col='COMMON'), {})
        self._check_group_info(group='group 0',
                               expected_name='group 0',
                               expected_suid=group_0,
                               expected_nodes=set(selection_GDS1_PFK27['nodes']) - set(selection_GDS1_node['nodes']),
                               expected_internal_edges=set(),
                               expected_external_edges=set(selection_GDS1_PFK27['edges']) - set(selection_GDS1_node['edges']))

        # Verify that removing the PFK27 edges leaves only the PFK27 node
        self.assertDictEqual(remove_from_group('group 0',
                                               nodes=[],
                                               edges=list(set(selection_GDS1_PFK27['edges']) - set(selection_GDS1_node['edges']))),
                             {})
        self._check_group_info(group='group 0',
                               expected_name='group 0',
                               expected_suid=group_0,
                               expected_nodes=set(selection_GDS1_PFK27['nodes']) - set(selection_GDS1_node['nodes']),
                               expected_internal_edges=set(),
                               expected_external_edges=set())

        # Verify that operating on an unknown group does nothing
        self.assertDictEqual(remove_from_group('bogus group'), {})

        self.assertRaises(CyError, remove_from_group, 'group x', network='Bogus')

    
    @print_entry_exit
    def test_delete_group(self):
        # Initialization
        load_test_session()
        select_nodes(['GDS1', 'PFK27'], by_col='COMMON')
        selection = select_edges_adjacent_to_selected_nodes()
        clear_selection()

        # Create a group out of just 2 selected nodes
        select_nodes(selection['nodes'])
        group_1_suid = self._check_whole_group('group 1', lambda x: create_group(x), selection)
        group_2_suid = self._check_whole_group('group 2', lambda x: create_group(x), selection)
        group_3_suid = self._check_whole_group('group 3', lambda x: create_group(x), selection)
        self.assertSetEqual(set(list_groups()['groups']), {group_1_suid, group_2_suid, group_3_suid})

        # Delete the first two groups (by name), leaving the third
        self.assertSetEqual(set(delete_group(['Group 1', 'Group 2'], groups_by_col='shared name')['groups']),
                            {group_1_suid, group_2_suid})
        self.assertSetEqual(set(list_groups()['groups']), {group_3_suid})

        # Delete the last by SUID
        self.assertSetEqual(set(delete_group([group_3_suid])['groups']), {group_3_suid})
        self.assertSetEqual(set(list_groups()['groups']), set())

        # Try deleting the third group again, and verify that nothing is deleted
        self.assertSetEqual(set(delete_group([group_3_suid])['groups']), set())

        # Add all of the groups back in and select 2 of them, leaving one unselected
        select_nodes(selection['nodes'])
        group_1_suid = self._check_whole_group('group 1', lambda x: create_group(x), selection)
        group_2_suid = self._check_whole_group('group 2', lambda x: create_group(x), selection)
        group_3_suid = self._check_whole_group('group 3', lambda x: create_group(x), selection)
        self.assertSetEqual(set(list_groups()['groups']), {group_1_suid, group_2_suid, group_3_suid})
        select_nodes([group_1_suid, group_2_suid], preserve_current_selection=False)

        # Delete 2 selected groups, which should leave one group left
        self.assertSetEqual(set(delete_group(groups='selected')['groups']), {group_1_suid, group_2_suid})
        self.assertSetEqual(set(list_groups()['groups']), {group_3_suid})

        # Delete unselected groups, which should leave no group left
        self.assertSetEqual(set(delete_group(groups='unselected')['groups']), {group_3_suid})
        self.assertSetEqual(set(list_groups()['groups']), set())

        # Add all of the groups back in
        select_nodes(selection['nodes'])
        group_1_suid = self._check_whole_group('group 1', lambda x: create_group(x), selection)
        group_2_suid = self._check_whole_group('group 2', lambda x: create_group(x), selection)
        group_3_suid = self._check_whole_group('group 3', lambda x: create_group(x), selection)
        self.assertSetEqual(set(list_groups()['groups']), {group_1_suid, group_2_suid, group_3_suid})

        # Delete all groups, which should leave no group left
        self.assertSetEqual(set(delete_group(groups='all')['groups']), {group_1_suid, group_2_suid, group_3_suid})
        self.assertSetEqual(set(list_groups()['groups']), set())

        self.assertRaises(CyError, delete_group, network='bogus')

    def _check_whole_group(self, group_name, group_create_func, selection):
        group = group_create_func(group_name)
        self.assertIsInstance(group, dict)
        self.assertIsInstance(group['group'], int)
        group_id = group['group']
        return self._check_group_info(group_name, group_name, group_id, set(selection['nodes']), set(),
                                      set(selection['edges']))

    def _check_group_info(self, group, expected_name, expected_suid, expected_nodes, expected_internal_edges,
                          expected_external_edges):
        group_info = get_group_info(group)
        self.assertIsInstance(group_info, dict)
        if expected_suid: self.assertEqual(group_info['group'], expected_suid)
        self.assertEqual(group_info['name'], expected_name)
        self.assertSetEqual(set(group_info['nodes']), expected_nodes)
        self.assertSetEqual(set(group_info['internalEdges']), expected_internal_edges)
        self.assertSetEqual(set(group_info['externalEdges']), expected_external_edges)
        self.assertFalse(group_info['collapsed'])
        return group_info['group']


if __name__ == '__main__':
    unittest.main()
