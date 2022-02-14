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
        self._check_annotation_list(res, 0)

        # Create an annotation in current network (gal_filtered) and verify that the annotation is returned in the list
        add_annotation_text(name='ann1', text='ann1 text')
        res = get_annotation_list()
        self._check_annotation_list(res, 1)
        ann1 = find_name('ann1', res)
        self.assertEqual(ann1['text'], 'ann1 text')

        # Verify that the annotation is present if gal_filtered is queried
        res = get_annotation_list(gal_filtered_suid)
        self._check_annotation_list(res, 1)
        ann1 = find_name('ann1', res)
        self.assertEqual(ann1['text'], 'ann1 text')

        # Verify that no annotations are in yeast_high_quality
        res = get_annotation_list(yeast_high_quality_suid)
        self._check_annotation_list(res, 0)

        # Verify that if two annotations are added to yeast_high_quality, they can be fetched
        add_annotation_text(network=yeast_high_quality_suid, name='ann10', text='ann10 text')
        add_annotation_text(network=yeast_high_quality_suid, name='ann11', text='ann11 text')
        res = get_annotation_list(yeast_high_quality_suid)
        self._check_annotation_list(res, 2)
        ann10 = find_name('ann10', res)
        ann11 = find_name('ann11', res)
        self.assertEqual(ann10['text'], 'ann10 text')
        self.assertEqual(ann11['text'], 'ann11 text')

        # Verify that the single annotation is still present if gal_filtered is queried
        res = get_annotation_list(gal_filtered_suid)
        self._check_annotation_list(res, 1)
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
        self._check_annotation_list(res1, 1)
        self.assertDictEqual(res, res1[0])

        # Verify that adding a second annotation (explicitly naming the network) also works
        res = add_annotation_text(network=gal_filtered_suid, text='ann2')
        res1 = get_annotation_list(network=gal_filtered_suid)
        self._check_annotation_list(res1, 2)

        # Verify that nothing was added to the other network
        self._check_annotation_list(get_annotation_list(network=yeast_high_quality_suid), 0)

        # Verify that supplying additional parameters is reflected in an annotation
        res = add_annotation_text(text='ann3', x_pos=100, y_pos=200, font_size=25, font_family='Courier New', font_style='bold', color='#F0F0F0', angle=45, name='ann3 name', canvas='background')
        self._check_expected_values(res, {'canvas': 'background', 'color': '#F0F0F0', 'rotation': '45.0', 'fontStyle': 'bold', 'fontFamily': 'Courier New', 'name': 'ann3 name', 'x': '100.0', 'y': '200.0', 'fontSize': '25', 'text': 'ann3'})

        # Verify that angle is properly normalized
        res = add_annotation_text(text='ann4', angle=181)
        self.assertEqual(res['rotation'], '-179.0')
        res = add_annotation_text(text='ann4', angle=180)
        self.assertEqual(res['rotation'], '180.0')
        res = add_annotation_text(text='ann4', angle=-180)
        self.assertEqual(res['rotation'], '-180.0')
        res = add_annotation_text(text='ann4', angle=-181)
        self.assertEqual(res['rotation'], '179.0')
        res = add_annotation_text(text='ann4', angle=1980)
        self.assertEqual(res['rotation'], '180.0')
        res = add_annotation_text(text='ann4', angle=-1980)
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


    def _check_expected_values(self, target, expected_values):
        for k, v in expected_values.items():
            self.assertEqual(v, target[k])

    def _check_annotation_list(self, annotation_list, expected_len):
        self.assertIsInstance(annotation_list, list)
        self.assertEqual(len(annotation_list), expected_len)

        expected_keys = {'canvas', 'color', 'rotation', 'type', 'fontStyle', 'uuid', 'fontFamily', 'name', 'x', 'y',
                         'z', 'fontSize', 'text'}
        for ann in annotation_list:
            if not expected_keys.issubset(set(ann.keys())):
                raise Exception(f'Expected to find {expected_keys} in {ann}')

    def _load_2_networks(self):
        load_test_session()
        gal_filtered_suid = get_network_suid()
        yeast_high_quality_suid, yeast_high_quality_view_suid = load_test_network('data/yeastHighQuality.sif', make_current=False)
        return gal_filtered_suid, yeast_high_quality_suid

if __name__ == '__main__':
    unittest.main()
