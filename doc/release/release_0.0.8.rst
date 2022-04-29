Announcement: py4cytoscape 0.0.8
--------------------------------

We're happy to announce the release of py4cytoscape 0.0.8!

py4cytoscape is a Python package that communicates with `Cytoscape <https://cytoscape.org>`_
via its `REST API <https://pubmed.ncbi.nlm.nih.gov/31477170/>`_, providing access to a set over 250 functions that
enable control of Cytoscape from within standalone and Notebook Python programming environments. It provides
nearly identical functionality to `RCy3 <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6880260/>`_, an R package in
Bioconductor available to R programmers.


Highlights
----------

The themes for this release are:

* Enable access to NDEx subdomains
* Support Cytoscape v3.9 separation of filter definition from execution
* Enable export functions to avoid popping a confirmation dialog
* Enable cloud files to be downloaded directly to Sandbox
* Fixes that allow commands_help to work

Many of these themes support the definition and execution of the GangSu workflows.

API Changes
-----------

* Added parameters in CyNDEX functions to support subdomains
* Added apply= parameter in filter definition functions to support Cytoscape v3.9.0 separating apply from definition
* Added overwrite_file parameter to export functions
* Added Sandbox direct download from URL
* Added functions for import network from tabular file & get current style, etc

Deprecations
------------

None

Contributors to this release
----------------------------

- Barry Demchak
- Yihang Xin
- Alex Pico

Pull requests merged in this release
------------------------------------

