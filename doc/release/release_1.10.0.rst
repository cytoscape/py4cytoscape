
py4cytoscape 1.10.0
-------------------
Release date: dd mmm yyyy

We're happy to announce the release of py4cytoscape 1.10.0!

py4cytoscape is a Python package that communicates with `Cytoscape <https://cytoscape.org>`_
via its `REST API <https://pubmed.ncbi.nlm.nih.gov/31477170/>`_, providing access to a set over 250 functions that
enable control of Cytoscape from within standalone and Notebook Python programming environments. It provides
nearly identical functionality to `RCy3 <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6880260/>`_, an R package in
Bioconductor available to R programmers.

The themes for this release are:

* Add missing parameters to enable non-default base_url
* Add documentation & checks for large commands

Release notes
~~~~~~~~~~~~~

* Added base_url parameter propagation in filters, networks and tables functions
* Add documentation & check for outsize commands_run and commands_get requests


API Changes
-----------

Added:

... add new function signatures here ...



Deprecations
------------

... add deprecated function signatures here ...

Contributors to this release
----------------------------

- Barry Demchak
- Harsh Sharma


Pull requests merged in this release
------------------------------------

- ... add pull request numbers here ...

Issues closed in this release
------------------------------------

- #137 by Harsh Sharma
- #135 by Minghao Gong
- #127 by Athina Gavriilidou


