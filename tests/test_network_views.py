# -*- coding: utf-8 -*-

""" Test functions in network_views.py.

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
from requests import HTTPError
import time
from test_utils import *


class NetworkViewsTests(unittest.TestCase):
    def setUp(self):
        try:
            py4cytoscape.delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    #    @py4cytoscape.skip
    @py4cytoscape.print_entry_exit
    def test_get_network_views(self):
        # Initialization
        load_test_session()

        def check_view_list(view_list):
            self.assertIsInstance(view_list, list)
            self.assertEqual(len(view_list), 1)
            return view_list[0]

        # Verify that the view list for galFiltered looks right
        gal_filtered_view_suid = check_view_list(py4cytoscape.get_network_views())

        # Verify that the view list for a different network looks right
        yeast_suid, yeast_view_suid = load_test_network('data/yeastHighQuality.sif', make_current=False)
        check_view_suid = check_view_list(py4cytoscape.get_network_views(network=yeast_suid))
        self.assertEqual(yeast_view_suid, check_view_suid)
        self.assertNotEqual(gal_filtered_view_suid, yeast_view_suid)

        # Verify that the view list for the original network is unchanged
        self.assertEqual(check_view_list(py4cytoscape.get_network_views('galFiltered.sif')), gal_filtered_view_suid)

        self.assertRaises(py4cytoscape.CyError, py4cytoscape.get_network_views, 'bogus network')

    #    @py4cytoscape.skip
    @py4cytoscape.print_entry_exit
    def test_get_network_view_suid(self):
        # Initialization
        load_test_session()

        def check_view(view_suid):
            self.assertIsInstance(view_suid, int)
            return view_suid

        # Verify that the view list for galFiltered looks right ... identify network by "current"
        gal_filtered_view_suid = check_view(py4cytoscape.get_network_view_suid())

        # Verify that the view suid for a different network looks right ... identify network by suid
        yeast_suid, yeast_view_suid = load_test_network('data/yeastHighQuality.sif', make_current=False)
        check_view_suid = check_view(py4cytoscape.get_network_view_suid(network=yeast_suid))
        self.assertEqual(yeast_view_suid, check_view_suid)
        self.assertNotEqual(gal_filtered_view_suid, yeast_view_suid)

        # Verify that the view list for the original network is unchanged ... identify network by string
        self.assertEqual(check_view(py4cytoscape.get_network_view_suid('galFiltered.sif')), gal_filtered_view_suid)

        # Verify that the view list for the original network is unchanged ... identify view by view suid
        self.assertEqual(check_view(py4cytoscape.get_network_view_suid(gal_filtered_view_suid)), gal_filtered_view_suid)

        self.assertRaises(py4cytoscape.CyError, py4cytoscape.get_network_view_suid, 'bogus network')

    #    @py4cytoscape.skip
    @py4cytoscape.print_entry_exit
    def test_fit_content(self):
        # Initialization
        load_test_session()
        yeast_suid, yeast_view_suid = load_test_network('data/yeastHighQuality.sif', make_current=False)

        # Verify that entire network gets fit into view window
        fit_res = py4cytoscape.fit_content(selected_only=False)
        self.assertIsInstance(fit_res, dict)
        self.assertDictEqual(fit_res, {})
        input('Verify that entire galFiltered.sif network is fit to view window')

        # Verify that the selected nodes fit into view window
        py4cytoscape.select_nodes(nodes=['RAP1'], by_col='COMMON')
        py4cytoscape.select_first_neighbors()
        time.sleep(5)
        fit_res = py4cytoscape.fit_content(selected_only=True)
        self.assertIsInstance(fit_res, dict)
        self.assertDictEqual(fit_res, {})
        input('Verify that selected nodes in galFiltered.sif network are fit to view window')

        # Verify that the selected nodes of a different network fit into the view window ... identify network by view
        py4cytoscape.select_nodes(['SIK1', 'PGK1'], by_col='COMMON', network=yeast_suid)
        fit_res = py4cytoscape.fit_content(selected_only=True, network=yeast_view_suid)
        self.assertIsInstance(fit_res, dict)
        self.assertDictEqual(fit_res, {})
        input('Verify that selected nodes in yeastHighQuality.sif network are fit to view window')

        self.assertRaises(py4cytoscape.CyError, py4cytoscape.fit_content, network='bogus network')

    #    @py4cytoscape.skip
    @py4cytoscape.print_entry_exit
    def test_set_current_view(self):
        # Initialization
        load_test_session()
        gal_filtered_view = py4cytoscape.get_network_view_suid()
        yeast_suid, yeast_view_suid = load_test_network('data/yeastHighQuality.sif', make_current=False)

        # Set the view for galFiltered by passing in network SUID
        res = py4cytoscape.set_current_view(network=py4cytoscape.get_network_suid('galFiltered.sif'))
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {})

        # Set the view for yeastHighQuality by passing in view
        res = py4cytoscape.set_current_view(network=yeast_view_suid)
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {})

        # Verify that both views seem to be set
        self.assertEqual(py4cytoscape.get_network_view_suid(network='galFiltered.sif'), gal_filtered_view)
        self.assertEqual(py4cytoscape.get_network_view_suid(network=yeast_suid), yeast_view_suid)

        self.assertRaises(py4cytoscape.CyError, py4cytoscape.set_current_network, network='bogus network')

    #    @py4cytoscape.skip
    @py4cytoscape.print_entry_exit
    def test_export_image(self):
        # Initialization
        load_test_session()
        gal_filtered_view = py4cytoscape.get_network_view_suid()
        gal_filtered_suid = py4cytoscape.get_network_suid()

        def check_export(export_res):
            self.assertIsInstance(export_res, dict)
            self.assertIsInstance(export_res['file'], str)
            self.assertIsNotNone(export_res['file'])

        check_export(
            py4cytoscape.export_image('output/test units-pixels height-1000 width-2000 zoom-500', type='JPEG', units='pixels',
                                      height=1000, width=2000, zoom=200, network=None))
        check_export(py4cytoscape.export_image('output/test', type='PDF', network=None))
        check_export(py4cytoscape.export_image('output/test res-600 units-inches height-1.7 width-3.5 zoom-500', type='PNG',
                                               resolution=600, units='inches', height=1.7, width=3.5, zoom=500,
                                               network=gal_filtered_view))
        check_export(py4cytoscape.export_image('output/test', type='SVG', network=gal_filtered_view))
        check_export(py4cytoscape.export_image('output/test', type='PS', network=gal_filtered_suid))
        check_export(py4cytoscape.export_image('output/test alldefault', type='PNG', resolution=None, units=None, height=None,
                                               width=None, zoom=None, network=gal_filtered_suid))

        input('Verify the export output files in the ./output folder by sight')

        # Verify that an unknown network is caught
        self.assertRaises(py4cytoscape.CyError, py4cytoscape.export_image, network='bogus')
        self.assertRaises(py4cytoscape.CyError, py4cytoscape.export_image, 'output/test', type='PNG', resolution=600, units='inches',
                          height=10.7, width=3.5, zoom=500, network=gal_filtered_view)

    #    @py4cytoscape.skip
    @py4cytoscape.print_entry_exit
    def test_export_image(self):
        # Initialization
        load_test_session()
        py4cytoscape.fit_content()

        # Verify that LOD can be changed
        res = py4cytoscape.toggle_graphics_details()
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {'message': 'Toggled Graphics level of details.'})
        input('Verify that level of detail has changed')

        # Verify that LOD can be changed back
        res = py4cytoscape.toggle_graphics_details()
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {'message': 'Toggled Graphics level of details.'})
        input('Verify that level of detail has changed back')


if __name__ == '__main__':
    unittest.main()
