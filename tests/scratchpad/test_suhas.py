# -*- coding: utf-8 -*-

""" Test functions in style_mappings.py.
"""

import unittest
import pandas as df
import igraph as ig

from requests import RequestException

from test_utils import *

class MyTestCase(unittest.TestCase):
    def setUp(self):
        try:
            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    @print_entry_exit
    def test_ui(self):

        def rename_dup_columns(col_list, col_name):
            # See if a column name exists, and if so, rename all other same-name columns.
            # Especially important for graphs that come with a ``source`` or ``target`` name
            # created by get_edge_dataframe (which creates these columns) when these columns
            # were already in the graph as a result of creating the graph from a Cytoscape
            # network.
            first_index = col_list.index(col_name)
            replacement_name = col_name + '.original'
            new_cols = [replacement_name if i != first_index and col_list[i] == col_name else col_list[i] for i in
                        range(len(col_list))]
            return new_cols

        # Read test network in as a DataFrame
        df_test = df.read_csv('../data/module_df.txt', sep='\t')

        # Convert the DataFrame into an iGraph
        ig_test = ig.Graph.DataFrame(df_test, directed=False)

        # Send iGraph to Cytoscape ... note that Source and Target columns get added to edge attributes
        test_suid = create_network_from_igraph(ig_test)['networkSUID']

        # Get iGraph back from Cytoscape (with Source and Target columns)
        ig_cytoscape = create_igraph_from_network(test_suid)

        # Convert iGraph to DataFrame ... note that iGraph creates its own Source and Target edge attributes
        df_cytoscape_edges = ig_cytoscape.get_edge_dataframe()
        df_cytoscape_nodes = ig_cytoscape.get_vertex_dataframe()

        # Rename the Cytoscape Source and Target attributes so they're not in the way
        edge_col_names = rename_dup_columns(list(df_cytoscape_edges.columns), 'source')
        df_cytoscape_edges.columns = rename_dup_columns(edge_col_names, 'target')

        # Convert iGraph vertex identifiers into vertex names
        df_cytoscape_edges['source'].replace(df_cytoscape_nodes['name'], inplace=True)
        df_cytoscape_edges['target'].replace(df_cytoscape_nodes['name'], inplace=True)

        # Extract the edge values from the original test file ... and compare them to what Cytoscape has
        dict_test = {(row.V1, row.V2): row.e_color  for row in df_test.itertuples()}
        dict_cytoscape_edges = {(row.source, row.target): row.e_color  for row in df_cytoscape_edges.itertuples()}
        self.assertDictEqual(dict_test, dict_cytoscape_edges)


if __name__ == '__main__':
    unittest.main()