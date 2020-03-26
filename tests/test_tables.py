# -*- coding: utf-8 -*-

import unittest
import pandas as df
from requests import HTTPError
from PyCy3 import *
from PyCy3.decorators import *

class TablesTests(unittest.TestCase):

    def setUp(self):
        try:
            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

#    @skip
    @print_entry_exit
    def test_delete_table_column(self):
        # Initialization
        self._load_test_session()

        def check_delete(table, column):
            columns = set(get_table_column_names(table=table))
            self.assertEqual(delete_table_column(table=table, column=column), '')
            columns.discard(column)
            fewer_columns = set(get_table_column_names(table=table))
            self.assertSetEqual(set(columns), set(fewer_columns))

        check_delete('node', 'BetweennessCentrality')
        check_delete('edge', 'EdgeBetweenness')
        check_delete('node', 'boguscolumn')
        self.assertRaises(HTTPError, delete_table_column, table='bogustable', column='boguscolumn')

        self.assertRaises(CyError, get_table_column_names, network='bogus')

#    @skip
    @print_entry_exit
    def test_get_table_columns(self):
        # Initialization
        self._load_test_session()

        # Verify that an empty column list returns all columns, and all columns have at least one non-nan value
        df = get_table_columns()
        self.assertSetEqual(set(df.columns), {'BetweennessCentrality', 'gal1RGexp', 'Eccentricity', 'Stress', 'NumberOfDirectedEdges', 'NeighborhoodConnectivity', 'NumberOfUndirectedEdges', 'selected', 'gal4RGsig', 'Degree', 'gal80Rsig', 'SUID', 'gal80Rexp', 'TopologicalCoefficient', 'ClusteringCoefficient', 'Radiality', 'gal4RGexp', 'gal1RGsig', 'name', 'degree.layout', 'ClosenessCentrality', 'COMMON', 'AverageShortestPathLength', 'shared name', 'PartnerOfMultiEdgedNodePairs', 'SelfLoops', 'isExcludedFromPaths', 'IsSingleNode'})
        self.assertEqual(len(df.index), get_node_count())
        self.assertNotIn(False, [True in list(df[col].notnull())   for col in df.columns])

        # Verify that an explicity column list returns exact columns, and each has at least one non-nan value
        df = get_table_columns(columns=['gal1RGexp', 'Eccentricity', 'Stress'])
        self.assertSetEqual(set(df.columns), {'gal1RGexp', 'Eccentricity', 'Stress'})
        self.assertEqual(len(df.index), get_node_count())
        self.assertNotIn(False, [True in list(df[col].notnull())   for col in df.columns])

        # Verify that a column list as a comma-separated string returns exact columns, and each has at least one non-nan value
        df = get_table_columns(columns='Stress, NumberOfDirectedEdges')
        self.assertSetEqual(set(df.columns), {'Stress', 'NumberOfDirectedEdges'})
        self.assertEqual(len(df.index), get_node_count())
        self.assertNotIn(False, [True in list(df[col].notnull())   for col in df.columns])

        # Verify that a bogus column name still returns a column, though it must be all nan
        df = get_table_columns(columns='Stress, bogus')
        self.assertSetEqual(set(df.columns), {'Stress', 'bogus'})
        self.assertEqual(len(df.index), get_node_count())
        self.assertTrue(True in list(df['Stress'].notnull()))
        self.assertFalse(False in df['bogus'].isnull())

        # Verify that an empty column list returns all columns for edges, too
        df = get_table_columns(table='edge')
        self.assertSetEqual(set(df.columns), {'SUID', 'shared name', 'shared interaction', 'name', 'selected', 'interaction', 'EdgeBetweenness'})
        self.assertEqual(len(df.index), get_edge_count())

        self.assertRaises(HTTPError, get_table_columns, table='bogustable', columns='boguscolumn')
        self.assertRaises(CyError, get_table_columns, network='bogus')


#    @skip
    @print_entry_exit
    def test_get_table_value(self):
        # Initialization
        self._load_test_session()

        self.assertEqual(get_table_value('node', 'YDL194W', 'gal1RGexp'), 0.139)
        self.assertEqual(get_table_value('node', 'YDL194W', 'Degree'), 1)
        self.assertFalse(get_table_value('node', 'YDL194W', 'IsSingleNode'))
        self.assertEqual(get_table_value('node', 'YDL194W', 'COMMON'), 'SNF3')

        self.assertEqual(get_table_value('edge', 'YLR197W (pp) YOR310C', 'EdgeBetweenness'), 2.0)
        self.assertEqual(get_table_value('network', 'galFiltered.sif', 'publication'),
                         'Integrated Genomic and Proteomic Analyses of a Systematically Perturbed Metabolic Network\n' 
                         'Trey Ideker, Vesteinn Thorsson, Jeffrey A. Ranish, Rowan Christmas, Jeremy Buhler, Jimmy K. Eng, Roger Bumgarner, David R. Goodlett, Ruedi Aebersold, and Leroy Hood\n' 
                         'Science 4 May 2001: 292 (5518), 929-934. [DOI:10.1126/science.292.5518.929]')

        # TODO: Fetching a None number raises an error, but should really return a None ... can this be changed?
        # TODO: Find out if a null string in Cytoscape is the same thing as a None
        self.assertRaises(HTTPError, get_table_value, 'node', 'YER056CA', 'gal1RGexp')
        self.assertIsNone(get_table_value('node', 'YER056CA', 'COMMON'))

        self.assertRaises(CyError, get_table_value, 'node', 'YDL194W', 'gal1RGexp', network='bogus')

#    @skip
    @print_entry_exit
    def test_get_table_column_names(self):
        # Initialization
        self._load_test_session()

        self.assertSetEqual(set(get_table_column_names()), {'SUID', 'shared name', 'name', 'selected', 'AverageShortestPathLength', 'BetweennessCentrality', 'ClosenessCentrality', 'ClusteringCoefficient', 'Degree', 'Eccentricity', 'IsSingleNode', 'NeighborhoodConnectivity', 'NumberOfDirectedEdges', 'NumberOfUndirectedEdges', 'PartnerOfMultiEdgedNodePairs', 'Radiality', 'SelfLoops', 'Stress', 'TopologicalCoefficient', 'degree.layout', 'COMMON', 'gal1RGexp', 'gal4RGexp', 'gal80Rexp', 'gal1RGsig', 'gal4RGsig', 'gal80Rsig', 'isExcludedFromPaths'})
        self.assertSetEqual(set(get_table_column_names('edge')), {'SUID', 'shared name', 'shared interaction', 'name', 'selected', 'interaction', 'EdgeBetweenness'})
        self.assertSetEqual(set(get_table_column_names('network')), {'SUID', 'shared name', 'name', 'selected', '__Annotations', 'publication', 'Dataset Name', 'Dataset URL'})
        self.assertRaises(HTTPError, get_table_column_names, 'library')

        self.assertRaises(CyError, get_table_column_names, network='bogus')

#    @skip
    @print_entry_exit
    def test_get_table_column_types(self):
        # Initialization
        self._load_test_session()

        self.assertDictEqual(get_table_column_types(), {'SUID': 'Long', 'shared name': 'String', 'name': 'String', 'selected': 'Boolean', 'AverageShortestPathLength': 'Double', 'BetweennessCentrality': 'Double', 'ClosenessCentrality': 'Double', 'ClusteringCoefficient': 'Double', 'Degree': 'Integer', 'Eccentricity': 'Integer', 'IsSingleNode': 'Boolean', 'NeighborhoodConnectivity': 'Double', 'NumberOfDirectedEdges': 'Integer', 'NumberOfUndirectedEdges': 'Integer', 'PartnerOfMultiEdgedNodePairs': 'Integer', 'Radiality': 'Double', 'SelfLoops': 'Integer', 'Stress': 'Long', 'TopologicalCoefficient': 'Double', 'degree.layout': 'Integer', 'COMMON': 'String', 'gal1RGexp': 'Double', 'gal4RGexp': 'Double', 'gal80Rexp': 'Double', 'gal1RGsig': 'Double', 'gal4RGsig': 'Double', 'gal80Rsig': 'Double', 'isExcludedFromPaths': 'Boolean'})
        self.assertDictEqual(get_table_column_types('edge'), {'SUID': 'Long', 'shared name': 'String', 'shared interaction': 'String', 'name': 'String', 'selected': 'Boolean', 'interaction': 'String', 'EdgeBetweenness': 'Double'})
        self.assertDictEqual(get_table_column_types('network'), {'SUID': 'Long', 'shared name': 'String', 'name': 'String', 'selected': 'Boolean', '__Annotations': 'List', 'publication': 'String', 'Dataset Name': 'String', 'Dataset URL': 'String'})
        self.assertRaises(HTTPError, get_table_column_types, 'library')

        self.assertRaises(CyError, get_table_column_types, 'edge', network='bogus')

#    @skip
    @print_entry_exit
    def test_load_table_data(self):
        # Initialization
        self._load_test_session()
        column_names = get_table_column_names()

        # Verify that adding into rows that don't exist fails
        unrelated_data = df.DataFrame(data={'id':['New1','New2','New3'], 'newcol':[1,2,3]})
        res = load_table_data(unrelated_data, data_key_column='id', table='node', table_key_column='name')
        self.assertEqual(res, 'Failed to load data: Provided key columns do not contain any matches')

        # Verify that adding into rows that do exist succeeds
        test_data = df.DataFrame(data={'id':['YDL194W','YDR277C','YBR043C'], 'newcol':[1,2,3]})
        res = load_table_data(test_data, data_key_column='id', table='node', table_key_column='name')
        self.assertEqual(res, 'Success: Data loaded in defaultnode table')

        # Verify that ID column and newcol were added, and that the newcols have values only for the named nodes
        data = get_table_columns()
        self.assertEqual(len(column_names) + 2, len(data.columns))
        self.assertIn('id', data.columns)
        self.assertIn('newcol', data.columns)
        added_data = data[data['name'] == data['id']]
        self.assertEqual(len(test_data.index), len(added_data.index))
        verify_each_newcol_value = [added_data[added_data['id'] == row['id']].iloc[0]['newcol'] == row['newcol']  for row_index, row in test_data.iterrows()]
        self.assertNotIn(False, verify_each_newcol_value)

        self.assertRaises(HTTPError, load_table_data, data, table='bogus')
        self.assertRaises(HTTPError, load_table_data, data, namespace='bogus')
        self.assertRaises(CyError, load_table_data, data, network='bogus')

    #    @skip
    @print_entry_exit
    def test_map_table_column(self):
        # Initialization
        self._load_test_session()

        # Verify that mapping Yeast from Ensembl to SGD produces a complete (name, SGD) mapping and that exactly one symbol isn't mapped
        df = map_table_column('name', 'Yeast', 'Ensembl', 'SGD')
        self.assertSetEqual({'name', 'SGD'}, set(df.columns))
        self.assertEqual(get_node_count(), len(df.index))
        self.assertSetEqual(set(df['name']), set(get_table_columns('node', ['name'])['name']))
        empty_mapping = df[df['SGD'].isnull()]
        self.assertEqual(len(empty_mapping.index), 1)
        self.assertEqual(empty_mapping.iloc[0]['name'], 'YER056CA')

        # Verify that mapping a non-existent column and other bad parameters are caught
        self.assertRaises(CyError, map_table_column, 'bogusname', 'Yeast', 'Ensembl', 'SGD')
        self.assertRaises(CyError, map_table_column, 'name', 'bogus', 'Ensembl', 'SGD')
        self.assertRaises(CyError, map_table_column, 'name', 'Yeast', 'bogus', 'SGD')
        self.assertRaises(CyError, map_table_column, 'name', 'Yeast', 'Ensembl', 'bogus')

        self.assertRaises(HTTPError, map_table_column, 'name', 'Yeast', 'Ensembl', 'SGD', table='bogus')
        self.assertRaises(HTTPError, map_table_column, 'name', 'Yeast', 'Ensembl', 'SGD', namespace='bogus')
        self.assertRaises(CyError, map_table_column, 'name', 'Yeast', 'Ensembl', 'SGD', network='bogus')

    #    @skip
    @print_entry_exit
    def test_rename_table_column(self):
        # Initialization
        self._load_test_session()

        # Verify that the rename reports OK and the column name is actually changed
        orig_columns = set(get_table_column_names())
        expected_columns = orig_columns.copy()
        expected_columns.discard('AverageShortestPathLength')
        expected_columns.add('xAveragex')
        self.assertEqual(rename_table_column('AverageShortestPathLength', 'xAveragex'), '')
        self.assertSetEqual(set(get_table_column_names()), expected_columns)

        # Verify that invalid parameters raise exceptions
        self.assertRaises(HTTPError, rename_table_column, 'bogus', 'xAveragex')
        self.assertRaises(HTTPError, rename_table_column, '', 'xAveragex')
        self.assertRaises(HTTPError, rename_table_column, None, 'xAveragex')
        self.assertRaises(HTTPError, rename_table_column, 'xAveragex', '')
        # self.assertRaises(HTTPError, rename_table_column, 'xAveragex', None) # This should fail, but doesn't
        # TODO: CyREST shouldn't allow change of name to None ... it shows up as null in Cytoscape
        self.assertRaises(HTTPError, rename_table_column, 'xAveragex', 'name')

        self.assertRaises(CyError, rename_table_column, 'AverageShortestPathLength', 'xAveragex', network='bogus')
        self.assertRaises(HTTPError, rename_table_column, 'AverageShortestPathLength', 'xAveragex', namespace='bogus')
        self.assertRaises(HTTPError, rename_table_column, 'AverageShortestPathLength', 'xAveragex', table='bogus')

    def _load_test_session(self, session_filename=None):
        open_session(session_filename)


if __name__ == '__main__':
    unittest.main()

