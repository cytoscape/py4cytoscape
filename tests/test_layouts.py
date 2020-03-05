# -*- coding: utf-8 -*-

import unittest
import os

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


#    @skip
    @print_entry_exit
    def test_layout_network(self):
        # Initialize
        self._load_test_session()
        self._load_test_network('sampleData/yeastHighQuality.sif', make_current=False)
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


    def _load_test_session(self, session_filename=None):
        open_session(session_filename)

    def _load_test_network(self, network_name, make_current=True):
        if make_current:
            input('Load network ' + network_name + " and make it current")
        else:
            try:
                cur_suid = get_network_suid()
            except:
                cur_suid = None
            input('Load network ' + network_name)
            if cur_suid: set_current_network(cur_suid)

if __name__ == '__main__':
    unittest.main()