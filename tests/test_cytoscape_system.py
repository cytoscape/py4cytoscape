# -*- coding: utf-8 -*-

""" Test functions in cytoscape_system.py.
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

from test_utils import *


class AppsTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skipIf(skip_for_ui(), 'Avoiding test that requires user response')
    @print_entry_exit
    def test_cytoscape_ping(self):
        self.assertIsNone(cytoscape_ping())

        input('Terminate Cytoscape and hit [enter]')
        self.assertRaises(requests.exceptions.RequestException, cytoscape_ping)
        input('Restart Cytoscape, wait for startup to complete, and then hit [enter]')

    
    @unittest.skipIf(skip_for_ui(), 'Avoiding test that requires user response')
    @print_entry_exit
    def test_cytoscape_version_info(self):
        version = cytoscape_version_info()
        self.assertEqual(version['apiVersion'], 'v1')
        self.assertRegex(version['cytoscapeVersion'], '([0-9]+\\.[0-9]+)\\..*$')

        input('Terminate Cytoscape and hit [enter]')
        self.assertRaises(requests.exceptions.RequestException, cytoscape_version_info)
        input('Restart Cytoscape, wait for startup to complete, and then hit [enter]')

    
    @print_entry_exit
    def test_cytoscape_api_versions(self):
        self.assertSetEqual(set(cytoscape_api_versions()), set(['v1']))

    
    @print_entry_exit
    def test_cytoscape_number_of_cores(self):
        cores = cytoscape_number_of_cores()
        self.assertIsInstance(cores, int)
        self.assertTrue(cores >= 1)

    
    @print_entry_exit
    def test_cytoscape_memory_status(self):
        status = cytoscape_memory_status()
        self.assertIsInstance(status, dict)
        self.assertTrue(set(status).issuperset({'usedMemory', 'freeMemory', 'totalMemory', 'maxMemory'}))
        for mem in status:
            self.assertIsInstance(status[mem], int)

    
    @print_entry_exit
    def test_cytoscape_free_memory(self):
        res = cytoscape_free_memory()
        self.assertEqual(res, 'Unused memory freed up.')


if __name__ == '__main__':
    unittest.main()
