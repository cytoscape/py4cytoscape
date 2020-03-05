# -*- coding: utf-8 -*-

import unittest
import os

from PyCy3 import *
from PyCy3.decorators import *

class SessionTests(unittest.TestCase):
    def setUp(self):
        try:
            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass


    @skip
    @print_entry_exit
    def test_close_session(self):

        # See what happens when closing and no session is open
        self.assertDictEqual(close_session(False), {})

        # Verify that closing a session without saving works
        self._load_test_session()
        self.assertDictEqual(close_session(False), {})

        # Verify that closing a session after saving works
        SESSION_TEST = 'close_session_test.cys'
        self._clean_session_file(SESSION_TEST)
        self._load_test_session()
        self.assertDictEqual(close_session(True, SESSION_TEST), {})
        self.assertTrue(os.path.isfile(SESSION_TEST))
        self._clean_session_file(SESSION_TEST)

        # Verify that an error is thrown if a crazy file name is used
        self._load_test_session()
        self.assertRaises(CyError, close_session, True, "totallybogusdir/bogusfile")

    #    @skip
    @print_entry_exit
    def test_open_session(self):

        # Verify that the default network is loaded
        self.assertDictEqual(open_session(), {})
        self.assertEqual(get_network_count(), 1)
        self.assertEqual(get_network_name(), 'galFiltered.sif')

        # Verify that an error is thrown if a crazy file name is used
        self.assertRaises(CyError, open_session, "bogusfile")

        # Verify that an error is thrown if a crazy URL is used
        self.assertRaises(CyError, open_session, "http://bogusfile")

        # Verify that file opens if a direct filename is used
        self.assertDictEqual(open_session('data/Affinity Purification.cys'), {})
        self.assertEqual(get_network_count(), 1)
        self.assertEqual(get_network_name(), 'HIV-human PPI')

    def _load_test_session(self, session_filename=None):
        open_session(session_filename)

    def _clean_session_file(self, session_filename):
        if os.path.isfile(session_filename): os.remove(session_filename)

if __name__ == '__main__':
    unittest.main()