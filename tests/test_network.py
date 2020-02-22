# -*- coding: utf-8 -*-

import unittest
import pandas as df
import igraph as ig

from PyCy3 import *
from PyCy3.decorators import *

class NetworkTests(unittest.TestCase):
    def setUp(self):
        try:
            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass



    @skip
    @print_entry_exit
    def test_first_func(self):
        res = first_func()
        self.assertIn('allAppsStarted', res)
        self.assertIn('apiVersion', res)
        self.assertIn('numberOfCores', res)
        self.assertIn('memoryStatus', res)

    @skip
    @print_entry_exit
    def test_set_current_network(self):
        # Initialization
        self._load_test_network('galFiltered.cys', make_current=False)
        self._load_test_network('yeastHighQuality.sif', make_current=False)

        self.assertRaises(CyError, set_current_network, 'bad title')

        self.assertRaises(CyError, set_current_network, 500) # bad SUID

        def set_and_check(new_network_name, new_network_suid):
            res = set_current_network(new_network_name)
            self.assertSequenceEqual(res, {})
            self.assertEqual(get_network_suid(), new_network_suid)
            res = set_current_network()
            self.assertSequenceEqual(res, {})
            self.assertEqual(get_network_suid(), new_network_suid)

        # Assume there are two networks: galFiltered.sif and BINDhuman.sif
        gal_suid = get_network_suid('galFiltered.sif')
        yeast_suid = get_network_suid('yeastHighQuality.sif')

        set_and_check('yeastHighQuality.sif', yeast_suid)
        set_and_check('galFiltered.sif', gal_suid)

    @unittest.skip('test_rename_network: Renaming non-current network needs fixing in Cytoscape')
    @print_entry_exit
    def test_rename_network(self):
        # Initialization
        self._load_test_network('galFiltered.cys', make_current=False)
        self._load_test_network('yeastHighQuality.sif', make_current=False)

        def rename_and_check(new_title, network_suid, network=None):
            res = rename_network(new_title, network)
            self.assertEqual(res['network'], network_suid)
            self.assertEqual(res['title'], new_title)

            new_suid = get_network_suid(new_title)
            self.assertEqual(new_suid, network_suid)

        self.assertRaises(CyError, rename_network, 'junk', 'doesnt exist')

        yeast_suid = get_network_suid('yeastHighQuality.sif')
        gal_suid = get_network_suid('galFiltered.sif')

        set_current_network('galFiltered.sif')
        rename_and_check('newcurrent', gal_suid)
        rename_and_check('newcurrent1', gal_suid, 'newcurrent')
        rename_and_check('newsuid', gal_suid, gal_suid)

        # This fails because of a Cytoscape error ... should be able to rename
        # non-current network, but Cytoscape fails on this
        rename_and_check('newyeast', yeast_suid, 'yeastHighQuality.sif')

    @skip
    @print_entry_exit
    def test_get_network_count(self):
        def check(count):
            res = get_network_count()
            self.assertIsInstance(res, int)
            self.assertEqual(res, count)

        check(0)

        # Initialization
        self._load_test_network()
        check(1)

    @skip
    @print_entry_exit
    def test_get_network_suid(self):
        self.assertRaises(CyError, get_network_suid, '')

        # Initialization
        self._load_test_network()
        self.assertRaises(CyError, get_network_suid, 'bad title')
        self.assertRaises(CyError, get_network_suid, 500) # bad SUID

        res = get_network_suid()
        self.assertIsInstance(res, int)

        self.assertEqual(get_network_suid('current'), res)
        self.assertEqual(get_network_suid('galFiltered.sif'), res)
        self.assertEqual(get_network_suid(res), res)

    @skip
    @print_entry_exit
    def test_get_network_name(self):
        self.assertRaises(CyError, get_network_name, '')

        # Initialization
        self._load_test_network()
        self.assertRaises(CyError, get_network_name, 'bad title')
        self.assertRaises(IndexError, get_network_name, 500) # bad SUID

        res = get_network_name()
        self.assertIsInstance(res, str)

        self.assertEqual(get_network_name('current'), res)
        self.assertEqual(get_network_name('galFiltered.sif'), res)
        self.assertEqual(get_network_name(res), res)

    @skip
    @print_entry_exit
    def test_get_network_list(self):
        # Initialization
        self._load_test_network('galFiltered.cys')
        self._load_test_network('yeastHighQuality.sif', make_current=False)

        self.assertListEqual(get_network_list(), ['yeastHighQuality.sif', 'galFiltered.sif'])

        delete_all_networks()
        self.assertListEqual(get_network_list(), [])

    @skip
    @print_entry_exit
    def test_export_network(self):
        # Initialization
        self._load_test_network('galFiltered.cys')
        self._load_test_network('yeastHighQuality.sif', make_current=False)

        def check(res):
            self.assertIsNotNone(res['file'])

        # For these tests, always answer Cytoscape verification message to allow overwrite
        input('On the following tests, allow Cytoscape to overwrite network')
        check(export_network())
        check(export_network(filename='test', network='yeastHighQuality.sif', type='sif'))

        self.assertRaises(CyError, export_network, filename='test', network='totallybogus', type='sif')

        # For this test, answer Cytoscape verification message to DISALLOW overwrite
        input('On on the following test, DISALLOW network overwrite')
        self.assertRaises(CyError, export_network)

    @skip
    @print_entry_exit
    def test_delete_network(self):
        # Initialization
        self._load_test_network('galFiltered.cys')
        self._load_test_network('yeastHighQuality.sif', make_current=False)

        self.assertEqual(delete_network('yeastHighQuality.sif'), '')
        self.assertRaises(CyError, delete_network, 'yeastHighQuality.sif')

    @skip
    @print_entry_exit
    def test_delete_all_networks(self):
        # Initialization
        self._load_test_network('galFiltered.cys')
        self._load_test_network('yeastHighQuality.sif', make_current=False)

        self.assertEqual(get_network_count(), 2)
        self.assertEqual(delete_all_networks(), '')
        self.assertEqual(get_network_count(), 0)
        self.assertEqual(delete_all_networks(), '')

    @skip
    @print_entry_exit
    def test_get_first_neighbors(self):
        # Initialization
        self._load_test_network('galFiltered.cys')

        self._select_nodes(['MIG1', 'GAL1'])
        self.assertSetEqual(set(get_first_neighbors(node_names=None, as_nested_list=False)), set(['YGL035C', 'YOL051W', 'YPL248C', 'YML051W', 'YLR044C', 'YLR377C', 'YIL162W', 'YBR019C', 'YBR020W', 'YKL109W', 'YKL074C', 'YDR009W', 'YDR146C']))

        # Verify that the two nested lists are equivalent
        nested_neighbor_list = get_first_neighbors(node_names = None, as_nested_list=True)
        expected_list = [['YBR020W', ['YGL035C', 'YOL051W', 'YPL248C', 'YML051W']], ['YGL035C', ['YLR044C', 'YLR377C', 'YIL162W', 'YBR019C', 'YBR020W', 'YPL248C', 'YKL109W', 'YKL074C', 'YDR009W', 'YDR146C']]]
        for nested_list in nested_neighbor_list:
            found = [nested_list[0] == expected[0] and set(nested_list[1]) == set(expected[1])  for expected in expected_list]
            self.assertIn(True, found)

        self._select_nodes([])
        self.assertSetEqual(set(get_first_neighbors(['YBR020W', 'YGL035C'], as_nested_list=False)), set(['YGL035C', 'YOL051W', 'YPL248C', 'YML051W', 'YLR044C', 'YLR377C', 'YIL162W', 'YBR019C', 'YBR020W', 'YKL109W', 'YKL074C', 'YDR009W', 'YDR146C']))
        self.assertIsNone(get_first_neighbors([], as_nested_list=False))
        self.assertRaises(CyError, get_first_neighbors)

        # TODO: test case of node_names being a single (str) node

    @skip
    @print_entry_exit
    def test_get_node_count(self):
        # Initialization
        self._load_test_network('galFiltered.cys')

        self.assertEqual(get_node_count(), 330)

    @skip
    @print_entry_exit
    def test_get_all_nodes(self):
        # Initialization
        self._load_test_network('galFiltered.cys')

        self.assertSetEqual(set(get_all_nodes()), set(['YDL194W', 'YDR277C', 'YBR043C', 'YPR145W', 'YER054C', 'YBR045C', 'YBL079W', 'YLR345W', 'YIL052C', 'YER056CA', 'YNL069C', 'YDL075W', 'YFR014C', 'YGR136W', 'YDL023C', 'YBR170C', 'YGR074W', 'YGL202W', 'YLR197W', 'YDL088C', 'YOR215C', 'YPR010C', 'YMR117C', 'YML114C', 'YNL036W', 'YOR212W', 'YDR070C', 'YNL164C', 'YGR046W', 'YLR153C', 'YIL070C', 'YPR113W', 'YER081W', 'YGR088W', 'YDR395W', 'YGR085C', 'YER124C', 'YMR005W', 'YDL030W', 'YER079W', 'YDL215C', 'YIL045W', 'YPR041W', 'YOR120W', 'YIL074C', 'YDR299W', 'YHR005C', 'YLR452C', 'YMR255W', 'YBR274W', 'YHR084W', 'YBL050W', 'YBL026W', 'YJL194W', 'YLR258W', 'YGL134W', 'YHR055C', 'YHR053C', 'YPR124W', 'YNL135C', 'YER052C', 'YLR284C', 'YHR198C', 'YPL240C', 'YPR102C', 'YLR075W', 'YKL161C', 'YAR007C', 'YIL160C', 'YDL078C', 'YDR142C', 'YDR244W', 'YLR432W', 'YDR167W', 'YLR175W', 'YNL117W', 'YOR089C', 'YPR167C', 'YNL214W', 'YBR135W', 'YML007W', 'YER110C', 'YGL153W', 'YLR191W', 'YOL149W', 'YMR044W', 'YOR362C', 'YER102W', 'YOL059W', 'YBR190W', 'YER103W', 'YPR110C', 'YNL113W', 'YDR354W', 'YER090W', 'YKL211C', 'YDR146C', 'YER111C', 'YOR039W', 'YML024W', 'YIL113W', 'YLL019C', 'YDR009W', 'YML051W', 'YHR071W', 'YPL031C', 'YML123C', 'YER145C', 'YMR058W', 'YJL190C', 'YML074C', 'YOR355W', 'YFL038C', 'YIL162W', 'YBR050C', 'YMR311C', 'YOR315W', 'YOR178C', 'YER133W', 'YOR290C', 'YFR037C', 'YFR034C', 'YAL040C', 'YPL222W', 'YGR048W', 'YMR291W', 'YGR009C', 'YMR183C', 'YDR100W', 'YGL161C', 'YPL131W', 'YDL063C', 'YNL167C', 'YHR115C', 'YEL041W', 'YDL113C', 'YJL036W', 'YBR109C', 'YOL016C', 'YKL001C', 'YNL311C', 'YLR319C', 'YPR062W', 'YPL111W', 'YDL236W', 'YNL189W', 'YBL069W', 'YGL073W', 'YBR072W', 'YLR321C', 'YPR048W', 'YNL199C', 'YPL075W', 'YHR179W', 'YCL040W', 'YFL039C', 'YDL130W', 'YDR382W', 'YJR066W', 'YKL204W', 'YNL154C', 'YNL047C', 'YNL116W', 'YHR135C', 'YML064C', 'YKL074C', 'YLR340W', 'YDL081C', 'YGL166W', 'YLL028W', 'YDR174W', 'YDR335W', 'YLR214W', 'YMR021C', 'YLR377C', 'YER065C', 'YJL089W', 'YHR030C', 'YPL089C', 'YGL208W', 'YGL115W', 'YLR310C', 'YNL098C', 'YGR019W', 'YPR035W', 'YER040W', 'YGL008C', 'YOR036W', 'YDR323C', 'YBL005W', 'YBR160W', 'YKL101W', 'YOL156W', 'YJL219W', 'YLL021W', 'YOL136C', 'YJL203W', 'YNR007C', 'YFL026W', 'YJL157C', 'YNL145W', 'YDR461W', 'YGR108W', 'YKR097W', 'YJL159W', 'YIL015W', 'YMR043W', 'YKL109W', 'YBR217W', 'YHR171W', 'YPL149W', 'YKL028W', 'YDR311W', 'YBL021C', 'YGL237C', 'YEL039C', 'YJR048W', 'YML054C', 'YLR256W', 'YOR303W', 'YJR109C', 'YGR058W', 'YLR229C', 'YDR309C', 'YOR264W', 'YLR116W', 'YNL312W', 'YML032C', 'YKL012W', 'YNL236W', 'YNL091W', 'YDR184C', 'YIL143C', 'YKR099W', 'YIR009W', 'YBR018C', 'YPL248C', 'YLR081W', 'YBR020W', 'YGL035C', 'YOL051W', 'YBR019C', 'YJR060W', 'YDR103W', 'YLR362W', 'YDR032C', 'YCL032W', 'YLR109W', 'YHR141C', 'YMR138W', 'YMR300C', 'YOL058W', 'YBR248C', 'YOR202W', 'YMR108W', 'YEL009C', 'YBR155W', 'YMR186W', 'YGL106W', 'YOR326W', 'YMR309C', 'YOR361C', 'YIL105C', 'YLR134W', 'YER179W', 'YOR310C', 'YDL014W', 'YPR119W', 'YLR117C', 'YGL013C', 'YCR086W', 'YDR412W', 'YPL201C', 'YER062C', 'YOR327C', 'YER143W', 'YAL030W', 'YOL086C', 'YDR050C', 'YOL127W', 'YIL069C', 'YER074W', 'YBR093C', 'YDR171W', 'YCL030C', 'YNL301C', 'YOL120C', 'YLR044C', 'YIL133C', 'YHR174W', 'YGR254W', 'YCR012W', 'YNL216W', 'YAL038W', 'YNL307C', 'YDL013W', 'YER116C', 'YNR053C', 'YLR264W', 'YEL015W', 'YNL050C', 'YNR050C', 'YJR022W', 'YOR167C', 'YER112W', 'YCL067C', 'YBR112C', 'YCR084C', 'YIL061C', 'YGR203W', 'YJL013C', 'YGL229C', 'YJL030W', 'YGR014W', 'YPL211W', 'YGL044C', 'YOL123W', 'YAL003W', 'YFL017C', 'YDR429C', 'YMR146C', 'YLR293C', 'YBR118W', 'YPR080W', 'YLR249W', 'YOR204W', 'YGL097W', 'YGR218W', 'YGL122C', 'YKR026C']))

    @skip
    @print_entry_exit
    def test_add_cy_nodes(self):
        # Initialization
        self._load_test_network('galFiltered.cys')

        res12 = add_cy_nodes(['newnode1', 'newnode2'], skip_duplicate_names=False)
        self.assertEqual(len(res12), 2)
        self.assertEqual(res12[0]['name'], 'newnode1')
        self.assertEqual(res12[1]['name'], 'newnode2')

        res23 = add_cy_nodes(['newnode2', 'newnode3'], skip_duplicate_names=True)
        self.assertEqual(len(res23), 1)
        self.assertEqual(res23[0]['name'], 'newnode3')

        res23x = add_cy_nodes(['newnode2', 'newnode3'], skip_duplicate_names=True)
        self.assertEqual(len(res23x), 0)
        self.assertEqual(get_node_count(), 333)

    @skip
    @print_entry_exit
    def test_add_cy_edges(self):
        # Initialization
        self._load_test_network('galFiltered.cys')
        df = tables.get_table_columns('node', ['name'], 'default')

        def check_edge(edge, source_name, target_name):
            self.assertIsInstance(edge, dict)
            source_suid = df[df.name.eq(source_name)].index[0]
            target_suid = df[df.name.eq(target_name)].index[0]
            self.assertEqual(edge['source'], source_suid)
            self.assertEqual(edge['target'], target_suid)
            self.assertIsNotNone(edge['SUID'])

        res = add_cy_edges(['YLR075W', 'YKL028W'])
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        check_edge(res[0], 'YLR075W', 'YKL028W')

        res = add_cy_edges([['YKL028W', 'YJR066W'], ['YJR066W', 'YLR452C'], ['YGR046W', 'YLR452C']])
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 3)
        check_edge(res[0], 'YKL028W', 'YJR066W')
        check_edge(res[1], 'YJR066W', 'YLR452C')
        check_edge(res[2], 'YGR046W', 'YLR452C')

    @skip
    @print_entry_exit
    def test_get_edge_count(self):
        # Initialization
        self._load_test_network('galFiltered.cys')

        self.assertEqual(get_edge_count(), 359)

    @skip
    @print_entry_exit
    def test_get_edge_info(self):
        # Initialization
        self._load_test_network('galFiltered.cys')

        def check_edge_info(edge_info, source_name, target_name, edge_name, betweenness):
            source_suid = node_name_to_node_suid(source_name)[0]
            target_suid = node_name_to_node_suid(target_name)[0]
            edge_suid = edge_name_to_edge_suid(edge_name)[0]
            self.assertIsInstance(edge_info, dict)
            self.assertEqual(edge_info['source'], source_suid)
            self.assertEqual(edge_info['target'], target_suid)
            self.assertEqual(edge_info['SUID'], edge_suid)
            self.assertEqual(edge_info['shared name'], edge_name)
            self.assertEqual(edge_info['shared interaction'], 'pp')
            self.assertEqual(edge_info['name'], edge_name)
            self.assertEqual(edge_info['selected'], False)
            self.assertEqual(edge_info['interaction'], 'pp')
            self.assertEqual(edge_info['EdgeBetweenness'], betweenness)

        res = get_edge_info('YDR277C (pp) YDL194W')
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        check_edge_info(res[0], 'YDR277C', 'YDL194W', 'YDR277C (pp) YDL194W', 496.0)

        res = get_edge_info(['YDR277C (pp) YDL194W'])
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        check_edge_info(res[0], 'YDR277C', 'YDL194W', 'YDR277C (pp) YDL194W', 496.0)

        res = get_edge_info(['YDR277C (pp) YDL194W', 'YDR277C (pp) YJR022W'])
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 2)
        check_edge_info(res[0], 'YDR277C', 'YDL194W', 'YDR277C (pp) YDL194W', 496.0)
        check_edge_info(res[1], 'YDR277C', 'YJR022W', 'YDR277C (pp) YJR022W', 988.0)

        self.assertRaises(CyError, get_edge_info, 'junk')

    @skip
    @print_entry_exit
    def test_get_all_edges(self):
        # Initialization
        self._load_test_network('galFiltered.cys')

        res = get_all_edges()
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 359)

    @skip
    @print_entry_exit
    def test_clone_network(self):
        # Initialization
        self._load_test_network('galFiltered.cys')

        self._check_cloned_network(clone_network(), get_network_suid(), get_network_name(), 330, 359)

    @skip
    @print_entry_exit
    def test_create_subnet(self):
        # Initialization
        self._load_test_network('galFiltered.cys')
        base_suid = get_network_suid()
        base_name = get_network_name(base_suid)

        self._check_cloned_network(create_subnetwork(nodes='all', network=base_suid), base_suid, base_name, 330, 359)
        self._check_cloned_network(create_subnetwork(nodes=['RAP1', 'HIS4', 'PDC1', 'RPL18A'], nodes_by_col='COMMON', subnetwork_name=base_name+'xx', network=base_suid), base_suid, base_name, 4, 3)

    @skip
    @print_entry_exit
    def test_create_network_from_data_frames(self):
        node_data = {'id':["node 0","node 1","node 2","node 3"],
                     'group':["A","A","B","B"],
                     'score':[20,10,15,5]}
        nodes = df.DataFrame(data=node_data, columns=['id', 'group', 'score'])
        edge_data = {'source':["node 0","node 0","node 0","node 2"],
                     'target':["node 1","node 2","node 3","node 3"],
                     'interaction':["inhibits","interacts","activates","interacts"],
                     'weight':[5.1,3.0,5.2,9.9]}
        edges = df.DataFrame(data=edge_data, columns=['source', 'target', 'interaction', 'weight'])

        res = create_network_from_data_frames(nodes, edges, title='From node & edge dataframe')
        suid_1 = res['networkSUID']
        self.assertEqual(networks.get_network_name(suid_1), 'From node & edge dataframe')
        self.assertEqual(networks.get_node_count(suid_1), 4)
        self.assertEqual(networks.get_edge_count(suid_1), 4)
        self.assertSetEqual(set(networks.get_all_nodes(suid_1)), set(['node 0', 'node 1', 'node 2', 'node 3']))
        self.assertSetEqual(set(networks.get_all_edges(suid_1)), set(['node 0 (inhibits) node 1', 'node 0 (interacts) node 2', 'node 0 (activates) node 3', 'node 2 (interacts) node 3']))
        self.assertSetEqual(set(tables.get_table_column_names('node', network=suid_1)), set(['SUID', 'shared name', 'id', 'score', 'group', 'name', 'selected']))
        self.assertSetEqual(set(tables.get_table_column_names('edge', network=suid_1)), set(['SUID', 'shared name', 'shared interaction', 'source', 'target', 'data.key.column', 'weight', 'name', 'selected', 'interaction']))
        self.assertDictEqual(tables.get_table_column_types('node', network=suid_1), {'SUID': 'Long', 'shared name': 'String', 'id': 'String', 'score': 'Integer', 'group': 'String', 'name': 'String', 'selected': 'Boolean'})
        self.assertDictEqual(tables.get_table_column_types('edge', network=suid_1), {'SUID': 'Long', 'shared name': 'String', 'shared interaction': 'String', 'source': 'String', 'target': 'String', 'data.key.column': 'Integer', 'weight': 'Double', 'name': 'String', 'selected': 'Boolean', 'interaction': 'String'})


        res = create_network_from_data_frames(edges=edges, collection='Another collection', title='From just edge dataframe')
        suid_2 = res['networkSUID']
        self.assertEqual(networks.get_network_name(suid_2), 'From just edge dataframe')
        self.assertEqual(networks.get_node_count(suid_2), 4)
        self.assertEqual(networks.get_edge_count(suid_2), 4)
        self.assertSetEqual(set(networks.get_all_nodes(suid_2)), set(['node 0', 'node 1', 'node 2', 'node 3']))
        self.assertSetEqual(set(networks.get_all_edges(suid_2)), set(['node 0 (inhibits) node 1', 'node 0 (interacts) node 2', 'node 0 (activates) node 3', 'node 2 (interacts) node 3']))
        self.assertSetEqual(set(tables.get_table_column_names('node', network=suid_2)), set(['SUID', 'shared name', 'id', 'name', 'selected']))
        self.assertSetEqual(set(tables.get_table_column_names('edge', network=suid_2)), set(['SUID', 'shared name', 'shared interaction', 'source', 'target', 'data.key.column', 'weight', 'name', 'selected', 'interaction']))
        self.assertDictEqual(tables.get_table_column_types('node', network=suid_2), {'SUID': 'Long', 'shared name': 'String', 'id': 'String', 'name': 'String', 'selected': 'Boolean'})
        self.assertDictEqual(tables.get_table_column_types('edge', network=suid_2), {'SUID': 'Long', 'shared name': 'String', 'shared interaction': 'String', 'source': 'String', 'target': 'String', 'data.key.column': 'Integer', 'weight': 'Double', 'name': 'String', 'selected': 'Boolean', 'interaction': 'String'})

        res = create_network_from_data_frames(nodes=nodes, collection='A third collection', title='From just nodes dataframe')
        suid_3 = res['networkSUID']
        self.assertEqual(networks.get_network_name(suid_3), 'From just nodes dataframe')
        self.assertEqual(networks.get_node_count(suid_3), 4)
        self.assertEqual(networks.get_edge_count(suid_3), 0)
        self.assertSetEqual(set(networks.get_all_nodes(suid_3)), set(['node 0', 'node 1', 'node 2', 'node 3']))
        self.assertIsNone(networks.get_all_edges(suid_3))
        self.assertSetEqual(set(tables.get_table_column_names('node', network=suid_3)), set(['SUID', 'shared name', 'id', 'score', 'group', 'name', 'selected']))
        # TODO: Verify that this list of edge columns should be created ... why not source, target?
        self.assertSetEqual(set(tables.get_table_column_names('edge', network=suid_3)), set(['SUID', 'shared name', 'shared interaction', 'name', 'selected', 'interaction']))
        self.assertDictEqual(tables.get_table_column_types('node', network=suid_3), {'SUID': 'Long', 'shared name': 'String', 'id': 'String', 'score': 'Integer', 'group': 'String', 'name': 'String', 'selected': 'Boolean'})
        self.assertDictEqual(tables.get_table_column_types('edge', network=suid_3), {'SUID': 'Long', 'shared name': 'String', 'shared interaction': 'String', 'name': 'String', 'selected': 'Boolean', 'interaction': 'String'})

    @skip
    @print_entry_exit
    def test_import_network_from_file(self):

        # TODO: Package inst/extdata/* as part of PyCy3 package
        res = import_network_from_file('galFiltered.cys')
        print(res)

        # TODO: Come up with a more platform independent test
        res = import_network_from_file('c:\\Program Files\\Cytoscape_v3.7.2\\sampleData\\galFiltered.sif')
        print(res)

    @skip
    @print_entry_exit
    def test_create_igraph_from_network(self):
        # Initialization
        self._load_test_network('galFiltered.cys')
        all_nodes = get_all_nodes()
        all_edges = get_all_edges()

        i = create_igraph_from_network()
        print(i)

        # verify that all nodes are present
        self.assertEqual(len(i.vs), len(all_nodes))
        self.assertNotIn(False, [v['name'] in all_nodes  for v in i.vs])

        # verify that all edges are present
        self.assertEqual(len(i.es), len(all_edges))
        i_edges = [[x['source'], x['target']]   for x in i.es]
        self.assertNotIn(False, [re.split("\ \\(.*\\)\ ", x) in i_edges   for x in all_edges])

#   @skip
    @print_entry_exit
    def test_create_network_from_igraph(self):
        # Initialization
        self._load_test_network('galFiltered.cys')
        cur_igraph = create_igraph_from_network()

        new_SUID = create_network_from_igraph(cur_igraph)
        new_igraph = create_igraph_from_network(new_SUID)

        print('cur_igraph: ' + str(cur_igraph))
        print('new_igraph: ' + str(new_igraph))

        # compare the new iGraph to cur_igraph ... watch out for null values



    def _check_cloned_network(self, subnet_suid, base_suid, base_name, base_nodes, base_edges):
        self.assertIsInstance(subnet_suid, int)
        self.assertNotEqual(base_suid, subnet_suid)
        self.assertEqual(get_node_count(subnet_suid), base_nodes)
        self.assertEqual(get_edge_count(subnet_suid), base_edges)
        self.assertIn(base_name, get_network_name(subnet_suid))

    def _load_test_network(self, network_name='galFiltered.cys', make_current=True):
        if make_current:
            input('Load network ' + network_name + " and make it current")
        else:
            try:
                cur_suid = get_network_suid()
            except:
                cur_suid = None
            input('Load network ' + network_name)
            if cur_suid: set_current_network(cur_suid)

    def _select_nodes(self, node_list):
        if len(node_list) == 0:
            input('Deselect all nodes')
        else:
            input('Select these nodes: ' + str(node_list))


