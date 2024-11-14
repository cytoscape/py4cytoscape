
py4cytoscape 1.12.0
-------------------
Release date: dd mmm yyyy

We're happy to announce the release of py4cytoscape 1.12.0!

py4cytoscape is a Python package that communicates with `Cytoscape <https://cytoscape.org>`_
via its `REST API <https://pubmed.ncbi.nlm.nih.gov/31477170/>`_, providing access to a set over 250 functions that
enable control of Cytoscape from within standalone and Notebook Python programming environments. It provides
nearly identical functionality to `RCy3 <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6880260/>`_, an R package in
Bioconductor available to R programmers.

The themes for this release are:

* Bug fixes


Release notes
~~~~~~~~~~~~~

* Updated style functions to propagate base_url parameters where needed


API Changes
-----------

Added:

* Added base_url=DEFAULT_BASE_URL parameter to style_auto_mappings.py functions (scheme_d_shapes(), scheme_d_line_styles(), and scheme_d_arrow_shapes())


Deprecations
------------

* Add deprecations here


Contributors to this release
----------------------------

- Barry Demchak
- Stephan Grein


Pull requests merged in this release
------------------------------------

- Add pull requests here (e.g., #140 by Barry Demchak)

Issues closed in this release
------------------------------------

- #147 by Barry Demchak

