
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
* Documentation improvements


Release notes
~~~~~~~~~~~~~

* Updated style functions to propagate base_url parameters where needed
* Removed incompatibilities with Python 3.13.2
* Fixed add_annotation_image mishandling of URL when it specified a local file
* Added Setting X-Y Coordinates to Concepts section of user manual
* Added better file: scheme handling for images in add_annotation_image() and update_annotation_image()


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
- Carissa Bleker


Pull requests merged in this release
------------------------------------

- Add pull requests here (e.g., #140 by Barry Demchak)

Issues closed in this release
------------------------------------

- #144 by Barry Demchak, Carissa Bleker
- #131 by Barry Demchak, Carissa Bleker
- #147 by Barry Demchak
- #148 by Barry Demchak, Carissa Bleker


