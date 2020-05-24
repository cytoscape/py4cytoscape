# -*- coding: utf-8 -*-

""" Test functions in user_interface.py.
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
# TODO: Remember to add licensing boilerplate to RCy3 modules

import unittest
from requests import HTTPError

from test_utils import *


class UserInterfaceTests(unittest.TestCase):
    def setUp(self):
        try:
            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    
    @print_entry_exit
    def test_dock_hide_float_panel(self):
        # Initialization
        load_test_session()

        def check_panel(panel_name, panel_aliases):
            self.assertEqual(float_panel(panel_name), '')
            input('Verify that "' + panel_name + '" has floated')
            self.assertEqual(hide_panel(panel_name), '')
            input('Verify that "' + panel_name + '" has hidden')
            self.assertEqual(dock_panel(panel_name), '')
            input('Verify that "' + panel_name + '" has docked')

            for p in panel_aliases:
                self.assertEqual(float_panel(panel_name), '')
                self.assertEqual(hide_panel(panel_name), '')
                self.assertEqual(dock_panel(panel_name), '')

        check_panel('table panel', {'SOUTH', 'table', 'ta'})
        check_panel('tool panel', {'SOUTH_WEST', 'tool', 'to'})
        check_panel('control panel', {'WEST', 'control', 'c'})
        check_panel('results panel', {'EAST', 'results', 'r'})

        # Verify that an unknown panel is caught
        self.assertRaises(CyError, dock_panel, 'bogus')

    
    @print_entry_exit
    def test_dock_hide_float_panel(self):
        # Initialization
        load_test_session()

        # Float everything so we can then hide everything
        self.assertEqual(float_panel('SOUTH'), '')
        self.assertEqual(float_panel('SOUTH_WEST'), '')
        self.assertEqual(float_panel('WEST'), '')
        self.assertEqual(float_panel('EAST'), '')

        input('Verify that all four panels are floated')
        hide_all_panels()
        input('Verify that all four panels are hidden')


if __name__ == '__main__':
    unittest.main()
