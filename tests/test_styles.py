# -*- coding: utf-8 -*-

""" Test functions in styles.py.

License:
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
from requests import RequestException

from test_utils import *


class StylesTests(unittest.TestCase):
    def setUp(self):
        try:
            py4cytoscape.delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    #    @py4cytoscape.skip
    @py4cytoscape.print_entry_exit
    def test_copy_visual_style(self):
        # Initialization
        load_test_session()

        # Verify that a new style can be added
        original_style_list = py4cytoscape.get_visual_style_names()
        res = py4cytoscape.copy_visual_style('Solid', 'SolidCopy')
        self.assertIsInstance(res, str)
        self.assertEqual(res, '')
        self.assertSetEqual(set(original_style_list) | {'SolidCopy'}, set(py4cytoscape.get_visual_style_names()))

        # Verify that an invalid style name is caught
        self.assertRaises(py4cytoscape.CyError, py4cytoscape.copy_visual_style, 'bogusStyle', 'bogusStyleCopy')
        self.assertRaises(RequestException, py4cytoscape.copy_visual_style, 'Solid', '')

        # TODO: When StyleValues.py exists, verify that the new style is a copy of the old style

    #    @py4cytoscape.skip
    @py4cytoscape.print_entry_exit
    def test_create_visual_style(self):
        # Initialization
        load_test_session()

        defaults = {'NODE_SHAPE': 'diamond', 'NODE_SIZE': 30, 'EDGE_TRANSPARENCY': 120,
                    'NODE_LABEL_POSITION': 'W,E,c,0.00,0.00'}
        node_labels = py4cytoscape.map_visual_property('node label', 'id', 'p')
        node_fills = py4cytoscape.map_visual_property('node fill color', 'group', 'd', ['A', 'B'], ['#FF9900', '#66AAAA'])
        arrow_shapes = py4cytoscape.map_visual_property('Edge Target Arrow Shape', 'interaction', 'd',
                                          ['activates', 'inhibits', 'interacts'], ['Arrow', 'T', 'None'])
        edge_width = py4cytoscape.map_visual_property('edge width', 'weight', 'p')
        res = py4cytoscape.create_visual_style('NewStyle', defaults=defaults, mappings=[node_labels, node_fills, arrow_shapes, edge_width])
        print(res)

if __name__ == '__main__':
    unittest.main()
