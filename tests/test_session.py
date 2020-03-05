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

    @skip
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

        # Verify that file opens if direct URL is used
        # This should work, but doesn't at the CyREST level ... so, I'm commenting it out for now
        # self.assertDictEqual(open_session('https://github.com/bdemchak/PyCy3/blob/master/tests/data/Affinity%20Purification.cys'), {})
        # self.assertEqual(get_network_count(), 1)
        # self.assertEqual(get_network_name(), 'HIV-human PPI')
        # close_session()

        # Verify that file opens if a direct filename is used
        self.assertDictEqual(open_session('data/Affinity Purification.cys'), {})
        self.assertEqual(get_network_count(), 1)
        self.assertEqual(get_network_name(), 'HIV-human PPI')

    @skip
    @print_entry_exit
    def test_save_session(self):
        # Verify that the .cys suffix is added if it's not in the filename
        OTHER_NAME = 'other'
        OTHER_NAME_CYS = OTHER_NAME + '.cys'
        self._clean_session_file(OTHER_NAME_CYS)
        self._load_test_session()
        save_session(OTHER_NAME)
        self.assertTrue(os.path.isfile(OTHER_NAME_CYS))
        self._clean_session_file(OTHER_NAME_CYS)

        # Verify that the .cys suffix is not added if it's already in the filename
        save_session(OTHER_NAME_CYS)
        self.assertTrue(os.path.isfile(OTHER_NAME_CYS))

        # Verify that a session file can be overwritten
        orig_written = os.stat(OTHER_NAME_CYS).st_mtime
        save_session(OTHER_NAME_CYS)
        last_written = os.stat(OTHER_NAME_CYS).st_mtime
        self.assertTrue(orig_written != last_written)

        # Verify that if a session was loaded from a file, saving to an empty filename refreshes the file
        open_session(OTHER_NAME_CYS)
        self._clean_session_file(OTHER_NAME_CYS)
        save_session()
        self.assertTrue(os.path.isfile(OTHER_NAME_CYS))
        self._clean_session_file(OTHER_NAME_CYS)

        # Verify that an error is thrown if a crazy file name is used
        self.assertRaises(CyError, save_session, "totallybogusdir/bogusfile")

    def _load_test_session(self, session_filename=None):
        open_session(session_filename)

    def _clean_session_file(self, session_filename):
        if os.path.isfile(session_filename): os.remove(session_filename)

if __name__ == '__main__':
    unittest.main()