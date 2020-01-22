# -*- coding: utf-8 -*-

import unittest
from PyCy3 import *
from PyCy3.decorators import *


class NetworkSelectionTests(unittest.TestCase):

    def setUp(self):
        input('Close all Cytoscape networks')

    def tearDown(self):
        pass

    @print_entry_exit
    def test_get_selected_node_count(self):
        # Initialization
        input('Load galFiltered.sif')

        res = get_selected_node_count()
        print(res)

    @print_entry_exit
    def test_get_selected_nodes(self):
        # Initialization
        input('Load galFiltered.sif')

        res = get_selected_nodes(False)
        print(res)

        res = get_selected_nodes(True)
        print(res)