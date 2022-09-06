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
import filecmp
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

    @print_entry_exit
    def test_export_image_3_10(self):
        # Initialization
        load_test_session("data/Yeast Gene Interactions.cys")
        gal_filtered_view = get_network_view_suid()
        gal_filtered_suid = get_network_suid()

        def check_export(export_res, expected_file_name, default_file, expected_comparison, compare_resolution=1):
            self.assertIsInstance(export_res, dict)
            self.assertIn('file', export_res)
            self.assertIsInstance(export_res['file'], str)
            self.assertIsNotNone(export_res['file'])
            file_name = export_res['file']
            self.assertTrue(file_name.endswith(expected_file_name), 'File name comparison')
            export_file_len = int(pathlib.Path(default_file).stat().st_size / compare_resolution)
            expected_file_len = int(pathlib.Path(file_name).stat().st_size / compare_resolution)
            self.assertEqual(export_file_len == expected_file_len, expected_comparison, 'File size comparison')

        def df(filename, type=None):
            type = f'.{type}' if type else ''
            fname = pathlib.Path(filename + type)
            if fname.exists(): fname.unlink()
            return filename

        if check_supported_versions(1, "3.10"):
            # This is pre-3.10 ... make sure 3.10-style parameters are rejected
            self.assertRaises(CyError, export_image, 'bogus image', type='JPEG', hide_labels=True)
            self.assertRaises(CyError, export_image, 'bogus image', type='JPEG', all_graphics_details=True)
            self.assertRaises(CyError, export_image, 'bogus image', type='JPEG', transparent_background=True)
            self.assertRaises(CyError, export_image, 'bogus image', type='JPEG', export_text_as_font=True)
            self.assertRaises(CyError, export_image, 'bogus image', type='JPEG', orientation='Portrait')
            self.assertRaises(CyError, export_image, 'bogus image', type='JPEG', page_size='Letter')
            return

        # Create the .JPEG that uses only default parameter values
        check_export(export_image(df('output/test default JPG', 'jpeg'), type='JPEG'), 'test default JPG.jpeg', 'output/test default JPG.jpeg', True)

        # Create the .JPEG that explicitly uses all parameters with their default values ... result should be the same
        check_export(export_image(df('output/test default JPG copy', 'jpeg'), type='JPEG', hide_labels=False, all_graphics_details=True, zoom=100),
                     'test default JPG copy.jpeg', 'output/test default JPG.jpeg', True)

        # Create .JPEGs that test each individual option ... should all be different from original .JPEG
        check_export(export_image(df('output/test default JPG hide_labels', 'jpeg'), type='JPEG', hide_labels=True),
                     'test default JPG hide_labels.jpeg', 'output/test default JPG.jpeg', False)
        check_export(export_image(df('output/test default JPG all_graphics_details', 'jpeg'), type='JPEG', all_graphics_details=False),
                     'test default JPG all_graphics_details.jpeg', 'output/test default JPG.jpeg', False)
        check_export(export_image(df('output/test default JPG zoom', 'jpeg'), type='JPEG', zoom=200),
                     'test default JPG zoom.jpeg', 'output/test default JPG.jpeg', False)

        # Create the PDF. that uses only default parameter values
        check_export(export_image(df('output/test default PDF', 'pdf'), type='PDF'), 'test default PDF.pdf', 'output/test default PDF.pdf', True)

        # Create the .JPEG that explicitly uses all parameters with their default values ... result should be the same
        check_export(export_image(df('output/test default PDF copy', 'pdf'), type='PDF', export_text_as_font=True, hide_labels=False, orientation='Portrait', page_size='Letter'),
                     'test default PDF copy.pdf', 'output/test default PDF.pdf', True)

        # Create .PDFs that test each individual option ... should all be different from original .PDF
        check_export(export_image(df('output/test export_text_as_font PDF', 'pdf'), type='PDF', export_text_as_font=False),
                     'test export_text_as_font PDF.pdf', 'output/test default PDF.pdf', False)
        check_export(export_image(df('output/test hide_labels PDF', 'pdf'), type='PDF', hide_labels=True),
                     'test hide_labels PDF.pdf', 'output/test default PDF.pdf', False)
        check_export(export_image(df('output/test orientation PDF', 'pdf'), type='PDF', orientation='Landscape'),
                     'test orientation PDF.pdf', 'output/test default PDF.pdf', False)
        check_export(export_image(df('output/test page_size PDF', 'pdf'), type='PDF', page_size='A4'),
                     'test page_size PDF.pdf', 'output/test default PDF.pdf', False)

        # Create the PNG. that uses only default parameter values
        check_export(export_image(df('output/test default PNG', 'png'), type='PNG'), 'test default PNG.png', 'output/test default PNG.png', True)

        # Create the .PNG that explicitly uses all parameters with their default values ... result should be the same
        check_export(export_image(df('output/test default PNG copy', 'png'), type='PNG', all_graphics_details=True, hide_labels=False, transparent_background=False, zoom=100),
                     'test default PNG copy.png', 'output/test default PNG.png', True)

        # Create .PNGs that test each individual option ... should all be different from original .PNG
        check_export(export_image(df('output/test all_graphics_details PNG', 'png'), type='PNG', all_graphics_details=False),
                     'test all_graphics_details PNG.png', 'output/test default PNG.png', False)
        check_export(export_image(df('output/test hide_labels PNG', 'png'), type='PNG', hide_labels=True),
                     'test hide_labels PNG.png', 'output/test default PNG.png', False)
        check_export(export_image(df('output/test transparent_background PNG', 'png'), type='PNG', transparent_background=True),
                     'test transparent_background PNG.png', 'output/test default PNG.png', False)
        check_export(export_image(df('output/test zoom PNG', 'png'), type='PNG', zoom=200),
                     'test zoom PNG.png', 'output/test default PNG.png', False)

        # Create the PS. that uses only default parameter values
        check_export(export_image(df('output/test default PS', 'ps'), type='PS'), 'test default PS.ps', 'output/test default PS.ps', True)

        # Create the .PS that explicitly uses all parameters with their default values ... result should be the same
        check_export(export_image(df('output/test default PS copy', 'ps'), type='PS', export_text_as_font=True, hide_labels=False),
                     'test default PS copy.ps', 'output/test default PS.ps', True, 1024)

        # Create .PSs that test each individual option ... should all be different from original .PS
        check_export(export_image(df('output/test export_text_as_font PS', 'ps'), type='PS', export_text_as_font=False),
                     'test export_text_as_font PS.ps', 'output/test default PS.ps', False, 1024)
        check_export(export_image(df('output/test hide_labels PS', 'ps'), type='PS', hide_labels=True),
                     'test hide_labels PS.ps', 'output/test default PS.ps', False, 1024)

        # Create the SVG. that uses only default parameter values
        check_export(export_image(df('output/test default SVG', 'svg'), type='SVG'), 'test default SVG.svg', 'output/test default SVG.svg', True)

        # Create the .SVG that explicitly uses all parameters with their default values ... result should be the same
        check_export(export_image(df('output/test default SVG copy', 'svg'), type='SVG', export_text_as_font=True, hide_labels=False),
                     'test default SVG copy.svg', 'output/test default SVG.svg', True)

        # # Create .SVGs that test each individual option ... should all be different from original .SVG
        check_export(export_image(df('output/test export_text_as_font SVG', 'svg'), type='SVG', export_text_as_font=False),
                     'test export_text_as_font SVG.svg', 'output/test default SVG.svg', False)
        check_export(export_image(df('output/test hide_labels SVG', 'svg'), type='SVG', hide_labels=True),
                     'test hide_labels SVG.svg', 'output/test default SVG.svg', False)

        # Verify that each file type is recognized and mapped to the proper file suffix
        check_export(export_image(df('output/test JPG', 'jpg'), type='JPG'), 'test JPG.jpg', 'output/test JPG.jpg', True)
        check_export(export_image(df('output/test JPEG', 'jpeg'), type='JPEG'), 'test JPEG.jpeg', 'output/test JPG.jpg', True)
        check_export(export_image(df('output/test JPG+', 'jpg'), type='jpeg (*.jpeg, *.jpg)'), 'test JPG+.jpg', 'output/test JPG.jpg', True)

        check_export(export_image(df('output/test PDF', 'pdf'), type='PDF'), 'test PDF.pdf', 'output/test PDF.pdf', True)
        check_export(export_image(df('output/test PDF+', 'pdf'), type='pdf (*.pdf)'), 'test PDF+.pdf', 'output/test PDF.pdf', True)

        check_export(export_image(df('output/test PNG', 'png'), type='PNG'), 'test PNG.png', 'output/test PNG.png', True)
        check_export(export_image(df('output/test PNG+', 'png'), type='png (*.png)'), 'test PNG+.png', 'output/test PNG.png', True)

        check_export(export_image(df('output/test PS', 'ps'), type='PS'), 'test PS.ps', 'output/test PS.ps', True)
        check_export(export_image(df('output/test PS+', 'ps'), type='postscript (*.ps)'), 'test PS+.ps', 'output/test PS.ps', True, 1024)

        check_export(export_image(df('output/test SVG', 'svg'), type='SVG'), 'test SVG.svg', 'output/test SVG.svg', True)
        check_export(export_image(df('output/test SVG+', 'svg'), type='svg (*.svg)'), 'test SVG+.svg', 'output/test SVG.svg', True)

        # Verify that a bad file type gets bounced
        self.assertRaises(CyError, export_image, 'bogus name', type='Bogus type')

        # Verify that the overwrite parameter doesn't stop a fresh file from being written
        check_export(export_image(df('output/overtest', 'png'), overwrite_file=True), 'overtest.png', 'output/overtest.png', True)

        # Verify that not using the overwrite parameter on an existing file fails
        self.assertRaises(CyError, export_image, 'output/overtest', overwrite_file=False)
        self.assertRaises(CyError, export_image, 'output/overtest', 'png')

        # Verify that using the overwrite parameter on an existin file succeeds
        check_export(export_image('output/overtest', overwrite_file=True), 'overtest.png', 'output/overtest.png', True)



    @unittest.skipIf(skip_for_ui(), 'Avoiding test that requires user response')
    @print_entry_exit
    def test_export_image(self):
        # Initialization
        load_test_session()
        gal_filtered_view = get_network_view_suid()
        gal_filtered_suid = get_network_suid()

        def check_export(export_res):
            self.assertIsInstance(export_res, dict)
            self.assertIn('file', export_res)
            self.assertIsInstance(export_res['file'], str)
            self.assertIsNotNone(export_res['file'])

        def df(filename, type=None):
            type = f'.{type}' if type else ''
            fname = pathlib.Path(filename + type)
            if fname.exists(): fname.unlink()
            return filename

        check_export(
          export_image(df('output/test units-pixels height-1000 width-2000 zoom-200', 'jpeg'), type='JPEG', units='pixels',
                       height=1000, width=2000, zoom=200, network=None))
        check_export(export_image(df('output/test', 'pdf'), type='PDF', network=None))
        check_export(export_image(df('output/test res-600 units-inches height-1.7 width-3.5 zoom-500', 'png'), type='PNG',
                                  resolution=600, units='inches', height=1.7, width=3.5, zoom=500,
                                  network=gal_filtered_view))
        check_export(export_image(df('output/test', 'svg'), type='SVG', network=gal_filtered_view))
        check_export(export_image(df('output/test', 'ps'), type='PS', network=gal_filtered_suid))
        check_export(export_image(df('output/test alldefault', 'png'), type='PNG', resolution=None, units=None, height=None,
                                  width=None, zoom=None, network=gal_filtered_suid))
        check_export(export_image(df('output/test alldefault same', 'png'), type='PNG',
                                  network=gal_filtered_suid))
        self.assertTrue(filecmp.cmp('output/test alldefault.png', 'output/test alldefault same.png'),
                        'test alldefault.png files differ')

        input('Verify the export output files in the ./output folder by sight')

        # Verify that the default overwrite behavior is to ask the user first, and no overwrite if decline
        fname = pathlib.Path('output/test.pdf')
        original_stat = fname.stat()
        input('Verify that Cytoscape gives a popup asking for permission to overwrite -- DECLINE permission')
        self.assertRaises(CyError, export_image, 'output/test', type='PDF', network=None, force_pre_3_10=True)
        self.assertEqual(original_stat, fname.stat())

        # Verify that the default overwrite behavior is to ask user first, and overwrite occurs if accept
        input('Verify that Cytoscape gives a popup asking for permission to overwrite -- ACCEPT permission')
        check_export(export_image('output/test', type='PDF', network=None, force_pre_3_10=True))
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
