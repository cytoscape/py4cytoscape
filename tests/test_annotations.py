# -*- coding: utf-8 -*-

""" Test functions in annotations.py.
"""

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
        self.assertRaises(CyError, add_annotation_text, text='bad', color='red')

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
                                         'color': '#F0F0F0', 'rotation': '45.0', 'fontStyle': 'bold',
                                         'fillColor': '#A0A0A0', 'shapeType': 'ELLIPSE', 'edgeColor': '#0F0F0F',
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
                                          font_style='bold', color='#F0F0F0', angle=45, type='ELLIPSE',
                                          custom_shape=None, fill_color='#A0A0A0', opacity=50, border_thickness=2,
                                          border_color='#0F0F0F', border_opacity=75, height=30, width=31,
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

        # Verify that bad shape is detected
        self.assertRaises(CyError, add_annotation_shape, type='bogus')

        # Verify that missing name is detected
        self.assertRaises(CyError, add_annotation_bounded_text)

        # Verify that bad font size is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', font_size='bogus')
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', font_size=0)

        # Verify that bad font style is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', font_style='bogus')

        # Verify that bad color is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', color='red')

        # Verify that bad type is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', type='bogus shape')

        # Verify that bad fill color is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', fill_color='red')

        # Verify that bad opacity is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', opacity='bad')
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', opacity=-1)
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', opacity=101)

        # Verify that bad border thickness is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', border_thickness='bad')
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', border_thickness=-1)

        # Verify that bad border color is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', border_color='red')

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
                               'shapeType': 'RECTANGLE', 'edgeColor': '#0F0F0F', 'brightness': '60',
                               'edgeOpacity': '75.0', 'contrast': '70', 'x': '100.0',
                               'width': '31.0', 'y': '200.0', 'opacity': '0.5', 'height': '30.0'}
        TEST_HTTP_URL = 'http://www.ucsd.edu/_resources/img/logo_UCSD.png'
        TEST_HTTPS_URL = 'https://www.ucsd.edu/_resources/img/logo_UCSD.png'
        TEST_FILE = 'data/annotation_image_1.jpg'

        # Initialize
        gal_filtered_suid, yeast_high_quality_suid = self._load_2_networks()

        # Verify that adding a minimal annotation to the current network works
        res = add_annotation_image(url=TEST_HTTPS_URL)
        res1 = get_annotation_list(network=gal_filtered_suid)
        self._check_annotation_list(res1, 1, EXPECTED_IMAGE_KEYS)
        self.assertDictEqual(res, res1[0])

        # Verify that adding a second annotation (explicitly naming the network) also works
        res = add_annotation_image(network=gal_filtered_suid, url=TEST_HTTPS_URL)
        res1 = get_annotation_list(network=gal_filtered_suid)
        self._check_annotation_list(res1, 2, EXPECTED_IMAGE_KEYS)

        # Verify that nothing was added to the other network
        self._check_annotation_list(get_annotation_list(network=yeast_high_quality_suid), 0, EXPECTED_IMAGE_KEYS)

        # Verify that supplying additional parameters is reflected in an annotation, using both HTTP and HTTPS
        res = add_annotation_image(url=TEST_HTTPS_URL, x_pos=100, y_pos=200, angle=45, opacity=50,
                                   brightness=60, contrast=70, border_thickness=2, border_color='#0F0F0F',
                                   border_opacity=75, height=30, width=31, name='ann3 name', canvas='background')
        self._check_expected_values(res, {**EXPECTED_IMAGE_VALS, **{'URL': TEST_HTTPS_URL, 'name': 'ann3 name'}})
        res = add_annotation_image(url=TEST_HTTP_URL, x_pos=100, y_pos=200, angle=45, opacity=50,
                                   brightness=60, contrast=70, border_thickness=2, border_color='#0F0F0F',
                                   border_opacity=75, height=30, width=31, name='ann3a name', canvas='background')
        self._check_expected_values(res, {**EXPECTED_IMAGE_VALS, **{'URL': TEST_HTTP_URL, 'name': 'ann3a name'}})

        # Verify that supplying additional parameters is reflected in an annotation
        res = add_annotation_image(url=TEST_FILE, x_pos=100, y_pos=200, angle=45, opacity=50,
                                   brightness=60, contrast=70, border_thickness=2, border_color='#0F0F0F',
                                   border_opacity=75, height=30, width=31, name='ann4 name', canvas='background')
        # TODO: Re-enable this check after CSD-675 is fixed
        # self._check_expected_values(res, {**EXPECTED_IMAGE_VALS, **{'URL': TEST_FILE, 'name': 'ann4 name'}})

        # Verify that angle is properly normalized
        res = add_annotation_image(url=TEST_HTTPS_URL, angle=181)
        self.assertEqual(res['rotation'], '-179.0')
        res = add_annotation_image(url=TEST_HTTPS_URL, angle=180)
        self.assertEqual(res['rotation'], '180.0')
        res = add_annotation_image(url=TEST_HTTPS_URL, angle=-180)
        self.assertEqual(res['rotation'], '-180.0')
        res = add_annotation_image(url=TEST_HTTPS_URL, angle=-181)
        self.assertEqual(res['rotation'], '179.0')
        res = add_annotation_image(url=TEST_HTTPS_URL, angle=1980)
        self.assertEqual(res['rotation'], '180.0')
        res = add_annotation_image(url=TEST_HTTPS_URL, angle=-1980)
        self.assertEqual(res['rotation'], '-180.0')

        # Verify that bad opacity is detected
        self.assertRaises(CyError, add_annotation_image, url=TEST_HTTPS_URL, opacity='bad')
        self.assertRaises(CyError, add_annotation_image, url=TEST_HTTPS_URL, opacity=-1)
        self.assertRaises(CyError, add_annotation_image, url=TEST_HTTPS_URL, opacity=101)

        # Verify that bad brightness is detected
        self.assertRaises(CyError, add_annotation_image, url=TEST_HTTPS_URL, brightness='bad')
        self.assertRaises(CyError, add_annotation_image, url=TEST_HTTPS_URL, brightness=-101)
        self.assertRaises(CyError, add_annotation_image, url=TEST_HTTPS_URL, brightness=101)

        # Verify that bad contrast is detected
        self.assertRaises(CyError, add_annotation_image, url=TEST_HTTPS_URL, contrast='bad')
        self.assertRaises(CyError, add_annotation_image, url=TEST_HTTPS_URL, contrast=-101)
        self.assertRaises(CyError, add_annotation_image, url=TEST_HTTPS_URL, contrast=101)

        # Verify that bad border thickness is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', border_thickness='bad')
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', border_thickness=-1)

        # Verify that bad border color is detected
        self.assertRaises(CyError, add_annotation_bounded_text, text='bad', border_color='red')

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
    def test_add_annotation_shape(self):
        EXPECTED_IMAGE_KEYS = {'edgeThickness', 'canvas', 'fillOpacity', 'rotation', 'type', 'uuid', 'shapeType',
                               'edgeColor', 'edgeOpacity', 'name', 'x', 'width', 'y', 'z', 'height'}
        EXPECTED_SHAPE_VALS = {'edgeThickness': '2.0', 'canvas': 'background', 'fillOpacity': '50.0',
                               'rotation': '45.0',
                               'type': 'org.cytoscape.view.presentation.annotations.ShapeAnnotation',
                               'fillColor': '#F0F0F0', 'shapeType': 'ELLIPSE', 'edgeColor': '#0F0F0F',
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

        # Verify that supplying additional parameters is reflected in an annotation, using both HTTP and HTTPS
        res = add_annotation_shape(type='ELLIPSE', custom_shape=None, x_pos=100, y_pos=200, angle=45,
                                   fill_color='#F0F0F0', opacity=50,
                                   border_thickness=2, border_color='#0F0F0F',
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
        self.assertRaises(CyError, add_annotation_shape, fill_color='red')

        # Verify that bad opacity is detected
        self.assertRaises(CyError, add_annotation_shape, opacity='bad')
        self.assertRaises(CyError, add_annotation_shape, opacity=-1)
        self.assertRaises(CyError, add_annotation_shape, opacity=101)

        # Verify that bad border thickness is detected
        self.assertRaises(CyError, add_annotation_shape, border_thickness='bad')
        self.assertRaises(CyError, add_annotation_shape, border_thickness=-1)

        # Verify that bad border color is detected
        self.assertRaises(CyError, add_annotation_shape, border_color='red')

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

    def _check_expected_values(self, target, expected_values):
        for k, v in expected_values.items():
            self.assertEqual(v, target[k], f'key={k} expected={v} actual={target[k]}')

    def _check_annotation_list(self, annotation_list, expected_len, expected_keys):
        self.assertIsInstance(annotation_list, list)
        self.assertEqual(len(annotation_list), expected_len)

        for ann in annotation_list:
            if not expected_keys.issubset(set(ann.keys())):
                raise Exception(f'Expected to find {expected_keys} in {ann}')

    def _load_2_networks(self):
        load_test_session()
        gal_filtered_suid = get_network_suid()
        yeast_high_quality_suid, yeast_high_quality_view_suid = load_test_network('data/yeastHighQuality.sif',
                                                                                  make_current=False)
        return gal_filtered_suid, yeast_high_quality_suid


if __name__ == '__main__':
    unittest.main()
