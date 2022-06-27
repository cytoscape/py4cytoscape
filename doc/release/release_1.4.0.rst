Announcement: py4cytoscape 1.4.0
---------------------------------

We're happy to announce the release of py4cytoscape 1.4.0!

py4cytoscape is a Python package that communicates with `Cytoscape <https://cytoscape.org>`_
via its `REST API <https://pubmed.ncbi.nlm.nih.gov/31477170/>`_, providing access to a set over 250 functions that
enable control of Cytoscape from within standalone and Notebook Python programming environments. It provides
nearly identical functionality to `RCy3 <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6880260/>`_, an R package in
Bioconductor available to R programmers.


Highlights
----------

The themes for this release are:

* Supporting Metascape migration from py2cytoscape to py4cytoscape
* Added sandbox support when Cytoscape is at URL different than 127.0.0.1
* Fixed bugs for calling Cytoscape at URL different than 127.0.0.1


API Changes
-----------

* Added names= to get_network_list
* Added create_cytoscapejs_from_network and create_network_from_cytoscapejs
* Added get_visual_style_JSON
* Added delete_all_visual_styles

Deprecations
------------

None

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


