Announcement: py4cytoscape 0.0.1
--------------------------------

We're happy to announce the release of py4cytoscape 0.0.3!

py4cytoscape is a Python package that communicates with `Cytoscape <https://cytoscape.org>`_
via its `REST API <https://pubmed.ncbi.nlm.nih.gov/31477170/>`_, providing access to a set over 250 functions that
enable control of Cytoscape from within standalone and Notebook Python programming environments. It provides
nearly identical functionality to `RCy3 <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6880260/>`_, an R package in
Bioconductor available to R programmers.


Highlights
----------

This themes for this release are:

* Reproduce RCy3 functions
* Create a testing system for all functions
* Create the py4cytoscape user documentation

API Changes
-----------

None

Deprecations
------------

None

Contributors to this release
----------------------------

- Barry Demchak
- Alex Pico
- Kozo Nashida
- Jorge Bouças
- Stevan Georg
- Chris Churas

Pull requests merged in this release
------------------------------------

- Set dependencies #10
- Fixed broken link to the tutorials page on readthedocs #9
- In the Verify Cytoscape connection code fragment made file path platform agnostic #8
- Add how to try tutorial without installation (by using Binder) #6
- Add a tutorial ipynb file to the Sphinx source #5
- Move python-igraph from extras_require to install_requires #4
- Rename the package name #3
- Add How to install and use #2
