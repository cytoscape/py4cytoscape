# -*- coding: utf-8 -*-

""" Test functions in tools.py.
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
import time
from requests import HTTPError

from test_utils import *


class ToolsTests(unittest.TestCase):
    def setUp(self):
        # Close all browser windows if possible
        try:
            for browser in cybrowser_list():
                cybrowser_close(browser['id'])
        except:
            pass

    def tearDown(self):
        pass

    BROWSER_HELLO = {'id': 'Browser Hello ID',
                     'show': {'func': lambda x, y: cybrowser_show(id=x, title=y,
                                                                               text='<HTML><HEAD><TITLE>Hello</TITLE></HEAD><BODY>Hello, world!</BODY></HTML>'),
                              'title': 'Browser Hello Page'},
                     'dialog': {'func': lambda x, y: cybrowser_dialog(id=x, title=y,
                                                                                   text='<HTML><HEAD><TITLE>Hello</TITLE></HEAD><BODY>Hello, world!</BODY></HTML>'),
                                'title': 'Hello'}}
    CYTOSCAPE_HOME_PAGE = {'id': 'Cytoscape Home Page ID',
                           'show': {
                               'func': lambda x, y: cybrowser_show(id=x, title=y, url='http://www.cytoscape.org'),
                               'title': 'Cytoscape Home Page'},
                           'dialog': {
                               'func': lambda x, y: cybrowser_dialog(id=x, title=y,
                                                                                  url='http://www.cytoscape.org'),
                               'title': 'Cytoscape: An Open Source Platform for Complex Network Analysis and Visualization'}}
    CYTOSCAPE_MANUAL = {'id': 'Cytoscape Manual ID',
                        'show': {'func': lambda x, y: cybrowser_show(id=x, title=y,
                                                                                  url='http://manual.cytoscape.org/en/3.7.2/'),
                                 'title': 'Cytoscape Manual Page'},
                        'dialog': {
                            'func': lambda x, y: cybrowser_dialog(id=x, title=y,
                                                                               url='http://manual.cytoscape.org/en/3.7.2/'),
                            'title': 'Cytoscape 3.7.2 User Manual â€” Cytoscape User Manual 3.7.2 documentation'}}

    
    @print_entry_exit
    def test_cybrowser_version(self):
        # Verify that a version is reported
        version = cybrowser_version()
        self.assertIsInstance(version, dict)
        self.assertIsInstance(version['version'], str)

    @unittest.skipIf(skip_for_ui(), 'Avoiding test that requires user response')
    @print_entry_exit
    def test_cybrowser_show_list_hide(self):
        self.cybrowser_windows('show')

    @unittest.skipIf(skip_for_ui(), 'Avoiding test that requires user response')
    @print_entry_exit
    def test_cybrowser_dialog_list_hide(self):
        self.cybrowser_windows('dialog')

    
    @unittest.skipIf(skip_for_ui(), 'Avoiding test that requires user response')
    @print_entry_exit
    def test_cybrowser_send(self):
        self._check_show('dialog', ToolsTests.CYTOSCAPE_HOME_PAGE)
        window_id = ToolsTests.CYTOSCAPE_HOME_PAGE['id']

        # Verify that the user agent variable can be fetched
        res = cybrowser_send(window_id, 'navigator.userAgent')
        self.assertIsInstance(res, dict)
        self.assertEqual(res['browserId'], window_id)
        self.assertIsInstance(res['result'], str)

        # Verify that the window can be moved to a different URL
        res = cybrowser_send(window_id, "window.location='http://google.com'")
        self.assertEqual(res['browserId'], window_id)
        self.assertEqual(res['result'], 'http://google.com')

        self.assertRaises(CyError, cybrowser_send, 'bogus window', 'navigator.userAgent')

        self.assertDictEqual(cybrowser_send(window_id, 'bogus_statement'), {})

    
    @print_entry_exit
    def test_diffusion_basic(self):
        # Initialization
        load_test_session()

        # Verify that selecting a node and calling diffusion returns a bunch of nodes
        select_nodes(['RAP1'], by_col='COMMON')
        res = diffusion_basic()
        self.assertIsInstance(res, dict)
        self.assertEqual(res['heatColumn'], 'diffusion_output_heat')
        self.assertEqual(res['rankColumn'], 'diffusion_output_rank')
        self.assertTrue(len(get_selected_nodes()) > 0)

        # Verify that diffusion returns nodes even when nothing is selected
        clear_selection()
        res = diffusion_basic()
        self.assertIsInstance(res, dict)
        self.assertEqual(res['heatColumn'], 'diffusion_output_1_heat')
        self.assertEqual(res['rankColumn'], 'diffusion_output_1_rank')
        self.assertTrue(len(get_selected_nodes()) > 0)

    @print_entry_exit
    def test_diffusion_advanced(self):
        # Initialization
        load_test_session()

        # Verify that selecting a node and calling diffusion returns a bunch of nodes
        select_nodes(['RAP1'], by_col='COMMON')
        res = diffusion_advanced(heat_column_name='', time=0.1)
        self.assertIsInstance(res, dict)
        self.assertEqual(res['heatColumn'], 'diffusion_output_heat')
        self.assertEqual(res['rankColumn'], 'diffusion_output_rank')
        self.assertTrue(len(get_selected_nodes()) > 0)

        # Verify that diffusion returns nodes even when nothing is selected
        clear_selection()
        res = diffusion_advanced(heat_column_name='diffusion_output_heat', time=0.2)
        self.assertIsInstance(res, dict)
        self.assertEqual(res['heatColumn'], 'diffusion_output_1_heat')
        self.assertEqual(res['rankColumn'], 'diffusion_output_1_rank')
        self.assertTrue(len(get_selected_nodes()) > 0)

        # Verify that a bad parameter causes an exception
        self.assertRaises(CyError, diffusion_advanced, heat_column_name='diffusion_output_heat', time='x')

    def cybrowser_windows(self, operation='show'):

        def check_browser_list(browser_list, expected_list):  # doesn't support duplicate ID keys
            browser = {b['id']: b for b in browser_list}
            expected = {b['id']: b for b in expected_list}
            self.assertEqual(len(browser), len(expected))
            for id, val in browser.items():
                self.assertIn(id, expected)
                self.assertEqual(val['title'], expected[id][operation]['title'])

        # Verify that the browser list starts out empty ... no browser windows displayed
        check_browser_list(cybrowser_list(), [])

        # Verify that a browser can be launched with all of its options
        self._check_show(operation, ToolsTests.BROWSER_HELLO)
        self._check_show(operation, ToolsTests.CYTOSCAPE_HOME_PAGE)
        self._check_show(operation, ToolsTests.CYTOSCAPE_MANUAL)

        # Verify that the browser list contains all of the new pages
        time.sleep(2)  # wait for windowing system to catch up
        check_browser_list(cybrowser_list(),
                           [ToolsTests.BROWSER_HELLO, ToolsTests.CYTOSCAPE_HOME_PAGE, ToolsTests.CYTOSCAPE_MANUAL])

        # Verify that adding the same pages doesn't change the browser list
        self._check_show(operation, ToolsTests.BROWSER_HELLO, skip_verify=True)
        self._check_show(operation, ToolsTests.BROWSER_HELLO, skip_verify=True)
        self._check_show(operation, ToolsTests.BROWSER_HELLO, skip_verify=True)
        time.sleep(2)  # wait for windowing system to catch up
        check_browser_list(cybrowser_list(),
                           [ToolsTests.BROWSER_HELLO, ToolsTests.CYTOSCAPE_HOME_PAGE, ToolsTests.CYTOSCAPE_MANUAL])

        # Verify that hiding a browser removes it from the browser list, and bogus browser windows don't cause error
        self.assertDictEqual(cybrowser_hide(ToolsTests.BROWSER_HELLO['id']), {})
        self.assertDictEqual(cybrowser_close(ToolsTests.CYTOSCAPE_HOME_PAGE['id']), {})
        time.sleep(2)  # wait for windowing system to catch up
        check_browser_list(cybrowser_list(), [ToolsTests.CYTOSCAPE_MANUAL, ToolsTests.BROWSER_HELLO])

        # Verify that closing a browser twice does no harm
        self.assertDictEqual(cybrowser_close(ToolsTests.CYTOSCAPE_HOME_PAGE['id']), {})
        time.sleep(2)  # wait for windowing system to catch up
        check_browser_list(cybrowser_list(), [ToolsTests.CYTOSCAPE_MANUAL, ToolsTests.BROWSER_HELLO])

        # Verify that closing the last browser window results in a clean browser list
        self.assertDictEqual(cybrowser_close(ToolsTests.BROWSER_HELLO['id']), {})
        self.assertDictEqual(cybrowser_close(ToolsTests.CYTOSCAPE_MANUAL['id']), {})
        time.sleep(2)  # wait for windowing system to catch up
        check_browser_list(cybrowser_list(), [])

    def _check_show(self, operation, window_def, skip_verify=False):
        show_result = window_def[operation]['func'](window_def['id'], window_def[operation]['title'])
        self.assertIsInstance(show_result, dict)
        self.assertEqual(show_result['id'], window_def['id'])
        if not skip_verify: input('Verify that the "' + window_def[operation]['title'] + '" is visible; hit Enter')


if __name__ == '__main__':
    unittest.main()
