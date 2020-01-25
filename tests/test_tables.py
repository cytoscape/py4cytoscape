# -*- coding: utf-8 -*-

import unittest
import pandas as df
from PyCy3 import *
from PyCy3.decorators import *

class TablesTests(unittest.TestCase):

    def setUp(self):
        input('Close all Cytoscape networks')

    def tearDown(self):
        pass

    @skip
    @print_entry_exit
    def test_get_table_column_types(self):
        # Initialization
        input('Load galFiltered.sif')

        res = get_table_column_types()
        print(res)

    @skip
    @print_entry_exit
    def test_get_table_columns(self):
        # Initialization
        input('Load galFiltered.sif')

        res = get_table_columns()
        print(res)

    @skip
    @print_entry_exit
    def test_get_table_column_names(self):
        # Initialization
        input('Load galFiltered.sif')

        res = get_table_column_names()
        print(res)

    @print_entry_exit
    def test_load_table_data(self):
        # Initialization
        input('Load galFiltered.sif')

        data = df.DataFrame(data={'id':['New1','New2','New3'], 'newcol':[1,2,3]})
        res = load_table_data(data, data_key_column='id', table='node', table_key_column='name')
        print(res)

        data = df.DataFrame(data={'id':['YDL194W','YDR277C','YBR043C'], 'newcol':[1,2,3]})
        res = load_table_data(data, data_key_column='id', table='node', table_key_column='name')
        print(res)

