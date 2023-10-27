Announcement: py4cytoscape 1.9.0
---------------------------------

We're happy to announce the release of py4cytoscape 1.9.0!

py4cytoscape is a Python package that communicates with `Cytoscape <https://cytoscape.org>`_
via its `REST API <https://pubmed.ncbi.nlm.nih.gov/31477170/>`_, providing access to a set over 250 functions that
enable control of Cytoscape from within standalone and Notebook Python programming environments. It provides
nearly identical functionality to `RCy3 <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6880260/>`_, an R package in
Bioconductor available to R programmers.








Highlights
----------

The themes for this release are:

* General bug fixes
* New Style functions for node label position and node position
* Improved Cytoscape version check



API Changes
-----------

Added:

set_node_position_bypass(node_names, new_x_locations=None, new_y_locations=None, network=None, base_url=DEFAULT_BASE_URL)

set_node_label_position_bypass(node_names, new_positions, network=None, base_url=DEFAULT_BASE_URL)

get_node_label_position_default(style_name=None, base_url=DEFAULT_BASE_URL)

set_node_label_position_default(new_node_anchor, new_graphic_anchor, new_justification, new_xoffset, new_yoffset, style_name=None, base_url=DEFAULT_BASE_URL)

get_node_label_position(node_names=None, network=None, base_url=DEFAULT_BASE_URL)

Deprecations
------------


Contributors to this release
----------------------------

- Barry Demchak
- Yihang Xin


Pull requests merged in this release
------------------------------------

- ... add pull request here: #xxx by yyy


Issues closed in this release
------------------------------------

- #125 by Barry Demchak
- #122 by Barry Demchak


