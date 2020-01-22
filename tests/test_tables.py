# -*- coding: utf-8 -*-

import unittest
from PyCy3 import *
from PyCy3.decorators import *

class TablesTests(unittest.TestCase):

    def setUp(self):
        input('Close all Cytoscape networks')

    def tearDown(self):
        pass

    @print_entry_exit
    def test_get_table_column_types(self):
        # Initialization
        input('Load galFiltered.sif')

        res = get_table_column_types()
        print(res)

    @print_entry_exit
    def test_get_table_columns(self):
        # Initialization
        input('Load galFiltered.sif')

        res = get_table_columns()
        print(res)

