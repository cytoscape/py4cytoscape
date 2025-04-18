# -*- coding: utf-8 -*-

""" Test functions in annotations.py.
"""
import os.path

"""License:
    Copyright 2022 The Cytoscape Consortium

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

from test_utils import *


class AppsTests(unittest.TestCase):
    def setUp(self):
        try:
            close_session(False)
        #            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    _EXPECTED_TEXT_KEYS = {'canvas', 'color', 'rotation', 'type', 'fontStyle', 'uuid', 'fontFamily', 'name', 'x', 'y',
                           'z', 'fontSize', 'text'}

    _TEST_HTTP_URL = 'http://www.ucsd.edu/_resources/img/logo_UCSD.png'
    _TEST_HTTPS_URL = 'https://www.ucsd.edu/_resources/img/logo_UCSD.png'
    _TEST_FILE = 'data/annotation_image_1.jpg'


    @print_entry_exit
    def test_get_annotation_list(self):

        def find_name(name, annotation):
            for ann in annotation:
                if ann['name'] == name:
                    return ann
            raise Exception(f'Could not find annotation with name "{name}" in {annotation}')

        # Initialize
        gal_filtered_suid, yeast_high_quality_suid = self._load_2_networks()

        # Verify that the current network (presumably gal_filtered) has no annotations
        res = get_annotation_list()
        self._check_annotation_list(res, 0, self._EXPECTED_TEXT_KEYS)

        # Create an annotation in current network (gal_filtered) and verify that the annotation is returned in the list
        add_annotation_text(name='ann1', text='ann1 text')
        res = get_annotation_list()
        self._check_annotation_list(res, 1, self._EXPECTED_TEXT_KEYS)
        ann1 = find_name('ann1', res)
        self.assertEqual(ann1['text'], 'ann1 text')

        # Verify that the annotation is present if gal_filtered is queried
        res = get_annotation_list(gal_filtered_suid)
        self._check_annotation_list(res, 1, self._EXPECTED_TEXT_KEYS)
        ann1 = find_name('ann1', res)
        self.assertEqual(ann1['text'], 'ann1 text')

        # Verify that no annotations are in yeast_high_quality
        res = get_annotation_list(yeast_high_quality_suid)
        self._check_annotation_list(res, 0, self._EXPECTED_TEXT_KEYS)

        # Verify that if two annotations are added to yeast_high_quality, they can be fetched
        add_annotation_text(network=yeast_high_quality_suid, name='ann10', text='ann10 text')
        add_annotation_text(network=yeast_high_quality_suid, name='ann11', text='ann11 text')
        res = get_annotation_list(yeast_high_quality_suid)
        self._check_annotation_list(res, 2, self._EXPECTED_TEXT_KEYS)
        ann10 = find_name('ann10', res)
        ann11 = find_name('ann11', res)
        self.assertEqual(ann10['text'], 'ann10 text')
        self.assertEqual(ann11['text'], 'ann11 text')

        # Verify that the single annotation is still present if gal_filtered is queried
        res = get_annotation_list(gal_filtered_suid)
        self._check_annotation_list(res, 1, self._EXPECTED_TEXT_KEYS)
        ann1 = find_name('ann1', res)
        self.assertEqual(ann1['text'], 'ann1 text')

        # Verify that an unknown app is caught
        self.assertRaises(CyError, get_annotation_list, 'bogus')

    @print_entry_exit
    def test_add_annotation_text(self):
        # Initialize
        gal_filtered_suid, yeast_high_quality_suid = self._load_2_networks()

        # Verify that adding a minimal annotation to the current network works
        res = add_annotation_text(text='ann1')
        res1 = get_annotation_list(network=gal_filtered_suid)
        self._check_annotation_list(res1, 1, self._EXPECTED_TEXT_KEYS)
        self.assertDictEqual(res, res1[0])

        # Verify that adding a second annotation (explicitly naming the network) also works
        res = add_annotation_text(network=gal_filtered_suid, text='ann2')
        res1 = get_annotation_list(network=gal_filtered_suid)
        self._check_annotation_list(res1, 2, self._EXPECTED_TEXT_KEYS)

        # Verify that nothing was added to the other network
        self._check_annotation_list(get_annotation_list(network=yeast_high_quality_suid), 0, self._EXPECTED_TEXT_KEYS)

        # Verify that supplying additional parameters is reflected in an annotation
        res = add_annotation_text(text='ann3', x_pos=100, y_pos=200, font_size=25, font_family='Courier New',
                                  font_style='bold', color='#F0F0F0', angle=45, name='ann3 name', canvas='background')
        self._check_expected_values(res, {'canvas': 'background', 'color': '#F0F0F0', 'rotation': '45.0',
                                          'fontStyle': 'bold', 'fontFamily': 'Courier New', 'name': 'ann3 name',
                                          'x': '100.0', 'y': '200.0', 'fontSize': '25', 'text': 'ann3'})

        # Verify that supplying color name is reflected in an annotation
        res = add_annotation_text(text='ann4', x_pos=100, y_pos=200, font_size=25, font_family='Courier New',
                                  font_style='bold', color='pink', angle=45, name='ann4 name', canvas='background')
        self._check_expected_values(res, {'canvas': 'background', 'color': '#FFC0CB', 'rotation': '45.0',
                                          'fontStyle': 'bold', 'fontFamily': 'Courier New', 'name': 'ann4 name',
                                          'x': '100.0', 'y': '200.0', 'fontSize': '25', 'text': 'ann4'})

        # Verify that angle is properly normalized
        res = add_annotation_text(text='angle 181', angle=181)
        self.assertEqual(res['rotation'], '-179.0')
        res = add_annotation_text(text='angle 180', angle=180)
        self.assertEqual(res['rotation'], '180.0')
        res = add_annotation_text(text='angle -180', angle=-180)
        self.assertEqual(res['rotation'], '-180.0')
        res = add_annotation_text(text='angle -181', angle=-181)
        self.assertEqual(res['rotation'], '179.0')
        res = add_annotation_text(text='angle 1980', angle=1980)
        self.assertEqual(res['rotation'], '180.0')
        res = add_annotation_text(text='angle -1980', angle=-1980)
        self.assertEqual(res['rotation'], '-180.0')

        # Verify that missing name is detected
        self.assertRaises(CyError, add_annotation_text)

        # Verify that bad font size is detected
        self.assertRaises(CyError, add_annotation_text, text='bad', font_size='bogus')
        self.assertRaises(CyError, add_annotation_text, text='bad', font_size=0)

        # Verify that bad font style is detected
        self.assertRaises(CyError, add_annotation_text, text='bad', font_style='bogus')

        # Verify that bad color is detected
        self.assertRaises(CyError, add_annotation_text, text='bad', color='bogus')

        # Verify that bad canvas is detected
        self.assertRaises(CyError, add_annotation_text, text='bad', canvas='bogus')

        # Verify that bad z-order is detected
        self.assertRaises(CyError, add_annotation_text, text='bad', z_order='bogus')

    @print_entry_exit
    def test_add_annotation_bounded_text(self):
        EXPECTED_BOUNDED_TEXT_KEYS = {'edgeThickness', 'canvas', 'fillOpacity', 'color', 'rotation', 'type',
                                      'fontStyle',
                                      'uuid', 'shapeType', 'edgeColor', 'fontFamily', 'edgeOpacity', 'name', 'x',
                                      'width',
                                      'y', 'z', 'fontSize', 'text', 'height'}
        EXPECTED_BOUNDED_ELLIPSE_VALS = {'edgeThickness': '2.0', 'canvas': 'background', 'fillOpacity': '50.0',
                                         'color': '#FFC0CB', 'rotation': '45.0', 'fontStyle': 'bold',
                                         'fillColor': '#008000', 'shapeType': 'ELLIPSE', 'edgeColor': '#800080',
                                         'fontFamily': 'Courier New', 'edgeOpacity': '75.0', 'name': 'ann3 name',
                                         'x': '100.0', 'width': '31.0', 'y': '200.0', 'z': '0', 'fontSize': '25',
                                         'text': 'ann3', 'height': '30.0'}
        # Initialize
        gal_filtered_suid, yeast_high_quality_suid = self._load_2_networks()

        # Verify that adding a minimal annotation to the current network works
        res = add_annotation_bounded_text(text='ann1')
        res1 = get_annotation_list(network=gal_filtered_suid)
        self._check_annotation_list(res1, 1, EXPECTED_BOUNDED_TEXT_KEYS)
        self.assertDictEqual(res, res1[0])

        # Verify that adding a second annotation (explicitly naming the network) also works
        res = add_annotation_bounded_text(network=gal_filtered_suid, text='ann2')
        res1 = get_annotation_list(network=gal_filtered_suid)
        self._check_annotation_list(res1, 2, EXPECTED_BOUNDED_TEXT_KEYS)

        # Verify that nothing was added to the other network
        self._check_annotation_list(get_annotation_list(network=yeast_high_quality_suid), 0, EXPECTED_BOUNDED_TEXT_KEYS)

        # Verify that supplying additional parameters is reflected in an annotation
        res = add_annotation_bounded_text(text='ann3', x_pos=100, y_pos=200, font_size=25, font_family='Courier New',
                                          font_style='bold', color='#ffc0cb', angle=45, type='ELLIPSE',
                                          custom_shape=None, fill_color='#008000', opacity=50, border_thickness=2,
                                          border_color='#800080', border_opacity=75, height=30, width=31,
                                          name='ann3 name', canvas='background')
        self._check_expected_values(res, EXPECTED_BOUNDED_ELLIPSE_VALS)

        # Verify that color names are reflected in an annotation
        delete_annotation('ann3 name')
        res = add_annotation_bounded_text(text='ann3', x_pos=100, y_pos=200, font_size=25, font_family='Courier New',
                                          font_style='bold', color='pink', angle=45, type='ELLIPSE',
                                          custom_shape=None, fill_color='green', opacity=50, border_thickness=2,
                                          border_color='purple', border_opacity=75, height=30, width=31,
                                          name='ann3 name', canvas='background')
        self._check_expected_values(res, EXPECTED_BOUNDED_ELLIPSE_VALS)

        # Verify that types are translated as expected
        res = add_annotation_bounded_text('ann5a', type='ROUND_RECTANGLE')
        self.assertEqual(res['shapeType'], 'ROUNDEDRECTANGLE')
        res = add_annotation_bounded_text('ann5b', type='VEE')
        self.assertEqual(res['shapeType'], 'V')

        # TODO: Figure out how to test custom_shape parameter
        res = add_annotation_bounded_text('ann5c', custom_shape='33.png')

        # Verify that angle is properly normalized
        res = add_annotation_bounded_text(text='angle 181', angle=181)
        self.assertEqual(res['rotation'], '-179.0')
        res = add_annotation_bounded_text(text='angle 180', angle=180)
        self.assertEqual(res['rotation'], '180.0')
        res = add_annotation_bounded_text(text='angle -180', angle=-180)
        self.assertEqual(res['rotation'], '-180.0')
        res = add_annotation_bounded_text(text='angle -181', angle=-181)
        self.assertEqual(res['rotation'], '179.0')
        res = add_annotation_bounded_text(text='angle 1980', angle=1980)
        self.assertEqual(res['rotation'], '180.0')
        res = add_annotation_bounded_text(text='angle -1980', angle=-1980)
        self.assertEqual(res['rotation'], '-180.0')

        # Verify that missing name is detected
        self.assertRaises(CyError, add_annotation_bounded_text)

        # Verify that bad font size is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', font_size='bogus')
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', font_size=0)

        # Verify that bad font style is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', font_style='bogus')

        # Verify that bad color is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', color='bogus')

        # Verify that bad type is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', type='bogus shape')

        # Verify that bad fill color is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', fill_color='bogus')

        # Verify that bad opacity is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', opacity='bad')
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', opacity=-1)
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', opacity=101)

        # Verify that bad border thickness is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', border_thickness='bad')
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', border_thickness=-1)

        # Verify that bad border color is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', border_color='bogus')

        # Verify that bad border opacity is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', border_opacity='bad')
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', border_opacity=-1)
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', border_opacity=101)

        # Verify that bad height is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', height='bad')
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', height=0)

        # Verify that bad width is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', width='bad')
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', width=0)

        # Verify that bad canvas is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', canvas='bogus')

        # Verify that bad z-order is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', z_order='bogus')

    @print_entry_exit
    def test_add_annotation_image(self):
        EXPECTED_IMAGE_KEYS = {'edgeThickness', 'canvas', 'rotation', 'type', 'uuid', 'shapeType', 'edgeColor',
                               'brightness', 'edgeOpacity', 'contrast', 'name', 'x', 'width', 'y', 'z', 'opacity',
                               'height'}
        EXPECTED_IMAGE_VALS = {'edgeThickness': '2.0', 'canvas': 'background', 'rotation': '45.0',
                               'type': 'org.cytoscape.view.presentation.annotations.ImageAnnotation',
                               'shapeType': 'RECTANGLE', 'edgeColor': '#FFC0CB', 'brightness': '60',
                               'edgeOpacity': '75.0', 'contrast': '70', 'x': '100.0',
                               'width': '31.0', 'y': '200.0', 'opacity': '0.5', 'height': '30.0'}

        # Initialize
        gal_filtered_suid, yeast_high_quality_suid = self._load_2_networks()

        # Verify that adding a minimal annotation to the current network works
        res = add_annotation_image(url=self._TEST_HTTPS_URL)
        res1 = get_annotation_list(network=gal_filtered_suid)
        self._check_annotation_list(res1, 1, EXPECTED_IMAGE_KEYS)
        self.assertDictEqual(res, res1[0])

        # Verify that adding a second annotation (explicitly naming the network) also works
        res = add_annotation_image(network=gal_filtered_suid, url=self._TEST_HTTPS_URL)
        res1 = get_annotation_list(network=gal_filtered_suid)
        self._check_annotation_list(res1, 2, EXPECTED_IMAGE_KEYS)

        # All variations of local file names should produce images, too
        res = add_annotation_image(network=gal_filtered_suid, url=self._TEST_FILE)
        local_file_with_scheme = res['URL']
        self.assertTrue(local_file_with_scheme.startswith('file:/'))
        res = add_annotation_image(network=gal_filtered_suid, url=local_file_with_scheme)
        local_file_no_schema = local_file_with_scheme[6:] # get rid of file:/
        res = add_annotation_image(network=gal_filtered_suid, url=local_file_no_schema)

        # Verify that nothing was added to the other network
        self._check_annotation_list(get_annotation_list(network=yeast_high_quality_suid), 0, EXPECTED_IMAGE_KEYS)

        # Verify that supplying additional parameters is reflected in an annotation, using both HTTP and HTTPS
        res = add_annotation_image(url=self._TEST_HTTPS_URL, x_pos=100, y_pos=200, angle=45, opacity=50,
                                   brightness=60, contrast=70, border_thickness=2, border_color='#FFC0CB',
                                   border_opacity=75, height=30, width=31, name='ann3 name', canvas='background')
        self._check_expected_values(res, {**EXPECTED_IMAGE_VALS, **{'URL': self._TEST_HTTPS_URL, 'name': 'ann3 name'}})
        res = add_annotation_image(url=self._TEST_HTTP_URL, x_pos=100, y_pos=200, angle=45, opacity=50,
                                   brightness=60, contrast=70, border_thickness=2, border_color='#FFC0CB',
                                   border_opacity=75, height=30, width=31, name='ann3a name', canvas='background')
        self._check_expected_values(res, {**EXPECTED_IMAGE_VALS, **{'URL': self._TEST_HTTP_URL, 'name': 'ann3a name'}})
        res = add_annotation_image(url=self._TEST_HTTP_URL, x_pos=100, y_pos=200, angle=45, opacity=50,
                                   brightness=60, contrast=70, border_thickness=2, border_color='pink',
                                   border_opacity=75, height=30, width=31, name='ann3b name', canvas='background')
        self._check_expected_values(res, {**EXPECTED_IMAGE_VALS, **{'URL': self._TEST_HTTP_URL, 'name': 'ann3b name'}})

        # Verify that supplying additional parameters is reflected in an annotation
        res = add_annotation_image(url=self._TEST_FILE, x_pos=100, y_pos=200, angle=45, opacity=50,
                                   brightness=60, contrast=70, border_thickness=2, border_color='#FFC0CB',
                                   border_opacity=75, height=30, width=31, name='ann4 name', canvas='background')
        # TODO: Re-enable this check after CSD-675 is fixed
        # self._check_expected_values(res, {**EXPECTED_IMAGE_VALS, **{'URL': self._TEST_FILE, 'name': 'ann4 image'}})

        # Verify that angle is properly normalized
        res = add_annotation_image(url=self._TEST_HTTPS_URL, angle=181)
        self.assertEqual(res['rotation'], '-179.0')
        res = add_annotation_image(url=self._TEST_HTTPS_URL, angle=180)
        self.assertEqual(res['rotation'], '180.0')
        res = add_annotation_image(url=self._TEST_HTTPS_URL, angle=-180)
        self.assertEqual(res['rotation'], '-180.0')
        res = add_annotation_image(url=self._TEST_HTTPS_URL, angle=-181)
        self.assertEqual(res['rotation'], '179.0')
        res = add_annotation_image(url=self._TEST_HTTPS_URL, angle=1980)
        self.assertEqual(res['rotation'], '180.0')
        res = add_annotation_image(url=self._TEST_HTTPS_URL, angle=-1980)
        self.assertEqual(res['rotation'], '-180.0')

        # Verify that bad opacity is detected
        self.assertRaises(CyError, add_annotation_image, url=self._TEST_HTTPS_URL, opacity='bad')
        self.assertRaises(CyError, add_annotation_image, url=self._TEST_HTTPS_URL, opacity=-1)
        self.assertRaises(CyError, add_annotation_image, url=self._TEST_HTTPS_URL, opacity=101)

        # Verify that bad brightness is detected
        self.assertRaises(CyError, add_annotation_image, url=self._TEST_HTTPS_URL, brightness='bad')
        self.assertRaises(CyError, add_annotation_image, url=self._TEST_HTTPS_URL, brightness=-101)
        self.assertRaises(CyError, add_annotation_image, url=self._TEST_HTTPS_URL, brightness=101)

        # Verify that bad contrast is detected
        self.assertRaises(CyError, add_annotation_image, url=self._TEST_HTTPS_URL, contrast='bad')
        self.assertRaises(CyError, add_annotation_image, url=self._TEST_HTTPS_URL, contrast=-101)
        self.assertRaises(CyError, add_annotation_image, url=self._TEST_HTTPS_URL, contrast=101)

        # Verify that bad border thickness is detected
        self.assertRaises(CyError, add_annotation_image, url=self._TEST_HTTPS_URL, border_thickness='bad')
        self.assertRaises(CyError, add_annotation_image, url=self._TEST_HTTPS_URL, border_thickness=-1)

        # Verify that bad border color is detected
        self.assertRaises(CyError, add_annotation_image, url=self._TEST_HTTPS_URL, border_color='bogus')

        # Verify that bad border opacity is detected
        self.assertRaises(CyError, add_annotation_image, url=self._TEST_HTTPS_URL, border_opacity='bad')
        self.assertRaises(CyError, add_annotation_image, url=self._TEST_HTTPS_URL, border_opacity=-1)
        self.assertRaises(CyError, add_annotation_image, url=self._TEST_HTTPS_URL, border_opacity=101)

        # Verify that bad height is detected
        self.assertRaises(CyError, add_annotation_image, url=self._TEST_HTTPS_URL, height='bad')
        self.assertRaises(CyError, add_annotation_image, url=self._TEST_HTTPS_URL, height=0)

        # Verify that bad width is detected
        self.assertRaises(CyError, add_annotation_image, url=self._TEST_HTTPS_URL, width='bad')
        self.assertRaises(CyError, add_annotation_image, url=self._TEST_HTTPS_URL, width=0)

        # Verify that bad canvas is detected
        self.assertRaises(CyError, add_annotation_image, url=self._TEST_HTTPS_URL, canvas='bogus')

        # Verify that bad z-order is detected
        self.assertRaises(CyError, add_annotation_image, url=self._TEST_HTTPS_URL, z_order='bogus')

    @print_entry_exit
    def test_add_annotation_shape(self):
        EXPECTED_IMAGE_KEYS = {'edgeThickness', 'canvas', 'fillOpacity', 'rotation', 'type', 'uuid', 'shapeType',
                               'edgeColor', 'edgeOpacity', 'name', 'x', 'width', 'y', 'z', 'height'}
        EXPECTED_SHAPE_VALS = {'edgeThickness': '2.0', 'canvas': 'background', 'fillOpacity': '50.0',
                               'rotation': '45.0',
                               'type': 'org.cytoscape.view.presentation.annotations.ShapeAnnotation',
                               'fillColor': '#008000', 'shapeType': 'ELLIPSE', 'edgeColor': '#FFC0CB',
                               'edgeOpacity': '75.0', 'name': 'ann3 name', 'x': '100.0', 'width': '31.0', 'y': '200.0',
                               'z': '0', 'height': '30.0'}

        # Initialize
        gal_filtered_suid, yeast_high_quality_suid = self._load_2_networks()

        # Verify that adding a minimal annotation to the current network works
        res = add_annotation_shape()
        res1 = get_annotation_list(network=gal_filtered_suid)
        self._check_annotation_list(res1, 1, EXPECTED_IMAGE_KEYS)
        self.assertDictEqual(res, res1[0])

        # Verify that adding a second annotation (explicitly naming the network) also works
        res = add_annotation_shape(network=gal_filtered_suid)
        res1 = get_annotation_list(network=gal_filtered_suid)
        self._check_annotation_list(res1, 2, EXPECTED_IMAGE_KEYS)

        # Verify that nothing was added to the other network
        self._check_annotation_list(get_annotation_list(network=yeast_high_quality_suid), 0, EXPECTED_IMAGE_KEYS)

        # Verify that supplying additional parameters is reflected in an annotation
        res = add_annotation_shape(type='ELLIPSE', custom_shape=None, x_pos=100, y_pos=200, angle=45,
                                   fill_color='#008000', opacity=50,
                                   border_thickness=2, border_color='#FFC0CB',
                                   border_opacity=75, height=30, width=31, name='ann3 name', canvas='background')
        self._check_expected_values(res, EXPECTED_SHAPE_VALS)

        # Verify that supplying color name parameters is reflected in an annotation
        delete_annotation('ann3 name')
        res = add_annotation_shape(type='ELLIPSE', custom_shape=None, x_pos=100, y_pos=200, angle=45,
                                   fill_color='green', opacity=50,
                                   border_thickness=2, border_color='pink',
                                   border_opacity=75, height=30, width=31, name='ann3 name', canvas='background')
        self._check_expected_values(res, EXPECTED_SHAPE_VALS)

        # Verify that types are translated as expected
        res = add_annotation_shape(type='ROUND_RECTANGLE')
        self.assertEqual(res['shapeType'], 'ROUNDEDRECTANGLE')
        res = add_annotation_shape(type='VEE')
        self.assertEqual(res['shapeType'], 'V')

        # TODO: Figure out how to test custom_shape parameter
        res = add_annotation_shape(custom_shape='33.png')

        # Verify that angle is properly normalized
        res = add_annotation_shape(angle=181)
        self.assertEqual(res['rotation'], '-179.0')
        res = add_annotation_shape(angle=180)
        self.assertEqual(res['rotation'], '180.0')
        res = add_annotation_shape(angle=-180)
        self.assertEqual(res['rotation'], '-180.0')
        res = add_annotation_shape(angle=-181)
        self.assertEqual(res['rotation'], '179.0')
        res = add_annotation_shape(angle=1980)
        self.assertEqual(res['rotation'], '180.0')
        res = add_annotation_shape(angle=-1980)
        self.assertEqual(res['rotation'], '-180.0')

        # Verify that bad shape is detected
        self.assertRaises(CyError, add_annotation_shape, type='bogus')

        # Verify that bad fill color is detected
        self.assertRaises(CyError, add_annotation_shape, fill_color='bogus')

        # Verify that bad opacity is detected
        self.assertRaises(CyError, add_annotation_shape, opacity='bad')
        self.assertRaises(CyError, add_annotation_shape, opacity=-1)
        self.assertRaises(CyError, add_annotation_shape, opacity=101)

        # Verify that bad border thickness is detected
        self.assertRaises(CyError, add_annotation_shape, border_thickness='bad')
        self.assertRaises(CyError, add_annotation_shape, border_thickness=-1)

        # Verify that bad border color is detected
        self.assertRaises(CyError, add_annotation_shape, border_color='bogus')

        # Verify that bad border opacity is detected
        self.assertRaises(CyError, add_annotation_shape, border_opacity='bad')
        self.assertRaises(CyError, add_annotation_shape, border_opacity=-1)
        self.assertRaises(CyError, add_annotation_shape, border_opacity=101)

        # Verify that bad height is detected
        self.assertRaises(CyError, add_annotation_shape, height='bad')
        self.assertRaises(CyError, add_annotation_shape, height=0)

        # Verify that bad width is detected
        self.assertRaises(CyError, add_annotation_shape, width='bad')
        self.assertRaises(CyError, add_annotation_shape, width=0)

        # Verify that bad canvas is detected
        self.assertRaises(CyError, add_annotation_shape, canvas='bogus')

        # Verify that bad z-order is detected
        self.assertRaises(CyError, add_annotation_shape, z_order='bogus')

    @print_entry_exit
    def test_delete_annotation(self):
        # Initialize
        load_test_session()

        # Verify that creating an annotation then deleting it by UUID works
        res = add_annotation_text(name='ann1', text='ann1 text')
        delete_annotation(names=res['uuid'])
        res = get_annotation_list()
        self.assertListEqual(res, [])

        # Verify that creating an annotation then deleting it by name works
        res = add_annotation_text(name='ann2', text='ann2 text')
        delete_annotation(names='ann2')
        res = get_annotation_list()
        self.assertListEqual(res, [])

        # Verify that creating 3 annotations and deleting two by name works
        res_a = add_annotation_text(name='ann3a', text='ann3a text')
        res_b = add_annotation_text(name='ann3b', text='ann3b text')
        res_c = add_annotation_text(name='ann3c', text='ann3c text')
        delete_annotation(names=['ann3a', 'ann3c'])
        res = get_annotation_list()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['uuid'], res_b['uuid'])  # Compare UUIDs only because z-order may change

        # Verify that creating 3 annotations and deleting two by UUID works
        res_a = add_annotation_text(name='ann3a', text='ann3a text')
        res_c = add_annotation_text(name='ann3c', text='ann3c text')
        delete_annotation(names=[res_b['uuid'], res_c['uuid']])
        res = get_annotation_list()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['uuid'], res_a['uuid'])  # Compare UUIDs only because z-order may change

        # We would try deleting a non-existent annotation, but Cytoscape doesn't return an error for this

        # Verify check for null names list
        self.assertRaises(CyError, delete_annotation)

    @print_entry_exit
    def test_group_annotation(self):
        EXPECTED_GROUP_KEYS = {'canvas', 'rotation', 'name', 'x', 'y', 'z', 'type', 'uuid', 'memberUUIDs'}

        # Initialize
        gal_filtered_suid, yeast_high_quality_suid = self._load_2_networks()

        res_a = add_annotation_text(name='ann3a', text='ann3a text')
        res_b = add_annotation_text(name='ann3b', text='ann3b text')
        res_c = add_annotation_text(name='ann3c', text='ann3c text')
        res_d = add_annotation_text(name='ann3d', text='ann3d text')
        res_e = add_annotation_text(name='ann3e', text='ann3e text')
        res_f = add_annotation_text(name='ann3f', text='ann3f text')
        res_g = add_annotation_text(name='ann3g', text='ann3g text')
        res_h = add_annotation_text(name='ann3h', text='ann3h text')
        res_i = add_annotation_text(name='ann3i', text='ann3i text')
        res_j = add_annotation_text(name='ann3j', text='ann3j text')
        res_k = add_annotation_text(name='ann3k', text='ann3k text')
        res_l = add_annotation_text(name='ann3l', text='ann3l text')
        res_m = add_annotation_text(name='ann3m', text='ann3m text')
        res_n = add_annotation_text(name='ann3n', text='ann3n text')

        # Verify that a group can be created from a list of UUIDs
        group_1_uuids_list = [res_a['uuid'], res_b['uuid'], res_c['uuid']]
        res_1 = group_annotation(group_1_uuids_list)
        self.assertTrue(EXPECTED_GROUP_KEYS.issubset(set(res_1.keys())))
        self.assertSetEqual(set(group_1_uuids_list), set(res_1['memberUUIDs'].split(',')))

        # Verify that a group can be created from a list of names
        group_2_names_list = [res_d['name'], res_e['name'], res_f['name']]
        group_2_uuids_list = [res_d['uuid'], res_e['uuid'], res_f['uuid']]
        res_2 = group_annotation(group_2_names_list, network=gal_filtered_suid)
        self.assertTrue(EXPECTED_GROUP_KEYS.issubset(set(res_2.keys())))
        self.assertSetEqual(set(group_2_uuids_list), set(res_2['memberUUIDs'].split(',')))

        # Verify that a group can be created from a comma-separated list of UUIDs
        group_3_uuids_list = [res_g['uuid'], res_h['uuid'], res_i['uuid']]
        res_3 = group_annotation(','.join(group_3_uuids_list))
        self.assertTrue(EXPECTED_GROUP_KEYS.issubset(set(res_3.keys())))
        self.assertSetEqual(set(group_3_uuids_list), set(res_3['memberUUIDs'].split(',')))

        # Verify that a group can be created from a comma-separated list of names
        group_4_names_list = [res_j['name'], res_k['name'], res_l['name']]
        group_4_uuids_list = [res_j['uuid'], res_k['uuid'], res_l['uuid']]
        res_4 = group_annotation(','.join(group_4_names_list), network=gal_filtered_suid)
        self.assertTrue(EXPECTED_GROUP_KEYS.issubset(set(res_4.keys())))
        self.assertSetEqual(set(group_4_uuids_list), set(res_4['memberUUIDs'].split(',')))

        # Verify that a group can be created from a single UUID
        group_5_uuids_list = [res_m['uuid']]
        res_5 = group_annotation(group_5_uuids_list[0])
        self.assertTrue(EXPECTED_GROUP_KEYS.issubset(set(res_5.keys())))
        self.assertSetEqual(set(group_5_uuids_list), set(res_5['memberUUIDs'].split(',')))

        # Verify that a group can be created from a single name
        group_6_names_list = [res_n['name']]
        group_6_uuids_list = [res_n['uuid']]
        res_6 = group_annotation(group_6_names_list[0], network=gal_filtered_suid)
        self.assertTrue(EXPECTED_GROUP_KEYS.issubset(set(res_6.keys())))
        self.assertSetEqual(set(group_6_uuids_list), set(res_6['memberUUIDs'].split(',')))

        # Verify that none of the groups were added to the yeast network
        self.assertEqual(len(get_annotation_list(network=gal_filtered_suid)), 20)
        self.assertEqual(len(get_annotation_list(network=yeast_high_quality_suid)), 0)

        # Verify that adding a group to the yeast network doesn't appear in the current network
        res_o = add_annotation_text(network=yeast_high_quality_suid, name='ann3o', text='ann3o text')
        group_annotation(res_o['name'], network=yeast_high_quality_suid)
        self.assertEqual(len(get_annotation_list(network=gal_filtered_suid)), 20)
        self.assertEqual(len(get_annotation_list(network=yeast_high_quality_suid)), 2)

        # Verify that errors are caught
        self.assertRaises(CyError, group_annotation)
        self.assertRaises(CyError, group_annotation, 'junk')
        self.assertRaises(CyError, group_annotation, ['junk'])
        self.assertRaises(CyError, group_annotation, '')
        self.assertRaises(CyError, group_annotation, [])

    @print_entry_exit
    def test_ungroup_annotation(self):
        # Initialize
        gal_filtered_suid, yeast_high_quality_suid = self._load_2_networks()

        # Create test annotations
        res_a = add_annotation_text(name='ann3a', text='ann3a text')
        res_b = add_annotation_text(name='ann3b', text='ann3b text')
        res_c = add_annotation_text(name='ann3c', text='ann3c text')
        res_d = add_annotation_text(name='ann3d', text='ann3d text')
        res_e = add_annotation_text(name='ann3e', text='ann3e text')
        res_f = add_annotation_text(name='ann3f', text='ann3f text')
        self.assertEqual(len(get_annotation_list()), 6)
        self.assertEqual(len(get_annotation_list(network=yeast_high_quality_suid)), 0)

        # Create a test group in default network, group it, and then ungroup it by UUID
        res_group = group_annotation([res_a['uuid'], res_b['uuid'], res_c['uuid']])
        self.assertEqual(len(get_annotation_list()), 7)
        ungroup_annotation(res_group['uuid'])
        self.assertEqual(len(get_annotation_list()), 6)

        # Create a test group in default network, group it, and then ungroup it by name
        res_group = group_annotation([res_a['uuid'], res_b['uuid'], res_c['uuid']])
        self.assertEqual(len(get_annotation_list()), 7)
        ungroup_annotation(res_group['name'])
        self.assertEqual(len(get_annotation_list()), 6)

        # Create a test group in named network, group it, and then ungroup it by UUID ... verify yeast network not affected
        res_group = group_annotation([res_a['uuid'], res_b['uuid'], res_c['uuid']], network=gal_filtered_suid)
        self.assertEqual(len(get_annotation_list(network=gal_filtered_suid)), 7)
        self.assertEqual(len(get_annotation_list(network=yeast_high_quality_suid)), 0)
        ungroup_annotation(res_group['uuid'], network=gal_filtered_suid)
        self.assertEqual(len(get_annotation_list(network=gal_filtered_suid)), 6)
        self.assertEqual(len(get_annotation_list(network=yeast_high_quality_suid)), 0)

        # Create a test group in named network, group it, and then ungroup it by name ... verify yeast network not affected
        res_group = group_annotation([res_a['uuid'], res_b['uuid'], res_c['uuid']], network=gal_filtered_suid)
        self.assertEqual(len(get_annotation_list(network=gal_filtered_suid)), 7)
        self.assertEqual(len(get_annotation_list(network=yeast_high_quality_suid)), 0)
        ungroup_annotation(res_group['name'], network=gal_filtered_suid)
        self.assertEqual(len(get_annotation_list(network=gal_filtered_suid)), 6)
        self.assertEqual(len(get_annotation_list(network=yeast_high_quality_suid)), 0)

        # Try creating a group in the Yeast network, and verify that it doesn't affect galFiltered network
        res_g = add_annotation_text(name='ann3g', text='ann3g text', network=yeast_high_quality_suid)
        res_h = add_annotation_text(name='ann3h', text='ann3h text', network=yeast_high_quality_suid)
        res_i = add_annotation_text(name='ann3i', text='ann3i text', network=yeast_high_quality_suid)
        res_group = group_annotation([res_g['uuid'], res_h['uuid'], res_i['uuid']], network=yeast_high_quality_suid)
        self.assertEqual(len(get_annotation_list(network=yeast_high_quality_suid)), 4)
        self.assertEqual(len(get_annotation_list(network=gal_filtered_suid)), 6)
        ungroup_annotation(res_group['uuid'], network=yeast_high_quality_suid)
        self.assertEqual(len(get_annotation_list(network=yeast_high_quality_suid)), 3)
        self.assertEqual(len(get_annotation_list(network=gal_filtered_suid)), 6)

        # Create two test groups in default network, group them, and then ungroup them by UUID
        res_group_1 = group_annotation([res_a['uuid'], res_b['uuid'], res_c['uuid']])
        res_group_2 = group_annotation([res_d['uuid'], res_e['uuid'], res_f['uuid']])
        self.assertEqual(len(get_annotation_list()), 8)
        ungroup_annotation([res_group_1['uuid'], res_group_2['uuid']])
        self.assertEqual(len(get_annotation_list()), 6)

        # Create two test groups in default network, group them, and then ungroup them by name
        res_group_1 = group_annotation([res_a['uuid'], res_b['uuid'], res_c['uuid']])
        res_group_2 = group_annotation([res_d['uuid'], res_e['uuid'], res_f['uuid']])
        self.assertEqual(len(get_annotation_list()), 8)
        ungroup_annotation([res_group_1['name'], res_group_2['name']])
        self.assertEqual(len(get_annotation_list()), 6)

        # Verify that errors are caught
        self.assertRaises(CyError, ungroup_annotation)

    @print_entry_exit
    def test_update_annotation_text(self):
        INITIAL_NAME = 'ann1 name'
        # Initialize
        gal_filtered_suid, yeast_high_quality_suid = self._load_2_networks()

        # Create ann1 annotation in Yeast High Quality network
        res_yeast_ann1 = add_annotation_text(name=INITIAL_NAME, text='ann1', network=yeast_high_quality_suid)

        # Create ann1 text annotation to play with in gal_filtered network, and explicitly set all attributes
        res = add_annotation_text(text='ann1', x_pos=100, y_pos=200, font_size=25, font_family='Courier New',
                                  font_style='bold', color='#008000', angle=45, name=INITIAL_NAME, canvas='background')
        text_uuid = res['uuid']
        self._check_expected_values(res, {'canvas': 'background', 'color': '#008000', 'rotation': '45.0',
                                          'fontStyle': 'bold', 'fontFamily': 'Courier New', 'name': INITIAL_NAME,
                                          'x': '100.0', 'y': '200.0', 'fontSize': '25', 'text': 'ann1'})

        # Verify that it's possible to change all of the annotation attributes when name identifies annotation
        # ... and this time, specify the network implicitly, too.
        res = update_annotation_text(text='ann1a', annotation_name=INITIAL_NAME, x_pos=101, y_pos=201, font_size=26,
                                     font_family='Arial', font_style='italic', color='#0000FF', angle=46,
                                     name='ann1a name', canvas='foreground')
        self._check_expected_values(res, {'canvas': 'foreground', 'color': '#0000FF', 'rotation': '46.0',
                                          'type': 'org.cytoscape.view.presentation.annotations.TextAnnotation',
                                          'fontStyle': 'italic', 'fontFamily': 'Arial', 'name': 'ann1a name',
                                          'x': '101.0', 'y': '201.0', 'fontSize': '26', 'text': 'ann1a'})

        # Verify that nothing in the yeast network changed
        # Warning ... this can fail if Cytoscape mixes up annotations ... see CSD-678
        res = get_annotation_list(network=yeast_high_quality_suid)[0]
        self.assertDictEqual(res, res_yeast_ann1)

        # Verify that it's possible to change all of the annotation attributes when UUID identifies annotation,
        # ... and this time, specify the network explicitly, too.
        res = update_annotation_text(text='ann1b', annotation_name=text_uuid, x_pos=102, y_pos=202, font_size=27,
                                     font_family='Courier New', font_style='bolditalic', color='#F0F0F2', angle=47,
                                     name='ann1b name', canvas='background', network=gal_filtered_suid)
        self._check_expected_values(res, {'canvas': 'background', 'color': '#F0F0F2', 'rotation': '47.0',
                                          'type': 'org.cytoscape.view.presentation.annotations.TextAnnotation',
                                          'fontStyle': 'bolditalic', 'fontFamily': 'Courier New', 'name': 'ann1b name',
                                          'x': '102.0', 'y': '202.0', 'fontSize': '27', 'text': 'ann1b'})

        # Verify that it's possible to use named colors
        res = add_annotation_text(text='ann1', x_pos=100, y_pos=200, font_size=25, font_family='Courier New',
                                  font_style='bold', color='aqua', angle=45, name=INITIAL_NAME, canvas='background')
        text_uuid = res['uuid']
        self._check_expected_values(res, {'canvas': 'background', 'color': '#00FFFF', 'rotation': '45.0',
                                          'fontStyle': 'bold', 'fontFamily': 'Courier New', 'name': INITIAL_NAME,
                                          'x': '100.0', 'y': '200.0', 'fontSize': '25', 'text': 'ann1'})

        # Verify that nothing in the yeast network changed
        res = get_annotation_list(network=yeast_high_quality_suid)[0]
        self.assertDictEqual(res, res_yeast_ann1)

        # Verify that angle is properly normalized
        res = update_annotation_text(annotation_name=text_uuid, angle=181)
        self.assertEqual(res['rotation'], '-179.0')
        res = update_annotation_text(annotation_name=text_uuid, angle=180)
        self.assertEqual(res['rotation'], '180.0')
        res = update_annotation_text(annotation_name=text_uuid, angle=-180)
        self.assertEqual(res['rotation'], '-180.0')
        res = update_annotation_text(annotation_name=text_uuid, angle=-181)
        self.assertEqual(res['rotation'], '179.0')
        res = update_annotation_text(annotation_name=text_uuid, angle=1980)
        self.assertEqual(res['rotation'], '180.0')
        res = update_annotation_text(annotation_name=text_uuid, angle=-1980)
        self.assertEqual(res['rotation'], '-180.0')

        # Verify that missing annotation name is detected
        self.assertRaises(CyError, update_annotation_text)

        # Verify that bad font size is detected
        self.assertRaises(CyError, update_annotation_text, annotation_name=text_uuid, font_size='bogus')
        self.assertRaises(CyError, update_annotation_text, annotation_name=text_uuid, font_size=0)

        # Verify that bad font style is detected
        self.assertRaises(CyError, update_annotation_text, annotation_name=text_uuid, font_style='bogus')

        # Verify that bad color is detected
        self.assertRaises(CyError, update_annotation_text, annotation_name=text_uuid, color='bogus')

        # Verify that bad canvas is detected
        self.assertRaises(CyError, update_annotation_text, annotation_name=text_uuid, canvas='bogus')

        # Verify that bad z-order is detected
        self.assertRaises(CyError, update_annotation_text, annotation_name=text_uuid, z_order='bogus')

    @print_entry_exit
    def test_update_annotation_bounded_text(self):
        INITIAL_NAME = 'ann1 name'
        # Initialize
        gal_filtered_suid, yeast_high_quality_suid = self._load_2_networks()

        # Create ann1 annotation in Yeast High Quality network
        res_yeast_ann1 = add_annotation_bounded_text(name=INITIAL_NAME, text='ann1', network=yeast_high_quality_suid)

        # Create ann1 text annotation to play with in gal_filtered network, and explicitly set all attributes
        res = add_annotation_bounded_text(text='ann1', x_pos=100, y_pos=200, font_size=25, font_family='Courier New',
                                          font_style='bold', color='#ffc0cb', angle=45, type='ELLIPSE',
                                          custom_shape=None, fill_color='#008000', opacity=50, border_thickness=2,
                                          border_color='#800080', border_opacity=75, height=30, width=31,
                                          name=INITIAL_NAME, canvas='background')
        text_uuid = res['uuid']
        self._check_expected_values(res, {'edgeThickness': '2.0', 'canvas': 'background', 'fillOpacity': '50.0',
                                          'color': '#FFC0CB', 'rotation': '45.0', 'fontStyle': 'bold',
                                          'fillColor': '#008000', 'shapeType': 'ELLIPSE', 'edgeColor': '#800080',
                                          'fontFamily': 'Courier New', 'edgeOpacity': '75.0', 'name': INITIAL_NAME,
                                          'x': '100.0', 'width': '31.0', 'y': '200.0', 'z': '0', 'fontSize': '25',
                                          'text': 'ann1', 'height': '30.0'})

        # Verify that it's possible to change all of the annotation attributes when name identifies annotation in gal_filtered network
        res = update_annotation_bounded_text(text='ann1a', annotation_name=INITIAL_NAME, x_pos=101, y_pos=201,
                                             font_size=26, font_family='Arial', font_style='italic',
                                             color='#F0F0F1', angle=46, type='DIAMOND', custom_shape=None,
                                             fill_color='#A0A0A1', opacity=51, border_thickness=3,
                                             border_color='#0F0F0E', border_opacity=76, height=31, width=32,
                                             name='ann1a name', canvas='foreground')
        self._check_expected_values(res, {'edgeThickness': '3.0', 'canvas': 'foreground', 'fillOpacity': '51.0',
                                          'color': '#F0F0F1', 'rotation': '46.0',
                                          'type': 'org.cytoscape.view.presentation.annotations.BoundedTextAnnotation',
                                          'fontStyle': 'italic', 'fillColor': '#A0A0A1', 'shapeType': 'DIAMOND',
                                          'edgeColor': '#0F0F0E', 'fontFamily': 'Arial', 'edgeOpacity': '76.0',
                                          'name': 'ann1a name', 'x': '101.0', 'width': '32.0', 'y': '201.0',
                                          'fontSize': '26', 'text': 'ann1a', 'height': '31.0'})

        # Verify that it's possible to use color names
        res = update_annotation_bounded_text(text='ann1c', annotation_name=INITIAL_NAME, x_pos=101, y_pos=201,
                                             font_size=26, font_family='Arial', font_style='italic',
                                             color='pink', angle=46, type='DIAMOND', custom_shape=None,
                                             fill_color='green', opacity=51, border_thickness=3,
                                             border_color='purple', border_opacity=76, height=31, width=32,
                                             name='ann1c name', canvas='foreground')
        self._check_expected_values(res, {'edgeThickness': '3.0', 'canvas': 'foreground', 'fillOpacity': '51.0',
                                          'color': '#FFC0CB', 'rotation': '46.0',
                                          'type': 'org.cytoscape.view.presentation.annotations.BoundedTextAnnotation',
                                          'fontStyle': 'italic', 'fillColor': '#008000', 'shapeType': 'DIAMOND',
                                          'edgeColor': '#800080', 'fontFamily': 'Arial', 'edgeOpacity': '76.0',
                                          'name': 'ann1c name', 'x': '101.0', 'width': '32.0', 'y': '201.0',
                                          'fontSize': '26', 'text': 'ann1c', 'height': '31.0'})

        # Verify that nothing in the yeast network changed
        res = get_annotation_list(network=yeast_high_quality_suid)[0]
        self.assertDictEqual(res, res_yeast_ann1)

        # Verify that it's possible to change all of the annotation attributes when UUID identifies annotation,
        # ... and this time, specify the network explicitly, too.
        res = update_annotation_bounded_text(text='ann1b', annotation_name=text_uuid, x_pos=102, y_pos=202,
                                             font_size=27, font_family='Courier New', font_style='bolditalic',
                                             color='#F0F0F2', angle=47, type='ELLIPSE', custom_shape=None,
                                             fill_color='#A0A0A2', opacity=52, border_thickness=4,
                                             border_color='#0F0F0D', border_opacity=77, height=32, width=33,
                                             name='ann1b name', canvas='background', network=gal_filtered_suid)
        self._check_expected_values(res, {'edgeThickness': '4.0', 'canvas': 'background', 'fillOpacity': '52.0',
                                          'color': '#F0F0F2', 'rotation': '47.0',
                                          'type': 'org.cytoscape.view.presentation.annotations.BoundedTextAnnotation',
                                          'fontStyle': 'bolditalic', 'fillColor': '#A0A0A2', 'shapeType': 'ELLIPSE',
                                          'edgeColor': '#0F0F0D', 'fontFamily': 'Courier New', 'edgeOpacity': '77.0',
                                          'name': 'ann1b name', 'x': '102.0', 'width': '33.0', 'y': '202.0',
                                          'fontSize': '27', 'text': 'ann1b', 'height': '32.0'})

        # Verify that nothing in the yeast network changed
        res = get_annotation_list(network=yeast_high_quality_suid)[0]
        self.assertDictEqual(res, res_yeast_ann1)

        # Verify that types are translated as expected
        res = update_annotation_bounded_text(annotation_name=text_uuid, type='ROUND_RECTANGLE')
        self.assertEqual(res['shapeType'], 'ROUNDEDRECTANGLE')
        res = update_annotation_bounded_text(annotation_name=text_uuid, type='VEE')
        self.assertEqual(res['shapeType'], 'V')

        # Verify that angle is properly normalized
        res = update_annotation_bounded_text(annotation_name=text_uuid, angle=181)
        self.assertEqual(res['rotation'], '-179.0')
        res = update_annotation_bounded_text(annotation_name=text_uuid, angle=180)
        self.assertEqual(res['rotation'], '180.0')
        res = update_annotation_bounded_text(annotation_name=text_uuid, angle=-180)
        self.assertEqual(res['rotation'], '-180.0')
        res = update_annotation_bounded_text(annotation_name=text_uuid, angle=-181)
        self.assertEqual(res['rotation'], '179.0')
        res = update_annotation_bounded_text(annotation_name=text_uuid, angle=1980)
        self.assertEqual(res['rotation'], '180.0')
        res = update_annotation_bounded_text(annotation_name=text_uuid, angle=-1980)
        self.assertEqual(res['rotation'], '-180.0')

        # Verify that missing annotation name is detected
        self.assertRaises(CyError, update_annotation_bounded_text)

        # Verify that bad font size is detected
        self.assertRaises(CyError, update_annotation_bounded_text, annotation_name=text_uuid, font_size='bogus')
        self.assertRaises(CyError, update_annotation_bounded_text, annotation_name=text_uuid, font_size=0)

        # Verify that bad font style is detected
        self.assertRaises(CyError, update_annotation_bounded_text, annotation_name=text_uuid, font_style='bogus')

        # Verify that bad color is detected
        self.assertRaises(CyError, update_annotation_bounded_text, annotation_name=text_uuid, color='bogus')

        # Verify that bad type is detected
        self.assertRaises(CyError, update_annotation_bounded_text, annotation_name=text_uuid, type='bogus shape')

        # Verify that bad fill color is detected
        self.assertRaises(CyError, update_annotation_bounded_text, annotation_name=text_uuid, fill_color='bogus')

        # Verify that bad opacity is detected
        self.assertRaises(CyError, update_annotation_bounded_text, annotation_name=text_uuid, opacity='bad')
        self.assertRaises(CyError, update_annotation_bounded_text, annotation_name=text_uuid, opacity=-1)
        self.assertRaises(CyError, update_annotation_bounded_text, annotation_name=text_uuid, opacity=101)

        # Verify that bad border thickness is detected
        self.assertRaises(CyError, update_annotation_bounded_text, annotation_name=text_uuid, border_thickness='bad')
        self.assertRaises(CyError, update_annotation_bounded_text, annotation_name=text_uuid, border_thickness=-1)

        # Verify that bad border color is detected
        self.assertRaises(CyError, update_annotation_bounded_text, annotation_name=text_uuid, border_color='bogus')

        # Verify that bad border opacity is detected
        self.assertRaises(CyError, update_annotation_bounded_text, annotation_name=text_uuid, border_opacity='bad')
        self.assertRaises(CyError, update_annotation_bounded_text, annotation_name=text_uuid, border_opacity=-1)
        self.assertRaises(CyError, update_annotation_bounded_text, annotation_name=text_uuid, border_opacity=101)

        # Verify that bad height is detected
        self.assertRaises(CyError, update_annotation_bounded_text, annotation_name=text_uuid, height='bad')
        self.assertRaises(CyError, update_annotation_bounded_text, annotation_name=text_uuid, height=0)

        # Verify that bad width is detected
        self.assertRaises(CyError, update_annotation_bounded_text, annotation_name=text_uuid, width='bad')
        self.assertRaises(CyError, update_annotation_bounded_text, annotation_name=text_uuid, width=0)

        # Verify that bad canvas is detected
        self.assertRaises(CyError, update_annotation_bounded_text, annotation_name=text_uuid, canvas='bogus')

        # Verify that bad z-order is detected
        self.assertRaises(CyError, update_annotation_bounded_text, annotation_name=text_uuid, z_order='bogus')

    @print_entry_exit
    def test_update_annotation_shape(self):
        INITIAL_NAME = 'ann1 name'
        # Initialize
        gal_filtered_suid, yeast_high_quality_suid = self._load_2_networks()

        # Create ann1 annotation in Yeast High Quality network
        res_yeast_ann1 = add_annotation_shape(name=INITIAL_NAME, network=yeast_high_quality_suid)

        # Create ann1 shape annotation to play with in gal_filtered network, and explicitly set all attributes
        res = add_annotation_shape(type='ELLIPSE', custom_shape=None, x_pos=100, y_pos=200, angle=45,
                                   fill_color='#F0F0F0', opacity=50, border_thickness=2, border_color='#0F0F0F',
                                   border_opacity=75, height=30, width=31, name=INITIAL_NAME, canvas='background')
        shape_uuid = res['uuid']
        self._check_expected_values(res, {'edgeThickness': '2.0', 'canvas': 'background', 'fillOpacity': '50.0',
                                          'rotation': '45.0',
                                          'type': 'org.cytoscape.view.presentation.annotations.ShapeAnnotation',
                                          'fillColor': '#F0F0F0', 'shapeType': 'ELLIPSE', 'edgeColor': '#0F0F0F',
                                          'edgeOpacity': '75.0', 'name': 'ann1 name', 'x': '100.0', 'width': '31.0',
                                          'y': '200.0', 'z': '0', 'height': '30.0'})

        # Verify that it's possible to change all of the annotation attributes when name identifies annotation in gal_filtered network
        res = update_annotation_shape(type='DIAMOND', custom_shape=None, annotation_name=INITIAL_NAME, x_pos=101,
                                      y_pos=202, angle=90,
                                      fill_color='#F0F0F1', opacity=51, border_thickness=3, border_color='#0F0F0E',
                                      border_opacity=76, height=31, width=32, name='ann1a name', canvas='foreground')
        self._check_expected_values(res, {'edgeThickness': '3.0', 'canvas': 'foreground', 'fillOpacity': '51.0',
                                          'rotation': '90.0',
                                          'type': 'org.cytoscape.view.presentation.annotations.ShapeAnnotation',
                                          'fillColor': '#F0F0F1', 'shapeType': 'DIAMOND', 'edgeColor': '#0F0F0E',
                                          'edgeOpacity': '76.0', 'name': 'ann1a name', 'x': '101.0', 'width': '32.0',
                                          'y': '202.0', 'z': '0', 'height': '31.0'})

        # Verify that nothing in the yeast network changed
        res = get_annotation_list(network=yeast_high_quality_suid)[0]
        self.assertDictEqual(res, res_yeast_ann1)

        # Verify that it's possible to change all of the annotation attributes when UUID identifies annotation,
        # ... and this time, specify the network explicitly, too.
        res = update_annotation_shape(type='OCTAGON', custom_shape=None, annotation_name=shape_uuid, x_pos=102,
                                      y_pos=203, angle=135,
                                      fill_color='#F0F0F2', opacity=52, border_thickness=4, border_color='#0F0F0D',
                                      border_opacity=77, height=32, width=33, name='ann1b name', canvas='background')
        self._check_expected_values(res, {'edgeThickness': '4.0', 'canvas': 'background', 'fillOpacity': '52.0',
                                          'rotation': '135.0',
                                          'type': 'org.cytoscape.view.presentation.annotations.ShapeAnnotation',
                                          'fillColor': '#F0F0F2', 'shapeType': 'OCTAGON', 'edgeColor': '#0F0F0D',
                                          'edgeOpacity': '77.0', 'name': 'ann1b name', 'x': '102.0', 'width': '33.0',
                                          'y': '203.0', 'z': '0', 'height': '32.0'})

        # Verify that nothing in the yeast network changed
        res = get_annotation_list(network=yeast_high_quality_suid)[0]
        self.assertDictEqual(res, res_yeast_ann1)

        # Verify that types are translated as expected
        res = update_annotation_shape(annotation_name=shape_uuid, type='ROUND_RECTANGLE')
        self.assertEqual(res['shapeType'], 'ROUNDEDRECTANGLE')
        res = update_annotation_shape(annotation_name=shape_uuid, type='VEE')
        self.assertEqual(res['shapeType'], 'V')

        # Verify that angle is properly normalized
        res = update_annotation_shape(annotation_name=shape_uuid, angle=181)
        self.assertEqual(res['rotation'], '-179.0')
        res = update_annotation_shape(annotation_name=shape_uuid, angle=180)
        self.assertEqual(res['rotation'], '180.0')
        res = update_annotation_shape(annotation_name=shape_uuid, angle=-180)
        self.assertEqual(res['rotation'], '-180.0')
        res = update_annotation_shape(annotation_name=shape_uuid, angle=-181)
        self.assertEqual(res['rotation'], '179.0')
        res = update_annotation_shape(annotation_name=shape_uuid, angle=1980)
        self.assertEqual(res['rotation'], '180.0')
        res = update_annotation_shape(annotation_name=shape_uuid, angle=-1980)
        self.assertEqual(res['rotation'], '-180.0')

        # Verify that missing annotation name is detected
        self.assertRaises(CyError, update_annotation_shape)

        # Verify that bad shape is detected
        self.assertRaises(CyError, update_annotation_shape, annotation_name=shape_uuid, type='bogus')

        # Verify that bad fill color is detected
        self.assertRaises(CyError, update_annotation_shape, annotation_name=shape_uuid, fill_color='bogus')

        # Verify that bad opacity is detected
        self.assertRaises(CyError, update_annotation_shape, annotation_name=shape_uuid, opacity='bad')
        self.assertRaises(CyError, update_annotation_shape, annotation_name=shape_uuid, opacity=-1)
        self.assertRaises(CyError, update_annotation_shape, annotation_name=shape_uuid, opacity=101)

        # Verify that bad border thickness is detected
        self.assertRaises(CyError, update_annotation_shape, annotation_name=shape_uuid, border_thickness='bad')
        self.assertRaises(CyError, update_annotation_shape, annotation_name=shape_uuid, border_thickness=-1)

        # Verify that bad border color is detected
        self.assertRaises(CyError, update_annotation_shape, annotation_name=shape_uuid, border_color='bogus')

        # Verify that bad border opacity is detected
        self.assertRaises(CyError, update_annotation_shape, annotation_name=shape_uuid, border_opacity='bad')
        self.assertRaises(CyError, update_annotation_shape, annotation_name=shape_uuid, border_opacity=-1)
        self.assertRaises(CyError, update_annotation_shape, annotation_name=shape_uuid, border_opacity=101)

        # Verify that bad height is detected
        self.assertRaises(CyError, update_annotation_shape, annotation_name=shape_uuid, height='bad')
        self.assertRaises(CyError, update_annotation_shape, annotation_name=shape_uuid, height=0)

        # Verify that bad width is detected
        self.assertRaises(CyError, update_annotation_shape, annotation_name=shape_uuid, width='bad')
        self.assertRaises(CyError, update_annotation_shape, annotation_name=shape_uuid, width=0)

        # Verify that bad canvas is detected
        self.assertRaises(CyError, update_annotation_shape, annotation_name=shape_uuid, canvas='bogus')

        # Verify that bad z-order is detected
        self.assertRaises(CyError, update_annotation_shape, annotation_name=shape_uuid, z_order='bogus')

    @print_entry_exit
    def test_update_annotation_image(self):
        INITIAL_NAME = 'ann1 name'
        # Initialize
        gal_filtered_suid, yeast_high_quality_suid = self._load_2_networks()

        # Create ann1 annotation in Yeast High Quality network
        res_yeast_ann1 = add_annotation_image(url=self._TEST_HTTPS_URL, name=INITIAL_NAME,
                                              network=yeast_high_quality_suid)

        # Create ann1 image annotation to play with in gal_filtered network, and explicitly set all attributes
        res = add_annotation_image(url=self._TEST_HTTPS_URL, x_pos=100, y_pos=200, angle=45, opacity=50,
                                   brightness=60, contrast=70, border_thickness=2, border_color='#0F0F0F',
                                   border_opacity=75, height=30, width=31, name=INITIAL_NAME, canvas='background')
        image_uuid = res['uuid']
        self._check_expected_values(res, {'edgeThickness': '2.0', 'canvas': 'background', 'rotation': '45.0',
                                          'type': 'org.cytoscape.view.presentation.annotations.ImageAnnotation',
                                          'URL': self._TEST_HTTPS_URL,
                                          'shapeType': 'RECTANGLE', 'edgeColor': '#0F0F0F', 'brightness': '60',
                                          'edgeOpacity': '75.0', 'contrast': '70', 'name': INITIAL_NAME, 'x': '100.0',
                                          'width': '31.0', 'y': '200.0', 'z': '0', 'opacity': '0.5', 'height': '30.0'})

        # Verify that it's possible to change all of the annotation attributes when name identifies annotation in gal_filtered network
        res = update_annotation_image(url=self._TEST_HTTP_URL, annotation_name=INITIAL_NAME, x_pos=101, y_pos=201,
                                      angle=90, opacity=51, brightness=61, contrast=71, border_thickness=3,
                                      border_color='#0F0F0E', border_opacity=76, height=31, width=32, name='ann1a name',
                                      canvas='foreground')
        self._check_expected_values(res, {'edgeThickness': '3.0', 'canvas': 'foreground', 'rotation': '90.0',
                                          'type': 'org.cytoscape.view.presentation.annotations.ImageAnnotation',
                                          'URL': self._TEST_HTTP_URL, 'shapeType': 'RECTANGLE', 'edgeColor': '#0F0F0E',
                                          'brightness': '61', 'edgeOpacity': '76.0', 'contrast': '71',
                                          'name': 'ann1a name', 'x': '101.0', 'width': '32.0', 'y': '201.0', 'z': '0',
                                          'opacity': '0.51', 'height': '31.0'})

        # Verify that colors names can be used as parameters
        res = update_annotation_image(url=self._TEST_HTTP_URL, annotation_name='ann1a name', x_pos=101, y_pos=201,
                                      angle=90, opacity=51, brightness=61, contrast=71, border_thickness=3,
                                      border_color='purple', border_opacity=76, height=31, width=32, name='ann1b name',
                                      canvas='foreground')
        self._check_expected_values(res, {'edgeThickness': '3.0', 'canvas': 'foreground', 'rotation': '90.0',
                                          'type': 'org.cytoscape.view.presentation.annotations.ImageAnnotation',
                                          'URL': self._TEST_HTTP_URL, 'shapeType': 'RECTANGLE', 'edgeColor': '#800080',
                                          'brightness': '61', 'edgeOpacity': '76.0', 'contrast': '71',
                                          'name': 'ann1b name', 'x': '101.0', 'width': '32.0', 'y': '201.0', 'z': '0',
                                          'opacity': '0.51', 'height': '31.0'})

        # Verify that nothing in the yeast network changed
        res = get_annotation_list(network=yeast_high_quality_suid)[0]
        self.assertDictEqual(res, res_yeast_ann1)

        # Verify that it's possible to change all of the annotation attributes when UUID identifies annotation,
        # ... and this time, specify the network explicitly, too.
        res = update_annotation_image(url=self._TEST_HTTPS_URL, annotation_name=image_uuid, x_pos=102, y_pos=202,
                                      angle=180, opacity=52, brightness=62, contrast=72, border_thickness=4,
                                      border_color='#0F0F0D', border_opacity=77, height=32, width=33, name='ann1c name',
                                      canvas='background', network=gal_filtered_suid)
        self._check_expected_values(res, {'edgeThickness': '4.0', 'canvas': 'background', 'rotation': '180.0',
                                          'type': 'org.cytoscape.view.presentation.annotations.ImageAnnotation',
                                          'URL': self._TEST_HTTPS_URL, 'shapeType': 'RECTANGLE', 'edgeColor': '#0F0F0D',
                                          'brightness': '62', 'edgeOpacity': '77.0', 'contrast': '72',
                                          'name': 'ann1c name', 'x': '102.0', 'width': '33.0', 'y': '202.0', 'z': '0',
                                          'opacity': '0.52', 'height': '32.0'})

        # Verify that nothing in the yeast network changed
        res = get_annotation_list(network=yeast_high_quality_suid)[0]
        self.assertDictEqual(res, res_yeast_ann1)

        # Verify that angle is properly normalized
        res = update_annotation_image(annotation_name=image_uuid, angle=181)
        self.assertEqual(res['rotation'], '-179.0')
        res = update_annotation_image(annotation_name=image_uuid, angle=180)
        self.assertEqual(res['rotation'], '180.0')
        res = update_annotation_image(annotation_name=image_uuid, angle=-180)
        self.assertEqual(res['rotation'], '-180.0')
        res = update_annotation_image(annotation_name=image_uuid, angle=-181)
        self.assertEqual(res['rotation'], '179.0')
        res = update_annotation_image(annotation_name=image_uuid, angle=1980)
        self.assertEqual(res['rotation'], '180.0')
        res = update_annotation_image(annotation_name=image_uuid, angle=-1980)
        self.assertEqual(res['rotation'], '-180.0')

        # Verify that missing annotation name is detected
        self.assertRaises(CyError, update_annotation_image)

        # Verify that bad opacity is detected
        self.assertRaises(CyError, update_annotation_image, annotation_name=image_uuid, opacity='bad')
        self.assertRaises(CyError, update_annotation_image, annotation_name=image_uuid, opacity=-1)
        self.assertRaises(CyError, update_annotation_image, annotation_name=image_uuid, opacity=101)

        # Verify that bad brightness is detected
        self.assertRaises(CyError, update_annotation_image, annotation_name=image_uuid, brightness='bad')
        self.assertRaises(CyError, update_annotation_image, annotation_name=image_uuid, brightness=-101)
        self.assertRaises(CyError, update_annotation_image, annotation_name=image_uuid, brightness=101)

        # Verify that bad contrast is detected
        self.assertRaises(CyError, update_annotation_image, annotation_name=image_uuid, contrast='bad')
        self.assertRaises(CyError, update_annotation_image, annotation_name=image_uuid, contrast=-101)
        self.assertRaises(CyError, update_annotation_image, annotation_name=image_uuid, contrast=101)

        # Verify that bad border thickness is detected
        self.assertRaises(CyError, update_annotation_image, annotation_name=image_uuid, border_thickness='bad')
        self.assertRaises(CyError, update_annotation_image, annotation_name=image_uuid, border_thickness=-1)

        # Verify that bad border color is detected
        self.assertRaises(CyError, update_annotation_image, annotation_name=image_uuid, border_color='bogus')

        # Verify that bad border opacity is detected
        self.assertRaises(CyError, update_annotation_image, annotation_name=image_uuid, border_opacity='bad')
        self.assertRaises(CyError, update_annotation_image, annotation_name=image_uuid, border_opacity=-1)
        self.assertRaises(CyError, update_annotation_image, annotation_name=image_uuid, border_opacity=101)

        # Verify that bad height is detected
        self.assertRaises(CyError, update_annotation_image, annotation_name=image_uuid, height='bad')
        self.assertRaises(CyError, update_annotation_image, annotation_name=image_uuid, height=0)

        # Verify that bad width is detected
        self.assertRaises(CyError, update_annotation_image, annotation_name=image_uuid, width='bad')
        self.assertRaises(CyError, update_annotation_image, annotation_name=image_uuid, width=0)

        # Verify that bad canvas is detected
        self.assertRaises(CyError, update_annotation_image, annotation_name=image_uuid, canvas='bogus')

        # Verify that bad z-order is detected
        self.assertRaises(CyError, update_annotation_image, annotation_name=image_uuid, z_order='bogus')

    @print_entry_exit
    def test_update_group_annotation(self):
        # Initialize
        gal_filtered_suid, yeast_high_quality_suid = self._load_2_networks()

        res_a = add_annotation_text(name='ann3a', text='ann3a text', network=gal_filtered_suid)
        res_b = add_annotation_text(name='ann3b', text='ann3b text', network=gal_filtered_suid)
        res_c = add_annotation_text(name='ann3c', text='ann3c text', network=gal_filtered_suid)

        res_ay = add_annotation_text(name='ann3a', text='ann3a text', network=yeast_high_quality_suid)
        res_by = add_annotation_text(name='ann3b', text='ann3b text', network=yeast_high_quality_suid)
        res_cy = add_annotation_text(name='ann3c', text='ann3c text', network=yeast_high_quality_suid)

        # Create grp1 annotation in Yeast High Quality network
        res_yeast_grp1 = group_annotation(names=[res_ay['uuid'], res_by['uuid'], res_cy['uuid']],
                                          network=yeast_high_quality_suid)

        # Create group annotation in galFiltered
        res_gal_filtered_grp1 = group_annotation(names=[res_a['uuid'], res_b['uuid'], res_c['uuid']],
                                                 network=gal_filtered_suid)
        group_uuid = res_gal_filtered_grp1['uuid']

        # Verify changes in properties of (implied) galFiltered group ... identify group by name
        res = update_group_annotation(name='grp1a name', annotation_name=res_gal_filtered_grp1['name'],
                                      x_pos=100, y_pos=200, angle=90, canvas='background')
        # TODO: This should work when CSD-682 is fixed
        # self._check_expected_values(res,
        #                             {'canvas': 'background', 'rotation': '90.0', 'name': 'grp1a name', 'x': '100.0',
        #                              'y': '200.0', 'z': '0',
        #                              'type': 'org.cytoscape.view.presentation.annotations.GroupAnnotation'})

        # Verify that nothing in the yeast network changed
        res = get_annotation_list(network=yeast_high_quality_suid)
        # TODO: This test won't work until CSD-678 is fixed
        # self.assertDictEqual(self._find_type(res, 'org.cytoscape.view.presentation.annotations.GroupAnnotation'), res_yeast_grp1)

        # Verify changes in properties of (explicit) galFiltered group ... identify group by UUID
        res = update_group_annotation(name='grp1b name', annotation_name=group_uuid,
                                      x_pos=101, y_pos=201, angle=180, canvas='foreground')
        self._check_expected_values(res,
                                    {'canvas': 'foreground', 'rotation': '180.0', 'name': 'grp1b name', 'x': '101.0',
                                     'y': '201.0', 'z': '0',
                                     'type': 'org.cytoscape.view.presentation.annotations.GroupAnnotation'})

        # Verify that nothing in the yeast network changed
        res = get_annotation_list(network=yeast_high_quality_suid)
        # TODO: This test won't work until CSD-678 is fixed
        # self.assertDictEqual(self._find_type(res, 'org.cytoscape.view.presentation.annotations.GroupAnnotation'), res_yeast_grp1)

        # Verify that angle is properly normalized
        res = update_group_annotation(annotation_name=group_uuid, angle=181)
        self.assertEqual(res['rotation'], '-179.0')
        res = update_group_annotation(annotation_name=group_uuid, angle=180)
        self.assertEqual(res['rotation'], '180.0')
        res = update_group_annotation(annotation_name=group_uuid, angle=-180)
        self.assertEqual(res['rotation'], '-180.0')
        res = update_group_annotation(annotation_name=group_uuid, angle=-181)
        self.assertEqual(res['rotation'], '179.0')
        res = update_group_annotation(annotation_name=group_uuid, angle=1980)
        self.assertEqual(res['rotation'], '180.0')
        res = update_group_annotation(annotation_name=group_uuid, angle=-1980)
        self.assertEqual(res['rotation'], '-180.0')

        # Verify that missing annotation name is detected
        self.assertRaises(CyError, update_group_annotation)

        # Verify that bad canvas is detected
        self.assertRaises(CyError, update_group_annotation, annotation_name=group_uuid, canvas='bogus')

        # Verify that bad z-order is detected
        self.assertRaises(CyError, update_group_annotation, annotation_name=group_uuid, z_order='bogus')

# ---------------------------------------------------------------

    def _check_expected_values(self, target, expected_values):
        for k, v in expected_values.items():
            self.assertEqual(v, target[k], f'key={k} expected={v} actual={target[k]}')

    def _check_annotation_list(self, annotation_list, expected_len, expected_keys):
        self.assertIsInstance(annotation_list, list)
        self.assertEqual(len(annotation_list), expected_len)

        for ann in annotation_list:
            if not expected_keys.issubset(set(ann.keys())):
                raise Exception(f'Expected to find {expected_keys} in {ann}')

    def _find_type(self, annotation_list, type):
        self.assertIsInstance(annotation_list, list)
        res = [ann   for ann in annotation_list if ann['type'] == type]
        self.assertEqual(len(res), 1)
        return res[0]


    def _load_2_networks(self):
        load_test_session()
        gal_filtered_suid = get_network_suid()
        yeast_high_quality_suid, yeast_high_quality_view_suid = load_test_network('data/yeastHighQuality.sif',
                                                                                  make_current=False)
        return gal_filtered_suid, yeast_high_quality_suid


if __name__ == '__main__':
    unittest.main()
