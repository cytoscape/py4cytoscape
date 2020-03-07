# -*- coding: utf-8 -*-

import unittest
import os
import time

from PyCy3 import *
from PyCy3.decorators import *

class LayoutsTests(unittest.TestCase):
    def setUp(self):
        try:
            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass


    @skip
    @print_entry_exit
    def test_layout_network(self):
        # Initialize
        self._load_test_session()
        self._load_test_network('data/yeastHighQuality.sif', make_current=False)
        cur_network_suid = get_network_suid()

        # Execute default layout ... should happen on galFiltered.sif
        self.assertDictEqual(layout_network(), {})
        # To verify, operator should eyeball the network in Cytoscape

        # Execute grid layout ... should happen on yeastHighQuality.sif
        self.assertDictEqual(layout_network('grid', 'yeastHighQuality.sif'), {})
        self.assertEqual(get_network_suid(), cur_network_suid)
        # To verify, operator should eyeball the network in Cytoscape

        # Execute bogus layout
        self.assertRaises(CyError, layout_network, 'bogus')
        self.assertEqual(get_network_suid(), cur_network_suid)

    @skip
    @print_entry_exit
    def test_bundle_edges(self):
        # Initialize
        self._load_test_session()
        self._load_test_network('data/yeastHighQuality.sif', make_current=False)
        cur_network_suid = get_network_suid()

        # Bundle edges ... should happen on galFiltered.sif
        self.assertDictEqual(bundle_edges(), {'message': 'Edge bundling success.'})
        # To verify, operator should eyeball the network in Cytoscape

        # Bundle edges ... should happen on yeastHighQuality.sif
        self.assertDictEqual(bundle_edges('yeastHighQuality.sif'), {'message': 'Edge bundling success.'})
        self.assertEqual(get_network_suid(), cur_network_suid)
        # To verify, operator should eyeball the network in Cytoscape

    @skip
    @print_entry_exit
    def test_clear_edge_bends(self):
        # Initialize
        self._load_test_session()
        self._load_test_network('data/yeastHighQuality.sif', make_current=False)
        cur_network_suid = get_network_suid()

        # Bundle then unbundle edges ... should happen on galFiltered.sif
        self.assertDictEqual(bundle_edges(), {'message': 'Edge bundling success.'})
        self.assertDictEqual(clear_edge_bends(), {'message': 'Clear all edge bends success.'})
        # To verify, operator should eyeball the network in Cytoscape

        # Bundle edges ... should happen on yeastHighQuality.sif
        self.assertDictEqual(bundle_edges('yeastHighQuality.sif'), {'message': 'Edge bundling success.'})
        self.assertDictEqual(clear_edge_bends('yeastHighQuality.sif'), {'message': 'Clear all edge bends success.'})
        self.assertEqual(get_network_suid(), cur_network_suid)
        # To verify, operator should eyeball the network in Cytoscape

    @skip
    @print_entry_exit
    def test_layout_copycat(self):
        # Initialize
        self._load_test_session()
        orig_suid = get_network_suid()
        cloned_suid = clone_network()

        # Verify that the basic copycat works by laying out clone in a grid, then returning it to original
        self.assertDictEqual(layout_network('grid', cloned_suid), {})
        self.assertDictEqual(layout_copycat(orig_suid, cloned_suid), {'mappedNodeCount': 330, 'unmappedNodeCount': 0})
        # To verify, operator should eyeball the network in Cytoscape

        # Verify that there are no unmapped nodes when we tell copycat to ignore them
        self.assertDictEqual(layout_network('grid', cloned_suid), {})
        self.assertDictEqual(layout_copycat('galFiltered.sif', 'galFiltered.sif_1', grid_unmapped=False, select_unmapped=False), {'mappedNodeCount': 330, 'unmappedNodeCount': 0})
        # To verify, operator should eyeball the network in Cytoscape

        # Verify that the copycat unmatched nodes work by removing original nodes, laying out clone in a grid, then returning it to original
        # TODO: Implement this when we have APIs for deleting nodes

#    @skip
    @print_entry_exit
    def test_get_layout_names(self):
        required_layouts = set(['attribute-circle', 'stacked-node-layout', 'degree-circle', 'circular', 'attributes-layout', 'kamada-kawai', 'force-directed', 'cose', 'grid', 'hierarchical', 'fruchterman-rheingold', 'isom'])
        found_layouts = set(get_layout_names())
        self.assertTrue(found_layouts.issuperset(required_layouts))

    def _load_test_session(self, session_filename=None):
            open_session(session_filename)

    def _load_test_network(self, network_name, make_current=True):
        if make_current:
            new_suid = import_network_from_file(network_name)
            set_current_network(new_suid)
        else:
            try:
                cur_suid = get_network_suid()
            except:
                cur_suid = None
            import_network_from_file(network_name)
            if cur_suid: set_current_network(cur_suid)


if __name__ == '__main__':
    unittest.main()