
py4cytoscape 1.9.0
-------------------
Release date: 26 Dec 2023

We're happy to announce the release of py4cytoscape 1.9.0!

py4cytoscape is a Python package that communicates with `Cytoscape <https://cytoscape.org>`_
via its `REST API <https://pubmed.ncbi.nlm.nih.gov/31477170/>`_, providing access to a set over 250 functions that
enable control of Cytoscape from within standalone and Notebook Python programming environments. It provides
nearly identical functionality to `RCy3 <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6880260/>`_, an R package in
Bioconductor available to R programmers.

The themes for this release are:

* General bug fixes
* New Style functions for node label position and node position
* Improved Cytoscape version check
* Added scale and rotate functions

Release notes
~~~~~~~~~~~~~

* Removed value validation warning from set_visual_property_default()
* Fixed missing URL parameter in create_network_from_data_frames() and create_network_from_networkx()
* Added style functions for node_position and node_label_position
* Allowed Cytoscape version check to include patch level (e.g., x.y.patch)
* Added layout functions scale_layout() and rotate_layout() to match Cytoscape's Layout Tools


API Changes
-----------

Added:

set_node_position_bypass(node_names, new_x_locations=None, new_y_locations=None, network=None, base_url=DEFAULT_BASE_URL)

set_node_label_position_bypass(node_names, new_positions, network=None, base_url=DEFAULT_BASE_URL)

get_node_label_position_default(style_name=None, base_url=DEFAULT_BASE_URL)

set_node_label_position_default(new_node_anchor, new_graphic_anchor, new_justification, new_xoffset, new_yoffset, style_name=None, base_url=DEFAULT_BASE_URL)

get_node_label_position(node_names=None, network=None, base_url=DEFAULT_BASE_URL)

scale_layout(axis, scale_factor, network=None, selected_only=False, base_url=DEFAULT_BASE_URL)

rotate_layout(angle, network=None, selected_only=False, base_url=DEFAULT_BASE_URL)


Deprecations
------------


Contributors to this release
----------------------------

- Barry Demchak
- Yihang Xin


Pull requests merged in this release
------------------------------------


Issues closed in this release
------------------------------------

- #125 by Barry Demchak
- #124 by Barry Demchak
- #123 by Barry Demchak
- #122 by Barry Demchak
- #121 by Minghao Gong
- #119 by Minghao Gong
- #118 by Minghao Gong
- #117 by Minghao Gong
- #116 by Minghao Gong
- #115 by Minghao Gong
- #113 by Jack Hart
- #111 by Minghao Gong
- #110 by Minghao Gong
- #109 by Minghao Gong
- #108 by Minghao Gong


