# -*- coding: utf-8 -*-

""" Test functions in collections.py.
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

from test_utils import *


class CollectionsTests(unittest.TestCase):
    def setUp(self):
        try:
            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    
    @print_entry_exit
    def test_get_collection_list(self):
        # Verify that case of no collections is handled
        self.assertListEqual(get_collection_list(), [])

        # Verify that loading a single session returns a single collection
        load_test_session()
        self.assertSetEqual(set(get_collection_list()), {'galFiltered.sif'})

        # Verify that having two collections (one with two networks) returns two collections
        load_test_session('data/Multiple Collections.cys')
        self.assertSetEqual(set(get_collection_list()), {'galFiltered.sif', 'BINDyeast.sif'})

    
    @print_entry_exit
    def test_get_collection_suid(self):
        # Verify that an error is raised when no collections exist
        self.assertRaises(CyError, get_collection_suid, 'current')

        # Initialization
        load_test_session()
        galFiltered_collection_suid = get_collection_suid()

        # Verify that current network returns the appropriate SUID
        self.assertEqual(get_collection_suid(), galFiltered_collection_suid)
        self.assertEqual(get_collection_suid('current'), galFiltered_collection_suid)
        self.assertEqual(get_collection_suid(get_network_suid()), galFiltered_collection_suid)
        self.assertEqual(get_collection_suid('galFiltered.sif'), galFiltered_collection_suid)

        # Verify that bogus network returns nothing
        self.assertRaises(CyError, get_collection_suid, 'bogus')
        self.assertRaises(CyError, get_collection_suid, -1)

    
    @print_entry_exit
    def test_get_collection_name(self):
        # Verify that an error is raised when no collections exist
        self.assertRaises(CyError, get_collection_name, None)

        # Initialization
        load_test_session()
        galFiltered_collection_suid = get_collection_suid()

        # Verify that current collection returns the appropriate name
        self.assertEqual(get_collection_name(), 'galFiltered.sif')
        self.assertEqual(get_collection_name(galFiltered_collection_suid), 'galFiltered.sif')

        # TODO: Can't test fetching other names because we don't have access to other collection SUIDs ... can we fix this?

        # Verify that bogus collection SUID returns nothing
        self.assertRaises(CyError, get_collection_name, -1)

    
    @print_entry_exit
    def test_get_collection_networks(self):
        # Verify that an error is raised when no collections exist
        self.assertRaises(CyError, get_collection_networks, None)

        # Initialization
        load_test_session('data/Multiple Collections.cys')
        galFiltered_collection_suid = get_collection_suid()

        # Verify that current collection returns four subnetworks
        network_list = get_collection_networks()
        self.assertIsInstance(network_list, list)
        self.assertSetEqual({get_network_name(suid) for suid in network_list},
                            {'galFiltered.sif', 'galFiltered.sif(1)', 'galFiltered.sif(2)', 'yeastHighQuality.sif'})

        # Verify that named collection returns the same subnetworks
        self.assertSetEqual(set(network_list), set(get_collection_networks(galFiltered_collection_suid)))

        # Verify that bogus collection SUID returns nothing
        self.assertRaises(CyError, get_collection_networks, -1)


if __name__ == '__main__':
    unittest.main()
