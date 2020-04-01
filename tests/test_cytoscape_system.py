# -*- coding: utf-8 -*-

import unittest

from test_utils import *

class AppsTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


#    @skip
    @print_entry_exit
    def test_cytoscape_ping(self):
        self.assertIsNone(cytoscape_ping())

        input('Terminate Cytoscape and hit [enter]')
        self.assertRaises(requests.exceptions.RequestException, cytoscape_ping)
        input('Restart Cytoscape, wait for startup to complete, and then hit [enter]')

#    @skip
    @print_entry_exit
    def test_cytoscape_version_info(self):
        version = cytoscape_version_info()
        self.assertEqual(version['apiVersion'], 'v1')
        self.assertRegex(version['cytoscapeVersion'], '([0-9]+\\.[0-9]+)\\..*$')

        input('Terminate Cytoscape and hit [enter]')
        self.assertRaises(requests.exceptions.RequestException, cytoscape_version_info)
        input('Restart Cytoscape, wait for startup to complete, and then hit [enter]')

#    @skip
    @print_entry_exit
    def test_cytoscape_api_versions(self):
        self.assertSetEqual(set(cytoscape_api_versions()), set(['v1']))

#    @skip
    @print_entry_exit
    def test_cytoscape_number_of_cores(self):
        cores = cytoscape_number_of_cores()
        self.assertIsInstance(cores, int)
        self.assertTrue(cores >= 1)

#    @skip
    @print_entry_exit
    def test_cytoscape_memory_status(self):
        status = cytoscape_memory_status()
        self.assertIsInstance(status, dict)
        self.assertTrue(set(status).issubset({'usedMemory', 'freeMemory', 'totalMemory', 'maxMemory'}))
        for mem in status:
            self.assertIsInstance(status[mem], int)

#    @skip
    @print_entry_exit
    def test_cytoscape_free_memory(self):
        x = cytoscape_free_memory()
        self.assertEqual(x, 'Unused memory freed up.')

if __name__ == '__main__':
    unittest.main()