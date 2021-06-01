# -*- coding: utf-8 -*-

""" Test functions in style_mappings.py.
"""

"""License:
    Copyright 2020 The Cytoscape Consortium

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
import pandas as df
import time

from requests import RequestException

from test_utils import *


class StyleAutoMappingsTests(unittest.TestCase):
    def setUp(self):
        try:
            close_session(False)
        #            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    _GAL_FILTERED_STYLE = 'galFiltered Style'

    @print_entry_exit
    def test_gen_color_map(self):

        def verify_discrete():
            # Initialization -- get a clean session
            load_test_session()

            # Verify that when the column doesn't exist, it's treated as a column with no values
            f = palette_color_brewer_q_Accent()
            no_map = gen_node_color_map('bogus column', palette_color_brewer_q_Accent(), mapping_type='d')
            self.assertDictEqual(no_map, {'table_column': 'bogus column', 'table_column_values': [], 'colors': [], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
            no_map = gen_edge_color_map('bogus column', palette_color_brewer_q_Accent(), mapping_type='d')
            self.assertDictEqual(no_map, {'table_column': 'bogus column', 'table_column_values': [], 'colors': [], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Create a column with one data value, and verify that the correct value and mapping are generated
            one_data = df.DataFrame(data={'id':['YBR043C'], 'newcol':[3]})
            load_table_data(one_data, data_key_column='id')
            one_map = gen_node_color_map('newcol', palette_color_brewer_q_Accent(), mapping_type='d')
            self.assertDictEqual(one_map, {'table_column': 'newcol', 'table_column_values': ['3'], 'colors': ['#7FC97F'], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that when no palette is provided, the right palette is chosen
            palette_map = gen_node_color_map('newcol', mapping_type='d')
            self.assertDictEqual(palette_map, {'table_column': 'newcol', 'table_column_values': ['3'], 'colors': ['#66C2A5'], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that when optional parameters are supplied, they are included in the generated dictionary
            one_map = gen_node_color_map('newcol', palette_color_brewer_q_Accent(), mapping_type='d', default_color='#00FF00', style_name='galFiltered Style', network='galFiltered.sif')
            self.assertDictEqual(one_map, {'table_column': 'newcol', 'table_column_values': ['3'], 'colors': ['#7FC97F'], 'mapping_type': 'd', 'default_color': '#00FF00', 'style_name': 'galFiltered Style', 'network': 'galFiltered.sif', 'base_url': 'http://127.0.0.1:1234/v1'})

            # Add a data value so now there are two (but still under minimum cy_palette threshold), and verify the correct values and mappings
            one_data = df.DataFrame(data={'id':['YDL194W'], 'newcol':[4]})
            load_table_data(one_data, data_key_column='id')
            two_map = gen_node_color_map('newcol', palette_color_brewer_q_Accent(), mapping_type='d')
            self.assertDictEqual(two_map, {'table_column': 'newcol', 'table_column_values': ['4', '3'], 'colors': ['#7FC97F', '#BEAED4'], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Add a data value so now there are three (and now at minimum cy_palette threshold), and verify the correct values and mappings
            one_data = df.DataFrame(data={'id':['YDR277C'], 'newcol':[5]})
            load_table_data(one_data, data_key_column='id')
            three_map = gen_node_color_map('newcol', palette_color_brewer_q_Accent(), mapping_type='d')
            self.assertDictEqual(three_map, {'table_column': 'newcol', 'table_column_values': ['5', '4', '3'], 'colors': ['#7FC97F', '#BEAED4', '#FDC086'], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Add 5 data values so now there 8 (which is at maximum cy_palette threshold), and verify the correct values and mappings
            five_data = df.DataFrame(data={'id':['YFR014C', 'YGR136W', 'YDL023C', 'YBR170C', 'YGR074W'], 'newcol':[6, 7, 8, 9, 10]})
            load_table_data(five_data, data_key_column='id')
            eight_map = gen_node_color_map('newcol', palette_color_brewer_q_Accent(), mapping_type='d')
            self.assertDictEqual(eight_map, {'table_column': 'newcol', 'table_column_values': ['10', '9', '8', '7', '6', '5', '4', '3'], 'colors': ['#7FC97F', '#BEAED4', '#FDC086', '#FFFF99', '#386CB0', '#F0027F', '#BF5B17', '#666666'], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Add 5 more data values so now there 8 (with 5 duplicates, which is still at maximum cy_palette threshold), and verify that values and mappings don't change
            five_data = df.DataFrame(data={'id':['YER079W', 'YDL215C', 'YIL045W', 'YPR041W', 'YOR120W'], 'newcol':[6, 7, 8, 9, 10]})
            load_table_data(five_data, data_key_column='id')
            eight_map = gen_node_color_map('newcol', palette_color_brewer_q_Accent(), mapping_type='d')
            self.assertDictEqual(eight_map, {'table_column': 'newcol', 'table_column_values': ['10', '9', '8', '7', '6', '5', '4', '3'], 'colors': ['#7FC97F', '#BEAED4', '#FDC086', '#FFFF99', '#386CB0', '#F0027F', '#BF5B17', '#666666'], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Add 1 more data values so now there 19 (with 5 duplicates, which forces cy_palette interpolation), and verify that values and mappings are right
            one_data = df.DataFrame(data={'id':['YBR118W'], 'newcol':[50]})
            load_table_data(one_data, data_key_column='id')
            nine_map = gen_node_color_map('newcol', palette_color_brewer_q_Accent(), mapping_type='d')
            self.assertDictEqual(nine_map, {'table_column': 'newcol', 'table_column_values': ['10', '9', '8', '7', '6', '50', '5', '4', '3'], 'colors': ['#7FC97F', '#B6B1C9', '#EDBC9A', '#FEE792', '#9CB6A5', '#7D449E', '#E41865', '#B45C21', '#666666'], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Add 5 more data values so now there 14 (with 5 duplicates, which forces cy_palette interpolation), and verify that values and mappings are right
            five_data = df.DataFrame(data={'id':['YKR026C', 'YGL122C', 'YGR218W', 'YGL097W', 'YOR204W'], 'newcol':[100, 101, 102, 103, 104]})
            load_table_data(five_data, data_key_column='id')
            fourteen_map = gen_node_color_map('newcol', palette_color_brewer_q_Accent(), mapping_type='d')
            self.assertDictEqual(fourteen_map, {'table_column': 'newcol', 'table_column_values': ['10', '9', '8', '7', '6', '50', '104', '103', '102', '101', '100', '5', '4', '3'], 'colors': ['#7FC97F', '#A1BAAD', '#C3AFCE', '#E5B9A4', '#FDCA89', '#FEEC93', '#D1DD9E', '#668EAB', '#714BA1', '#D41287', '#DD2457', '#C3541F', '#96603B', '#666666'], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

        def verify_palettes():
            # Initialization -- get a clean session back
            load_test_session()

            # Create 8 values -- all qualitative (discrete) Brewer palettes support 8 values --  and verify that values and mappings are right
            eight_data = df.DataFrame(data={'id':['YDL194W', 'YDR277C', 'YBR043C', 'YKR026C', 'YGL122C', 'YGR218W', 'YGL097W', 'YOR204W'], 'newcol':[1, 2, 3, 4, 5, 6, 7, 8]})
            load_table_data(eight_data, data_key_column='id')

            # Verify that Pastel2 palette is available
            eight_map = gen_node_color_map('newcol', palette_color_brewer_q_Pastel2(), mapping_type='d')
            self.assertDictEqual(eight_map, {'table_column': 'newcol', 'table_column_values': ['8', '7', '6', '5', '4', '3', '2', '1'], 'colors': ['#B3E2CD', '#FDCDAC', '#CBD5E8', '#F4CAE4', '#E6F5C9', '#FFF2AE', '#F1E2CC', '#CCCCCC'], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that Pastel1 palette is available
            eight_map = gen_node_color_map('newcol', palette_color_brewer_q_Pastel1(), mapping_type='d')
            self.assertDictEqual(eight_map, {'table_column': 'newcol', 'table_column_values': ['8', '7', '6', '5', '4', '3', '2', '1'], 'colors': ['#FBB4AE', '#B3CDE3', '#CCEBC5', '#DECBE4', '#FED9A6', '#FFFFCC', '#E5D8BD', '#FDDAEC'], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that Dark2 palette is available
            eight_map = gen_node_color_map('newcol', palette_color_brewer_q_Dark2(), mapping_type='d')
            self.assertDictEqual(eight_map, {'table_column': 'newcol', 'table_column_values': ['8', '7', '6', '5', '4', '3', '2', '1'], 'colors': ['#1B9E77', '#D95F02', '#7570B3', '#E7298A', '#66A61E', '#E6AB02', '#A6761D', '#666666'], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that Accent palette is available
            eight_map = gen_node_color_map('newcol', palette_color_brewer_q_Accent(), mapping_type='d')
            self.assertDictEqual(eight_map, {'table_column': 'newcol', 'table_column_values': ['8', '7', '6', '5', '4', '3', '2', '1'], 'colors': ['#7FC97F', '#BEAED4', '#FDC086', '#FFFF99', '#386CB0', '#F0027F', '#BF5B17', '#666666'], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that Paired palette is available
            eight_map = gen_node_color_map('newcol', palette_color_brewer_q_Paired(), mapping_type='d')
            self.assertDictEqual(eight_map, {'table_column': 'newcol', 'table_column_values': ['8', '7', '6', '5', '4', '3', '2', '1'], 'colors': ['#A6CEE3', '#1F78B4', '#B2DF8A', '#33A02C', '#FB9A99', '#E31A1C', '#FDBF6F', '#FF7F00'], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that Set1 palette is available
            eight_map = gen_node_color_map('newcol', palette_color_brewer_q_Set1(), mapping_type='d')
            self.assertDictEqual(eight_map, {'table_column': 'newcol', 'table_column_values': ['8', '7', '6', '5', '4', '3', '2', '1'], 'colors': ['#E41A1C', '#377EB8', '#4DAF4A', '#984EA3', '#FF7F00', '#FFFF33', '#A65628', '#F781BF'], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that Set2 palette is available
            eight_map = gen_node_color_map('newcol', palette_color_brewer_q_Set2(), mapping_type='d')
            self.assertDictEqual(eight_map, {'table_column': 'newcol', 'table_column_values': ['8', '7', '6', '5', '4', '3', '2', '1'], 'colors': ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854', '#FFD92F', '#E5C494', '#B3B3B3'], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that Set3 palette is available
            eight_map = gen_node_color_map('newcol', palette_color_brewer_q_Set3(), mapping_type='d')
            self.assertDictEqual(eight_map, {'table_column': 'newcol', 'table_column_values': ['8', '7', '6', '5', '4', '3', '2', '1'], 'colors': ['#8DD3C7', '#FFFFB3', '#BEBADA', '#FB8072', '#80B1D3', '#FDB462', '#B3DE69', '#FCCDE5'], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that Blues palette is available and 1-tailed mapping is calculated
            continuous_map = gen_node_color_map('newcol', palette_color_brewer_s_Blues())
            self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'colors': ['#DEEBF7', '#9ECAE1', '#3182BD'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that BuGn palette is available and 1-tailed mapping is calculated
            continuous_map = gen_node_color_map('newcol', palette_color_brewer_s_BuGn())
            self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'colors': ['#E5F5F9', '#99D8C9', '#2CA25F'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that BuPu palette is available and 1-tailed mapping is calculated
            continuous_map = gen_node_color_map('newcol', palette_color_brewer_s_BuPu())
            self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'colors': ['#E0ECF4', '#9EBCDA', '#8856A7'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that GnBu palette is available and 1-tailed mapping is calculated
            continuous_map = gen_node_color_map('newcol', palette_color_brewer_s_GnBu())
            self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'colors': ['#E0F3DB', '#A8DDB5', '#43A2CA'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that Greens palette is available and 1-tailed mapping is calculated
            continuous_map = gen_node_color_map('newcol', palette_color_brewer_s_Greens())
            self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'colors': ['#E5F5E0', '#A1D99B', '#31A354'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that Greys palette is available and 1-tailed mapping is calculated
            continuous_map = gen_node_color_map('newcol', palette_color_brewer_s_Greys())
            self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'colors': ['#F0F0F0', '#BDBDBD', '#636363'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that Oranges palette is available and 1-tailed mapping is calculated
            continuous_map = gen_node_color_map('newcol', palette_color_brewer_s_Oranges())
            self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'colors': ['#FEE6CE', '#FDAE6B', '#E6550D'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that OrRd palette is available and 1-tailed mapping is calculated
            continuous_map = gen_node_color_map('newcol', palette_color_brewer_s_OrRd())
            self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'colors': ['#FEE8C8', '#FDBB84', '#E34A33'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that PuBu palette is available and 1-tailed mapping is calculated
            continuous_map = gen_node_color_map('newcol', palette_color_brewer_s_PuBu())
            self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'colors': ['#ECE7F2', '#A6BDDB', '#2B8CBE'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that PuBuGn palette is available and 1-tailed mapping is calculated
            continuous_map = gen_node_color_map('newcol', palette_color_brewer_s_PuBuGn())
            self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'colors': ['#ECE2F0', '#A6BDDB', '#1C9099'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that RdPu palette is available and 1-tailed mapping is calculated
            continuous_map = gen_node_color_map('newcol', palette_color_brewer_s_RdPu())
            self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'colors': ['#FDE0DD', '#FA9FB5', '#C51B8A'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that PuRd palette is available and 1-tailed mapping is calculated
            continuous_map = gen_node_color_map('newcol', palette_color_brewer_s_PuRd())
            self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'colors': ['#E7E1EF', '#C994C7', '#DD1C77'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that Purples palette is available and 1-tailed mapping is calculated
            continuous_map = gen_node_color_map('newcol', palette_color_brewer_s_Purples())
            self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'colors': ['#EFEDF5', '#BCBDDC', '#756BB1'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that Reds palette is available and 1-tailed mapping is calculated
            continuous_map = gen_node_color_map('newcol', palette_color_brewer_s_Reds())
            self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'colors': ['#FEE0D2', '#FC9272', '#DE2D26'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that YlGn palette is available and 1-tailed mapping is calculated
            continuous_map = gen_node_color_map('newcol', palette_color_brewer_s_YlGn())
            self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'colors': ['#F7FCB9', '#ADDD8E', '#31A354'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that YlGnBu palette is available and 1-tailed mapping is calculated
            continuous_map = gen_node_color_map('newcol', palette_color_brewer_s_YlGnBu())
            self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'colors': ['#EDF8B1', '#7FCDBB', '#2C7FB8'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that YlOrBr palette is available and 1-tailed mapping is calculated
            continuous_map = gen_node_color_map('newcol', palette_color_brewer_s_YlOrBr())
            self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'colors': ['#FFF7BC', '#FEC44F', '#D95F0E'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that YlOrRd palette is available and 1-tailed mapping is calculated
            continuous_map = gen_node_color_map('newcol', palette_color_brewer_s_YlOrRd())
            self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'colors': ['#FFEDA0', '#FEB24C', '#F03B20'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that random palette is available
            eight_map = gen_node_color_map('newcol', palette_color_random(), mapping_type='d')
            self.assertListEqual(eight_map['table_column_values'], ['8', '7', '6', '5', '4', '3', '2', '1'])
            self.assertEqual(len(eight_map['colors']), 8)

        def verify_setters_and_continuous():
            # Initialize -- work with clean session
            load_test_session()

            # Create 8 values -- all qualitative (discrete) Brewer palettes support 8 values --  and verify that values and mappings are right
            eight_data = df.DataFrame(
                data={'id': ['YDL194W', 'YDR277C', 'YBR043C', 'YKR026C', 'YGL122C', 'YGR218W', 'YGL097W', 'YOR204W'],
                      'newcol': [1, 2, 3, 4, 5, 6, 7, 8]})
            load_table_data(eight_data, data_key_column='id')

            # Verify that a continuous mapping can't be done when the column is non-numeric
            self.assertRaises(CyError, gen_node_color_map, 'name', palette_color_brewer_s_Blues(), style_name='galFiltered Style')

            # Verify that edge mapping generation for discrete and continuous 1-tailed edges work as expected
            edge_map = gen_edge_color_map('interaction', palette_color_brewer_q_Accent(), mapping_type='d')
            self.assertDictEqual(edge_map, {'table_column': 'interaction', 'table_column_values': ['pp', 'pd'], 'colors': ['#7FC97F', '#BEAED4'], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
            edge_map = gen_edge_color_map('interaction', mapping_type='d')
            self.assertDictEqual(edge_map, {'table_column': 'interaction', 'table_column_values': ['pp', 'pd'], 'colors': ['#66C2A5', '#FC8D62'], 'mapping_type': 'd', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
            edge_map = gen_edge_color_map('EdgeBetweenness')
            self.assertDictEqual(edge_map, {'table_column': 'EdgeBetweenness', 'table_column_values': [2.0, 9591.11110001, 19180.22220002], 'colors': ['#E0F3DB', '#A8DDB5', '#43A2CA'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
            edge_map = gen_edge_color_map('EdgeBetweenness', palette_color_brewer_s_Blues())
            self.assertDictEqual(edge_map, {'table_column': 'EdgeBetweenness', 'table_column_values': [2.0, 9591.11110001, 19180.22220002], 'colors': ['#DEEBF7', '#9ECAE1', '#3182BD'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
            edge_map = gen_edge_color_map('EdgeBetweenness', (palette_color_brewer_s_Blues(), palette_color_brewer_d_BrBG()))
            self.assertDictEqual(edge_map, {'table_column': 'EdgeBetweenness', 'table_column_values': [2.0, 9591.11110001, 19180.22220002], 'colors': ['#DEEBF7', '#9ECAE1', '#3182BD'], 'mapping_type': 'c', 'default_color': None, 'style_name': None, 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})


            # Verify that setting border color works as expected for discrete and continuous
            set_node_border_color_mapping(**gen_node_color_map('newcol', palette_color_brewer_q_Accent(), mapping_type='d', style_name='galFiltered Style'))
            self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_BORDER_PAINT'), {'mappingType': 'discrete', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_BORDER_PAINT', 'map': [{'key': '1', 'value': '#666666'}, {'key': '2', 'value': '#BF5B17'}, {'key': '3', 'value': '#F0027F'}, {'key': '4', 'value': '#386CB0'}, {'key': '5', 'value': '#FFFF99'}, {'key': '6', 'value': '#FDC086'}, {'key': '7', 'value': '#BEAED4'}, {'key': '8', 'value': '#7FC97F'}]})
            set_node_border_color_mapping(**gen_node_color_map('newcol', palette_color_brewer_s_Blues(), style_name='galFiltered Style'))
            self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_BORDER_PAINT'), {'mappingType': 'continuous', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_BORDER_PAINT', 'points': [{'value': 1.0, 'lesser': '#DEEBF7', 'equal': '#DEEBF7', 'greater': '#DEEBF7'}, {'value': 4.5, 'lesser': '#9ECAE1', 'equal': '#9ECAE1', 'greater': '#9ECAE1'}, {'value': 8.0, 'lesser': '#3182BD', 'equal': '#3182BD', 'greater': '#3182BD'}]})

            # Verify that node border color works as expected for discrete and continuous
            set_node_color_mapping(**gen_node_color_map('newcol', palette_color_brewer_q_Accent(), mapping_type='d', style_name='galFiltered Style'))
            self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_FILL_COLOR'), {'mappingType': 'discrete', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_FILL_COLOR', 'map': [{'key': '1', 'value': '#666666'}, {'key': '2', 'value': '#BF5B17'}, {'key': '3', 'value': '#F0027F'}, {'key': '4', 'value': '#386CB0'}, {'key': '5', 'value': '#FFFF99'}, {'key': '6', 'value': '#FDC086'}, {'key': '7', 'value': '#BEAED4'}, {'key': '8', 'value': '#7FC97F'}]})
            set_node_color_mapping(**gen_node_color_map('newcol', palette_color_brewer_s_Blues(), style_name='galFiltered Style'))
            self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_FILL_COLOR'), {'mappingType': 'continuous', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_FILL_COLOR', 'points': [{'value': 1.0, 'lesser': '#DEEBF7', 'equal': '#DEEBF7', 'greater': '#DEEBF7'}, {'value': 4.5, 'lesser': '#9ECAE1', 'equal': '#9ECAE1', 'greater': '#9ECAE1'}, {'value': 8.0, 'lesser': '#3182BD', 'equal': '#3182BD', 'greater': '#3182BD'}]})

            # Verify that label border color works as expected for discrete and continuous
            set_node_label_color_mapping(**gen_node_color_map('newcol', palette_color_brewer_q_Accent(), mapping_type='d', style_name='galFiltered Style'))
            self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_LABEL_COLOR'), {'mappingType': 'discrete', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_LABEL_COLOR', 'map': [{'key': '1', 'value': '#666666'}, {'key': '2', 'value': '#BF5B17'}, {'key': '3', 'value': '#F0027F'}, {'key': '4', 'value': '#386CB0'}, {'key': '5', 'value': '#FFFF99'}, {'key': '6', 'value': '#FDC086'}, {'key': '7', 'value': '#BEAED4'}, {'key': '8', 'value': '#7FC97F'}]})
            set_node_label_color_mapping(**gen_node_color_map('newcol', palette_color_brewer_s_Blues(), style_name='galFiltered Style'))
            self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_LABEL_COLOR'), {'mappingType': 'continuous', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_LABEL_COLOR', 'points': [{'value': 1.0, 'lesser': '#DEEBF7', 'equal': '#DEEBF7', 'greater': '#DEEBF7'}, {'value': 4.5, 'lesser': '#9ECAE1', 'equal': '#9ECAE1', 'greater': '#9ECAE1'}, {'value': 8.0, 'lesser': '#3182BD', 'equal': '#3182BD', 'greater': '#3182BD'}]})

            # Verify that setting edge color works as expected for discrete and continuous
            set_edge_color_mapping(**gen_edge_color_map('interaction', palette_color_brewer_q_Accent(), mapping_type='d', style_name='galFiltered Style'))
            self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_UNSELECTED_PAINT'), {'mappingType': 'discrete', 'mappingColumn': 'interaction', 'mappingColumnType': 'String', 'visualProperty': 'EDGE_UNSELECTED_PAINT', 'map': [{'key': 'pp', 'value': '#7FC97F'}, {'key': 'pd', 'value': '#BEAED4'}]})
            set_edge_color_mapping(**gen_edge_color_map('EdgeBetweenness', palette_color_brewer_s_Blues(), style_name='galFiltered Style'))
            self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_UNSELECTED_PAINT'), {'mappingType': 'continuous', 'mappingColumn': 'EdgeBetweenness', 'mappingColumnType': 'Double', 'visualProperty': 'EDGE_UNSELECTED_PAINT', 'points': [{'value': 2.0, 'lesser': '#DEEBF7', 'equal': '#DEEBF7', 'greater': '#DEEBF7'}, {'value': 9591.11110001, 'lesser': '#9ECAE1', 'equal': '#9ECAE1', 'greater': '#9ECAE1'}, {'value': 19180.22220002, 'lesser': '#3182BD', 'equal': '#3182BD', 'greater': '#3182BD'}]})

            # Verify that setting edge label color works as expected for discrete and continuous
            set_edge_label_color_mapping(**gen_edge_color_map('interaction', palette_color_brewer_q_Accent(), mapping_type='d', style_name='galFiltered Style'))
            self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_LABEL_COLOR'), {'mappingType': 'discrete', 'mappingColumn': 'interaction', 'mappingColumnType': 'String', 'visualProperty': 'EDGE_LABEL_COLOR', 'map': [{'key': 'pp', 'value': '#7FC97F'}, {'key': 'pd', 'value': '#BEAED4'}]})
            set_edge_label_color_mapping(**gen_edge_color_map('EdgeBetweenness', palette_color_brewer_s_Blues(), style_name='galFiltered Style'))
            self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_LABEL_COLOR'), {'mappingType': 'continuous', 'mappingColumn': 'EdgeBetweenness', 'mappingColumnType': 'Double', 'visualProperty': 'EDGE_LABEL_COLOR', 'points': [{'value': 2.0, 'lesser': '#DEEBF7', 'equal': '#DEEBF7', 'greater': '#DEEBF7'}, {'value': 9591.11110001, 'lesser': '#9ECAE1', 'equal': '#9ECAE1', 'greater': '#9ECAE1'}, {'value': 19180.22220002, 'lesser': '#3182BD', 'equal': '#3182BD', 'greater': '#3182BD'}]})

            # Verify that setting target arrow color works as expected for discrete and continuous
            set_edge_target_arrow_color_mapping(**gen_edge_color_map('interaction', palette_color_brewer_q_Accent(), mapping_type='d', style_name='galFiltered Style'))
            self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_TARGET_ARROW_UNSELECTED_PAINT'), {'mappingType': 'discrete', 'mappingColumn': 'interaction', 'mappingColumnType': 'String', 'visualProperty': 'EDGE_TARGET_ARROW_UNSELECTED_PAINT', 'map': [{'key': 'pp', 'value': '#7FC97F'}, {'key': 'pd', 'value': '#BEAED4'}]})
            set_edge_target_arrow_color_mapping(**gen_edge_color_map('EdgeBetweenness', palette_color_brewer_s_Blues(), style_name='galFiltered Style'))
            self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_TARGET_ARROW_UNSELECTED_PAINT'), {'mappingType': 'continuous', 'mappingColumn': 'EdgeBetweenness', 'mappingColumnType': 'Double', 'visualProperty': 'EDGE_TARGET_ARROW_UNSELECTED_PAINT', 'points': [{'value': 2.0, 'lesser': '#DEEBF7', 'equal': '#DEEBF7', 'greater': '#DEEBF7'}, {'value': 9591.11110001, 'lesser': '#9ECAE1', 'equal': '#9ECAE1', 'greater': '#9ECAE1'}, {'value': 19180.22220002, 'lesser': '#3182BD', 'equal': '#3182BD', 'greater': '#3182BD'}]})

            # Verify that setting source arrow color works as expected for discrete and continuous
            set_edge_source_arrow_color_mapping(**gen_edge_color_map('interaction', palette_color_brewer_q_Accent(), mapping_type='d', style_name='galFiltered Style'))
            self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_SOURCE_ARROW_UNSELECTED_PAINT'), {'mappingType': 'discrete', 'mappingColumn': 'interaction', 'mappingColumnType': 'String', 'visualProperty': 'EDGE_SOURCE_ARROW_UNSELECTED_PAINT', 'map': [{'key': 'pp', 'value': '#7FC97F'}, {'key': 'pd', 'value': '#BEAED4'}]})
            set_edge_source_arrow_color_mapping(**gen_edge_color_map('EdgeBetweenness', palette_color_brewer_s_Blues(), style_name='galFiltered Style'))
            self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_SOURCE_ARROW_UNSELECTED_PAINT'), {'mappingType': 'continuous', 'mappingColumn': 'EdgeBetweenness', 'mappingColumnType': 'Double', 'visualProperty': 'EDGE_SOURCE_ARROW_UNSELECTED_PAINT', 'points': [{'value': 2.0, 'lesser': '#DEEBF7', 'equal': '#DEEBF7', 'greater': '#DEEBF7'}, {'value': 9591.11110001, 'lesser': '#9ECAE1', 'equal': '#9ECAE1', 'greater': '#9ECAE1'}, {'value': 19180.22220002, 'lesser': '#3182BD', 'equal': '#3182BD', 'greater': '#3182BD'}]})

            # Verify that when no palette is given, the correct palette is chosen for one-tailed treatment
            palette_map = gen_node_color_map('newcol', style_name='galFiltered Style')
            self.assertDictEqual(palette_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'colors': ['#E0F3DB', '#A8DDB5', '#43A2CA'], 'mapping_type': 'c', 'default_color': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})


            # Add 0 value to see whether this changes palette used ... it should switch to two-tail treatment
            set_node_color_mapping(**gen_node_color_map('newcol', (palette_color_brewer_s_Blues(), palette_color_brewer_d_Spectral()), style_name='galFiltered Style'))
            self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_FILL_COLOR'), {'mappingType': 'continuous', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_FILL_COLOR', 'points': [{'value': 1.0, 'lesser': '#DEEBF7', 'equal': '#DEEBF7', 'greater': '#DEEBF7'}, {'value': 4.5, 'lesser': '#9ECAE1', 'equal': '#9ECAE1', 'greater': '#9ECAE1'}, {'value': 8.0, 'lesser': '#3182BD', 'equal': '#3182BD', 'greater': '#3182BD'}]})
            zero_data = df.DataFrame(data={'id':['YER056CA'], 'newcol':[0]})
            load_table_data(zero_data, data_key_column='id')
            set_node_color_mapping(**gen_node_color_map('newcol', (palette_color_brewer_s_Blues(), palette_color_brewer_d_Spectral()), style_name='galFiltered Style'))
            self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_FILL_COLOR'), {'mappingType': 'continuous', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_FILL_COLOR', 'points': [{'value': -8.0, 'lesser': '#FC8D59', 'equal': '#FC8D59', 'greater': '#FC8D59'}, {'value': 0.0, 'lesser': '#FFFFBF', 'equal': '#FFFFBF', 'greater': '#FFFFBF'}, {'value': 8.0, 'lesser': '#99D594', 'equal': '#99D594', 'greater': '#99D594'}]})

            # Verify that when no palette is given, the correct palette is chosen for two-tailed treatment
            palette_map = gen_node_color_map('newcol', style_name='galFiltered Style')
            self.assertDictEqual(palette_map, {'table_column': 'newcol', 'table_column_values': [-8, 0, 8], 'colors': ['#FC8D59', '#FFFFBF', '#91BFDB'], 'mapping_type': 'c', 'default_color': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

            # Verify that when divergent palette is only palette given, we get valid result if data is two-tailed
            set_node_color_mapping(**gen_node_color_map('newcol', palette_color_brewer_d_Spectral(), style_name='galFiltered Style'))
            self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_FILL_COLOR'), {'mappingType': 'continuous', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_FILL_COLOR', 'points': [{'value': -8.0, 'lesser': '#FC8D59', 'equal': '#FC8D59', 'greater': '#FC8D59'}, {'value': 0.0, 'lesser': '#FFFFBF', 'equal': '#FFFFBF', 'greater': '#FFFFBF'}, {'value': 8.0, 'lesser': '#99D594', 'equal': '#99D594', 'greater': '#99D594'}]})

            # Verify that when sequential palette is used on two-tailed data, it's allowed, but warning is given
            set_node_color_mapping(**gen_node_color_map('newcol', palette_color_brewer_s_Blues(), style_name='galFiltered Style'))
            self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_FILL_COLOR'), {'mappingType': 'continuous', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_FILL_COLOR', 'points': [{'value': -8.0, 'lesser': '#DEEBF7', 'equal': '#DEEBF7', 'greater': '#DEEBF7'}, {'value': 0.0, 'lesser': '#9ECAE1', 'equal': '#9ECAE1', 'greater': '#9ECAE1'}, {'value': 8.0, 'lesser': '#3182BD', 'equal': '#3182BD', 'greater': '#3182BD'}]})

        # Run all of the color tests
        verify_discrete()
        verify_palettes()
        verify_setters_and_continuous()

        # Verify that when the network doesn't exist, an appropriate error is returned
        self.assertRaises(CyError, gen_node_color_map, 'newcol', palette_color_brewer_q_Accent(), mapping_type='d', network='bogus network')
        self.assertRaises(CyError, gen_edge_color_map, 'interaction', palette_color_brewer_q_Accent(), mapping_type='d', network='bogus network')
        self.assertRaises(CyError, gen_node_color_map, 'newcol', palette_color_brewer_s_Blues(), network='bogus network')
        self.assertRaises(CyError, gen_edge_color_map, 'interaction', palette_color_brewer_s_Blues(), network='bogus network')


    @print_entry_exit
    def test_gen_opacity_map(self):
        # Initialization
        load_test_session()

        # Verify that when the column doesn't exist, it's treated as a column with no values
        no_map = gen_node_opacity_map('bogus column', style_name='galFiltered Style', mapping_type='d')
        self.assertDictEqual(no_map, {'table_column': 'bogus column', 'table_column_values': [], 'opacities': [], 'mapping_type': 'd', 'default_opacity': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        no_map = gen_edge_opacity_map('bogus column', style_name='galFiltered Style', mapping_type='d')
        self.assertDictEqual(no_map, {'table_column': 'bogus column', 'table_column_values': [], 'opacities': [], 'mapping_type': 'd', 'default_opacity': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        no_map = gen_node_opacity_map('bogus column', style_name='galFiltered Style')
        self.assertDictEqual(no_map, {'table_column': 'bogus column', 'table_column_values': [0, 0.5, 1], 'opacities': [10, 20.0, 30], 'mapping_type': 'c', 'default_opacity': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        no_map = gen_edge_opacity_map('bogus column', style_name='galFiltered Style')
        self.assertDictEqual(no_map, {'table_column': 'bogus column', 'table_column_values': [0, 0.5, 1], 'opacities': [10, 20.0, 30], 'mapping_type': 'c', 'default_opacity': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

        # Create a column with eight data values, and verify that the correct values and mappings are generated for series & random
        eight_data = df.DataFrame(data={'id':['YDL194W', 'YDR277C', 'YBR043C', 'YKR026C', 'YGL122C', 'YGR218W', 'YGL097W', 'YOR204W'], 'newcol':[1, 2, 3, 4, 5, 6, 7, 8]})
        load_table_data(eight_data, data_key_column='id')
        eight_map = gen_node_opacity_map('newcol', style_name='galFiltered Style', mapping_type='d')
        self.assertDictEqual(eight_map, {'table_column': 'newcol', 'table_column_values': ['8', '7', '6', '5', '4', '3', '2', '1'], 'opacities': [0, 10, 20, 30, 40, 50, 60, 70], 'mapping_type': 'd', 'default_opacity': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        eight_map = gen_node_opacity_map('newcol', scheme_d_number_series(start_value=100, step=20), style_name='galFiltered Style', mapping_type='d')
        self.assertDictEqual(eight_map, {'table_column': 'newcol', 'table_column_values': ['8', '7', '6', '5', '4', '3', '2', '1'], 'opacities': [100, 120, 140, 160, 180, 200, 220, 240], 'mapping_type': 'd', 'default_opacity': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        random_map = gen_node_opacity_map('newcol', scheme_d_number_random(min_value=30, max_value=100), style_name='galFiltered Style', mapping_type='d')
        self.assertEqual(len(random_map['opacities']), 8)

        # Verify that continuous maps are generated for the data values, using both default and non-default domains
        continuous_map = gen_node_opacity_map('newcol', style_name='galFiltered Style')
        self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'opacities': [10, 20.0, 30], 'mapping_type': 'c', 'default_opacity': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        continuous_alt_map = gen_node_opacity_map('newcol', scheme_c_number_continuous(100, 200), style_name='galFiltered Style')
        self.assertDictEqual(continuous_alt_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'opacities': [100, 150.0, 200], 'mapping_type': 'c', 'default_opacity': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

        # Verify that each node opacity mapping works for both discrete and continuous
        set_node_border_opacity_mapping(**eight_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_BORDER_TRANSPARENCY'), {'mappingType': 'discrete', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_BORDER_TRANSPARENCY', 'map': [{'key': '1', 'value': '240'}, {'key': '2', 'value': '220'}, {'key': '3', 'value': '200'}, {'key': '4', 'value': '180'}, {'key': '5', 'value': '160'}, {'key': '6', 'value': '140'}, {'key': '7', 'value': '120'}, {'key': '8', 'value': '100'}]})
        set_node_border_opacity_mapping(**continuous_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_BORDER_TRANSPARENCY'), {'mappingType': 'continuous', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_BORDER_TRANSPARENCY', 'points': [{'value': 1.0, 'lesser': '10', 'equal': '10', 'greater': '10'}, {'value': 4.5, 'lesser': '20', 'equal': '20', 'greater': '20'}, {'value': 8.0, 'lesser': '30', 'equal': '30', 'greater': '30'}]})

        set_node_fill_opacity_mapping(**eight_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_TRANSPARENCY'), {'mappingType': 'discrete', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_TRANSPARENCY', 'map': [{'key': '1', 'value': '240'}, {'key': '2', 'value': '220'}, {'key': '3', 'value': '200'}, {'key': '4', 'value': '180'}, {'key': '5', 'value': '160'}, {'key': '6', 'value': '140'}, {'key': '7', 'value': '120'}, {'key': '8', 'value': '100'}]})
        set_node_fill_opacity_mapping(**continuous_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_TRANSPARENCY'), {'mappingType': 'continuous', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_TRANSPARENCY', 'points': [{'value': 1.0, 'lesser': '10', 'equal': '10', 'greater': '10'}, {'value': 4.5, 'lesser': '20', 'equal': '20', 'greater': '20'}, {'value': 8.0, 'lesser': '30', 'equal': '30', 'greater': '30'}]})

        set_node_label_opacity_mapping(**eight_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_LABEL_TRANSPARENCY'), {'mappingType': 'discrete', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_LABEL_TRANSPARENCY', 'map': [{'key': '1', 'value': '240'}, {'key': '2', 'value': '220'}, {'key': '3', 'value': '200'}, {'key': '4', 'value': '180'}, {'key': '5', 'value': '160'}, {'key': '6', 'value': '140'}, {'key': '7', 'value': '120'}, {'key': '8', 'value': '100'}]})
        set_node_label_opacity_mapping(**continuous_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_LABEL_TRANSPARENCY'), {'mappingType': 'continuous', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_LABEL_TRANSPARENCY', 'points': [{'value': 1.0, 'lesser': '10', 'equal': '10', 'greater': '10'}, {'value': 4.5, 'lesser': '20', 'equal': '20', 'greater': '20'}, {'value': 8.0, 'lesser': '30', 'equal': '30', 'greater': '30'}]})

        # Verify that the alt mapping works for continuous, too
        set_node_border_opacity_mapping(**continuous_alt_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_BORDER_TRANSPARENCY'), {'mappingType': 'continuous', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_BORDER_TRANSPARENCY', 'points': [{'value': 1.0, 'lesser': '100', 'equal': '100', 'greater': '100'}, {'value': 4.5, 'lesser': '150', 'equal': '150', 'greater': '150'}, {'value': 8.0, 'lesser': '200', 'equal': '200', 'greater': '200'}]})

        # Take advantage of edge interaction column already existing
        two_map = gen_edge_opacity_map('interaction', style_name='galFiltered Style', mapping_type='d')
        self.assertDictEqual(two_map, {'table_column': 'interaction', 'table_column_values': ['pp', 'pd'], 'opacities': [0, 10], 'mapping_type': 'd', 'default_opacity': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        two_map = gen_edge_opacity_map('interaction', scheme_d_number_series(start_value=100, step=20), style_name='galFiltered Style', mapping_type='d')
        self.assertDictEqual(two_map, {'table_column': 'interaction', 'table_column_values': ['pp', 'pd'], 'opacities': [100, 120], 'mapping_type': 'd', 'default_opacity': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        random_map = gen_edge_opacity_map('interaction', scheme_d_number_random(min_value=30, max_value=100), style_name='galFiltered Style', mapping_type='d')
        self.assertEqual(len(random_map['opacities']), 2)

        # Verify that continuous maps are generated for the data values, using both default and non-default domains
        continuous_map = gen_edge_opacity_map('EdgeBetweenness', style_name='galFiltered Style')
        self.assertDictEqual(continuous_map, {'table_column': 'EdgeBetweenness', 'table_column_values': [2.0, 9591.11110001, 19180.22220002], 'opacities': [10, 20.0, 30], 'mapping_type': 'c', 'default_opacity': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        continuous_alt_map = gen_edge_opacity_map('EdgeBetweenness', scheme_c_number_continuous(100, 200), style_name='galFiltered Style')
        self.assertDictEqual(continuous_alt_map, {'table_column': 'EdgeBetweenness', 'table_column_values': [2.0, 9591.11110001, 19180.22220002], 'opacities': [100, 150.0, 200], 'mapping_type': 'c', 'default_opacity': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

        # Verify that each edge opacity mapping works for both discrete and continuous
        set_edge_label_opacity_mapping(**two_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_LABEL_TRANSPARENCY'), {'mappingType': 'discrete', 'mappingColumn': 'interaction', 'mappingColumnType': 'String', 'visualProperty': 'EDGE_LABEL_TRANSPARENCY', 'map': [{'key': 'pp', 'value': '100'}, {'key': 'pd', 'value': '120'}]})
        set_edge_label_opacity_mapping(**continuous_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_LABEL_TRANSPARENCY'), {'mappingType': 'continuous', 'mappingColumn': 'EdgeBetweenness', 'mappingColumnType': 'Double', 'visualProperty': 'EDGE_LABEL_TRANSPARENCY', 'points': [{'value': 2.0, 'lesser': '10', 'equal': '10', 'greater': '10'}, {'value': 9591.11110001, 'lesser': '20', 'equal': '20', 'greater': '20'}, {'value': 19180.22220002, 'lesser': '30', 'equal': '30', 'greater': '30'}]})

        set_edge_opacity_mapping(**two_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_TRANSPARENCY'), {'mappingType': 'discrete', 'mappingColumn': 'interaction', 'mappingColumnType': 'String', 'visualProperty': 'EDGE_TRANSPARENCY', 'map': [{'key': 'pp', 'value': '100'}, {'key': 'pd', 'value': '120'}]})
        set_edge_opacity_mapping(**continuous_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_TRANSPARENCY'), {'mappingType': 'continuous', 'mappingColumn': 'EdgeBetweenness', 'mappingColumnType': 'Double', 'visualProperty': 'EDGE_TRANSPARENCY', 'points': [{'value': 2.0, 'lesser': '10', 'equal': '10', 'greater': '10'}, {'value': 9591.11110001, 'lesser': '20', 'equal': '20', 'greater': '20'}, {'value': 19180.22220002, 'lesser': '30', 'equal': '30', 'greater': '30'}]})

        # Verify that the alt mapping works for continuous, too
        set_edge_opacity_mapping(**continuous_alt_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_TRANSPARENCY'), {'mappingType': 'continuous', 'mappingColumn': 'EdgeBetweenness', 'mappingColumnType': 'Double', 'visualProperty': 'EDGE_TRANSPARENCY', 'points': [{'value': 2.0, 'lesser': '100', 'equal': '100', 'greater': '100'}, {'value': 9591.11110001, 'lesser': '150', 'equal': '150', 'greater': '150'}, {'value': 19180.22220002, 'lesser': '200', 'equal': '200', 'greater': '200'}]})

        # Verify that when the network doesn't exist, an appropriate error is returned
        self.assertRaises(CyError, gen_node_opacity_map, 'newcol', network='bogus network', mapping_type='d')
        self.assertRaises(CyError, gen_edge_opacity_map, 'EdgeBetweenness', network='bogus network', mapping_type='d')
        self.assertRaises(CyError, gen_node_opacity_map, 'newcol', network='bogus network')
        self.assertRaises(CyError, gen_edge_opacity_map, 'EdgeBetweenness', network='bogus network')


    @print_entry_exit
    def test_gen_width_map(self):
        # Initialization
        load_test_session()

        # Verify that when the column doesn't exist, it's treated as a column with no values
        no_map = gen_node_width_map('bogus column', style_name='galFiltered Style', mapping_type='d')
        self.assertDictEqual(no_map, {'table_column': 'bogus column', 'table_column_values': [], 'widths': [], 'mapping_type': 'd', 'default_width': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        no_map = gen_edge_width_map('bogus column', style_name='galFiltered Style', mapping_type='d')
        self.assertDictEqual(no_map, {'table_column': 'bogus column', 'table_column_values': [], 'widths': [], 'mapping_type': 'd', 'default_width': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        no_map = gen_node_width_map('bogus column', style_name='galFiltered Style')
        self.assertDictEqual(no_map, {'table_column': 'bogus column', 'table_column_values': [0, 0.5, 1], 'widths': [10, 20.0, 30], 'mapping_type': 'c', 'default_width': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        no_map = gen_edge_width_map('bogus column', style_name='galFiltered Style')
        self.assertDictEqual(no_map, {'table_column': 'bogus column', 'table_column_values': [0, 0.5, 1], 'widths': [10, 20.0, 30], 'mapping_type': 'c', 'default_width': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

        # Create a column with eight data values, and verify that the correct values and mappings are generated for series & random
        eight_data = df.DataFrame(data={'id':['YDL194W', 'YDR277C', 'YBR043C', 'YKR026C', 'YGL122C', 'YGR218W', 'YGL097W', 'YOR204W'], 'newcol':[1, 2, 3, 4, 5, 6, 7, 8]})
        load_table_data(eight_data, data_key_column='id')
        eight_map = gen_node_width_map('newcol', style_name='galFiltered Style', mapping_type='d')
        self.assertDictEqual(eight_map, {'table_column': 'newcol', 'table_column_values': ['8', '7', '6', '5', '4', '3', '2', '1'], 'widths': [0, 10, 20, 30, 40, 50, 60, 70], 'mapping_type': 'd', 'default_width': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        eight_map = gen_node_width_map('newcol', scheme_d_number_series(start_value=100, step=20), style_name='galFiltered Style', mapping_type='d')
        self.assertDictEqual(eight_map, {'table_column': 'newcol', 'table_column_values': ['8', '7', '6', '5', '4', '3', '2', '1'], 'widths': [100, 120, 140, 160, 180, 200, 220, 240], 'mapping_type': 'd', 'default_width': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        random_map = gen_node_width_map('newcol', scheme_d_number_random(min_value=30, max_value=100), style_name='galFiltered Style', mapping_type='d')
        self.assertEqual(len(random_map['widths']), 8)

        # Verify that continuous maps are generated for the data values, using both default and non-default domains
        continuous_map = gen_node_width_map('newcol', style_name='galFiltered Style')
        self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'widths': [10, 20.0, 30], 'mapping_type': 'c', 'default_width': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        continuous_alt_map = gen_node_width_map('newcol', scheme_c_number_continuous(100, 200), style_name='galFiltered Style')
        self.assertDictEqual(continuous_alt_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'widths': [100, 150.0, 200], 'mapping_type': 'c', 'default_width': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

        # Verify that each node width mapping works for both discrete and continuous
        set_node_border_width_mapping(**eight_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_BORDER_WIDTH'), {'mappingType': 'discrete', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_BORDER_WIDTH', 'map': [{'key': '1', 'value': '240.0'}, {'key': '2', 'value': '220.0'}, {'key': '3', 'value': '200.0'}, {'key': '4', 'value': '180.0'}, {'key': '5', 'value': '160.0'}, {'key': '6', 'value': '140.0'}, {'key': '7', 'value': '120.0'}, {'key': '8', 'value': '100.0'}]})
        set_node_border_width_mapping(**continuous_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_BORDER_WIDTH'), {'mappingType': 'continuous', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_BORDER_WIDTH', 'points': [{'value': 1.0, 'lesser': '10.0', 'equal': '10.0', 'greater': '10.0'}, {'value': 4.5, 'lesser': '20.0', 'equal': '20.0', 'greater': '20.0'}, {'value': 8.0, 'lesser': '30.0', 'equal': '30.0', 'greater': '30.0'}]})

        set_node_width_mapping(**eight_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_WIDTH'), {'mappingType': 'discrete', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_WIDTH', 'map': [{'key': '1', 'value': '240.0'}, {'key': '2', 'value': '220.0'}, {'key': '3', 'value': '200.0'}, {'key': '4', 'value': '180.0'}, {'key': '5', 'value': '160.0'}, {'key': '6', 'value': '140.0'}, {'key': '7', 'value': '120.0'}, {'key': '8', 'value': '100.0'}]})
        set_node_width_mapping(**continuous_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_WIDTH'), {'mappingType': 'continuous', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_WIDTH', 'points': [{'value': 1.0, 'lesser': '10.0', 'equal': '10.0', 'greater': '10.0'}, {'value': 4.5, 'lesser': '20.0', 'equal': '20.0', 'greater': '20.0'}, {'value': 8.0, 'lesser': '30.0', 'equal': '30.0', 'greater': '30.0'}]})

        # Verify that the alt mapping works for continuous, too
        set_node_border_width_mapping(**continuous_alt_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_BORDER_WIDTH'), {'mappingType': 'continuous', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_BORDER_WIDTH', 'points': [{'value': 1.0, 'lesser': '100.0', 'equal': '100.0', 'greater': '100.0'}, {'value': 4.5, 'lesser': '150.0', 'equal': '150.0', 'greater': '150.0'}, {'value': 8.0, 'lesser': '200.0', 'equal': '200.0', 'greater': '200.0'}]})

        # Take advantage of edge interaction column already existing
        two_map = gen_edge_width_map('interaction', style_name='galFiltered Style', mapping_type='d')
        self.assertDictEqual(two_map, {'table_column': 'interaction', 'table_column_values': ['pp', 'pd'], 'widths': [0, 10], 'mapping_type': 'd', 'default_width': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        two_map = gen_edge_width_map('interaction', scheme_d_number_series(start_value=100, step=20), style_name='galFiltered Style', mapping_type='d')
        self.assertDictEqual(two_map, {'table_column': 'interaction', 'table_column_values': ['pp', 'pd'], 'widths': [100, 120], 'mapping_type': 'd', 'default_width': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        random_map = gen_edge_width_map('interaction', scheme_d_number_random(min_value=30, max_value=100), style_name='galFiltered Style', mapping_type='d')
        self.assertEqual(len(random_map['widths']), 2)

        # Verify that continuous maps are generated for the data values, using both default and non-default domains
        continuous_map = gen_edge_width_map('EdgeBetweenness', style_name='galFiltered Style')
        self.assertDictEqual(continuous_map, {'table_column': 'EdgeBetweenness', 'table_column_values': [2.0, 9591.11110001, 19180.22220002], 'widths': [10, 20.0, 30], 'mapping_type': 'c', 'default_width': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        continuous_alt_map = gen_edge_width_map('EdgeBetweenness', scheme_c_number_continuous(100, 200), style_name='galFiltered Style')
        self.assertDictEqual(continuous_alt_map, {'table_column': 'EdgeBetweenness', 'table_column_values': [2.0, 9591.11110001, 19180.22220002], 'widths': [100, 150.0, 200], 'mapping_type': 'c', 'default_width': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

        # Verify that each edge width mapping works for both discrete and continuous
        set_edge_line_width_mapping(**two_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_WIDTH'), {'mappingType': 'discrete', 'mappingColumn': 'interaction', 'mappingColumnType': 'String', 'visualProperty': 'EDGE_WIDTH', 'map': [{'key': 'pp', 'value': '100.0'}, {'key': 'pd', 'value': '120.0'}]})
        set_edge_line_width_mapping(**continuous_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_WIDTH'), {'mappingType': 'continuous', 'mappingColumn': 'EdgeBetweenness', 'mappingColumnType': 'Double', 'visualProperty': 'EDGE_WIDTH', 'points': [{'value': 2.0, 'lesser': '10.0', 'equal': '10.0', 'greater': '10.0'}, {'value': 9591.11110001, 'lesser': '20.0', 'equal': '20.0', 'greater': '20.0'}, {'value': 19180.22220002, 'lesser': '30.0', 'equal': '30.0', 'greater': '30.0'}]})

        # Verify that the alt mapping works for continuous, too
        set_edge_line_width_mapping(**continuous_alt_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_WIDTH'), {'mappingType': 'continuous', 'mappingColumn': 'EdgeBetweenness', 'mappingColumnType': 'Double', 'visualProperty': 'EDGE_WIDTH', 'points': [{'value': 2.0, 'lesser': '100.0', 'equal': '100.0', 'greater': '100.0'}, {'value': 9591.11110001, 'lesser': '150.0', 'equal': '150.0', 'greater': '150.0'}, {'value': 19180.22220002, 'lesser': '200.0', 'equal': '200.0', 'greater': '200.0'}]})

        # Verify that when the network doesn't exist, an appropriate error is returned
        self.assertRaises(CyError, gen_node_width_map, 'newcol', network='bogus network', mapping_type='d')
        self.assertRaises(CyError, gen_edge_width_map, 'EdgeBetweenness', network='bogus network', mapping_type='d')
        self.assertRaises(CyError, gen_node_width_map, 'newcol', network='bogus network')
        self.assertRaises(CyError, gen_edge_width_map, 'EdgeBetweenness', network='bogus network')

    @print_entry_exit
    def test_gen_height_map(self):
        # Initialization
        load_test_session()

        # Verify that when the column doesn't exist, it's treated as a column with no values
        no_map = gen_node_height_map('bogus column', scheme_d_number_random(min_value=30, max_value=100), style_name='galFiltered Style', mapping_type='d')
        self.assertDictEqual(no_map, {'table_column': 'bogus column', 'table_column_values': [], 'heights': [], 'mapping_type': 'd', 'default_height': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

        # Create a column with eight data values, and verify that the correct values and mappings are generated for series & random
        eight_data = df.DataFrame(data={'id':['YDL194W', 'YDR277C', 'YBR043C', 'YKR026C', 'YGL122C', 'YGR218W', 'YGL097W', 'YOR204W'], 'newcol':[1, 2, 3, 4, 5, 6, 7, 8]})
        load_table_data(eight_data, data_key_column='id')
        eight_map = gen_node_height_map('newcol', style_name='galFiltered Style', mapping_type='d')
        self.assertDictEqual(eight_map, {'table_column': 'newcol', 'table_column_values': ['8', '7', '6', '5', '4', '3', '2', '1'], 'heights': [0, 10, 20, 30, 40, 50, 60, 70], 'mapping_type': 'd', 'default_height': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        eight_map = gen_node_height_map('newcol', scheme_d_number_series(start_value=100, step=20), style_name='galFiltered Style', mapping_type='d')
        self.assertDictEqual(eight_map, {'table_column': 'newcol', 'table_column_values': ['8', '7', '6', '5', '4', '3', '2', '1'], 'heights': [100, 120, 140, 160, 180, 200, 220, 240], 'mapping_type': 'd', 'default_height': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        random_map = gen_node_height_map('newcol', scheme_d_number_random(min_value=30, max_value=100), style_name='galFiltered Style', mapping_type='d')
        self.assertEqual(len(random_map['heights']), 8)

        # Verify that continuous maps are generated for the data values, using both default and non-default domains
        continuous_map = gen_node_height_map('newcol', style_name='galFiltered Style')
        self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'heights': [10, 20.0, 30], 'mapping_type': 'c', 'default_height': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        continuous_alt_map = gen_node_height_map('newcol', scheme_c_number_continuous(100, 200), style_name='galFiltered Style')
        self.assertDictEqual(continuous_alt_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'heights': [100, 150.0, 200], 'mapping_type': 'c', 'default_height': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

        # Verify that each node height mapping works for both discrete and continuous
        set_node_height_mapping(**eight_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_HEIGHT'), {'mappingType': 'discrete', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_HEIGHT', 'map': [{'key': '1', 'value': '240.0'}, {'key': '2', 'value': '220.0'}, {'key': '3', 'value': '200.0'}, {'key': '4', 'value': '180.0'}, {'key': '5', 'value': '160.0'}, {'key': '6', 'value': '140.0'}, {'key': '7', 'value': '120.0'}, {'key': '8', 'value': '100.0'}]})
        set_node_height_mapping(**continuous_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_HEIGHT'), {'mappingType': 'continuous', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_HEIGHT', 'points': [{'value': 1.0, 'lesser': '10.0', 'equal': '10.0', 'greater': '10.0'}, {'value': 4.5, 'lesser': '20.0', 'equal': '20.0', 'greater': '20.0'}, {'value': 8.0, 'lesser': '30.0', 'equal': '30.0', 'greater': '30.0'}]})

        # Verify that the alt mapping works for continuous, too
        set_node_height_mapping(**continuous_alt_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_HEIGHT'), {'mappingType': 'continuous', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_HEIGHT', 'points': [{'value': 1.0, 'lesser': '100.0', 'equal': '100.0', 'greater': '100.0'}, {'value': 4.5, 'lesser': '150.0', 'equal': '150.0', 'greater': '150.0'}, {'value': 8.0, 'lesser': '200.0', 'equal': '200.0', 'greater': '200.0'}]})

        # Verify that when the network doesn't exist, an appropriate error is returned
        self.assertRaises(CyError, gen_node_height_map, 'newcol', network='bogus network', mapping_type='d')
        self.assertRaises(CyError, gen_node_height_map, 'newcol', network='bogus network')

    @print_entry_exit
    def test_gen_size_map(self):
        # Initialization
        load_test_session()

        # Verify that when the column doesn't exist, it's treated as a column with no values
        no_map = gen_node_size_map('bogus column', style_name='galFiltered Style', mapping_type='d')
        self.assertDictEqual(no_map, {'table_column': 'bogus column', 'table_column_values': [], 'sizes': [], 'mapping_type': 'd', 'default_size': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        no_map = gen_edge_size_map('bogus column', style_name='galFiltered Style', mapping_type='d')
        self.assertDictEqual(no_map, {'table_column': 'bogus column', 'table_column_values': [], 'sizes': [], 'mapping_type': 'd', 'default_size': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        no_map = gen_node_size_map('bogus column', style_name='galFiltered Style')
        self.assertDictEqual(no_map, {'table_column': 'bogus column', 'table_column_values': [0, 0.5, 1], 'sizes': [10, 20.0, 30], 'mapping_type': 'c', 'default_size': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        no_map = gen_edge_size_map('bogus column', style_name='galFiltered Style')
        self.assertDictEqual(no_map, {'table_column': 'bogus column', 'table_column_values': [0, 0.5, 1], 'sizes': [10, 20.0, 30], 'mapping_type': 'c', 'default_size': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

        # Create a column with eight data values, and verify that the correct values and mappings are generated for series & random
        eight_data = df.DataFrame(data={'id':['YDL194W', 'YDR277C', 'YBR043C', 'YKR026C', 'YGL122C', 'YGR218W', 'YGL097W', 'YOR204W'], 'newcol':[1, 2, 3, 4, 5, 6, 7, 8]})
        load_table_data(eight_data, data_key_column='id')
        eight_map = gen_node_size_map('newcol', style_name='galFiltered Style', mapping_type='d')
        self.assertDictEqual(eight_map, {'table_column': 'newcol', 'table_column_values': ['8', '7', '6', '5', '4', '3', '2', '1'], 'sizes': [0, 10, 20, 30, 40, 50, 60, 70], 'mapping_type': 'd', 'default_size': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        eight_map = gen_node_size_map('newcol', scheme_d_number_series(start_value=100, step=20), style_name='galFiltered Style', mapping_type='d')
        self.assertDictEqual(eight_map, {'table_column': 'newcol', 'table_column_values': ['8', '7', '6', '5', '4', '3', '2', '1'], 'sizes': [100, 120, 140, 160, 180, 200, 220, 240], 'mapping_type': 'd', 'default_size': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        random_map = gen_node_size_map('newcol', scheme_d_number_random(min_value=30, max_value=100), style_name='galFiltered Style', mapping_type='d')
        self.assertEqual(len(random_map['sizes']), 8)

        # Verify that continuous maps are generated for the data values, using both default and non-default domains
        continuous_map = gen_node_size_map('newcol', style_name='galFiltered Style')
        self.assertDictEqual(continuous_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'sizes': [10, 20.0, 30], 'mapping_type': 'c', 'default_size': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        continuous_alt_map = gen_node_size_map('newcol', scheme_c_number_continuous(100, 200), style_name='galFiltered Style')
        self.assertDictEqual(continuous_alt_map, {'table_column': 'newcol', 'table_column_values': [1, 4.5, 8], 'sizes': [100, 150.0, 200], 'mapping_type': 'c', 'default_size': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

        # Verify that each node size mapping works for both discrete and continuous
        set_node_font_size_mapping(**eight_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_LABEL_FONT_SIZE'), {'mappingType': 'discrete', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_LABEL_FONT_SIZE', 'map': [{'key': '1', 'value': '240'}, {'key': '2', 'value': '220'}, {'key': '3', 'value': '200'}, {'key': '4', 'value': '180'}, {'key': '5', 'value': '160'}, {'key': '6', 'value': '140'}, {'key': '7', 'value': '120'}, {'key': '8', 'value': '100'}]})
        set_node_font_size_mapping(**continuous_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_LABEL_FONT_SIZE'), {'mappingType': 'continuous', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_LABEL_FONT_SIZE', 'points': [{'value': 1.0, 'lesser': '10', 'equal': '10', 'greater': '10'}, {'value': 4.5, 'lesser': '20', 'equal': '20', 'greater': '20'}, {'value': 8.0, 'lesser': '30', 'equal': '30', 'greater': '30'}]})

        set_node_size_mapping(**eight_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_SIZE'), {'mappingType': 'discrete', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_SIZE', 'map': [{'key': '1', 'value': '240.0'}, {'key': '2', 'value': '220.0'}, {'key': '3', 'value': '200.0'}, {'key': '4', 'value': '180.0'}, {'key': '5', 'value': '160.0'}, {'key': '6', 'value': '140.0'}, {'key': '7', 'value': '120.0'}, {'key': '8', 'value': '100.0'}]})
        set_node_size_mapping(**continuous_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_SIZE'), {'mappingType': 'continuous', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_SIZE', 'points': [{'value': 1.0, 'lesser': '10.0', 'equal': '10.0', 'greater': '10.0'}, {'value': 4.5, 'lesser': '20.0', 'equal': '20.0', 'greater': '20.0'}, {'value': 8.0, 'lesser': '30.0', 'equal': '30.0', 'greater': '30.0'}]})

        # Verify that the alt mapping works for continuous, too
        set_node_font_size_mapping(**continuous_alt_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_LABEL_FONT_SIZE'), {'mappingType': 'continuous', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_LABEL_FONT_SIZE', 'points': [{'value': 1.0, 'lesser': '100', 'equal': '100', 'greater': '100'}, {'value': 4.5, 'lesser': '150', 'equal': '150', 'greater': '150'}, {'value': 8.0, 'lesser': '200', 'equal': '200', 'greater': '200'}]})

        # Take advantage of edge interaction column already existing
        two_map = gen_edge_size_map('interaction', style_name='galFiltered Style', mapping_type='d')
        self.assertDictEqual(two_map, {'table_column': 'interaction', 'table_column_values': ['pp', 'pd'], 'sizes': [0, 10], 'mapping_type': 'd', 'default_size': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        two_map = gen_edge_size_map('interaction', scheme_d_number_series(start_value=100, step=20), style_name='galFiltered Style', mapping_type='d')
        self.assertDictEqual(two_map, {'table_column': 'interaction', 'table_column_values': ['pp', 'pd'], 'sizes': [100, 120], 'mapping_type': 'd', 'default_size': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        random_map = gen_edge_size_map('interaction', scheme_d_number_random(min_value=30, max_value=100), style_name='galFiltered Style', mapping_type='d')
        self.assertEqual(len(random_map['sizes']), 2)

        # Verify that continuous maps are generated for the data values, using both default and non-default domains
        continuous_map = gen_edge_size_map('EdgeBetweenness', style_name='galFiltered Style')
        self.assertDictEqual(continuous_map, {'table_column': 'EdgeBetweenness', 'table_column_values': [2.0, 9591.11110001, 19180.22220002], 'sizes': [10, 20.0, 30], 'mapping_type': 'c', 'default_size': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        continuous_alt_map = gen_edge_size_map('EdgeBetweenness', scheme_c_number_continuous(100, 200), style_name='galFiltered Style')
        self.assertDictEqual(continuous_alt_map, {'table_column': 'EdgeBetweenness', 'table_column_values': [2.0, 9591.11110001, 19180.22220002], 'sizes': [100, 150.0, 200], 'mapping_type': 'c', 'default_size': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

        # Verify that each edge font size mapping works for both discrete and continuous
        set_edge_font_size_mapping(**two_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_LABEL_FONT_SIZE'), {'mappingType': 'discrete', 'mappingColumn': 'interaction', 'mappingColumnType': 'String', 'visualProperty': 'EDGE_LABEL_FONT_SIZE', 'map': [{'key': 'pp', 'value': '100'}, {'key': 'pd', 'value': '120'}]})
        set_edge_font_size_mapping(**continuous_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_LABEL_FONT_SIZE'), {'mappingType': 'continuous', 'mappingColumn': 'EdgeBetweenness', 'mappingColumnType': 'Double', 'visualProperty': 'EDGE_LABEL_FONT_SIZE', 'points': [{'value': 2.0, 'lesser': '10', 'equal': '10', 'greater': '10'}, {'value': 9591.11110001, 'lesser': '20', 'equal': '20', 'greater': '20'}, {'value': 19180.22220002, 'lesser': '30', 'equal': '30', 'greater': '30'}]})

        # Verify that the alt mapping works for continuous, too
        set_edge_font_size_mapping(**continuous_alt_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_LABEL_FONT_SIZE'), {'mappingType': 'continuous', 'mappingColumn': 'EdgeBetweenness', 'mappingColumnType': 'Double', 'visualProperty': 'EDGE_LABEL_FONT_SIZE', 'points': [{'value': 2.0, 'lesser': '100', 'equal': '100', 'greater': '100'}, {'value': 9591.11110001, 'lesser': '150', 'equal': '150', 'greater': '150'}, {'value': 19180.22220002, 'lesser': '200', 'equal': '200', 'greater': '200'}]})

        # Verify that when the network doesn't exist, an appropriate error is returned
        self.assertRaises(CyError, gen_node_size_map, 'newcol', network='bogus network', mapping_type='d')
        self.assertRaises(CyError, gen_edge_size_map, 'EdgeBetweenness', network='bogus network', mapping_type='d')
        self.assertRaises(CyError, gen_node_size_map, 'newcol', network='bogus network')
        self.assertRaises(CyError, gen_edge_size_map, 'EdgeBetweenness', network='bogus network')

    @print_entry_exit
    def test_gen_shapes_map(self):
        # Initialization
        load_test_session()

        # Verify that when the column doesn't exist, it's treated as a column with no values
        no_map = gen_node_shape_map('bogus column', style_name='galFiltered Style')
        self.assertDictEqual(no_map, {'table_column': 'bogus column', 'table_column_values': [], 'shapes': [], 'default_shape': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        no_map = gen_edge_line_style_map('bogus column', style_name='galFiltered Style')
        self.assertDictEqual(no_map, {'table_column': 'bogus column', 'table_column_values': [], 'line_styles': [], 'default_line_style': 'SOLID', 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        no_map = gen_edge_arrow_map('bogus column', style_name='galFiltered Style')
        self.assertDictEqual(no_map, {'table_column': 'bogus column', 'table_column_values': [], 'shapes': [], 'default_shape': 'ARROW', 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

        # Create a column with eight data values, and verify that the correct values and mappings are generated
        eight_data = df.DataFrame(data={'id':['YDL194W', 'YDR277C', 'YBR043C', 'YKR026C', 'YGL122C', 'YGR218W', 'YGL097W', 'YOR204W'], 'newcol':[1, 2, 3, 4, 5, 6, 7, 8]})
        load_table_data(eight_data, data_key_column='id')
        eight_map = gen_node_shape_map('newcol', style_name='galFiltered Style')
        self.assertDictEqual(eight_map, {'table_column': 'newcol', 'table_column_values': ['8', '7', '6', '5', '4', '3', '2', '1'], 'shapes': ['DIAMOND', 'ELLIPSE', 'HEXAGON', 'OCTAGON', 'PARALLELOGRAM', 'RECTANGLE', 'ROUND_RECTANGLE', 'TRIANGLE'], 'default_shape': None, 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

        # Verify that each shape mapping works
        set_node_shape_mapping(**eight_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='NODE_SHAPE'), {'mappingType': 'discrete', 'mappingColumn': 'newcol', 'mappingColumnType': 'Integer', 'visualProperty': 'NODE_SHAPE', 'map': [{'key': '1', 'value': 'TRIANGLE'}, {'key': '2', 'value': 'ROUND_RECTANGLE'}, {'key': '3', 'value': 'RECTANGLE'}, {'key': '4', 'value': 'PARALLELOGRAM'}, {'key': '5', 'value': 'OCTAGON'}, {'key': '6', 'value': 'HEXAGON'}, {'key': '7', 'value': 'ELLIPSE'}, {'key': '8', 'value': 'DIAMOND'}]})

        # Verify that when there are too many discrete values for the shape list, an error is generated
        four_data = df.DataFrame(data={'id':['YAL003W', 'YFL017C', 'YDR429C', 'YMR146C'], 'newcol':[100, 200, 300, 400]})
        load_table_data(four_data, data_key_column='id')
        self.assertRaises(CyError, gen_node_shape_map, 'newcol')

        # Take advantage of edge interaction column already existing
        two_line_style_map = gen_edge_line_style_map('interaction', style_name='galFiltered Style')
        self.assertDictEqual(two_line_style_map, {'table_column': 'interaction', 'table_column_values': ['pp', 'pd'], 'line_styles': ['BACKWARD_SLASH', 'CONTIGUOUS_ARROW'], 'default_line_style': 'SOLID', 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})
        two_arrow_map = gen_edge_arrow_map('interaction', style_name='galFiltered Style')
        self.assertDictEqual(two_arrow_map, {'table_column': 'interaction', 'table_column_values': ['pp', 'pd'], 'shapes': ['ARROW', 'ARROW_SHORT'], 'default_shape': 'ARROW', 'style_name': 'galFiltered Style', 'network': None, 'base_url': 'http://127.0.0.1:1234/v1'})

        # Verify that each edge line style mapping works
        set_edge_line_style_mapping(**two_line_style_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_LINE_TYPE'), {'mappingType': 'discrete', 'mappingColumn': 'interaction', 'mappingColumnType': 'String', 'visualProperty': 'EDGE_LINE_TYPE', 'map': [{'key': 'pp', 'value': 'BACKWARD_SLASH'}, {'key': 'pd', 'value': 'CONTIGUOUS_ARROW'}]})

        # Verify that each edge source/target arrow mapping works
        set_edge_source_arrow_shape_mapping(**two_arrow_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_SOURCE_ARROW_SHAPE'), {'mappingType': 'discrete', 'mappingColumn': 'interaction', 'mappingColumnType': 'String', 'visualProperty': 'EDGE_SOURCE_ARROW_SHAPE', 'map': [{'key': 'pp', 'value': 'ARROW'}, {'key': 'pd', 'value': 'ARROW_SHORT'}]})
        set_edge_target_arrow_shape_mapping(**two_arrow_map)
        self.assertDictEqual(get_style_mapping(style_name='galFiltered Style', visual_prop='EDGE_TARGET_ARROW_SHAPE'), {'mappingType': 'discrete', 'mappingColumn': 'interaction', 'mappingColumnType': 'String', 'visualProperty': 'EDGE_TARGET_ARROW_SHAPE', 'map': [{'key': 'pp', 'value': 'ARROW'}, {'key': 'pd', 'value': 'ARROW_SHORT'}]})

        # Verify that when the network doesn't exist, an appropriate error is returned
        self.assertRaises(CyError, gen_node_shape_map, 'newcol', network='bogus network')
        self.assertRaises(CyError, gen_edge_line_style_map, 'newcol', network='bogus network')
        self.assertRaises(CyError, gen_edge_arrow_map, 'newcol', network='bogus network')

if __name__ == '__main__':
    unittest.main()
