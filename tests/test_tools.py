# -*- coding: utf-8 -*-

""" Test functions in tools.py.
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
import time
from requests import HTTPError

from test_utils import *


class ToolsTests(unittest.TestCase):
    def setUp(self):
        # Close all browser windows if possible
        try:
            for browser in cybrowser_list():
                cybrowser_close(browser['id'])
        except:
            pass

    def tearDown(self):
        pass

    BROWSER_HELLO = {'id': 'Browser Hello ID',
                     'show': {'func': lambda x, y: cybrowser_show(id=x, title=y,
                                                                  text='<HTML><HEAD><TITLE>Hello</TITLE></HEAD><BODY>Hello, world!</BODY></HTML>'),
                              'title': 'Browser Hello Page'},
                     'dialog': {'func': lambda x, y: cybrowser_dialog(id=x, title=y,
                                                                      text='<HTML><HEAD><TITLE>Hello</TITLE></HEAD><BODY>Hello, world!</BODY></HTML>'),
                                'title': 'Hello'}}
    CYTOSCAPE_HOME_PAGE = {'id': 'Cytoscape Home Page ID',
                           'show': {
                               'func': lambda x, y: cybrowser_show(id=x, title=y, url='http://www.cytoscape.org'),
                               'title': 'Cytoscape Home Page'},
                           'dialog': {
                               'func': lambda x, y: cybrowser_dialog(id=x, title=y,
                                                                     url='http://www.cytoscape.org'),
                               'title': 'Cytoscape: An Open Source Platform for Complex Network Analysis and Visualization'}}
    CYTOSCAPE_MANUAL = {'id': 'Cytoscape Manual ID',
                        'show': {'func': lambda x, y: cybrowser_show(id=x, title=y,
                                                                     url='http://manual.cytoscape.org/en/3.7.2/'),
                                 'title': 'Cytoscape Manual Page'},
                        'dialog': {
                            'func': lambda x, y: cybrowser_dialog(id=x, title=y,
                                                                  url='http://manual.cytoscape.org/en/3.7.2/'),
                            'title': 'Cytoscape 3.7.2 User Manual â€” Cytoscape User Manual 3.7.2 documentation'}}

    @print_entry_exit
    def test_cybrowser_version(self):
        # Verify that a version is reported
        version = cybrowser_version()
        self.assertIsInstance(version, dict)
        self.assertIsInstance(version['version'], str)

    @unittest.skipIf(skip_for_ui(), 'Avoiding test that requires user response')
    @print_entry_exit
    def test_cybrowser_show_list_hide(self):
        self._cybrowser_windows('show')

    @unittest.skipIf(skip_for_ui(), 'Avoiding test that requires user response')
    @print_entry_exit
    def test_cybrowser_dialog_list_hide(self):
        self._cybrowser_windows('dialog')

    @unittest.skipIf(skip_for_ui(), 'Avoiding test that requires user response')
    @print_entry_exit
    def test_cybrowser_send(self):
        self._check_show('dialog', ToolsTests.CYTOSCAPE_HOME_PAGE)
        window_id = ToolsTests.CYTOSCAPE_HOME_PAGE['id']

        # Verify that the user agent variable can be fetched
        res = cybrowser_send(window_id, 'navigator.userAgent')
        self.assertIsInstance(res, dict)
        self.assertEqual(res['browserId'], window_id)
        self.assertIsInstance(res['result'], str)

        # Verify that the window can be moved to a different URL
        res = cybrowser_send(window_id, "window.location='http://google.com'")
        self.assertEqual(res['browserId'], window_id)
        self.assertEqual(res['result'], 'http://google.com')

        self.assertRaises(CyError, cybrowser_send, 'bogus window', 'navigator.userAgent')

        self.assertDictEqual(cybrowser_send(window_id, 'bogus_statement'), {})

    @print_entry_exit
    def test_diffusion_basic(self):
        # Initialization
        load_test_session()

        # Verify that selecting a node and calling diffusion returns a bunch of nodes
        select_nodes(['RAP1'], by_col='COMMON')
        res = diffusion_basic()
        self.assertIsInstance(res, dict)
        self.assertEqual(res['heatColumn'], 'diffusion_output_heat')
        self.assertEqual(res['rankColumn'], 'diffusion_output_rank')
        self.assertTrue(len(get_selected_nodes()) > 0)

        # Verify that diffusion returns nodes even when nothing is selected
        clear_selection()
        res = diffusion_basic()
        self.assertIsInstance(res, dict)
        self.assertEqual(res['heatColumn'], 'diffusion_output_1_heat')
        self.assertEqual(res['rankColumn'], 'diffusion_output_1_rank')
        self.assertTrue(len(get_selected_nodes()) > 0)

    @print_entry_exit
    def test_diffusion_advanced(self):
        # Initialization
        load_test_session()

        # Verify that selecting a node and calling diffusion returns a bunch of nodes
        select_nodes(['RAP1'], by_col='COMMON')
        res = diffusion_advanced(heat_column_name='', time=0.1)
        self.assertIsInstance(res, dict)
        self.assertEqual(res['heatColumn'], 'diffusion_output_heat')
        self.assertEqual(res['rankColumn'], 'diffusion_output_rank')
        self.assertTrue(len(get_selected_nodes()) > 0)

        # Verify that diffusion returns nodes even when nothing is selected
        clear_selection()
        res = diffusion_advanced(heat_column_name='diffusion_output_heat', time=0.2)
        self.assertIsInstance(res, dict)
        self.assertEqual(res['heatColumn'], 'diffusion_output_1_heat')
        self.assertEqual(res['rankColumn'], 'diffusion_output_1_rank')
        self.assertTrue(len(get_selected_nodes()) > 0)

        # Verify that a bad parameter causes an exception
        self.assertRaises(CyError, diffusion_advanced, heat_column_name='diffusion_output_heat', time='x')

    @print_entry_exit
    def test_analyze_network(self):

        def check_analysis(actual, expected, compare_props):
            self.assertIsInstance(actual, dict)
            self.assertTrue(set(expected).issubset(set(actual)))
            member_equal = [expected[prop] == actual[prop] for prop in compare_props]
            self.assertFalse(False in member_equal)

        # Initialization
        load_test_session()

        check_analysis(analyze_network(),
                       {'networkTitle': 'galFiltered.sif (undirected)', 'nodeCount': '330', 'edgeCount': '359',
                        'avNeighbors': '2.379032258064516', 'diameter': '27', 'radius': '14',
                        'avSpl': '9.127660963823953', 'cc': '0.06959203036053131', 'density': '0.009631709546819902',
                        'heterogeneity': '0.8534500004035027', 'centralization': '0.06375695335900727', 'ncc': '26'},
                       {'networkTitle', 'nodeCount', 'edgeCount', 'diameter', 'radius', 'ncc'})
        check_analysis(analyze_network(True),
                       {'networkTitle': 'galFiltered.sif (directed)', 'nodeCount': '330', 'edgeCount': '359',
                        'avNeighbors': '2.16969696969697', 'diameter': '10', 'radius': '1',
                        'avSpl': '3.4919830756382395', 'cc': '0.03544266191325015', 'density': '0.003297411808050106',
                        'ncc': '26', 'mnp': '1', 'nsl': '0'},
                       {'networkTitle', 'nodeCount', 'edgeCount', 'diameter', 'radius', 'ncc', 'mnp', 'nsl'})

    @print_entry_exit
    def test_network_merge(self):

        BASIC_MERGED_NODE_PROPS = {'SUID': 'Long', 'shared name': 'String', 'name': 'String', 'selected': 'Boolean',
                                   'age': 'Integer', 'first name': 'String', 'given name': 'String', 'group': 'String',
                                   'id': 'String', 'score': 'Integer'}
        BASIC_MERGED_EDGE_PROPS = {'SUID': 'Long', 'shared name': 'String', 'shared interaction': 'String',
                                   'name': 'String',
                                   'selected': 'Boolean', 'interaction': 'String', 'data.key.column': 'Integer',
                                   'owes': 'Integer', 'relationship': 'String', 'source': 'String', 'target': 'String',
                                   'weight': 'Double'}
        BASIC_MERGED_NETWORK_PROPS = {'SUID': 'Long', 'shared name': 'String', 'name': 'String', 'selected': 'Boolean',
                                      '__Annotations': 'List'}
        BASIC_MERGED_NODES = {'node X', 'node 12', 'node 13', 'node 10', 'node 11', 'node 2', 'node 3', 'node 0',
                              'node 1'}
        BASIC_MERGED_EDGES = {'node 2 (interacts) node 3', 'node X (destroys) node 0',
                              'node 10 (interacts with) node 13', 'node 12 (interacts with) node 13',
                              'node 10 (interacts with) node 11', 'node 10 (interacts with) node 12',
                              'node 0 (interacts) node 2', 'node 0 (activates) node 3',
                              'node X (interacts with) node 10', 'node 0 (inhibits) node 1'}

        def check_merge(new_suid, new_title, node_count=9, edge_count=10,
                        extra_node_props={}, extra_edge_props={}, extra_network_props={},
                        merged_nodes=BASIC_MERGED_NODES, merged_edges=BASIC_MERGED_EDGES):
            self.assertEqual(get_network_name(suid=new_suid), new_title)
            self.assertEqual(get_node_count(network=new_suid), node_count)
            self.assertEqual(get_edge_count(network=new_suid), edge_count)
            if node_count:
                self.assertEqual(set(get_all_nodes(network=new_suid)), merged_nodes)
            if edge_count:
                self.assertSetEqual(set(get_all_edges(network=new_suid)), merged_edges)
            actual_nodes = BASIC_MERGED_NODE_PROPS.copy()
            actual_nodes.update(extra_node_props)
            actual_edges = BASIC_MERGED_EDGE_PROPS.copy()
            actual_edges.update(extra_edge_props)
            actual_networks = BASIC_MERGED_NETWORK_PROPS.copy()
            actual_networks.update(extra_network_props)
            self.assertDictEqual(get_table_column_types('node', network=new_suid), actual_nodes)
            self.assertDictEqual(get_table_column_types('edge', network=new_suid), actual_edges)
            self.assertDictEqual(get_table_column_types('network', network=new_suid), actual_networks)

        # Setup: clean out previous test
        close_session(False)

        # Setup: Create the first network (Network_0)
        node_data_0 = {'id': ["node 0", "node 1", "node 2", "node 3", 'node X'],
                       'given name': ["Barry", "Karen", "Scott", "Robyn", "X"],
                       'group': ["A", "A", "B", "B", "C"],
                       'score': [20, 10, 15, 5, -10]}
        nodes_0 = df.DataFrame(data=node_data_0, columns=['id', 'given name', 'group', 'score'])
        edge_data_0 = {'source': ["node 0", "node 0", "node 0", "node 2", "node X"],
                       'target': ["node 1", "node 2", "node 3", "node 3", "node 0"],
                       'interaction': ["inhibits", "interacts", "activates", "interacts", "destroys"],
                       'weight': [5.1, 3.0, 5.2, 9.9, -100]}
        edges_0 = df.DataFrame(data=edge_data_0, columns=['source', 'target', 'interaction', 'weight'])

        create_network_from_data_frames(nodes_0, edges_0, title='Network_0')

        # Setup: Create the second network (Network_1)
        node_data_1 = {'id': ["node 10", "node 11", "node 12", "node 13", "node X"],
                       'first name': ["Barry", "Karen", "Scott", "Robyn", "X"],
                       'age': [7, 5, 4, 0, -1]}
        nodes_1 = df.DataFrame(data=node_data_1, columns=['id', 'first name', 'age'])
        edge_data_1 = {'source': ["node 10", "node 10", "node 10", "node 12", 'node X'],
                       'target': ["node 11", "node 12", "node 13", "node 13", "node 10"],
                       'relationship': ["sister", "brother", "brother", "sister", "cousin"],
                       'owes': [10, 20, 30, 40, -1000]}
        edges_1 = df.DataFrame(data=edge_data_1, columns=['source', 'target', 'relationship', 'owes'])

        # Verify that a network can be created containing dataframe encoding both nodes and edges
        create_network_from_data_frames(nodes_1, edges_1, title='Network_1')

        # Verify that the simplest union merge works
        check_merge(merge_networks(['Network_0', 'Network_1']), 'union: Network_0,Network_2')
        check_merge(merge_networks(['Network_0', 'Network_1'], title='My Cool Network'), 'My Cool Network')

        # Verify that a node merge map works -- 'called' and 'score_m' were created and have String/Integer types
        res = merge_networks(['Network_0', 'Network_1'],
                             node_merge_map=[['given name', 'first name', 'called', 'String'],
                                             ['score', 'age', 'score_m', 'Integer']],
                             title='nodes mapped')
        check_merge(res, 'nodes mapped', 9, 10, extra_node_props={'called': 'String', 'score_m': 'Integer'})

        # Verify that an edge merge map works -- 'profile' was created and has Double type
        res = merge_networks(['Network_0', 'Network_1'],
                             edge_merge_map=[['weight', 'owes', 'profile', 'Double']],
                             title='edges mapped')
        check_merge(res, 'edges mapped', 9, 10, extra_edge_props={'profile': 'Double'})

        # Verify that a network merge map works -- 'jumble forward' and 'jumble backward' were created and have String type
        res = merge_networks(['Network_0', 'Network_1'],
                             network_merge_map=[['shared name', 'name', 'jumble forward', 'String'],
                                                ['shared name', 'name', 'jumble backward', 'String']],
                             title='networks mapped')
        check_merge(res, 'networks mapped', 9, 10,
                    extra_network_props={'jumble forward': 'String', 'jumble backward': 'String'})

        # It would be very reasonable to add more tests for the nodes_only, edge_keys, node_keys, and in_network_merge
        # parameters, but I can't get a good definition of what these parameters do, so I don't know what to test for. So,
        # for now, we pass them on and hope for the best.

        # For the operation='difference' parameter, the best test would be to execute a merge that corresponds to the
        # GUI's "Remove all nodes that are in the 2nd network". I don't think the parameter for this is exposed, so
        # I have to punt on checking the 'difference' operation.

        # Verify that an intersection leaves only the single node 'node X'
        res = merge_networks(['Network_0', 'Network_1'], operation='intersection', title='Cool Intersection')
        check_merge(res, 'Cool Intersection', node_count=1, edge_count=0, merged_nodes={'node X'}, merged_edges={})

        # Verify that exception is thrown for bad cases
        self.assertRaises(CyError, merge_networks, [])
        self.assertRaises(CyError, merge_networks, None)

    def _cybrowser_windows(self, operation='show'):

        def check_browser_list(browser_list, expected_list):  # doesn't support duplicate ID keys
            browser = {b['id']: b for b in browser_list}
            expected = {b['id']: b for b in expected_list}
            self.assertEqual(len(browser), len(expected))
            for id, val in browser.items():
                self.assertIn(id, expected)
                self.assertEqual(val['title'], expected[id][operation]['title'])

        # Verify that the browser list starts out empty ... no browser windows displayed
        check_browser_list(cybrowser_list(), [])

        # Verify that a browser can be launched with all of its options
        self._check_show(operation, ToolsTests.BROWSER_HELLO)
        self._check_show(operation, ToolsTests.CYTOSCAPE_HOME_PAGE)
        self._check_show(operation, ToolsTests.CYTOSCAPE_MANUAL)

        # Verify that the browser list contains all of the new pages
        time.sleep(2)  # wait for windowing system to catch up
        check_browser_list(cybrowser_list(),
                           [ToolsTests.BROWSER_HELLO, ToolsTests.CYTOSCAPE_HOME_PAGE, ToolsTests.CYTOSCAPE_MANUAL])

        # Verify that adding the same pages doesn't change the browser list
        self._check_show(operation, ToolsTests.BROWSER_HELLO, skip_verify=True)
        self._check_show(operation, ToolsTests.BROWSER_HELLO, skip_verify=True)
        self._check_show(operation, ToolsTests.BROWSER_HELLO, skip_verify=True)
        time.sleep(2)  # wait for windowing system to catch up
        check_browser_list(cybrowser_list(),
                           [ToolsTests.BROWSER_HELLO, ToolsTests.CYTOSCAPE_HOME_PAGE, ToolsTests.CYTOSCAPE_MANUAL])

        # Verify that hiding a browser removes it from the browser list, and bogus browser windows don't cause error
        self.assertDictEqual(cybrowser_hide(ToolsTests.BROWSER_HELLO['id']), {})
        self.assertDictEqual(cybrowser_close(ToolsTests.CYTOSCAPE_HOME_PAGE['id']), {})
        time.sleep(2)  # wait for windowing system to catch up
        check_browser_list(cybrowser_list(), [ToolsTests.CYTOSCAPE_MANUAL, ToolsTests.BROWSER_HELLO])

        # Verify that closing a browser twice does no harm
        self.assertDictEqual(cybrowser_close(ToolsTests.CYTOSCAPE_HOME_PAGE['id']), {})
        time.sleep(2)  # wait for windowing system to catch up
        check_browser_list(cybrowser_list(), [ToolsTests.CYTOSCAPE_MANUAL, ToolsTests.BROWSER_HELLO])

        # Verify that closing the last browser window results in a clean browser list
        self.assertDictEqual(cybrowser_close(ToolsTests.BROWSER_HELLO['id']), {})
        self.assertDictEqual(cybrowser_close(ToolsTests.CYTOSCAPE_MANUAL['id']), {})
        time.sleep(2)  # wait for windowing system to catch up
        check_browser_list(cybrowser_list(), [])

    def _check_show(self, operation, window_def, skip_verify=False):
        show_result = window_def[operation]['func'](window_def['id'], window_def[operation]['title'])
        self.assertIsInstance(show_result, dict)
        self.assertEqual(show_result['id'], window_def['id'])
        if not skip_verify: input('Verify that the "' + window_def[operation]['title'] + '" is visible; hit Enter')


if __name__ == '__main__':
    unittest.main()
