# -*- coding: utf-8 -*-

""" Test functions in apps.py.

License:
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

    
    @print_entry_exit
    def test_get_app_information(self):
        # Verify that a well-formed information record is returned for a known app
        res = get_app_information('stringApp')
        self.assertIsInstance(res, dict)
        self.assertTrue(set(res).issuperset({'app', 'descriptionName', 'version'}))
        self.assertEqual(res['app'], 'stringApp')
        self.assertIsInstance(res['descriptionName'], str)
        self.assertRegex(res['version'], '[0-9]+\\.[0-9]+\\.[0-9]+.*$')  # Verify that version looks like x.y.z

        # Verify that an unknown app is caught
        self.assertRaises(CyError, get_app_information, 'bogus')

    
    @print_entry_exit
    def test_get_available_apps(self):
        # Verify that app list contains expected dicts and at least some of the expected apps
        res = get_available_apps()
        self.assertIsInstance(res, list)
        self.assertFalse(False in [set(app_info).issuperset({'appName', 'description', 'details'}) for app_info in res])
        app_names = {app_info['appName'] for app_info in res}
        self.assertTrue(app_names.issuperset({'stringApp', 'BiNGO', 'CyPath2'}))

    
    @print_entry_exit
    def test_get_installed_apps(self):
        # Verify that app list contains expected dicts and at least some of the expected apps
        res = get_installed_apps()
        self.assertIsInstance(res, list)
        self.assertFalse(
            False in [set(app_info).issuperset({'appName', 'version', 'description', 'status'}) for app_info in res])
        app_names = {app_info['appName'] for app_info in res}
        self.assertTrue(app_names.issuperset(
            {'PSICQUIC Web Service Client', 'JSON Support', 'Diffusion', "PSI-MI Reader", "CX Support", "Analyzer",
             "OpenCL Prefuse Layout", "Core Apps", "Merge", "cyREST", "copycatLayout", "CyCL", "cyChart", "SBML Reader",
             "BioPAX Reader", "Biomart Web Service Client", "cyBrowser", "ID Mapper", "CyNDEx-2"}))

    
    @print_entry_exit
    def test_list_disable_enable_apps(self):
        # Initialization
        APP_NAME = 'boundaryLayout'  # Some app that's unlikely to be already installed
        BAD_APP_NAME = 'totaljunk'
        EMPTY_APP_NAME = ''
        uninstall_app(APP_NAME)

        # Install an app and remember what the disabled list was ... verify that the app isn't on it
        self.assertDictEqual(install_app(APP_NAME), {})
        pre_disabled_app_names = {app['appName'] for app in get_disabled_apps()}
        self.assertNotIn(APP_NAME, pre_disabled_app_names)

        # Verify that the app can be disabled and that it then shows up on the disabled list
        self.assertDictEqual(disable_app(APP_NAME), {'appName': APP_NAME})
        self.assertIn(APP_NAME, [app['appName'] for app in get_disabled_apps()])

        # Verify that the disabled list is in good form
        res = get_installed_apps()
        self.assertIsInstance(res, list)
        self.assertFalse(
            False in [set(app_info).issuperset({'appName', 'version', 'description', 'status'}) for app_info in res])

        # Verify that disabling the app again doesn't have any effect
        self.assertDictEqual(disable_app(APP_NAME), {'appName': APP_NAME})
        self.assertIn(APP_NAME, [app['appName'] for app in get_disabled_apps()])

        # Verify that the app can be enabled and that it doesn't show up on the disabled list after that
        self.assertDictEqual(enable_app(APP_NAME), {'appName': APP_NAME})
        self.assertSetEqual({app['appName'] for app in get_disabled_apps()}, pre_disabled_app_names)

        # Verify that enabling the app again doesn't have any effect
        self.assertDictEqual(enable_app(APP_NAME), {'appName': APP_NAME})
        self.assertSetEqual({app['appName'] for app in get_disabled_apps()}, pre_disabled_app_names)

        # Uninstall the app just to be clean
        self.assertDictEqual(uninstall_app(APP_NAME), {'appName': APP_NAME})

        # Verify that enabling and disabling a non-existent app is caught
        self.assertDictEqual(enable_app(BAD_APP_NAME), {'appName': BAD_APP_NAME})
        self.assertNotIn(BAD_APP_NAME, [app['appName'] for app in get_disabled_apps()])
        self.assertDictEqual(disable_app(BAD_APP_NAME), {'appName': BAD_APP_NAME})
        self.assertNotIn(BAD_APP_NAME, [app['appName'] for app in get_disabled_apps()])
        self.assertDictEqual(enable_app(EMPTY_APP_NAME), {'appName': EMPTY_APP_NAME})
        self.assertNotIn(EMPTY_APP_NAME, [app['appName'] for app in get_disabled_apps()])
        self.assertDictEqual(disable_app(EMPTY_APP_NAME), {'appName': EMPTY_APP_NAME})
        self.assertNotIn(EMPTY_APP_NAME, [app['appName'] for app in get_disabled_apps()])

    
    @print_entry_exit
    def test_install_uninstall_app(self):
        # Initialization
        APP_NAME = 'boundaryLayout'  # Some app that's unlikely to be already installed
        BAD_APP_NAME = 'totaljunk'
        EMPTY_APP_NAME = ''

        # Verify that app list doesn't already contain the test app
        pre_install = get_installed_apps()
        pre_install_app_names = {app_info['appName'] for app_info in pre_install}
        self.assertNotIn(APP_NAME, pre_install_app_names)

        # Verify that app is in uninstalled list
        pre_uninstall = get_uninstalled_apps()
        pre_uninstall_app_names = {app_info['appName'] for app_info in pre_uninstall}
        self.assertIn(APP_NAME, pre_uninstall_app_names)

        # Verify that installing an app is reflected in the app list and is removed from uninstalled list
        self.assertDictEqual(install_app(APP_NAME), {})
        self.assertIn(APP_NAME, {app_info['appName'] for app_info in get_installed_apps()})
        self.assertNotIn(APP_NAME, {app_info['appName'] for app_info in get_uninstalled_apps()})

        # Verify that installing an app twice doesn't change the app list
        self.assertDictEqual(install_app(APP_NAME), {})
        self.assertIn(APP_NAME, {app_info['appName'] for app_info in get_installed_apps()})

        # Verify that uninstalling an app is reflected in the app list and the uninstalled list
        self.assertDictEqual(uninstall_app(APP_NAME), {'appName': APP_NAME})
        self.assertNotIn(APP_NAME, {app_info['appName'] for app_info in get_installed_apps()})
        self.assertSetEqual({app['appName'] for app in get_installed_apps()}, pre_install_app_names)
        self.assertIn(APP_NAME, {app_info['appName'] for app_info in get_uninstalled_apps()})
        self.assertSetEqual({app['appName'] for app in get_uninstalled_apps()}, pre_uninstall_app_names)

        # Verify that uninstalling an app twice doesn't change the app list
        self.assertDictEqual(uninstall_app(APP_NAME), {'appName': APP_NAME})
        self.assertNotIn(APP_NAME, {app_info['appName'] for app_info in get_installed_apps()})

        # Verify that installing or uninstalling a non-existent app doesn't change the app list
        self.assertDictEqual(install_app(BAD_APP_NAME), {})
        self.assertNotIn(BAD_APP_NAME, {app_info['appName'] for app_info in get_installed_apps()})
        self.assertDictEqual(uninstall_app(BAD_APP_NAME), {'appName': BAD_APP_NAME})
        self.assertNotIn(BAD_APP_NAME, {app_info['appName'] for app_info in get_installed_apps()})
        self.assertDictEqual(install_app(EMPTY_APP_NAME), {})
        self.assertNotIn(EMPTY_APP_NAME, {app_info['appName'] for app_info in get_installed_apps()})
        self.assertDictEqual(uninstall_app(EMPTY_APP_NAME), {'appName': EMPTY_APP_NAME})
        self.assertNotIn(EMPTY_APP_NAME, {app_info['appName'] for app_info in get_installed_apps()})

    
    @print_entry_exit
    def test_get_app_updates(self):
        # Testing this requires some pretty contrived app store setup, so we just go simple here
        self.assertIsInstance(get_app_updates(), list)

    
    @print_entry_exit
    def test_open_app_store(self):
        # Initialization
        APP_NAME = 'boundaryLayout'  # Some app that's unlikely to be already installed
        BAD_APP_NAME = 'totaljunk'

        self.assertDictEqual(open_app_store(APP_NAME), {})
        input('Verify that the app store page for ' + APP_NAME + ' is loaded')

        self.assertDictEqual(open_app_store(BAD_APP_NAME), {})
        input('Verify that an app store error page is loaded')

        self.assertDictEqual(open_app_store(''), {})
        input('Verify that the app store main page is loaded')

    
    @print_entry_exit
    def test_get_app_status(self):
        # Initialization
        APP_NAME = 'boundaryLayout'
        BAD_APP_NAME = 'totaljunk'
        EMPTY_APP_NAME = ''

        self.assertDictEqual(install_app(APP_NAME), {})
        self.assertDictEqual(get_app_status(APP_NAME), {'appName': APP_NAME, 'status': 'Installed'})

        self.assertDictEqual(disable_app(APP_NAME), {'appName': APP_NAME})
        self.assertDictEqual(get_app_status(APP_NAME), {'appName': APP_NAME, 'status': 'Disabled'})

        self.assertDictEqual(enable_app(APP_NAME), {'appName': APP_NAME})
        self.assertDictEqual(get_app_status(APP_NAME), {'appName': APP_NAME, 'status': 'Installed'})

        self.assertDictEqual(uninstall_app(APP_NAME), {'appName': APP_NAME})
        self.assertDictEqual(get_app_status(APP_NAME), {'appName': APP_NAME, 'status': 'Uninstalled'})

        self.assertRaises(CyError, get_app_status, EMPTY_APP_NAME)
        self.assertRaises(CyError, get_app_status, BAD_APP_NAME)

    
    @print_entry_exit
    def test_update_app(self):
        # Initialization
        APP_NAME = 'boundaryLayout'
        BAD_APP_NAME = 'totaljunk'
        EMPTY_APP_NAME = ''

        # Testing this requires some pretty contrived app store setup, so we just go simple here
        self.assertIsInstance(update_app(APP_NAME), list)
        self.assertIsInstance(update_app(BAD_APP_NAME), list)
        self.assertIsInstance(update_app(EMPTY_APP_NAME), list)


if __name__ == '__main__':
    unittest.main()
