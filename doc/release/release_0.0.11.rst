Announcement: py4cytoscape 0.0.11
---------------------------------

We're happy to announce the release of py4cytoscape 0.0.11!

py4cytoscape is a Python package that communicates with `Cytoscape <https://cytoscape.org>`_
via its `REST API <https://pubmed.ncbi.nlm.nih.gov/31477170/>`_, providing access to a set over 250 functions that
enable control of Cytoscape from within standalone and Notebook Python programming environments. It provides
nearly identical functionality to `RCy3 <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6880260/>`_, an R package in
Bioconductor available to R programmers.


Highlights
----------

The themes for this release are:

* Improved documentation and tutorials
* Improved Automatic value generators support for style mapping (consistent with RCy3)
* Improved support for Notebook initialization and image display

Many of these themes support the definition and execution of the GangSu workflows.

API Changes
-----------

* Added reverse= parameter for Value Generators
* Automatically reverse color sequence for divergent palettes
* Added notebook_show_image(), notebook_export_show_image() functions for Notebook execution

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

- #51 by Kozo Nishida
- #53 by Kozo Nishida
- #55 by Kozo Nishida
- #58 by Kozo Nishida
- #59 by Kozo Nishida
- #60 by Kozo Nishida
- #61 by Kozo Nishida
- #63 by Kozo Nishida
- #64 by Kozo Nishida
- #65 by Kozo Nishida
- #66 by Kozo Nishida
- #68 by Kozo Nishida


Issues closed in this release
------------------------------------

- #52 by StefanR-github
- #56 by Kozo Nishida
- #57 by Rafael Diaz
- #62 by Alex Pico


