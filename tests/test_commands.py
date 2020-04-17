# -*- coding: utf-8 -*-

import unittest
import json
from requests import HTTPError

from test_utils import *

class CommandsTests(unittest.TestCase):
    def setUp(self):
        try:
            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

#    @skip
    @print_entry_exit
    def test_cyrest_api(self):
        self.assertTrue(cyrest_api())

    @skip
    @print_entry_exit
    def test_cyrest_delete(self):
        # Initialization
        load_test_session()

        # Verify that deleting a view returns a non-JSON result
        self.assertEqual(len(get_network_views()), 1)
        res = cyrest_delete('networks/' + str(get_network_suid()) + '/views', require_json=False)
        self.assertEqual(res, '')

        # Verify that an HTTP error results in an exception
        self.assertRaises(HTTPError, get_network_views) # Behavior when there are no views
        self.assertRaises(requests.exceptions.ConnectionError, cyrest_delete, 'session', base_url='http://totallybogus')
        load_test_session()
        self.assertRaises(ValueError, cyrest_delete, 'networks/' + str(get_network_suid()) + '/views', require_json=True)

        # Verify that getting rid of the session returns a valid JSON result
        res = cyrest_delete('session')
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {'message': 'New session created.'})

    @skip
    @print_entry_exit
    def test_cyrest_get(self):

        # Verify that starting a garbage collection returns a non-JSON result
        res = cyrest_get('gc', require_json=False)
        self.assertIsInstance(res, str)
        self.assertEqual(res, '')

        # Verify that errors are caught
        self.assertRaises(requests.exceptions.ConnectionError, cyrest_get, 'gc', base_url='http://totallybogus')
        self.assertRaises(ValueError, cyrest_get, 'gc', require_json=True)

        # Verify that getting the CyREST version returns a valid JSON result
        res = cyrest_get('version')
        self.assertIsInstance(res, dict)
        self.assertIsInstance(res['apiVersion'], str)
        self.assertIsInstance(res['cytoscapeVersion'], str)

    @skip
    @print_entry_exit
    def test_cyrest_post(self):
        # Initialization
        load_test_session()

        # We would test for a POST that doesn't return JSON, but CyREST doesn't have any

        # Verify that adding a view returns a valid JSON result
        res = cyrest_delete('networks/' + str(get_network_suid()) + '/views', require_json=False) # Delete the existing view first
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
        self.assertRaises(requests.exceptions.ConnectionError, cyrest_post, 'commands/command/echo', body={'message': 'Hi there'}, base_url='http://totallybogus')

#    @skip
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
        self.assertRaises(requests.exceptions.ConnectionError, cyrest_post, 'networks/views/currentNetworkView', body={'networkViewSUID': view}, base_url='http://totallybogus')

#    @skip
    @print_entry_exit
    def test_commands_api(self):
        self.assertTrue(commands_api())

    @skip
    @print_entry_exit
    def test_command_get(self):
        x,y = commands._command_2_get_query('layout force-directed')
        print((x, y))
        x,y = commands._command_2_get_query('layout force-directed defaultNodeMass=1')
        print((x, y))
        x,y = commands._command_2_get_query('layout force-directed defaultNodeMass=1 file="C:\\file name"')
        print((x, y))
        x = command_sleep(5)
        print(x)
        x = command_quit()
        print(x)
        x = command_pause('hi there')
        print(x)
        x = command_open_dialog()
        print(x)
        x = command_echo('Hi there')
        print(x)
        x = commands_help('apps')
        print(x)
        x = commands_get('command sleep duration=5')
        print(x)
        x = commands_get('')
        print(x)
        x = commands_get('view')
        print(x)
        x = commands_get('apps list available')
        print(x)
        x = commands_get('apps status app="clusterMaker2"')
        print(x)
        x = commands_get('session open file="c:/file name"')
        print(x)


if __name__ == '__main__':
    unittest.main()