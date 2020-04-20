# -*- coding: utf-8 -*-

import unittest

from test_utils import *

class LayoutsTests(unittest.TestCase):
    def setUp(self):
        try:
            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass


#    @skip
    @print_entry_exit
    def test_layout_network(self):
        # Initialize

        load_test_session()
        load_test_network('data/yeastHighQuality.sif', make_current=False)
        cur_network_suid = get_network_suid()

        # Execute default layout ... should happen on galFiltered.sif
        self.assertDictEqual(layout_network(), {})
        # To verify, operator should eyeball the network in Cytoscape

        # Execute grid layout ... should happen on yeastHighQuality.sif
        self.assertDictEqual(layout_network('grid', 'yeastHighQuality.sif'), {})
        self.assertEqual(get_network_suid(), cur_network_suid)
        # To verify, operator should eyeball the network in Cytoscape

        # Execute bogus layout
        self.assertRaises(CyError, layout_network, 'bogus')
        self.assertEqual(get_network_suid(), cur_network_suid)

#    @skip
    @print_entry_exit
    def test_bundle_edges(self):
        # Initialize
        load_test_session()
        load_test_network('data/yeastHighQuality.sif', make_current=False)
        cur_network_suid = get_network_suid()

        # Bundle edges ... should happen on galFiltered.sif
        self.assertDictEqual(bundle_edges(), {'message': 'Edge bundling success.'})
        # To verify, operator should eyeball the network in Cytoscape

        # Bundle edges ... should happen on yeastHighQuality.sif
        self.assertDictEqual(bundle_edges('yeastHighQuality.sif'), {'message': 'Edge bundling success.'})
        self.assertEqual(get_network_suid(), cur_network_suid)
        # To verify, operator should eyeball the network in Cytoscape

#    @skip
    @print_entry_exit
    def test_clear_edge_bends(self):
        # Initialize
        load_test_session()
        load_test_network('data/yeastHighQuality.sif', make_current=False)
        cur_network_suid = get_network_suid()

        # Bundle then unbundle edges ... should happen on galFiltered.sif
        self.assertDictEqual(bundle_edges(), {'message': 'Edge bundling success.'})
        self.assertDictEqual(clear_edge_bends(), {'message': 'Clear all edge bends success.'})
        # To verify, operator should eyeball the network in Cytoscape

        # Bundle edges ... should happen on yeastHighQuality.sif
        self.assertDictEqual(bundle_edges('yeastHighQuality.sif'), {'message': 'Edge bundling success.'})
        self.assertDictEqual(clear_edge_bends('yeastHighQuality.sif'), {'message': 'Clear all edge bends success.'})
        self.assertEqual(get_network_suid(), cur_network_suid)
        # To verify, operator should eyeball the network in Cytoscape

#    @skip
    @print_entry_exit
    def test_layout_copycat(self):
        # Initialize
        load_test_session()
        orig_suid = get_network_suid()
        cloned_suid = clone_network()

        # Verify that the basic copycat works by laying out clone in a grid, then returning it to original
        self.assertDictEqual(layout_network('grid', cloned_suid), {})
        self.assertDictEqual(layout_copycat(orig_suid, cloned_suid), {'mappedNodeCount': 330, 'unmappedNodeCount': 0})
        # To verify, operator should eyeball the network in Cytoscape

        # Verify that there are no unmapped nodes when we tell copycat to ignore them
        self.assertDictEqual(layout_network('grid', cloned_suid), {})
        self.assertDictEqual(layout_copycat('galFiltered.sif', 'galFiltered.sif_1', grid_unmapped=False, select_unmapped=False), {'mappedNodeCount': 330, 'unmappedNodeCount': 0})
        # To verify, operator should eyeball the network in Cytoscape

        # Verify that the copycat unmatched nodes work by removing original nodes, laying out clone in a grid, then returning it to original
        # TODO: Implement this when we have APIs for deleting nodes

#    @skip
    @print_entry_exit
    def test_get_layout_names(self):
        required_layouts = set(['attribute-circle', 'stacked-node-layout', 'degree-circle', 'circular', 'attributes-layout', 'kamada-kawai', 'force-directed', 'cose', 'grid', 'hierarchical', 'fruchterman-rheingold', 'isom'])
        found_layouts = set(get_layout_names())
        self.assertTrue(found_layouts.issuperset(required_layouts))

#    @skip
    @print_entry_exit
    def test_get_layout_name_mapping(self):
        required_layouts = {'Attribute Circle Layout': 'attribute-circle', 'Stacked Node Layout': 'stacked-node-layout', 'Degree Sorted Circle Layout': 'degree-circle', 'Circular Layout': 'circular', 'Group Attributes Layout': 'attributes-layout', 'Edge-weighted Spring Embedded Layout': 'kamada-kawai', 'Prefuse Force Directed Layout': 'force-directed', 'Compound Spring Embedder (CoSE)': 'cose', 'Grid Layout': 'grid', 'Hierarchical Layout': 'hierarchical', 'Edge-weighted Force directed (BioLayout)': 'fruchterman-rheingold', 'Inverted Self-Organizing Map Layout': 'isom'}
        required_keys = set(required_layouts.keys())

        # Verify that all expected gui layout names are present, and that the layout names are what's expected
        found_layouts = get_layout_name_mapping()
        found_keys = set(found_layouts.keys())
        self.assertTrue(found_keys.issuperset(required_keys))
        self.assertFalse(False in [found_layouts[gui_layout_name] == required_layouts[gui_layout_name]    for gui_layout_name in required_layouts])

#    @skip
    @print_entry_exit
    def test_get_layout_property_names(self):
        layouts = {'force-directed': set(['numIterations', 'defaultSpringCoefficient', 'defaultSpringLength', 'defaultNodeMass', 'isDeterministic', 'singlePartition']),
                   'attribute-circle': set(['spacing', 'singlePartition'])}

        # Verify that the parameter names for some layouts return as expected
        for layout, params in layouts.items():
            found_params = set(get_layout_property_names(layout))
            self.assertSetEqual(params, found_params)

        self.assertRaises(CyError, get_layout_property_names, 'boguslayout')

#    @skip
    @print_entry_exit
    def test_get_layout_property_type(self):
        layouts = {'force-directed': [('numIterations', 'int'), ('defaultSpringCoefficient', 'double'), ('defaultSpringLength', 'double'), ('defaultNodeMass', 'double'), ('isDeterministic', 'boolean'), ('singlePartition', 'boolean')],
                   'attribute-circle': [('spacing', 'double'), ('singlePartition', 'boolean')]}

        # Verify that the parameter types for some layouts return as expected
        for layout, params in layouts.items():
            for param_def in params:
                self.assertEqual(get_layout_property_type(layout, param_def[0]), param_def[1])

        self.assertRaises(CyError, get_layout_property_type, 'boguslayout', 'bogusparam')
        self.assertRaises(KeyError, get_layout_property_type, 'force-directed', 'bogusparam')

#    @skip
    @print_entry_exit
    def test_get_layout_property_value(self):
        layouts = {'force-directed': [('numIterations', '100'), ('defaultSpringCoefficient', '0.0001'), ('defaultSpringLength', '50.0'), ('defaultNodeMass', '3.0'), ('isDeterministic', 'False'), ('singlePartition', 'False')],
                   'attribute-circle': [('spacing', '100.0'), ('singlePartition', 'False')]}

        # Verify that the parameter values for some layouts return as expected
        for layout, params in layouts.items():
            for param_def in params:
                self.assertEqual(str(get_layout_property_value(layout, param_def[0])), param_def[1])

        self.assertRaises(CyError, get_layout_property_value, 'boguslayout', 'bogusparam')
        self.assertRaises(KeyError, get_layout_property_value, 'force-directed', 'bogusparam')

#    @skip
    @print_entry_exit
    def test_set_layout_properties(self):
        # This is tricky ... short of restarting Cytoscape, there doesn't appear to be a way of starting with fresh
        # copies of layout properties. So, when testing, set layout properties to new values, but be sure to set
        # them back to their originals.
        orig_default_spring_length = get_layout_property_value('force-directed', 'defaultSpringLength')
        NEW_DEFAULT_SPRING_LENGTH = 5
        orig_default_spring_coefficient = get_layout_property_value('force-directed', 'defaultSpringCoefficient')
        NEW_DEFAULT_SPRING_COEFFICIENT = 6E-01

        self.assertEqual(set_layout_properties('force-directed', {'defaultSpringLength':NEW_DEFAULT_SPRING_LENGTH, 'defaultSpringCoefficient':NEW_DEFAULT_SPRING_COEFFICIENT}), '')
        self.assertEqual(get_layout_property_value('force-directed', 'defaultSpringLength'), NEW_DEFAULT_SPRING_LENGTH)
        self.assertEqual(get_layout_property_value('force-directed', 'defaultSpringCoefficient'), NEW_DEFAULT_SPRING_COEFFICIENT)

        self.assertEqual(set_layout_properties('force-directed', {'defaultSpringLength':orig_default_spring_length, 'defaultSpringCoefficient':orig_default_spring_coefficient}), '')
        self.assertEqual(get_layout_property_value('force-directed', 'defaultSpringLength'), orig_default_spring_length)
        self.assertEqual(get_layout_property_value('force-directed', 'defaultSpringCoefficient'), orig_default_spring_coefficient)

        self.assertRaises(CyError, set_layout_properties, 'boguslayout', {})
        self.assertEqual(set_layout_properties('force-directed', {'bogusparam':666}), '')

if __name__ == '__main__':
    unittest.main()