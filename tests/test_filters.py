# -*- coding: utf-8 -*-

""" Test functions in filters.py.
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
from requests import HTTPError
import pandas as df

from test_utils import *


class FiltersTests(unittest.TestCase):
    def setUp(self):
        try:
            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    
    @print_entry_exit
    def test_create_column_filter(self):
        # Initialization
        load_test_session()
        all_nodes = list(get_table_columns(columns=['name'])['name'])
        all_nodes_set = set(all_nodes)
        all_edges = list(get_table_columns(table='edge', columns=['name'])['name'])
        all_edges_set = set(all_edges)

        # Verify that all of the kinds of string filters work
        self.check_result('column filter 1x', lambda x: create_column_filter(x, 'COMMON', 'HIS', 'CONTAINS'),
                          {'YBR248C', 'YOR202W', 'YCL030C'}, None)
        self.check_result('column filter 2x', lambda x: create_column_filter(x, 'COMMON', 'RAP1', 'CONTAINS'),
                          {'YNL216W'}, None)
        self.check_result('column filter 3x',
                          lambda x: create_column_filter(x, 'COMMON', 'RAP1', 'DOES_NOT_CONTAIN'),
                          all_nodes_set - {'YNL216W'}, None)
        self.check_result('column filter 4x', lambda x: create_column_filter(x, 'COMMON', 'RAP1', 'IS'),
                          {'YNL216W'}, None)
        self.check_result('column filter 5x', lambda x: create_column_filter(x, 'COMMON', 'RAP1', 'IS_NOT'),
                          all_nodes_set - {'YNL216W'}, None)
        self.check_result('column filter 6x', lambda x: create_column_filter(x, 'COMMON', 'H.S.', 'REGEX'),
                          {'YBR248C', 'YOR202W', 'YCL030C'}, None)

        # Verify that all kinds of boolean filters work ... start by adding a boolean column and setting it to True for a few nodes
        all_nodes.sort()  # A cheap way of getting a consistent ordering from run to run
        test_data = df.DataFrame(
            data={'id': all_nodes, 'BoolTest': [False] * len(all_nodes), 'IntTest': [x for x in range(len(all_nodes))]})
        res = load_table_data(test_data, data_key_column='id', table='node', table_key_column='name')
        self.assertEqual(res, 'Success: Data loaded in defaultnode table')
        test_data = df.DataFrame(data={'id': ['YBR248C', 'YOR202W', 'YCL030C'], 'BoolTest': [True, True, True]})
        res = load_table_data(test_data, data_key_column='id', table='node', table_key_column='name')
        self.assertEqual(res, 'Success: Data loaded in defaultnode table')

        self.check_result('column filter 10x', lambda x: create_column_filter(x, 'BoolTest', False, 'IS'),
                          all_nodes_set - {'YBR248C', 'YOR202W', 'YCL030C'}, None)
        self.check_result('column filter 11x', lambda x: create_column_filter(x, 'BoolTest', True, 'IS'),
                          {'YBR248C', 'YOR202W', 'YCL030C'}, None)
        self.check_result('column filter 12x', lambda x: create_column_filter(x, 'BoolTest', False, 'IS_NOT'),
                          {'YBR248C', 'YOR202W', 'YCL030C'}, None)
        self.check_result('column filter 13x', lambda x: create_column_filter(x, 'BoolTest', True, 'IS_NOT'),
                          all_nodes_set - {'YBR248C', 'YOR202W', 'YCL030C'}, None)

        # Verify that an integer filter works
        self.check_result('column filter 20x',
                          lambda x: create_column_filter(x, 'NumberOfDirectedEdges', [7, 8], 'BETWEEN'),
                          {'YEL009C', 'YPL075W', 'YDR412W', 'YJR022W', 'YDR395W'}, None)
        self.check_result('column filter 21x',
                          lambda x: create_column_filter(x, 'NumberOfDirectedEdges', [7, 8], 'IS_NOT_BETWEEN'),
                          all_nodes_set - {'YEL009C', 'YPL075W', 'YDR412W', 'YJR022W', 'YDR395W'}, None)
        self.check_result('column filter 22x',
                          lambda x: create_column_filter(x, 'NumberOfDirectedEdges', 7, 'IS'),
                          {'YEL009C', 'YPL075W', 'YDR412W', 'YJR022W'}, None)
        self.check_result('column filter 23x',
                          lambda x: create_column_filter(x, 'NumberOfDirectedEdges', 7, 'IS_NOT'),
                          all_nodes_set - {'YEL009C', 'YPL075W', 'YDR412W', 'YJR022W'}, None)
        self.check_result('column filter 24x',
                          lambda x: create_column_filter(x, 'NumberOfDirectedEdges', 17, 'GREATER_THAN_OR_EQUAL'),
                          {'YNL216W', 'YMR043W'}, None)
        self.check_result('column filter 25x',
                          lambda x: create_column_filter(x, 'NumberOfDirectedEdges', 17, 'GREATER_THAN'),
                          {'YMR043W'}, None)
        self.check_result('column filter 26x',
                          lambda x: create_column_filter(x, 'IntTest', 1, 'LESS_THAN_OR_EQUAL'),
                          {'YAL030W', 'YAL003W'}, None)
        self.check_result('column filter 27x', lambda x: create_column_filter(x, 'IntTest', 1, 'LESS_THAN'),
                          {'YAL003W'}, None)

        # Verify that a floating point filter works
        self.check_result('column filter 30x',
                          lambda x: create_column_filter(x, 'AverageShortestPathLength', [6.253, 6.591],
                                                               'BETWEEN'), {'YKR099W', 'YJL157C', 'YPR119W', 'YNL216W'},
                          None)
        self.check_result('column filter 31x',
                          lambda x: create_column_filter(x, 'AverageShortestPathLength', [6.253, 6.591],
                                                               'IS_NOT_BETWEEN'),
                          all_nodes_set - {'YKR099W', 'YJL157C', 'YPR119W', 'YNL216W'}, None)
        self.check_result('column filter 32x',
                          lambda x: create_column_filter(x, 'AverageShortestPathLength', 14.08064516, 'IS'),
                          {'YHR141C', 'YLR109W'}, None)
        self.check_result('column filter 33x',
                          lambda x: create_column_filter(x, 'AverageShortestPathLength', 14.08064516, 'IS_NOT'),
                          all_nodes_set - {'YHR141C', 'YLR109W'}, None)
        self.check_result('column filter 34x',
                          lambda x: create_column_filter(x, 'AverageShortestPathLength', 14.731,
                                                               'GREATER_THAN_OR_EQUAL'),
                          {'YKR026C', 'YOL123W', 'YGL044C'}, None)
        self.check_result('column filter 35x',
                          lambda x: create_column_filter(x, 'AverageShortestPathLength', 16.001, 'GREATER_THAN'),
                          {'YGL044C'}, None)
        self.check_result('column filter 36x',
                          lambda x: create_column_filter(x, 'gal1RGexp', -1.135, 'LESS_THAN_OR_EQUAL'),
                          {'YBR072W', 'YBR020W'}, None)
        self.check_result('column filter 37x', lambda x: create_column_filter(x, 'gal1RGexp', -2.1, 'LESS_THAN'),
                          {'YBR020W'}, None)

        # Verify that various edge filters work
        network_selection.clear_selection()
        self.check_result('column filter 40x',
                          lambda x: create_column_filter(x, 'EdgeBetweenness', [18040.0, 18360.0], 'BETWEEN',
                                                                      type='edges'), None,
                          {'YPR119W (pd) YMR043W', 'YDR412W (pp) YPR119W'})
        self.check_result('column filter 41x',
                          lambda x: create_column_filter(x, 'EdgeBetweenness', [18040.0, 18360.0],
                                                               'IS_NOT_BETWEEN', type='edges'), None,
                          all_edges_set - {'YPR119W (pd) YMR043W', 'YDR412W (pp) YPR119W'})
        self.check_result('column filter 42x',
                          lambda x: create_column_filter(x, 'name', 'YLR044C', 'CONTAINS', type='edges'), None,
                          {'YGL035C (pd) YLR044C', 'YER179W (pp) YLR044C', 'YNL216W (pd) YLR044C'})
        self.check_result('column filter 43x',
                          lambda x: create_column_filter(x, 'name', 'YLR044C', 'DOES_NOT_CONTAIN', type='edges'),
                          None,
                          all_edges_set - {'YGL035C (pd) YLR044C', 'YER179W (pp) YLR044C', 'YNL216W (pd) YLR044C'})

        # Verify that invalid forms fail
        self.check_bad_filter('', lambda x: create_column_filter(x, 'COMMON', 'RAP1',
                                                                       'BOGUS'))  # TODO: Can't we throw an exception instead of having to check this way?
        self.assertRaises(CyError, self.check_bad_filter, 'column filter 7x',
                          lambda x: create_column_filter(x, 'BOGUS_COLUMN', 'RAP1', 'BOGUS'))
        self.check_bad_filter('column filter 7x',
                              lambda x: create_column_filter(x, 'COMMON', 'RAP1', 'BOGUS_PREDICATE'))

    
    @print_entry_exit
    def test_create_degree_filter(self):
        # Initialization
        load_test_session()
        all_nodes = list(get_table_columns(columns=['name'])['name'])
        all_nodes_set = set(all_nodes)

        # Verify that all of the kinds of degree filters work
        self.check_result('degree filter 1x', lambda x: create_degree_filter(x, [8, 10], 'BETWEEN'),
                          {'YDR395W', 'YLR362W', 'YPL248C', 'YGL035C'}, None)
        self.check_result('degree filter 2x', lambda x: create_degree_filter(x, [8, 10], 'IS_NOT_BETWEEN'),
                          all_nodes_set - {'YDR395W', 'YLR362W', 'YPL248C', 'YGL035C'}, None)
        self.check_result('degree filter 3x',
                          lambda x: create_degree_filter(x, [8, 10], 'BETWEEN', edge_type='UNDIRECTED'),
                          {'YDR395W', 'YLR362W', 'YPL248C', 'YGL035C'}, None)
        # The following should work, but Cytoscape creates an IN+OUT filter for all of them, so we can't check these tests
        #        self.check_result('degree filter 4x', lambda x: create_degree_filter(x, [8, 10], 'BETWEEN', edge_type='INCOMING'), {'YMR043W'}, None)
        #        self.check_result('degree filter 5x', lambda x: create_degree_filter(x, [8, 10], 'BETWEEN', edge_type='OUTGOING'), {'YMR043W', 'YPL248C'}, None)
        #        self.check_result('degree filter 6x', lambda x: create_degree_filter(x, [8, 10], 'BETWEEN', edge_type='DIRECTED'), {'YMR043W', 'YPL248C'}, None)
        self.check_result('degree filter 7x',
                          lambda x: create_degree_filter(x, [8, 10], 'BETWEEN', edge_type='ANY'),
                          {'YDR395W', 'YLR362W', 'YPL248C', 'YGL035C'}, None)

        # Verify that all bad filters are caught
        self.check_bad_filter('degree filter 10x', lambda x: create_degree_filter(x, [8, 10], 'BOGUS_PREDICATE'))
        self.assertRaises(CyError, create_degree_filter, 'degree filter 11x', [8], 'BETWEEN')
        self.assertRaises(CyError, create_degree_filter, 'degree filter 12x', [8, 10, 12], 'BETWEEN')
        self.assertRaises(CyError, create_degree_filter, 'degree filter 13x', '8, 10', 'BETWEEN')
        self.check_bad_filter('degree filter 14x',
                              lambda x: create_degree_filter(x, [8, 10], 'BETWEEN', edge_type='BOGUS_EDGETYPE'))

    
    @print_entry_exit
    def test_create_composite_filter(self):
        # Initialization
        load_test_session()

        # Create two independent filters
        self.check_result('degree filter 1x', lambda x: create_degree_filter(x, [9, 11], 'BETWEEN'),
                          {'YGL035C', 'YLR362W', 'YPL248C'}, None)
        self.check_result('degree filter 2x', lambda x: create_degree_filter(x, [10, 17], 'BETWEEN'),
                          {'YGL035C', 'YNL216W', 'YPL248C'}, None)

        # Create a composite that ANDs the two
        self.check_result('composite filter 1x',
                          lambda x: create_composite_filter(x, ['degree filter 1x', 'degree filter 2x'],
                                                                         type='ALL'), {'YGL035C', 'YPL248C'}, None)
        self.check_result('composite filter 2x',
                          lambda x: create_composite_filter(x, ['degree filter 1x', 'degree filter 2x']),
                          {'YGL035C', 'YPL248C'}, None)

        # create a composite that ORs the two
        self.check_result('composite filter 3x',
                          lambda x: create_composite_filter(x, ['degree filter 1x', 'degree filter 2x'],
                                                                         type='ANY'),
                          {'YGL035C', 'YNL216W', 'YLR362W', 'YPL248C'}, None)

    
    @print_entry_exit
    def test_get_filter_list(self):
        # Initialization
        load_test_session()

        # Check for a new session's filter
        self.assertSetEqual(set(get_filter_list()), {'Default filter'})

        # Create two independent filters
        self.check_result('degree filter 1x', lambda x: create_degree_filter(x, [9, 11], 'BETWEEN'),
                          {'YGL035C', 'YLR362W', 'YPL248C'}, None)
        self.check_result('degree filter 2x', lambda x: create_degree_filter(x, [10, 17], 'BETWEEN'),
                          {'YGL035C', 'YNL216W', 'YPL248C'}, None)

        # Check that the original filter and the two new ones are loaded
        self.assertSetEqual(set(get_filter_list()), {'Default filter', 'degree filter 1x', 'degree filter 2x'})

    
    @print_entry_exit
    def test_apply_filter_list(self):
        # Initialization
        load_test_session()

        # Create two independent filters
        self.check_result('degree filter 1x', lambda x: create_degree_filter(x, [9, 11], 'BETWEEN'),
                          {'YGL035C', 'YLR362W', 'YPL248C'}, None)
        self.check_result('degree filter 2x', lambda x: create_degree_filter(x, [10, 17], 'BETWEEN'),
                          {'YGL035C', 'YNL216W', 'YPL248C'}, None)

        # Verify that the filters can be executed independently
        selected = apply_filter('degree filter 1x')
        self.check_values(selected['nodes'], {'YGL035C', 'YLR362W', 'YPL248C'})
        self.check_values(selected['edges'], None)
        selected = apply_filter('degree filter 2x')
        self.check_values(selected['nodes'], {'YGL035C', 'YNL216W', 'YPL248C'})
        self.check_values(selected['edges'], None)

        # Verify that invalid filter is caught
        self.assertRaises(CyError, apply_filter, 'bogus_filter')

    
    @print_entry_exit
    def test_export_import_filters(self):
        # Initialization
        load_test_session()
        FILTER_FILE = 'test'
        FILTER_SUFFIX = '.json'

        # Create two independent filters
        self.check_result('degree filter 1x', lambda x: create_degree_filter(x, [9, 11], 'BETWEEN'),
                          {'YGL035C', 'YLR362W', 'YPL248C'}, None)
        self.check_result('degree filter 2x', lambda x: create_degree_filter(x, [10, 17], 'BETWEEN'),
                          {'YGL035C', 'YNL216W', 'YPL248C'}, None)

        # Verify that a file suffix is added if none is provided for a filter file
        if os.path.exists(FILTER_FILE + FILTER_SUFFIX): os.remove(FILTER_FILE + FILTER_SUFFIX)
        self.assertDictEqual(export_filters(FILTER_FILE), {})
        self.assertTrue(os.path.exists(FILTER_FILE + FILTER_SUFFIX))

        # Verify that importing filters results in the expected filters
        load_test_session()
        self.assertDictEqual(import_filters(FILTER_FILE + FILTER_SUFFIX), {})
        self.assertSetEqual(set(get_filter_list()),
                            {'Default filter', 'Default filter 1', 'degree filter 1x', 'degree filter 2x'})

        # Verify that the filters produce the expected result (i.e., the filters are the filters we expect)
        selected = apply_filter('degree filter 1x')
        self.check_values(selected['nodes'], {'YGL035C', 'YLR362W', 'YPL248C'})
        self.check_values(selected['edges'], None)
        selected = apply_filter('degree filter 2x')
        self.check_values(selected['nodes'], {'YGL035C', 'YNL216W', 'YPL248C'})
        self.check_values(selected['edges'], None)

        # Verify that no file suffix is added if the filter file name already has one
        if os.path.exists(FILTER_FILE + FILTER_SUFFIX): os.remove(FILTER_FILE + FILTER_SUFFIX)
        self.assertDictEqual(export_filters(FILTER_FILE + FILTER_SUFFIX), {})
        self.assertTrue(os.path.exists(FILTER_FILE + FILTER_SUFFIX))

        # Verify that the filter file contains the expected filters
        load_test_session()
        self.assertDictEqual(import_filters(FILTER_FILE + FILTER_SUFFIX), {})
        self.assertSetEqual(set(get_filter_list()),
                            {'Default filter', 'Default filter 1', 'Default filter 2', 'degree filter 1x',
                             'degree filter 2x'})
        os.remove(FILTER_FILE + FILTER_SUFFIX)

        # Verify that a filter file containing all types of filters is loaded
        load_test_session()
        self.assertDictEqual(import_filters('data/All Predicates.filter'), {})
        self.assertSetEqual(set(get_filter_list()), {'Default filter', 'All Predicates'})

    def check_result(self, filter_name, create_func, expected_nodes, expected_edges):
        self.assertNotIn(filter_name, get_filter_list())
        selected = create_func(filter_name)
        self.assertIn(filter_name, get_filter_list())
        self.check_values(selected['nodes'], expected_nodes)
        self.check_values(selected['edges'], expected_edges)

    def check_bad_filter(self, filter_name, create_func):
        selected = create_func(filter_name)
        self.assertNotIn(filter_name, get_filter_list())

    def check_values(self, selected, expected_set):
        if expected_set:
            self.assertSetEqual(set(selected), expected_set)
        else:
            self.assertIsNone(selected)


if __name__ == '__main__':
    unittest.main()
