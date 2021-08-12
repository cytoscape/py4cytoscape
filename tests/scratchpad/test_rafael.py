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
        import pandas as pd
        import py4cytoscape as p4c

        project_name = 'barry'
        nodes = pd.read_csv(project_name + '_nodes.csv')
        edges = pd.read_csv(project_name + '_edges.csv')
        print(nodes)
        print(edges)

        nodes['id'] = nodes.id.astype(str)
        nodes['font'] = nodes['size'].map(lambda x: x / 3)  # adding font sizes -> scale factor here
        nodes.at[len(nodes['id'].tolist()) - 1, 'name'] = 'root'  # change name of root for clearness

        # must be strings for cytoscape to read them in
        edges['source'] = edges['source'].astype(str)
        edges['target'] = edges['target'].astype(str)

        p4c.create_network_from_data_frames(nodes, edges, title="lbd_test", collection="tests")
        p4c.toggle_graphics_details()
        p4c.set_node_shape_default('ELLIPSE')  # default shape of ALL nodes - except root
        p4c.set_node_color_default('#00FF00')  # color should NOT appear
        p4c.set_node_size_mapping('id', nodes['id'].tolist(), nodes['size'].tolist(), mapping_type='d')
        p4c.set_node_font_size_mapping('id', nodes['id'].tolist(), nodes['font'].tolist(), mapping_type='d')
        p4c.set_edge_line_width_bypass(edges['name'].tolist(), edges['width'].tolist())
        p4c.set_edge_color_bypass(edges['name'].tolist(), edges['color'].tolist())
        p4c.set_node_shape_bypass(['root'], 'HEXAGON')  # root becomes hexagon
        p4c.set_node_color_bypass(['root'], '#FF0000')  # root becomes red



if __name__ == '__main__':
    unittest.main()