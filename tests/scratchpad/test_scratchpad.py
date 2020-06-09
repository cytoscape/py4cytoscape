# -*- coding: utf-8 -*-

""" Test functions in style_mappings.py.
"""

import unittest
import pandas as df
import time
import urllib.request

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


    # def test_something(self):
    #     # 1.2
    #     cytoscape_ping()
    #     print(cytoscape_version_info())
    #
    #     # 2.1
    #     url = 'https://nrnb.org/data/BasicDataVizDemo.cys'
    #     urllib.request.urlretrieve(url, './BasicDataVizDemo.cys')
    #
    #     open_session(file_location='./BasicDataVizDemo.cys')
    #
    #     export_image("./BasicDataVizDemo.png")
    #
    #     # 2.2
    #     select_nodes(["YDL194W", "YLR345W"], by_col="name")
    #
    #     # 2.2.1
    #     gal80Rexp_score_table = get_table_columns('node', 'gal80Rexp')
    #     # https://thispointer.com/pandas-dataframe-get-minimum-values-in-rows-or-columns-their-index-position/
    #     bad_gal80Rexp_min = gal80Rexp_score_table.min()
    #     gal80Rexp_min = gal80Rexp_score_table['gal80Rexp'].min()
    #     bad_gal80Rexp_max = gal80Rexp_score_table.max()
    #     gal80Rexp_max = gal80Rexp_score_table['gal80Rexp'].max()
    #     gal80Rexp_center = gal80Rexp_min + (gal80Rexp_max - gal80Rexp_min) / 2
    #
    #     set_node_color_mapping('gal80Rexp', [gal80Rexp_min, gal80Rexp_center, gal80Rexp_max],
    #                         ['#0000FF', '#FFFFFF', '#FF0000'])
    #
    #     # 2.2.2
    #     set_node_color_default('#666666')
    #
    #     # 2.2.3
    #     gal80Rsig_score_table = get_table_columns('node', 'gal80Rsig')
    #     gal80Rsig_min = gal80Rsig_score_table['gal80Rsig'].min()
    #     gal80Rsig_max = gal80Rsig_score_table['gal80Rsig'].max()
    #
    #     set_node_border_width_mapping('gal80Rsig', [gal80Rsig_min, gal80Rsig_max], [10, 30])
    #
    #     # 2.3
    #     layout_network("degree-circle")
    #     export_image("./degree-circle.png")
    #
    #     layout_network("force-directed")
    #     export_image("./force-directed.png")
    #
    #     # 2.4
    #     create_column_filter('myFilter', 'gal80Rexp', 2.00, "GREATER_THAN")
    #     export_image("./column-filter.png")
    #
    #     # 2.4.1
    #     select_first_neighbors()
    #     export_image("./first-neighbors.png")
    #
    #     # 2.5
    #     save_session('./basic-data-visualization.cys')
    #     export_image('./basic-data-visualization', 'PDF')
    #     export_image('./basic-data-visualization', 'PNG')
    #     export_image('./basic-data-visualization', 'JPEG')
    #     export_image('./basic-data-visualization', 'SVG')
    #     export_image('./basic-data-visualization', 'PS')
    #
    #     # Skip writing to NDEx because I don't have an NDEx account for this demo
    #
    #     export_network('./basic-data-visualization', 'CX')
    #     export_network('./basic-data-visualization', 'cyjs')
    #     export_network('./basic-data-visualization', 'graphML')
    #     export_network('./basic-data-visualization', 'xGMML')
    #     export_network('./basic-data-visualization', 'SIF')

    @unittest.skipIf(skip_for_ui(), 'Avoiding test that requires user response')
    @print_entry_exit
    def test_ui(self):
        print("into test_ui")

if __name__ == '__main__':
    unittest.main()
