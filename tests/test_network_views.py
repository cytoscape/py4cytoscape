# -*- coding: utf-8 -*-

""" Test functions in network_views.py.
"""

"""License:
    Copyright 2020-2022 The Cytoscape Consortium

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
import pathlib
from test_utils import *


class NetworkViewsTests(unittest.TestCase):
    def setUp(self):
        try:
            close_session(False)
#            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    @print_entry_exit
    def test_get_network_views(self):
        # Initialization
        load_test_session()

        # Verify that the view list for galFiltered looks right
        gal_filtered_view_suid = self._check_view_list(get_network_views())

        # Verify that the view list for a different network looks right
        yeast_suid, yeast_view_suid = load_test_network('data/yeastHighQuality.sif', make_current=False)
        check_view_suid = self._check_view_list(get_network_views(network=yeast_suid))
        self.assertEqual(yeast_view_suid, check_view_suid)
        self.assertNotEqual(gal_filtered_view_suid, yeast_view_suid)

        # Verify that the view list for the original network is unchanged
        self.assertEqual(self._check_view_list(get_network_views('galFiltered.sif')), gal_filtered_view_suid)

        self.assertRaises(CyError, get_network_views, 'bogus network')

    @print_entry_exit
    def test_create_view(self):

        def verify_layout(net_suid, expected_empty=False):
            self._check_view_list(get_network_views(network=net_suid))

            node_positions = get_node_position(all_nodes, network=net_suid)
            laid_out_nodes = node_positions.loc[(node_positions['x'] != 0) & (node_positions['y'] != 0)]
            self.assertEqual(len(laid_out_nodes.index) == 0, expected_empty)

        # Initialization
        load_test_session()
        all_nodes = get_all_nodes()
        yeast_suid, yeast_view_suid = load_test_network('data/yeastHighQuality.sif', make_current=False)
        self._delete_view(yeast_suid)

        # Get SUIDs for galFiltered network and verify there is a view
        net_suid = get_network_suid()
        self._check_view_list(get_network_views())

        # Verify that creating a view without a layout leaves all nodes at (0, 0)
        self._delete_view(net_suid)
        gal_filtered_view_suid = create_view(layout=False)
        verify_layout(net_suid, True)

        # Verify that creating a view where one already exists just returns the existing view
        self.assertEqual(gal_filtered_view_suid, create_view())

        # Create a new view and do a layout, then verify that some nodes shift position
        self._delete_view(net_suid)
        gal_filtered_view_suid = create_view()
        verify_layout(net_suid, False)

        # Verify that creating galFiltered views hasn't added views to yeastHighQuality
        self._check_view_list(get_network_views(network=yeast_suid), 0)

        # Verify that creating a view in one network doesn't affect another network
        self._delete_view(net_suid) # Both networks should have no views
        create_view(network=yeast_suid)
        self._check_view_list(get_network_views(network=yeast_suid), 1)
        self._check_view_list(get_network_views(network=net_suid), 0)

        self.assertRaises(CyError, create_view, network='bogus network')

    @print_entry_exit
    def test_get_network_view_suid(self):
        # Initialization
        load_test_session()
        net_suid = get_network_suid()

        def check_view(view_suid):
            self.assertIsInstance(view_suid, int)
            return view_suid

        # Verify that the view list for galFiltered looks right regardless of how the network is accessed
        gal_filtered_view_suid = check_view(get_network_view_suid())
        self.assertEqual(get_network_view_suid(network=net_suid), gal_filtered_view_suid)
        self.assertEqual(get_network_view_suid(network='galFiltered.sif'), gal_filtered_view_suid)
        self.assertEqual(get_network_view_suid(network='current'), gal_filtered_view_suid)
        self.assertEqual(get_network_view_suid(network=gal_filtered_view_suid), gal_filtered_view_suid)

        # Verify that the view suid for a different network looks right ... identify network by suid
        yeast_suid, yeast_view_suid = load_test_network('data/yeastHighQuality.sif', make_current=False)
        check_view_suid = check_view(get_network_view_suid(network=yeast_suid))
        self.assertEqual(yeast_view_suid, check_view_suid)
        self.assertNotEqual(gal_filtered_view_suid, yeast_view_suid)

        # Verify that the view list for the original network is unchanged ... identify network by string
        self.assertEqual(check_view(get_network_view_suid('galFiltered.sif')), gal_filtered_view_suid)

        # Delete view and make sure that None is returned for network view
        self._delete_view(net_suid)
        self.assertIsNone(get_network_view_suid())
        self.assertIsNone(get_network_view_suid(network=net_suid))
        self.assertIsNone(get_network_view_suid(network='galFiltered.sif'))
        self.assertIsNone(get_network_view_suid(network='current'))
        self.assertRaises(CyError, get_network_view_suid, gal_filtered_view_suid)

        self.assertRaises(CyError, get_network_view_suid, 'bogus network')
        self.assertRaises(CyError, get_network_view_suid, -1)


    @unittest.skipIf(skip_for_ui(), 'Avoiding test that requires user response')
    @print_entry_exit
    def test_fit_content(self):
        # Initialization
        load_test_session()
        yeast_suid, yeast_view_suid = load_test_network('data/yeastHighQuality.sif', make_current=False)

        # Verify that entire network gets fit into view window
        fit_res = fit_content(selected_only=False)
        self.assertIsInstance(fit_res, dict)
        self.assertDictEqual(fit_res, {})
        input('Verify that entire galFiltered.sif network is fit to view window')

        # Verify that the selected nodes fit into view window
        select_nodes(nodes=['RAP1'], by_col='COMMON')
        select_first_neighbors()
        time.sleep(5)
        fit_res = fit_content(selected_only=True)
        self.assertIsInstance(fit_res, dict)
        self.assertDictEqual(fit_res, {})
        input('Verify that selected nodes in galFiltered.sif network are fit to view window')

        # Verify that the selected nodes of a different network fit into the view window ... identify network by view
        select_nodes(['SIK1', 'PGK1'], by_col='COMMON', network=yeast_suid)
        fit_res = fit_content(selected_only=True, network=yeast_view_suid)
        self.assertIsInstance(fit_res, dict)
        self.assertDictEqual(fit_res, {})
        input('Verify that selected nodes in yeastHighQuality.sif network are fit to view window')

        self.assertRaises(CyError, fit_content, network='bogus network')


    @print_entry_exit
    def test_set_current_view(self):
        # Initialization
        load_test_session()
        gal_filtered_view = get_network_view_suid()
        yeast_suid, yeast_view_suid = load_test_network('data/yeastHighQuality.sif', make_current=False)

        # Set the view for galFiltered by passing in network SUID
        res = set_current_view(network=get_network_suid('galFiltered.sif'))
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {})

        # Set the view for yeastHighQuality by passing in view
        res = set_current_view(network=yeast_view_suid)
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {})

        # Verify that both views seem to be set
        self.assertEqual(get_network_view_suid(network='galFiltered.sif'), gal_filtered_view)
        self.assertEqual(get_network_view_suid(network=yeast_suid), yeast_view_suid)

        self.assertRaises(CyError, set_current_network, network='bogus network')


    @unittest.skipIf(skip_for_ui(), 'Avoiding test that requires user response')
    @print_entry_exit
    def test_export_image(self):
        # Initialization
        load_test_session()
        gal_filtered_view = get_network_view_suid()
        gal_filtered_suid = get_network_suid()

        def check_export(export_res):
            self.assertIsInstance(export_res, dict)
            self.assertIsInstance(export_res['file'], str)
            self.assertIsNotNone(export_res['file'])

        def delete_first(filename, type=None):
            type = f'.{type}' if type else ''
            fname = pathlib.Path(filename + type)
            if fname.exists(): fname.unlink()
            return filename

        check_export(
          export_image(delete_first('output/test units-pixels height-1000 width-2000 zoom-500', 'jpeg'), type='JPEG', units='pixels',
                                    height=1000, width=2000, zoom=200, network=None))
        check_export(export_image(delete_first('output/test', 'pdf'), type='PDF', network=None))
        check_export(export_image(delete_first('output/test res-600 units-inches height-1.7 width-3.5 zoom-500', 'png'), type='PNG',
                                               resolution=600, units='inches', height=1.7, width=3.5, zoom=500,
                                               network=gal_filtered_view))
        check_export(export_image(delete_first('output/test', 'svg'), type='SVG', network=gal_filtered_view))
        check_export(export_image(delete_first('output/test', 'ps'), type='PS', network=gal_filtered_suid))
        check_export(export_image(delete_first('output/test alldefault', 'png'), type='PNG', resolution=None, units=None, height=None,
                                               width=None, zoom=None, network=gal_filtered_suid))

        input('Verify the export output files in the ./output folder by sight')

        # Verify that the default overwrite behavior is to ask the user first, and no overwrite if decline
        fname = pathlib.Path('output/test.pdf')
        original_stat = fname.stat()
        input('Verify that Cytoscape gives a popup asking for permission to overwrite -- DECLINE permission')
        self.assertRaises(CyError, export_image, 'output/test', type='PDF', network=None)
        self.assertEqual(original_stat, fname.stat())

        # Verify that the default overwrite behavior is to ask user first, and overwrite occurs if accept
        input('Verify that Cytoscape gives a popup asking for permission to overwrite -- ACCEPT permission')
        check_export(export_image('output/test', type='PDF', network=None))
        replaced_stat = fname.stat()
        self.assertNotEqual(original_stat, replaced_stat)

        # Verify that when default overwrite behavior is overridden, overwrite occurs
        check_export(export_image('output/test', type='PDF', network=None, overwrite_file=True))
        self.assertNotEqual(replaced_stat, fname.stat())

        # Verify that an unknown network is caught
        self.assertRaises(CyError, export_image, network='bogus')


    @unittest.skipIf(skip_for_ui(), 'Avoiding test that requires user response')
    @print_entry_exit
    def test_level_of_detail(self):
        # Initialization
        load_test_session()
        fit_content()

        # Verify that LOD can be changed
        res = toggle_graphics_details()
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {'message': 'Toggled Graphics level of details.'})
        input('Verify that level of detail has changed')

        # Verify that LOD can be changed back
        res = toggle_graphics_details()
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {'message': 'Toggled Graphics level of details.'})
        input('Verify that level of detail has changed back')

    def _check_view_list(self, view_list, expected_length=1):
        self.assertIsInstance(view_list, list)
        self.assertEqual(len(view_list), expected_length)
        return view_list[0] if expected_length > 0 else None

    def _delete_view(self, net_suid):
        cyrest_delete(f'networks/{net_suid}/views', require_json=False)
        self._check_view_list(get_network_views(network=net_suid), 0)




if __name__ == '__main__':
    unittest.main()
