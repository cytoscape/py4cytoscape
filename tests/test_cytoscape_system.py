# -*- coding: utf-8 -*-

import unittest

from test_utils import *


class AppsTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    #    @PyCy3.skip
    @PyCy3.print_entry_exit
    def test_cytoscape_ping(self):
        self.assertIsNone(PyCy3.cytoscape_ping())

        input('Terminate Cytoscape and hit [enter]')
        self.assertRaises(requests.exceptions.RequestException, PyCy3.cytoscape_ping)
        input('Restart Cytoscape, wait for startup to complete, and then hit [enter]')

    #    @PyCy3.skip
    @PyCy3.print_entry_exit
    def test_cytoscape_version_info(self):
        version = PyCy3.cytoscape_version_info()
        self.assertEqual(version['apiVersion'], 'v1')
        self.assertRegex(version['cytoscapeVersion'], '([0-9]+\\.[0-9]+)\\..*$')

        input('Terminate Cytoscape and hit [enter]')
        self.assertRaises(requests.exceptions.RequestException, PyCy3.cytoscape_version_info)
        input('Restart Cytoscape, wait for startup to complete, and then hit [enter]')

    #    @PyCy3.skip
    @PyCy3.print_entry_exit
    def test_cytoscape_api_versions(self):
        self.assertSetEqual(set(PyCy3.cytoscape_api_versions()), set(['v1']))

    #    @PyCy3.skip
    @PyCy3.print_entry_exit
    def test_cytoscape_number_of_cores(self):
        cores = PyCy3.cytoscape_number_of_cores()
        self.assertIsInstance(cores, int)
        self.assertTrue(cores >= 1)

    #    @PyCy3.skip
    @PyCy3.print_entry_exit
    def test_cytoscape_memory_status(self):
        status = PyCy3.cytoscape_memory_status()
        self.assertIsInstance(status, dict)
        self.assertTrue(set(status).issuperset({'usedMemory', 'freeMemory', 'totalMemory', 'maxMemory'}))
        for mem in status:
            self.assertIsInstance(status[mem], int)

    #    @PyCy3.skip
    @PyCy3.print_entry_exit
    def test_cytoscape_free_memory(self):
        res = PyCy3.cytoscape_free_memory()
        self.assertEqual(res, 'Unused memory freed up.')


if __name__ == '__main__':
    unittest.main()
