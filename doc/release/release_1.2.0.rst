Announcement: py4cytoscape 1.2.0
---------------------------------

We're happy to announce the release of py4cytoscape 1.2.0!

py4cytoscape is a Python package that communicates with `Cytoscape <https://cytoscape.org>`_
via its `REST API <https://pubmed.ncbi.nlm.nih.gov/31477170/>`_, providing access to a set over 250 functions that
enable control of Cytoscape from within standalone and Notebook Python programming environments. It provides
nearly identical functionality to `RCy3 <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6880260/>`_, an R package in
Bioconductor available to R programmers.


Highlights
----------

The themes for this release are:

* Addition of annotation functions (per new Cytoscape features)
* Changed default for sandboxing when running Notebook on local Workstation
* Add new functions: create_view, select_all
* Sped up select_all_nodes, select_all_edges

API Changes
-----------

* Added annotation functions
* Added create_view in network_views
* Added select_all in network_selection
* Changed get_network_view_suid to return None instead of exception when network has no view
* Changed get_network_views to return [] instead of exception when network has no view

Deprecations
------------

None

Contributors to this release
----------------------------

- Barry Demchak
- Yihang Xin
- Alex Pico
- Kozo Nishida
- Nilsoberg2

Pull requests merged in this release
------------------------------------

- #72 by Nilsoberg2


Issues closed in this release
------------------------------------

- #40 by kyxhik
- #54 by pkzerel
- #67 by Kozo Nishida
- #71 by Nilsoberg2
- #73 by Barry Demchak
- #75 by Barry Demchak
- #76 by Yihang Xin
- #77 by Eirinland


