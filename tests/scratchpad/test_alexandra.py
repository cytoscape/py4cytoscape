# -*- coding: utf-8 -*-

""" Test functions in style_mappings.py.
"""

import unittest
import pandas as df
import time
import urllib.request
import uuid
import os
import sys

from requests import RequestException


from test_utils import *

class MyTestCase(unittest.TestCase):
    def setUp(self):
        try:
            # delete_all_networks()
            pass
        except:
            pass

    def tearDown(self):
        pass

    @print_entry_exit
    def test_ui(self):
        print('should go to tests')
        print(export_network('foo'))
        print('should set up tests directory')
        print(sandbox_set(None))
        print(export_network('foo'))
        try:
            print(export_network('c:\\foo.blob'))
        except:
            pass
        print('should go to sandbox mine')
        print(sandbox_set('mine'))
        print(export_network('foo'))
        try:
            print(export_network('c:\\foo.blob'))
        except:
            pass

        nodes = pd.read_csv('nodes_COAD.tsv', sep='\t')
        edges = pd.read_csv('edges_COAD.tsv', sep='\t')

        node_degree = pd.concat([edges['source'].value_counts(), edges['target'].value_counts()])
        node_degree.rename('degree', inplace=True)
        nodes = nodes.set_index('id').join(node_degree).reset_index()

        create_network_from_data_frames(nodes, edges, title="my project", collection="DataFrame Example")

        set_node_size_mapping('id', nodes['id'].tolist(), nodes['degree'].tolist(), mapping_type='d')

        notebook_export_show_image()


if __name__ == '__main__':
    unittest.main()