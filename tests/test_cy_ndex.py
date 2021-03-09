# -*- coding: utf-8 -*-

""" Test functions cy_ndex.py.
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


class CyNDExTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    _NDEX_USERID = 'cytoscape_test'
    _NDEX_PASSWORD = 'cytoscape_rocks'
    _NDEX_SERVER_WAIT_SECS = 10

    @unittest.skip('Get_network_ndex_id returns the first network UUID regardless ... it should scan for the network SUID')
    @print_entry_exit
    def test_get_export_network_ndex_id(self):
        # Initialization
        load_test_session()
        load_test_network('data/yeastHighQuality.sif', make_current=False)

        # Verify that unstored networks have a UUID of None
        self.assertIsNone(get_network_ndex_id())
        self.assertIsNone(get_network_ndex_id(network='yeastHighQuality.sif'))

        # Verify that storing the first (and selected) network returns a UUID and it matches what's fetched separately
        galFiltered_uuid = export_network_to_ndex(self._NDEX_USERID, self._NDEX_PASSWORD, False)
        self.assertIsInstance(galFiltered_uuid, str)
        fetched_galFiltered_uuid = get_network_ndex_id()
        self.assertIsInstance(fetched_galFiltered_uuid, str)
        self.assertEqual(galFiltered_uuid, fetched_galFiltered_uuid)
        time.sleep(self._NDEX_SERVER_WAIT_SECS) # Give NDEx a chance to file the network before asking for it again.

        # Verify that storing the second (and unselected) network returns a UUID and it matches what's fetched separately
        yeast_uuid = export_network_to_ndex(self._NDEX_USERID, self._NDEX_PASSWORD, False, network='yeastHighQuality.sif')
        self.assertIsInstance(yeast_uuid, str)
        fetched_yeast_uuid = get_network_ndex_id(network='yeastHighQuality.sif')
        self.assertIsInstance(fetched_yeast_uuid, str)
        # TODO: This fails because get_network_ndex_id returns the first network's UUID regardless ... it should scan for the network's SUID
        self.assertEqual(yeast_uuid, fetched_yeast_uuid)

        # Verify that bad credentials are caught
        self.assertRaises(CyError, export_network_to_ndex, 'BogusUser', self._NDEX_PASSWORD, False)
        self.assertRaises(CyError, export_network_to_ndex, self._NDEX_USERID, 'BogusPassword', False)

        # Verify that a bad network is caught
        self.assertRaises(CyError, get_network_ndex_id, network='BogusNetwork')
        self.assertRaises(CyError, export_network_to_ndex, self._NDEX_USERID, self._NDEX_PASSWORD, False, network='BogusNetwork')

    @print_entry_exit
    def test_update_network_ndex_id(self):
        # TODO: Find out how to test isPublic and metadata
        # Initialization
        load_test_session()
        galFiltered_uuid = export_network_to_ndex(self._NDEX_USERID, self._NDEX_PASSWORD, False)
        time.sleep(self._NDEX_SERVER_WAIT_SECS) # Give NDEx a chance to file the network before asking for it again.

        # Verify that the network (with all nodes selected) can be updated on NDEx and that the same UUID is returned
        all_node_names = node_suid_to_node_name(select_all_nodes())
        updated_galFiltered_uuid = update_network_in_ndex(self._NDEX_USERID, self._NDEX_PASSWORD, False)
        self.assertIsInstance(updated_galFiltered_uuid, str)
        self.assertEqual(updated_galFiltered_uuid, galFiltered_uuid)
        time.sleep(self._NDEX_SERVER_WAIT_SECS) # Give NDEx a chance to file the network before asking for it again.

        # Verify that when the network is reloaded, it still has all nodes selected and the same UUID
        close_session(False)
        fetched_galFiltered_suid = import_network_from_ndex(updated_galFiltered_uuid, self._NDEX_USERID, self._NDEX_PASSWORD)
        self.assertIsInstance(fetched_galFiltered_suid, int)
        selected_nodes = get_selected_nodes(network=fetched_galFiltered_suid)
        self.assertSetEqual(set(selected_nodes), set(all_node_names))

        # Verify that bad credentials are caught
        self.assertRaises(CyError, update_network_in_ndex, 'BogusUser', self._NDEX_PASSWORD, False)
        self.assertRaises(CyError, update_network_in_ndex, self._NDEX_USERID, 'BogusPassword', False)

        # Verify that a bad network is caught
        self.assertRaises(CyError, update_network_in_ndex, self._NDEX_USERID, self._NDEX_PASSWORD, False, network='BogusNetwork')

    @print_entry_exit
    def test_import_network_from_ndex(self):
        # TODO: Find out how to test accessKey
        # Initialization
        load_test_session()
        galFiltered_uuid = export_network_to_ndex(self._NDEX_USERID, self._NDEX_PASSWORD, False)
        all_node_names = get_all_nodes()
        close_session(False)
        time.sleep(self._NDEX_SERVER_WAIT_SECS) # Give NDEx a chance to file the network before asking for it again.

        # Verify that the network can be loaded from NDEx and it has the same nodes
        fetched_galFiltered_suid = import_network_from_ndex(galFiltered_uuid, self._NDEX_USERID, self._NDEX_PASSWORD)
        self.assertIsInstance(fetched_galFiltered_suid, int)
        all_fetched_node_names = get_all_nodes(fetched_galFiltered_suid)
        self.assertSetEqual(set(all_fetched_node_names), set(all_node_names))

        # Verify that bad credentials are caught
        self.assertRaises(CyError, import_network_from_ndex, galFiltered_uuid, 'BogusUser', self._NDEX_PASSWORD)
        self.assertRaises(CyError, import_network_from_ndex, galFiltered_uuid, self._NDEX_USERID, 'BogusPassword')
        self.assertRaises(CyError, import_network_from_ndex, galFiltered_uuid, access_key='BogusKey')

        # Initialization for subdomain param
        load_test_session()
        sub_galFiltered_uuid = export_network_to_ndex(self._NDEX_USERID, self._NDEX_PASSWORD, False, ndex_url="http://test.ndexbio.org/", ndex_version="v2")
        sub_all_node_names = get_all_nodes()
        close_session(False)
        time.sleep(self._NDEX_SERVER_WAIT_SECS) # Give NDEx a chance to file the network before asking for it again.

        # Verify that the network can be loaded from test server and it has the same nodes
        sub_fetched_galFiltered_suid = import_network_from_ndex(galFiltered_uuid, self._NDEX_USERID, self._NDEX_PASSWORD, ndex_url="http://test.ndexbio.org/", ndex_version="v2")
        self.assertIsInstance(sub_fetched_galFiltered_suid, int)
        sub_all_fetched_node_names = get_all_nodes(sub_fetched_galFiltered_suid)
        self.assertSetEqual(set(sub_all_fetched_node_names), set(sub_all_node_names))

if __name__ == '__main__':
    unittest.main()
