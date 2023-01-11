Announcement: py4cytoscape 1.6.0
---------------------------------

We're happy to announce the release of py4cytoscape 1.6.0!

py4cytoscape is a Python package that communicates with `Cytoscape <https://cytoscape.org>`_
via its `REST API <https://pubmed.ncbi.nlm.nih.gov/31477170/>`_, providing access to a set over 250 functions that
enable control of Cytoscape from within standalone and Notebook Python programming environments. It provides
nearly identical functionality to `RCy3 <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6880260/>`_, an R package in
Bioconductor available to R programmers.








Highlights
----------

The themes for this release are:

* Bug fixes and API additions to support Novartis' Metascape
* Enable use of color names wherever hex colors are allowed
* Support updated Python and Pandas libraries (for comparisons)
* Added environment variables for easier runtime configuration
* Better syntax checking for visual style properties and values
* Upgraded to support Cytoscape 3.10


API Changes
-----------

* Added names= to get_network_list
* Added create_cytoscapejs_from_network() and create_network_from_cytoscapejs()
* Added get_visual_style_JSON()
* Added delete_all_visual_styles()
* Added parameters in export_image() to support Cytoscape 3.10 export functions
* Added set_catchup_network_merge_secs() and PY4CYTOSCAPE_CATCHUP_NETWORK_MERGE_SECS environment variable to control post-merge delay
* Added select_edges_adjacent_to_nodes()

Deprecations
------------

* export_image() parameters (resolution=, units=, height=, width=) when calling Cytoscape 3.10 or later

Contributors to this release
----------------------------

- Barry Demchak
- Alex Pico
- Kozo Nishida
- Yingyao Zhou
- Yihang Xin


Pull requests merged in this release
------------------------------------

- #87 by Kozo Nashida


Issues closed in this release
------------------------------------

- #83 by Barry Demchak
- #84 by Barry Demchak
- #86 by Barry Demchak
- #87 by Yihang Xin
- #96 by Barry Demchak
- #97 by Kozo Nashida


