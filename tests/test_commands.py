# -*- coding: utf-8 -*-

import unittest
from requests import HTTPError

from test_utils import *

class CommandsTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @skip
    @print_entry_exit
    def test_cyrest_api(self):
        self.assertTrue(cyrest_api())

#    @skip
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