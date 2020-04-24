# -*- coding: utf-8 -*-

import unittest
from requests import HTTPError

from test_utils import *

class UserInterfaceTests(unittest.TestCase):
    def setUp(self):
        try:
            PyCy3.delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

#    @PyCy3.skip
    @PyCy3.print_entry_exit
    def test_dock_hide_float_panel(self):
        # Initialization
        load_test_session()

        def check_panel(panel_name, panel_aliases):
            self.assertEqual(PyCy3.float_panel(panel_name), '')
            input('Verify that "' + panel_name + '" has floated')
            self.assertEqual(PyCy3.hide_panel(panel_name), '')
            input('Verify that "' + panel_name + '" has hidden')
            self.assertEqual(PyCy3.dock_panel(panel_name), '')
            input('Verify that "' + panel_name + '" has docked')

            for p in panel_aliases:
                self.assertEqual(PyCy3.float_panel(panel_name), '')
                self.assertEqual(PyCy3.hide_panel(panel_name), '')
                self.assertEqual(PyCy3.dock_panel(panel_name), '')

        check_panel('table panel', {'SOUTH', 'table', 'ta'})
        check_panel('tool panel', {'SOUTH_WEST', 'tool', 'to'})
        check_panel('control panel', {'WEST', 'control', 'c'})
        check_panel('results panel', {'EAST', 'results', 'r'})

        # Verify that an unknown panel is caught
        self.assertRaises(PyCy3.CyError, PyCy3.dock_panel, 'bogus')

#    @PyCy3.skip
    @PyCy3.print_entry_exit
    def test_dock_hide_float_panel(self):
        # Initialization
        load_test_session()

        # Float everything so we can then hide everything
        self.assertEqual(PyCy3.float_panel('SOUTH'), '')
        self.assertEqual(PyCy3.float_panel('SOUTH_WEST'), '')
        self.assertEqual(PyCy3.float_panel('WEST'), '')
        self.assertEqual(PyCy3.float_panel('EAST'), '')

        input('Verify that all four panels are floated')
        PyCy3.hide_all_panels()
        input('Verify that all four panels are hidden')

if __name__ == '__main__':
    unittest.main()