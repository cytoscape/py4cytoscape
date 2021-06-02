Announcement: py4cytoscape 0.0.9
--------------------------------

We're happy to announce the release of py4cytoscape 0.0.9!

py4cytoscape is a Python package that communicates with `Cytoscape <https://cytoscape.org>`_
via its `REST API <https://pubmed.ncbi.nlm.nih.gov/31477170/>`_, providing access to a set over 250 functions that
enable control of Cytoscape from within standalone and Notebook Python programming environments. It provides
nearly identical functionality to `RCy3 <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6880260/>`_, an R package in
Bioconductor available to R programmers.


Highlights
----------

This themes for this release are:

* Improved documentation and tutorials
* Improved iGraph support (consistent with RCy3)
* Allow edge direction to be ignored when deleting duplicate edges
* Automatic value generators (including Brewer colors) for style mappings

Many of these themes support the definition and execution of the GangSu workflows.

API Changes
-----------

* Added style_auto_mappers.py module to support automatic value generators
* Added ignore_direction=False parameter for delete_duplicate_edges
* Added unique_list=True to node/edge_name_to_suid utility functions
* Added Value Generators section in Concepts documentation
* Added iGraph support for Graph, DiGraph, MultiGraph, MultiDiGraph in create_network_from_networkx

Deprecations
------------

None

Contributors to this release
----------------------------

- Barry Demchak
- Yihang Xin
- Alex Pico
- Kozo Nishida

Pull requests merged in this release
------------------------------------
- #46 by Kozo Nishida
- #47 by Kozo Nishida
- #48 by Kozo Nishida
- #50 by Kozo Nishida
- #51 by Kozo Nishida

Issues closed in this release
------------------------------------

- #41 by Alex Pico
- #43 by Barry Demchak
- #45 by Kozo Nishida
- #49 by Jiafi


