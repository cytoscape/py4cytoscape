# -*- coding: utf-8 -*-

""" Test functions in style_mappings.py.
"""

import unittest
import pandas as df
import igraph as ig

from requests import RequestException

from test_utils import *

class MyTestCase(unittest.TestCase):
    def setUp(self):
        try:
            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    @print_entry_exit
    def test_ui(self):
        pass

    def discrete_node_map_gen(self, table_column, map_param_name, gen_function, network=None, base_url=DEFAULT_BASE_URL):
        # Return a dict containing {'table_column': xx, 'table_column_values': [...], map_param_name: [...], 'mapping_type': 'c'}.
        # Caller should expect to use dict as a parameter to a style setter such as set_node_border_width_mapping().
        # For example: set_node_border_color_mapping(**discrete_node_map_gen(table_column='disease type', map_param_name='colors', gen_random_colors, network=network, base_url=base_url))
        pass


if __name__ == '__main__':
    unittest.main()