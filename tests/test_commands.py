# -*- coding: utf-8 -*-

""" Test functions in commands.py.
"""

"""License:
    Copyright 2020-2022 The Cytoscape Consortium

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
import json
from requests import RequestException

from test_utils import *


class CommandsTests(unittest.TestCase):
    def setUp(self):
        try:
            close_session(False)
        #            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    @print_entry_exit
    def test_cyrest_api(self):
        self.assertTrue(cyrest_api())

        time.sleep(30) # This is tricky ... it seems like bad things happen if cyrest_api doesn't wait until completion

    @print_entry_exit
    def test_cyrest_delete(self):
        # Initialization
        load_test_session()
        cur_network_suid = get_network_suid()

        # Verify that deleting a view returns a non-JSON result
        self.assertEqual(len(get_network_views()), 1)
        res = cyrest_delete('networks/' + str(get_network_suid()) + '/views', require_json=False)
        self.assertEqual(res, '')

        # Verify that an HTTP error results in an exception
        self.assertListEqual(get_network_views(cur_network_suid), [])  # Behavior when there are no views
        self.assertRaises(RequestException, cyrest_delete, 'session',
                          base_url='http://totallybogus')  # test non-existent URL
        self.assertRaises(RequestException, cyrest_delete, 'session',
                          base_url='http://yahoo.com')  # test real URL that doesn't have API
        load_test_session()
        self.assertRaises(ValueError, cyrest_delete, 'networks/' + str(get_network_suid()) + '/views',
                          require_json=True)

        # Verify that getting rid of the session returns a valid JSON result
        res = cyrest_delete('session')
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {'message': 'New session created.'})

    @print_entry_exit
    def test_cyrest_get(self):

        #        running_remote(True)

        # Verify that starting a garbage collection returns a non-JSON result
        res = cyrest_get('gc', require_json=False)
        self.assertIsInstance(res, str)
        self.assertEqual(res, '')

        # Verify that errors are caught
        self.assertRaises(RequestException, cyrest_get, 'gc',
                          base_url='http://totallybogus')  # test non-existent URL
        self.assertRaises(RequestException, cyrest_get, 'gc',
                          base_url='http://yahoo.com')  # test real URL that doesn't have API
        self.assertRaises(ValueError, cyrest_get, 'gc', require_json=True)

        # Verify that getting the CyREST version returns a valid JSON result
        res = cyrest_get('version')
        self.assertIsInstance(res, dict)
        self.assertIsInstance(res['apiVersion'], str)
        self.assertIsInstance(res['cytoscapeVersion'], str)

    @print_entry_exit
    def test_cyrest_post(self):
        # Initialization
        load_test_session()

        # We would test for a POST that doesn't return JSON, but CyREST doesn't have any

        # Verify that adding a view returns a valid JSON result
        res = cyrest_delete('networks/' + str(get_network_suid()) + '/views',
                            require_json=False)  # Delete the existing view first
        self.assertEqual(res, '')
        res = cyrest_post('networks/' + str(get_network_suid()) + '/views')
        self.assertIsInstance(res, dict)
        self.assertIsInstance(res['networkViewSUID'], int)

        # Verify that passing a body works properly
        res = cyrest_post('commands/command/echo', body={'message': 'Hi there'})
        self.assertIsInstance(res, dict)
        self.assertListEqual(res['data'], ['Hi there'])
        self.assertListEqual(res['errors'], [])

        # Verify that errors are caught
        self.assertRaises(RequestException, cyrest_post, 'commands/command/echo', body={'message': 'Hi there'},
                          base_url='http://totallybogus')
        self.assertRaises(RequestException, cyrest_post, 'commands/command/echo', body={'message': 'Hi there'},
                          base_url='http://yahoo.com')

    @print_entry_exit
    def test_cyrest_put(self):
        # Initialization
        load_test_session()

        # We would test for a PUT that doesn't return JSON, but CyREST doesn't have any

        # Verify that setting a view returns a valid JSON result
        view = get_network_views()[0]
        res = cyrest_put('networks/views/currentNetworkView', body={'networkViewSUID': view})
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res['data'], {})
        self.assertListEqual(res['errors'], [])

        # Verify that errors are caught
        self.assertRaises(RequestException, cyrest_post, 'networks/views/currentNetworkView',
                          body={'networkViewSUID': view}, base_url='http://totallybogus')
        self.assertRaises(RequestException, cyrest_post, 'networks/views/currentNetworkView',
                          body={'networkViewSUID': view}, base_url='http://yahoo.com')

    @print_entry_exit
    def test_commands_api(self):
        self.assertTrue(commands_api())

        time.sleep(30) # This is tricky ... it seems like bad things happen if commands_api doesn't wait until completion

    @print_entry_exit
    def test_commands_get(self):
        # Verify the expected return from common commands
        self._check_cy_result(commands_get('command sleep duration=5'), [])
        self._check_cy_result(commands_get(''),
                              ['Available namespaces:', 'analyzer', 'apps', 'command', 'cybrowser', 'cychart',
                               'diffusion', 'edge', 'filter', 'group', 'idmapper', 'layout', 'network', 'node',
                               'session', 'table', 'view', 'vizmap'], allow_subset=True)
        self._check_cy_result(commands_get('view'),
                              ["Available commands for 'view':", 'create', 'destroy', 'export', 'fit content',
                               'fit selected', 'get current', 'list', 'set current', 'update'], allow_subset=True)
        self._check_cy_result(commands_get('apps status app="Network Merge"'),
                              ['app: Network Merge, status: Installed'])

        # Verify that we give a decent error when the command line is too long for an HTTP GET call
        try:
            res = commands_run(' long' * 10000)
            self.assertTrue(False, 'commands_get should have thrown a long URI exception but did not')
        except CyError as e:
            self.assertTrue('Bad Message 414' in str(e))
            self.assertTrue('URI Too Long' in str(e))

        # Verify that bad commands are caught
        self.assertRaises(CyError, commands_get, 'session open file="c:/file name"')
        self.assertRaises(RequestException, commands_get, '', base_url='http://totallybogus')
        self.assertRaises(Exception, commands_get, '', base_url='http://yahoo.com')

    @print_entry_exit
    def test_commands_help(self):
        # Verify the expected return from common commands
        self._check_cy_result(commands_help(),
                              ['analyzer', 'annotation', 'apps', 'command', 'cybrowser', 'cychart', 'diffusion', 'edge',
                               'filetransfer', 'filter', 'group', 'idmapper', 'layout', 'network', 'node', 'session',
                               'table', 'view', 'vizmap'], allow_subset=True)

        self._check_cy_result(commands_help('help'),
                              ['analyzer', 'annotation', 'apps', 'command', 'cybrowser', 'cychart', 'diffusion', 'edge',
                               'filetransfer', 'filter', 'group', 'idmapper', 'layout', 'network', 'node', 'session',
                               'table', 'view', 'vizmap'], allow_subset=True)

        self._check_cy_result(commands_help('apps'),
                              ['disable', 'enable', 'information', 'install', 'list available', 'list disabled',
                               'list installed', 'list uninstalled', 'list updates', 'open appstore', 'status',
                               'uninstall', 'update'], allow_subset=True)

        self._check_cy_result(commands_help('help apps'),
                              ['disable', 'enable', 'information', 'install', 'list available', 'list disabled',
                               'list installed', 'list uninstalled', 'list updates', 'open appstore', 'status',
                               'uninstall', 'update'], allow_subset=True)

        self._check_cy_result(commands_help('apps install'), ['app', 'file'], allow_subset=True)

        # Verify that bad commands are caught
        self.assertRaises(Exception, commands_help, 'bogus_junk')
        self.assertRaises(RequestException, commands_help, '', base_url='http://totallybogus')
        self.assertRaises(Exception, commands_help, '', base_url='http://yahoo.com')

    @print_entry_exit
    def test_commands_post(self):
        # Verify the expected return from common commands
        self._check_cy_result(commands_post('command sleep duration=5'), {})
        self._check_cy_result(commands_post('apps status app="Network Merge"'),
                              {'appName': 'Network Merge', 'status': 'Installed'})

        # Verify that bad commands are caught
        self.assertRaises(CyError, commands_post, 'session open file="c:/file name"')
        self.assertRaises(RequestException, commands_post, '', base_url='http://totallybogus')
        self.assertRaises(RequestException, commands_post, '', base_url='http://yahoo.com')

    @print_entry_exit
    def test_commands_run(self):
        # Initialization
        load_test_session()

        # Verify that a command can execute
        res = commands_run('session new destroyCurrentSession=true')
        self.assertIsInstance(res, list)
        self.assertListEqual(res, [])

        # Verify that we give a decent error when the command line is too long for an HTTP GET call
        try:
            res = commands_run('session new destroyCurrentSession=true' + ' long' * 10000)
            self.assertTrue(False, 'commands_run should have thrown a long URI exception but did not')
        except CyError as e:
            self.assertTrue('Bad Message 414' in str(e))
            self.assertTrue('URI Too Long' in str(e))

        # Verify that bad commands are caught
        self.assertRaises(CyError, commands_run, 'total junk')
        self.assertRaises(CyError, commands_run, 'session open file="c:/file name"')
        self.assertRaises(RequestException, commands_run, '', base_url='http://totallybogus')
        self.assertRaises(Exception, commands_run, '', base_url='http://yahoo.com')

    @print_entry_exit
    def test_commands_echo(self):
        # Verify that the command returns what's sent to it
        res = command_echo('Hi there')
        self.assertIsInstance(res, list)
        self.assertListEqual(res, ['Hi there'])

        # Verify that an empty message comes back as '*'
        res = command_echo()
        self.assertIsInstance(res, list)
        self.assertListEqual(res, ['*'])

        # Verify that bad commands are caught
        self.assertRaises(RequestException, command_echo, 'Hi there', base_url='http://totallybogus')
        self.assertRaises(RequestException, command_echo, 'Hi there', base_url='http://yahoo.com')

    @print_entry_exit
    def test_command_open_dialog(self):
        # Verify that open dialog command fails ... it seems to be missing in the CyREST command set
        self.assertRaises(CyError, command_open_dialog)

        # Verify that bad commands are caught
        self.assertRaises(RequestException, command_open_dialog, base_url='http://totallybogus')
        self.assertRaises(RequestException, command_open_dialog, base_url='http://yahoo.com')

    @unittest.skipIf(skip_for_ui(), 'Avoiding test that requires user response')
    @print_entry_exit
    def test_command_pause(self):
        # Verify that pause returns nothing at all
        input('Verify that the pause message appears next ...')
        res = command_pause()
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {})

        input('Verify that the pause message appears next ...')
        res = command_pause('Please click OK to continue.')
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {})

        # Verify that bad commands are caught
        self.assertRaises(RequestException, command_pause, base_url='http://totallybogus')
        self.assertRaises(RequestException, command_pause, base_url='http://yahoo.com')

    @unittest.skipIf(skip_for_ui(), 'Avoiding test that requires user response')
    @print_entry_exit
    def test_command_quit(self):
        # Verify that pause returns nothing at all
        res = command_quit()
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {})
        input('Verify that Cytoscape has terminated, then restart it ...')

        # Verify that bad commands are caught
        self.assertRaises(RequestException, command_quit, base_url='http://totallybogus')
        self.assertRaises(RequestException, command_quit, base_url='http://yahoo.com')

    @print_entry_exit
    def test_command_run_file(self):
        # Initialization
        load_test_session()
        CMD_FILE = 'data/CommandScript.txt'
        self.assertIsInstance(get_network_suid(), int)

        # Verify that script file returns nothing at all
        res = command_run_file(CMD_FILE)  # Execute cmd to create a new session (i.e., no network)
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {})
        self.assertRaises(Exception, get_network_suid)  # Check for there being no network anymore

        # Verify that bad commands are caught
        self.assertRaises(CyError, command_run_file, 'nosuchfile')
        self.assertRaises(RequestException, command_run_file, CMD_FILE, base_url='http://totallybogus')
        self.assertRaises(RequestException, command_run_file, CMD_FILE, base_url='http://yahoo.com')

    @unittest.skipIf(skip_for_ui(), 'Avoiding test that requires user response')
    @print_entry_exit
    def test_command_sleep(self):
        # Verify that pause returns nothing at all
        res = command_sleep()  # Try a no-duration sleep
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {})

        input('Ready to try a 10 second sleep ...')
        res = command_sleep(10)  # Try a 10s sleep
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {})

        # Verify that bad commands are caught
        self.assertRaises(RequestException, command_sleep, base_url='http://totallybogus')
        self.assertRaises(RequestException, command_sleep, base_url='http://yahoo.com')

    @print_entry_exit
    def test_command_2_get_query(self):

        def check_cmd(query, expected_url, expected_args):
            url = query[0]
            args = query[1]
            self.assertIsInstance(url, str)
            self.assertEqual(url, expected_url)
            if args or expected_args:
                self.assertIsInstance(args, dict)
                self.assertDictEqual(args, expected_args)

        # Check for a URL with no parameters
        check_cmd(commands._command_2_get_query('layout force-directed'),
                  'http://127.0.0.1:1234/v1/commands/layout/force-directed', None)

        # Check for a URL with a single scalar parameter
        check_cmd(commands._command_2_get_query('layout force-directed defaultNodeMass=1'),
                  'http://127.0.0.1:1234/v1/commands/layout/force-directed', {'defaultNodeMass': '1'})

        # Check for a URL with two parameters, one of which has an embedded blank
        check_cmd(commands._command_2_get_query('layout force-directed defaultNodeMass=1 file="C:\\file name"'),
                  'http://127.0.0.1:1234/v1/commands/layout/force-directed',
                  {'defaultNodeMass': '1', 'file': 'C:\\file name'})

    def _check_cy_result(self, actual_res, expected_res, allow_subset=False):
        if type(expected_res) is dict:
            self.assertDictEqual(actual_res, expected_res)
        else:
            self.assertIsInstance(actual_res, list)
            if allow_subset:
                self.assertTrue(set(expected_res).issubset(set(actual_res)))
            else:
                self.assertListEqual(actual_res, expected_res)


if __name__ == '__main__':
    unittest.main()
