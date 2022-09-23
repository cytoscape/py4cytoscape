# -*- coding: utf-8 -*-

""" A brief sanity test to verify a good connection.
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


import os
import unittest
import math

from test_utils import *


class SanityTests(unittest.TestCase):

    if os.environ.get('TESTS_FOLDER'):
        path=os.environ.get('TESTS_FOLDER')+"/"
    else:
        path=""

    def setUp(self):
        close_session(False)
        pass

    def tearDown(self):
        pass

    @print_entry_exit
    def test_open_session(self,path=path):
        # Verify that the default network is loaded
        self.assertDictEqual(open_session(), {})
        self.assertEqual(get_network_count(), 1)
        self.assertEqual(get_network_name(), 'galFiltered.sif')

        # Verify that file opens if a direct filename is used
        self.assertDictEqual(open_session(path+'data/Affinity Purification.cys'), {})
        self.assertEqual(get_network_count(), 1)
        self.assertEqual(get_network_name(), 'HIV-human PPI')

    @print_entry_exit
    def test_create_network_from_data_frames(self):
        node_data = {'id': ["node 0", "node 1", "node 2", "node 3"],
                     'group': ["A", "A", "B", "B"],
                     'score': [20, 10, 15, 5]}
        nodes = df.DataFrame(data=node_data, columns=['id', 'group', 'score'])
        edge_data = {'source': ["node 0", "node 0", "node 0", "node 2"],
                     'target': ["node 1", "node 2", "node 3", "node 3"],
                     'interaction': ["inhibits", "interacts", "activates", "interacts"],
                     'weight': [5.1, 3.0, 5.2, 9.9]}
        edges = df.DataFrame(data=edge_data, columns=['source', 'target', 'interaction', 'weight'])

        # Verify that a network can be created containing dataframe encoding both nodes and edges
        res = create_network_from_data_frames(nodes, edges, title='From node & edge dataframe')
        suid_1 = res
        self.assertEqual(get_network_name(suid_1), 'From node & edge dataframe')
        self.assertEqual(get_node_count(suid_1), 4)
        self.assertEqual(get_edge_count(suid_1), 4)
        self.assertSetEqual(set(get_all_nodes(suid_1)), set(['node 0', 'node 1', 'node 2', 'node 3']))
        self.assertSetEqual(set(get_all_edges(suid_1)), set(
            ['node 0 (inhibits) node 1', 'node 0 (interacts) node 2', 'node 0 (activates) node 3',
             'node 2 (interacts) node 3']))
        self.assertSetEqual(set(get_table_column_names('node', network=suid_1)),
                            set(['SUID', 'shared name', 'id', 'score', 'group', 'name', 'selected']))
        self.assertSetEqual(set(get_table_column_names('edge', network=suid_1)), set(
            ['SUID', 'shared name', 'shared interaction', 'source', 'target', 'data.key.column', 'weight', 'name',
             'selected', 'interaction']))
        self.assertDictEqual(get_table_column_types('node', network=suid_1),
                             {'SUID': 'Long', 'shared name': 'String', 'id': 'String', 'score': 'Integer',
                              'group': 'String', 'name': 'String', 'selected': 'Boolean'})
        self.assertDictEqual(get_table_column_types('edge', network=suid_1),
                             {'SUID': 'Long', 'shared name': 'String', 'shared interaction': 'String',
                              'source': 'String', 'target': 'String', 'data.key.column': 'Integer', 'weight': 'Double',
                              'name': 'String', 'selected': 'Boolean', 'interaction': 'String'})

    @print_entry_exit
    def test_import_network_from_file(self,path=path):

        # Verify that test network loads from test data directory
        res = import_network_from_file(path+'data/galFiltered.sif')
        self.assertIsInstance(res['networks'], list)
        self.assertEqual(len(res['networks']), 1)
        self.assertIsInstance(res['views'], list)
        self.assertEqual(len(res['views']), 1)

        # Verify that default network loads
        res = import_network_from_file()
        self.assertIsInstance(res['networks'], list)
        self.assertEqual(len(res['networks']), 1)
        self.assertIsInstance(res['views'], list)
        self.assertEqual(len(res['views']), 1)

    @print_entry_exit
    def test_create_igraph_from_network(self):
        # Initialization
        load_test_session()
        all_nodes = get_all_nodes()
        all_edges = get_all_edges()

        i = create_igraph_from_network()

        # verify that all nodes are present
        self.assertEqual(len(i.vs), len(all_nodes))
        self.assertNotIn(False, [v['name'] in all_nodes for v in i.vs])

        # verify that all edges are present
        self.assertEqual(len(i.es), len(all_edges))
        i_edges = [[x['source'], x['target']] for x in i.es]
        self.assertNotIn(False, [re.split("\ \\(.*\\)\ ", x) in i_edges for x in all_edges])

    @print_entry_exit
    def test_create_networkx_from_network(self):
        # Initialization
        load_test_session()
        self.maxDiff = None

        def normalize_dict(dict_val):
            # When comparing dicts, we can't be sure of the key ordering, and we don't know whether
            # some values could be 'nan'. So, to get the comparison right (because nan != nan), we
            # compare string values.
            return str({k:dict_val[k]  for k in sorted(dict_val)})


        cyedge_table = tables.get_table_columns('edge')
        cynode_table = tables.get_table_columns('node')
        cynode_table.set_index('name', inplace=True) # Index by 'name' instead of SUID ... drop 'name' from attributes

        # Verify that the networkx returns the right number of rows and columns
        netx = create_networkx_from_network()
        self.assertEqual(netx.number_of_nodes(), len(cynode_table.index))
        self.assertEqual(netx.number_of_edges(), len(cyedge_table.index))

        # Verify that all edges are present, and all of their attributes are correct
        # Note that edge SUIDs are carried to distinguish multiple edges that connect the same nodes
        netx_out_edges = netx.out_edges(data=True, keys=True)
        for src_node, targ_node, edge_suid, edge_attrs in netx_out_edges:
            self.assertEqual(normalize_dict(edge_attrs), normalize_dict(dict(cyedge_table.loc[edge_suid])))

        # Verify that all nodes are present, and all attributes are correct. Note that node YER056CA has 'nan' values,
        # so this verifies that nan is carried into the networkx. (The dictionary comparison is done as as
        # str() comparison because two nan values don't compare directly as equal.)
        netx_nodes = netx.nodes(data=True)
        for node_name, node_attrs in netx_nodes:
            self.assertEqual(normalize_dict(node_attrs), normalize_dict(dict(cynode_table.loc[node_name])))

        # Verify that invalid network is caught
        self.assertRaises(CyError, create_networkx_from_network, network='BogusNetwork')


    @print_entry_exit
    def test_create_network_from_networkx(self):
        # Initialization
        load_test_session()
        cyedge_table = tables.get_table_columns('edge')
        cyedge_table.set_index('name', inplace=True)  # Index by 'name' instead of SUID ... drop 'name' from attributes
        cyedge_table.sort_index(inplace=True)
        cynode_table = tables.get_table_columns('node')
        cynode_table.set_index('name', inplace=True)  # Index by 'name' instead of SUID ... drop 'name' from attributes
        cynode_table.sort_index(inplace=True)

        def compare_table(orig_table, table_name, network):
            # Compare nodes in new Cytoscape network created from NetworkX to those in the original Cytoscape network
            # Start by lining up the dataframe rows for each
            netx_table = tables.get_table_columns(table_name, network=network)
            netx_table.set_index('name', inplace=True)  # Index by 'name' to match up with orig_table
            netx_table.sort_index(inplace=True)

            # Verify that the new network has at least the columns of the original. There may be a few more if they were
            # created for reference.
            orig_table_cols = set(orig_table.columns)
            netx_table_cols = set(netx_table.columns)
            self.assertTrue(orig_table_cols <= netx_table_cols)

            # Create a vector showing which new columns are the same as the original columns. Use .equals() to compare 'nan' properly.
            s = [orig_table[col].equals(netx_table[col]) for col in orig_table_cols - {'SUID'}]
            self.assertFalse(False in s)

        # Get the NetworkX for a known good network galFiltered.sif and send it to Cytoscape as a new network
        netx = create_networkx_from_network()
        netx_suid = create_network_from_networkx(netx)
        self.assertEqual(netx_suid, get_network_suid())  # Verify that the new network is the selected network

        compare_table(cynode_table, 'node', netx)
        compare_table(cyedge_table, 'edge', netx)

    @print_entry_exit
    def test_create_network_from_igraph(self):
        # Initialization
        load_test_session()

        # TODO: Consider allowing creation of a network from an empty igraph
        # This will fail but probably should not ... create_network_from_igraph requires nodes and edges, but shouldn't
        #        g = ig.Graph()
        #        create_network_from_igraph(g)

        cur_igraph = create_igraph_from_network()

        new_SUID = create_network_from_igraph(cur_igraph)
        new_igraph = create_igraph_from_network(new_SUID)

        self.assertEqual(get_network_name(new_SUID), 'From igraph')

        # Verify that all nodes in the new network are present along with their attributes. This doesn't test
        # whether there are extra attributes on the nodes ... there well may be because of the extra ``id`` attribute
        # added by ``create_network_from_igraph()``.
        self._check_igraph_attributes(cur_igraph.vs, new_igraph.vs)

        # Verify that all edges in the new network are present along with their attributes. This doesn't test
        # whether there are extra attributes on the edges ... there well may be because of the extra ``data.key`` attribute
        # added by ``create_network_from_igraph()``.
        self._check_igraph_attributes(cur_igraph.es, new_igraph.es)

    def _check_igraph_attributes(self, original_collection, new_collection):
        def vals_eq(name, e_cur_key, val1, val2):
            eq = type(val1) is type(val2) and \
                 ((val1 == val2) or \
                  (type(val1) is float and math.isnan(val1) and math.isnan(val2)))
            if not eq:
                print('For ' + name + ', key ' + e_cur_key + ': ' + str(val1) + ' != ' + str(val2))
            return eq

        for orig in original_collection:
            new = new_collection.find(name=orig['name'])
            self.assertFalse(
                False in [vals_eq(orig['name'], e_cur_key, orig[e_cur_key], new[e_cur_key]) for e_cur_key in
                          orig.attributes().keys()])

if __name__ == '__main__':
    unittest.main()
