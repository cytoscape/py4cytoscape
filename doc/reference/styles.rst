.. _styles:

******
Styles
******

Basic Styles
------------

.. automodule:: py4cytoscape.styles

Style Management
================
.. autosummary::
   :toctree: generated/

   copy_visual_style
   create_visual_style
   delete_visual_style
   delete_all_visual_styles
   export_visual_styles
   get_current_style
   get_visual_style_JSON
   get_visual_style_names
   import_visual_styles
   set_visual_style

Visual Property Names and Values
================================
.. autosummary::
   :toctree: generated/

   get_arrow_shapes
   get_line_styles
   get_node_shapes
   get_visual_property_names

.. _styleautomappings:

Style Automatic Mappings
------------------------

.. automodule:: py4cytoscape.style_auto_mappings

Node Style Mapping Generators
=============================
.. autosummary::
   :toctree: generated/

   gen_node_color_map
   gen_node_height_map
   gen_node_opacity_map
   gen_node_shape_map
   gen_node_size_map
   gen_node_width_map

Edge Style Mapping Generators
=============================
.. autosummary::
   :toctree: generated/

   gen_edge_arrow_map
   gen_edge_color_map
   gen_edge_line_style_map
   gen_edge_opacity_map
   gen_edge_size_map
   gen_edge_width_map

Schemes for Discrete Shape and Numeric Generators
=================================================
.. autosummary::
   :toctree: generated/

   scheme_c_number_continuous
   scheme_d_arrow_shapes
   scheme_d_line_styles
   scheme_d_number_random
   scheme_d_number_series
   scheme_d_shapes

Palettes for Discrete (Qualitative) Color Generators
====================================================
.. autosummary::
   :toctree: generated/

   palette_color_brewer_q_Accent
   palette_color_brewer_q_Dark2
   palette_color_brewer_q_Paired
   palette_color_brewer_q_Pastel1
   palette_color_brewer_q_Pastel2
   palette_color_brewer_q_Set1
   palette_color_brewer_q_Set2
   palette_color_brewer_q_Set3
   palette_color_random

Palettes for One-Tailed Continuous (Sequential) Color Generators
================================================================
.. autosummary::
   :toctree: generated/

   palette_color_brewer_s_Blues
   palette_color_brewer_s_BuGn
   palette_color_brewer_s_BuPu
   palette_color_brewer_s_GnBu
   palette_color_brewer_s_Greens
   palette_color_brewer_s_Greys
   palette_color_brewer_s_Oranges
   palette_color_brewer_s_OrRd
   palette_color_brewer_s_PuBu
   palette_color_brewer_s_PuBuGn
   palette_color_brewer_s_RdPu
   palette_color_brewer_s_PuRd
   palette_color_brewer_s_Purples
   palette_color_brewer_s_Reds
   palette_color_brewer_s_YlGn
   palette_color_brewer_s_YlGnBu
   palette_color_brewer_s_YlOrBr
   palette_color_brewer_s_YlOrRd

Palettes for Two-Tailed Continuous (Diverging) Color Generators
===============================================================
.. autosummary::
   :toctree: generated/

   palette_color_brewer_d_BrBG
   palette_color_brewer_d_PiYG
   palette_color_brewer_d_PRGn
   palette_color_brewer_d_PuOr
   palette_color_brewer_d_RdBu
   palette_color_brewer_d_RdGy
   palette_color_brewer_d_RdYlBu
   palette_color_brewer_d_RdYlGn
   palette_color_brewer_d_Spectral

.. _stylebypasses:

Style Bypasses
--------------

.. automodule:: py4cytoscape.style_bypasses


General Style Bypasses
======================
.. autosummary::
   :toctree: generated/

   set_node_property_bypass
   set_edge_property_bypass

Node Style Bypasses
===================
.. autosummary::
   :toctree: generated/

   clear_node_opacity_bypass
   clear_node_property_bypass
   hide_nodes
   hide_selected_nodes
   set_node_border_color_bypass
   set_node_border_opacity_bypass
   set_node_border_width_bypass
   set_node_color_bypass
   set_node_fill_opacity_bypass
   set_node_font_face_bypass
   set_node_font_size_bypass
   set_node_height_bypass
   set_node_label_bypass
   set_node_label_color_bypass
   set_node_label_opacity_bypass
   set_node_opacity_bypass
   set_node_position_bypass
   set_node_label_position_bypass
   set_node_shape_bypass
   set_node_size_bypass
   set_node_tooltip_bypass
   set_node_width_bypass
   unhide_nodes

Edge Style Bypasses
===================
.. autosummary::
   :toctree: generated/

   clear_edge_property_bypass
   hide_edges
   hide_selected_edges
   set_edge_color_bypass
   set_edge_font_face_bypass
   set_edge_font_size_bypass
   set_edge_label_bypass
   set_edge_label_color_bypass
   set_edge_label_opacity_bypass
   set_edge_line_style_bypass
   set_edge_line_width_bypass
   set_edge_opacity_bypass
   set_edge_source_arrow_color_bypass
   set_edge_source_arrow_shape_bypass
   set_edge_target_arrow_color_bypass
   set_edge_target_arrow_shape_bypass
   set_edge_tooltip_bypass
   unhide_edges

Network Style Bypasses
======================
.. autosummary::
   :toctree: generated/

   clear_network_center_bypass
   clear_network_property_bypass
   clear_network_zoom_bypass
   set_network_center_bypass
   set_network_property_bypass
   set_network_zoom_bypass
   unhide_all

.. _styledefaults:

Style Defaults
--------------

.. automodule:: py4cytoscape.style_defaults

General Style Defaults
======================
.. autosummary::
   :toctree: generated/

   get_visual_property_default
   set_visual_property_default
   update_style_defaults

Custom Graphics
===============
.. autosummary::
   :toctree: generated/

   remove_node_custom_graphics
   set_node_custom_bar_chart
   set_node_custom_box_chart
   set_node_custom_heat_map_chart
   set_node_custom_line_chart
   set_node_custom_linear_gradient
   set_node_custom_pie_chart
   set_node_custom_position
   set_node_custom_radial_gradient
   set_node_custom_ring_chart

Node Style Defaults
===================
.. autosummary::
   :toctree: generated/

   get_node_label_position_default
   get_node_selection_color_default
   set_node_border_color_default
   set_node_border_opacity_default
   set_node_border_width_default
   set_node_color_default
   set_node_fill_opacity_default
   set_node_font_face_default
   set_node_font_size_default
   set_node_height_default
   set_node_label_color_default
   set_node_label_default
   set_node_label_opacity_default
   set_node_label_position_default
   set_node_selection_color_default
   set_node_shape_default
   set_node_size_default
   set_node_tooltip_default
   set_node_width_default

Edge Style Defaults
===================
.. autosummary::
   :toctree: generated/

   get_edge_selection_color_default
   set_edge_color_default
   set_edge_font_face_default
   set_edge_font_size_default
   set_edge_label_color_default
   set_edge_label_default
   set_edge_label_opacity_default
   set_edge_line_style_default
   set_edge_line_width_default
   set_edge_opacity_default
   set_edge_selection_color_default
   set_edge_source_arrow_color_default
   set_edge_source_arrow_shape_default
   set_edge_target_arrow_color_default
   set_edge_target_arrow_shape_default
   set_edge_tooltip_default


Network Style Defaults
======================
.. autosummary::
   :toctree: generated/

   get_background_color_default
   set_background_color_default

.. _styledependencies:

Style Dependencies
------------------

.. automodule:: py4cytoscape.style_dependencies

General Style Dependencies
==========================
.. autosummary::
   :toctree: generated/

   get_style_dependencies
   set_style_dependencies

Custom Graphics
===============
.. autosummary::
   :toctree: generated/

    sync_node_custom_graphics_size

Node Style Dependencies
=======================
.. autosummary::
   :toctree: generated/

   lock_node_dimensions

Edge Style Dependencies
=======================
.. autosummary::
   :toctree: generated/

   match_arrow_color_to_edge

.. _stylemappings:

Style Mappings
--------------

.. automodule:: py4cytoscape.style_mappings

General Style Mappings
======================
.. autosummary::
   :toctree: generated/

   delete_style_mapping
   get_style_all_mappings
   get_style_mapping
   map_visual_property
   update_style_mapping

Node Style Mappings
===================
.. autosummary::
   :toctree: generated/

   set_node_border_color_mapping
   set_node_border_opacity_mapping
   set_node_border_width_mapping
   set_node_color_mapping
   set_node_combo_opacity_mapping
   set_node_fill_opacity_mapping
   set_node_font_face_mapping
   set_node_font_size_mapping
   set_node_height_mapping
   set_node_label_color_mapping
   set_node_label_mapping
   set_node_label_opacity_mapping
   set_node_shape_mapping
   set_node_size_mapping
   set_node_tooltip_mapping
   set_node_width_mapping

Edge Style Mappings
===================
.. autosummary::
   :toctree: generated/

   set_edge_color_mapping
   set_edge_font_face_mapping
   set_edge_font_size_mapping
   set_edge_label_color_mapping
   set_edge_label_mapping
   set_edge_label_opacity_mapping
   set_edge_line_style_mapping
   set_edge_line_width_mapping
   set_edge_opacity_mapping
   set_edge_source_arrow_color_mapping
   set_edge_source_arrow_mapping
   set_edge_source_arrow_shape_mapping
   set_edge_target_arrow_color_mapping
   set_edge_target_arrow_maping
   set_edge_target_arrow_shape_mapping
   set_edge_tooltip_mapping

.. _stylevalues:

Style Values
------------

.. automodule:: py4cytoscape.style_values

Node Style Values
=================
.. autosummary::
   :toctree: generated/

   get_node_color
   get_node_height
   get_node_label_position
   get_node_position
   get_node_property
   get_node_size
   get_node_width

Edge Style Values
=================
.. autosummary::
   :toctree: generated/

   get_edge_color
   get_edge_line_style
   get_edge_line_width
   get_edge_property
   get_edge_target_arrow_shape

Network Style Values
====================
.. autosummary::
   :toctree: generated/

   get_network_center
   get_network_property
   get_network_zoom

