# -*- coding: utf-8 -*-

""" Test functions in tables.py.
"""
import numpy as np

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
import pandas as df
from requests import HTTPError

from test_utils import *


class TablesTests(unittest.TestCase):

    def setUp(self):
        try:
            close_session(False)
#            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    
    @print_entry_exit
    def test_delete_table_column(self):
        # Initialization
        load_test_session()

        def check_delete(table, column):
            columns = set(get_table_column_names(table=table))
            self.assertEqual(delete_table_column(table=table, column=column), '')
            columns.discard(column)
            fewer_columns = set(get_table_column_names(table=table))
            self.assertSetEqual(set(columns), set(fewer_columns))

        check_delete('node', 'BetweennessCentrality')
        check_delete('edge', 'EdgeBetweenness')
        check_delete('node', 'boguscolumn')
        self.assertRaises(CyError, delete_table_column, table='bogustable', column='boguscolumn')

        self.assertRaises(CyError, get_table_column_names, network='bogus')

    
    @print_entry_exit
    def test_get_table_columns(self):
        # Initialization
        load_test_session()

        # Verify that an empty column list returns all columns, and all columns have at least one non-nan value
        df = get_table_columns()
        self.assertSetEqual(set(df.columns),
                            {'BetweennessCentrality', 'gal1RGexp', 'Eccentricity', 'Stress', 'NumberOfDirectedEdges',
                             'NeighborhoodConnectivity', 'NumberOfUndirectedEdges', 'selected', 'gal4RGsig', 'Degree',
                             'gal80Rsig', 'SUID', 'gal80Rexp', 'TopologicalCoefficient', 'ClusteringCoefficient',
                             'Radiality', 'gal4RGexp', 'gal1RGsig', 'name', 'degree.layout', 'ClosenessCentrality',
                             'COMMON', 'AverageShortestPathLength', 'shared name', 'PartnerOfMultiEdgedNodePairs',
                             'SelfLoops', 'isExcludedFromPaths', 'IsSingleNode'})
        self.assertEqual(len(df.index), get_node_count())
        self.assertNotIn(False, [True in list(df[col].notnull()) for col in df.columns])

        # Verify that an explicity column list returns exact columns, and each has at least one non-nan value
        df = get_table_columns(columns=['gal1RGexp', 'Eccentricity', 'Stress'])
        self.assertSetEqual(set(df.columns), {'gal1RGexp', 'Eccentricity', 'Stress'})
        self.assertEqual(len(df.index), get_node_count())
        self.assertNotIn(False, [True in list(df[col].notnull()) for col in df.columns])

        # Verify that a column list as a comma-separated string returns exact columns, and each has at least one non-nan value
        df = get_table_columns(columns='Stress, NumberOfDirectedEdges')
        self.assertSetEqual(set(df.columns), {'Stress', 'NumberOfDirectedEdges'})
        self.assertEqual(len(df.index), get_node_count())
        self.assertNotIn(False, [True in list(df[col].notnull()) for col in df.columns])

        # Verify that a bogus column name still returns a column, though it must be all nan
        df = get_table_columns(columns='Stress, bogus')
        self.assertSetEqual(set(df.columns), {'Stress', 'bogus'})
        self.assertEqual(len(df.index), get_node_count())
        self.assertTrue(True in list(df['Stress'].notnull()))
        self.assertFalse(False in df['bogus'].isnull())

        # Verify that an empty column list returns all columns for edges, too
        df = get_table_columns(table='edge')
        self.assertSetEqual(set(df.columns),
                            {'SUID', 'shared name', 'shared interaction', 'name', 'selected', 'interaction',
                             'EdgeBetweenness'})
        self.assertEqual(len(df.index), get_edge_count())

        self.assertRaises(CyError, get_table_columns, table='bogustable', columns='boguscolumn')
        self.assertRaises(CyError, get_table_columns, network='bogus')

    
    @print_entry_exit
    def test_get_table_value(self):
        # Initialization
        load_test_session()

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
        self.assertRaises(CyError, get_table_value, 'node', 'YER056CA', 'gal1RGexp')
        self.assertIsNone(get_table_value('node', 'YER056CA', 'COMMON'))

        self.assertRaises(CyError, get_table_value, 'node', 'YDL194W', 'gal1RGexp', network='bogus')

    
    @print_entry_exit
    def test_get_table_column_names(self):
        # Initialization
        load_test_session()

        self.assertSetEqual(set(get_table_column_names()),
                            {'SUID', 'shared name', 'name', 'selected', 'AverageShortestPathLength',
                             'BetweennessCentrality', 'ClosenessCentrality', 'ClusteringCoefficient', 'Degree',
                             'Eccentricity', 'IsSingleNode', 'NeighborhoodConnectivity', 'NumberOfDirectedEdges',
                             'NumberOfUndirectedEdges', 'PartnerOfMultiEdgedNodePairs', 'Radiality', 'SelfLoops',
                             'Stress', 'TopologicalCoefficient', 'degree.layout', 'COMMON', 'gal1RGexp', 'gal4RGexp',
                             'gal80Rexp', 'gal1RGsig', 'gal4RGsig', 'gal80Rsig', 'isExcludedFromPaths'})
        self.assertSetEqual(set(get_table_column_names('edge')),
                            {'SUID', 'shared name', 'shared interaction', 'name', 'selected', 'interaction',
                             'EdgeBetweenness'})
        self.assertSetEqual(set(get_table_column_names('network')),
                            {'SUID', 'shared name', 'name', 'selected', '__Annotations', 'publication', 'Dataset Name',
                             'Dataset URL'})
        self.assertRaises(CyError, get_table_column_names, 'library')

        self.assertRaises(CyError, get_table_column_names, network='bogus')

    
    @print_entry_exit
    def test_get_table_column_types(self):
        # Initialization
        load_test_session()

        self.assertDictEqual(get_table_column_types(),
                             {'SUID': 'Long', 'shared name': 'String', 'name': 'String', 'selected': 'Boolean',
                              'AverageShortestPathLength': 'Double', 'BetweennessCentrality': 'Double',
                              'ClosenessCentrality': 'Double', 'ClusteringCoefficient': 'Double', 'Degree': 'Integer',
                              'Eccentricity': 'Integer', 'IsSingleNode': 'Boolean',
                              'NeighborhoodConnectivity': 'Double', 'NumberOfDirectedEdges': 'Integer',
                              'NumberOfUndirectedEdges': 'Integer', 'PartnerOfMultiEdgedNodePairs': 'Integer',
                              'Radiality': 'Double', 'SelfLoops': 'Integer', 'Stress': 'Long',
                              'TopologicalCoefficient': 'Double', 'degree.layout': 'Integer', 'COMMON': 'String',
                              'gal1RGexp': 'Double', 'gal4RGexp': 'Double', 'gal80Rexp': 'Double',
                              'gal1RGsig': 'Double', 'gal4RGsig': 'Double', 'gal80Rsig': 'Double',
                              'isExcludedFromPaths': 'Boolean'})
        self.assertDictEqual(get_table_column_types('edge'),
                             {'SUID': 'Long', 'shared name': 'String', 'shared interaction': 'String', 'name': 'String',
                              'selected': 'Boolean', 'interaction': 'String', 'EdgeBetweenness': 'Double'})
        self.assertDictEqual(get_table_column_types('network'),
                             {'SUID': 'Long', 'shared name': 'String', 'name': 'String', 'selected': 'Boolean',
                              '__Annotations': 'List', 'publication': 'String', 'Dataset Name': 'String',
                              'Dataset URL': 'String'})
        self.assertRaises(CyError, get_table_column_types, 'library')

        self.assertRaises(CyError, get_table_column_types, 'edge', network='bogus')

    @print_entry_exit
    def test_load_table_data_from_file(self):

        def check_table(original_columns, new_column_name, key_values, table_name='node'):
            # Make sure we get exactly the expected columns
            self.assertSetEqual(set(get_table_column_names(table=table_name)), original_columns | {new_column_name})

            # Make sure we get exactly the expected number of values in the new column
            table = get_table_columns(table=table_name, columns=['name', new_column_name])
            table.dropna(inplace=True)
            table.set_index('name', inplace=True)
            self.assertEqual(len(table.index), len(key_values))

            # Make sure the new column values are as expected
            for key, val in key_values:
                self.assertEqual(table[new_column_name][key], val)

        # Initialization
        load_test_session()
        node_column_names = set(get_table_column_names())
        edge_column_names = set(get_table_column_names(table='edge'))


        # Verify that a table with column headers can be loaded into the node table
        res = load_table_data_from_file('data/defaultnode_table.tsv', first_row_as_column_names=True)
        check_table(node_column_names, 'newcol', [('YDR277C', 2), ('YDL194W', 1), ('YBR043C', 3)])

        # Verify that a table with column headers can be loaded into the edge table
        res = load_table_data_from_file('data/defaultedge_table.tsv', first_row_as_column_names=True, table='edge')
        check_table(edge_column_names, 'newcol_e', [('YDR277C (pp) YDL194W', 1000), ('YDR277C (pp) YJR022W', 2000), ('YPR145W (pp) YMR117C', 3000)], table_name='edge')

        # Verify that a spreadsheet with column headers can be loaded into the node table
        load_test_session()
        res = load_table_data_from_file('data/defaultnode_table.xlsx', first_row_as_column_names=True)
        check_table(node_column_names, 'newcol', [('YDR277C', 2), ('YDL194W', 1), ('YBR043C', 3)])

        # Verify that a table with no header can be loaded into the node table
        load_test_session()
        res = load_table_data_from_file('data/defaultnode_table.no-header.tsv', first_row_as_column_names=False)
        check_table(node_column_names, '1', [('YDR277C', 2), ('YDL194W', 1), ('YBR043C', 3)])

        # Verify that a table with extra lines at the beginning can be loaded into the node table
        load_test_session()
        res = load_table_data_from_file('data/defaultnode_table.extra-lines.tsv', first_row_as_column_names=False, start_load_row=4)
        check_table(node_column_names, '1', [('YDR277C', 2), ('YDL194W', 1), ('YBR043C', 3)])

        # Verify that a table with different field delimiters can be loaded into the node table
        load_test_session()
        res = load_table_data_from_file('data/defaultnode_table.semi-delimiter.txt', first_row_as_column_names=False, delimiters=' ,;')
        check_table(node_column_names, '1', [('YDR277C', 2), ('YDL194W', 1), ('YBR043C', 3)])

        # Verify that a table with values in a different order can be loaded into the node table
        load_test_session()
        res = load_table_data_from_file('data/defaultnode_table.backwards.tsv', first_row_as_column_names=True, data_key_column_index=2)
        check_table(node_column_names, 'newcol', [('YDR277C', 2), ('YDL194W', 1), ('YBR043C', 3)])

        # Verify that a table with indexing on a different table column can be loaded into the node table
        load_test_session()
        res = load_table_data_from_file('data/defaultnode_table.COMMON.tsv', first_row_as_column_names=True, table_key_column='COMMON')
        check_table(node_column_names, 'newcol', [('YDR277C', 2), ('YDL194W', 1), ('YBR043C', 3)])

        self.assertRaises(CyError, load_table_data_from_file, 'bogus file name')
        self.assertRaises(CyError, load_table_data_from_file, 'data/defaultnode_table.tsv', start_load_row=-1)
        self.assertRaises(CyError, load_table_data_from_file, 'data/defaultnode_table.tsv', delimiters='bogus')
        self.assertRaises(CyError, load_table_data_from_file, 'data/defaultnode_table.tsv', data_key_column_index='newcol')
        self.assertRaises(CyError, load_table_data_from_file, 'data/defaultnode_table.tsv', data_key_column_index=-1)
        self.assertRaises(CyError, load_table_data_from_file, 'data/defaultnode_table.tsv', table_key_column='bogus column')


    @print_entry_exit
    def test_load_table_data(self):

        def check_values_added(table_column_names, table_key_name, test_data, data_key_name, data_value_name, table='node'):
            data = get_table_columns(table=table)
            self.assertEqual(len(table_column_names) + 2, len(data.columns))
            self.assertIn(data_key_name, data.columns)
            self.assertIn(data_value_name, data.columns)
            added_data = data[data[table_key_name] == data[data_key_name]]
            self.assertEqual(len(test_data.index), len(added_data.index))
            verify_each_newcol_value = [added_data[added_data[data_key_name] == row[data_key_name]].iloc[0][data_value_name] == row[data_value_name]
                                        for row_index, row in test_data.iterrows()]
            self.assertNotIn(False, verify_each_newcol_value)


        # Initialization
        load_test_session()

        # Verify that adding into rows that don't exist fails
        unrelated_data = df.DataFrame(data={'id': ['New1', 'New2', 'New3'], 'newcol': [1, 2, 3]})
        self.assertRaises(CyError, load_table_data, unrelated_data, data_key_column='id', table='node', table_key_column='name')

        # Verify that adding into node table rows that do exist succeeds ... checks that string-keys work
        column_names_string_keyed = get_table_column_names()
        test_data_string_keyed = df.DataFrame(data={'id': ['YDL194W', 'YDR277C', 'YBR043C'], 'newcol': [1, 2, 3]})
        res = load_table_data(test_data_string_keyed, data_key_column='id', table='node', table_key_column='name')
        self.assertEqual(res, 'Success: Data loaded in defaultnode table')

        # Verify that table key name is a string, not None or a list
        self.assertRaises(CyError, load_table_data, test_data_string_keyed, data_key_column='id', table='node', table_key_column=None)
        self.assertRaises(CyError, load_table_data, test_data_string_keyed, data_key_column='id', table='node', table_key_column=['BadCol1', 'BadCol2'])

        # Verify that ID column and newcol were added, and that the newcols have values only for the named nodes
        check_values_added(column_names_string_keyed, 'name', test_data_string_keyed, 'id', 'newcol')

        # Given newcol values, use them as non-string keys to add yet another column
        column_names_int_keyed = get_table_column_names()
        test_data_int_keyed = df.DataFrame(data={'newcol_val': [1, 2, 3], 'derived': [100, 200, 300]})
        res = load_table_data(test_data_int_keyed, data_key_column='newcol_val', table='node', table_key_column='newcol')
        self.assertEqual(res, 'Success: Data loaded in defaultnode table')

        # Verify that newcol_val column and derived were added, and that derived has values only for the newcol nodes
        check_values_added(column_names_int_keyed, 'newcol', test_data_int_keyed, 'newcol_val', 'derived')

        # Verify that adding data into edge table rows that do exist succeeds
        column_names_string_keyed = get_table_column_names(table='edge')
        test_data_string_keyed = df.DataFrame(data={'id_e': ['YDR277C (pp) YDL194W', 'YDR277C (pp) YJR022W', 'YPR145W (pp) YMR117C'], 'newcol_e': [1000, 2000, 3000]})
        res = load_table_data(test_data_string_keyed, data_key_column='id_e', table='edge', table_key_column='name')
        self.assertEqual(res, 'Success: Data loaded in defaultedge table')

        # Verify that newcol_val column and derived were added, and that derived has values only for the newcol nodes
        check_values_added(column_names_string_keyed, 'name', test_data_string_keyed, 'id_e', 'newcol_e', table='edge')

        # Verify that adding a column with a null works properly, and that adding columns of different types does, too
        # While we're at it, eyeball the running time to see that it's not crazy slow
        test_data_suid_name = get_table_columns(columns=['SUID', 'name'])
        test_data_suid_name['IntCol'] = test_data_suid_name['SUID']
        test_data_suid_name['StrCol'] = test_data_suid_name['SUID']
        test_data_suid_name['FloatCol'] = test_data_suid_name['SUID']
        test_data_suid_name = test_data_suid_name.astype({'IntCol': np.int64, 'StrCol': np.str_, 'FloatCol': np.float_})
        suid_YBL079W = test_data_suid_name.index[test_data_suid_name.name == 'YBL079W'][0]
        del test_data_suid_name['name']
        test_data_suid_name.at[suid_YBL079W, 'FloatCol'] = np.nan # used to be set_value, but it was deprecated
#        test_data_suid_name.set_value(suid_YBL079W, 'FloatCol', np.nan)
        res = load_table_data(test_data_suid_name, data_key_column='SUID', table_key_column='SUID')
        self.assertEqual(res, 'Success: Data loaded in defaultnode table')
        # Make sure that Cytoscape got all of the column types and values right, including the NAN
        t = get_table_columns(columns=['SUID', 'IntCol', 'StrCol', 'FloatCol'])
        for suid, intcol, strcol, floatcol in zip(t['SUID'], t['IntCol'], t['StrCol'], t['FloatCol']):
            str_suid = str(suid)
            self.assertEqual(str_suid, str(intcol))
            self.assertEqual(str_suid, strcol)
            if suid == suid_YBL079W:
                self.assertTrue(np.isnan(floatcol))
            else:
                self.assertEqual(str_suid, str(int(floatcol)))

        data = get_table_columns()
        self.assertRaises(CyError, load_table_data, data, table='bogus')
        self.assertRaises(CyError, load_table_data, data, namespace='bogus')
        self.assertRaises(CyError, load_table_data, data, network='bogus')

    
    @print_entry_exit
    def test_map_table_column(self):
        # Initialization
        load_test_session()

        # Verify that mapping Yeast from Ensembl to SGD produces a complete (name, SGD) mapping, though
        # the number of unmapped symbols depends on the mapping database used ... we can't know this
        df = map_table_column('name', 'Yeast', 'Ensembl', 'SGD')
        self.assertSetEqual({'name', 'SGD'}, set(df.columns))
        self.assertEqual(get_node_count(), len(df.index))
        self.assertSetEqual(set(df['name']), set(get_table_columns('node', ['name'])['name']))
        empty_mapping = df[df['SGD'].isnull()]
        self.assertTrue(0 < len(empty_mapping.index) <= len(df.index))

        # Verify that mapping a non-existent column and other bad parameters are caught
        self.assertRaises(CyError, map_table_column, 'bogusname', 'Yeast', 'Ensembl', 'SGD')
        self.assertRaises(CyError, map_table_column, 'name', 'bogus', 'Ensembl', 'SGD')
        self.assertRaises(CyError, map_table_column, 'name', 'Yeast', 'bogus', 'SGD')
        self.assertRaises(CyError, map_table_column, 'name', 'Yeast', 'Ensembl', 'bogus')

        self.assertRaises(CyError, map_table_column, 'name', 'Yeast', 'Ensembl', 'SGD', table='bogus')
        self.assertRaises(CyError, map_table_column, 'name', 'Yeast', 'Ensembl', 'SGD', namespace='bogus')
        self.assertRaises(CyError, map_table_column, 'name', 'Yeast', 'Ensembl', 'SGD', network='bogus')

    
    @print_entry_exit
    def test_rename_table_column(self):
        # Initialization
        load_test_session()

        # Verify that the rename reports OK and the column name is actually changed
        orig_columns = set(get_table_column_names())
        expected_columns = orig_columns.copy()
        expected_columns.discard('AverageShortestPathLength')
        expected_columns.add('xAveragex')
        self.assertEqual(rename_table_column('AverageShortestPathLength', 'xAveragex'), '')
        self.assertSetEqual(set(get_table_column_names()), expected_columns)

        # Verify that invalid parameters raise exceptions
        self.assertRaises(CyError, rename_table_column, 'bogus', 'xAveragex')
        self.assertRaises(CyError, rename_table_column, '', 'xAveragex')
        self.assertRaises(CyError, rename_table_column, None, 'xAveragex')
        self.assertRaises(CyError, rename_table_column, 'xAveragex', '')
        # self.assertRaises(HTTPError, rename_table_column, 'xAveragex', None) # This should fail, but doesn't
        # TODO: CyREST shouldn't allow change of name to None ... it shows up as null in Cytoscape
        self.assertRaises(CyError, rename_table_column, 'xAveragex', 'name')

        self.assertRaises(CyError, rename_table_column, 'AverageShortestPathLength', 'xAveragex',
                          network='bogus')
        self.assertRaises(CyError, rename_table_column, 'AverageShortestPathLength', 'xAveragex',
                          namespace='bogus')
        self.assertRaises(CyError, rename_table_column, 'AverageShortestPathLength', 'xAveragex',
                          table='bogus')


if __name__ == '__main__':
    unittest.main()
