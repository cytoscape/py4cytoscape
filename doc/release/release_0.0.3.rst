Announcement: py4cytoscape 0.0.3
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

* Add support for remote Notebook execution (via Jupyter-Bridge)
* Sync with changes made to RCy3 since Jan 1, 2020

Remote Notebook execution involves a round trip between the Python kernel running on a
remote server and Cytoscape running on a private workstation. The main component is
`Jupyter-Bridge <https://github.com/cytoscape/jupyter-bridge>`_, which routes py4cytoscape
requests through the user's browser and on to Cytoscape, and then returns the result in the
reverse direction. Requests and responses are routed through the Jupyter-Bridge server, which
is an independent entity on the web.

For most Cytoscape operations, it's necessary to transfer files from the Notebook server so
that Cytoscape can load them, or to transfer files created by Cytoscape to the Notebook server
so Python can analyze them. Sandboxing was implemented to enable these transfers, and to
enable portability of workflows across different Cytoscape workstations.

Finally, py4cytoscape functions and definitions were sync'd with RCy3 changes since 1/1/20,
and a reference interface spec was created independent of py4cytoscape and RCy3: Conform to `Cytoscape Automation API Definition <https://docs.google.com/spreadsheets/d/1XLWsKxGLqcBWLzoW2y6HyAUU2jMXaEaWw7QLn3NE5nY/edit?usp=sharing>`_.

API Changes
-----------

* Add tools.merge_networks() and tools.analyze_network()

* Add sandbox.* functions

* Added a number of maintenance functions in commands and py4cytoscape_sandbox modules

Deprecations
------------

None

Contributors to this release
----------------------------

- Barry Demchak
- Alex Pico
- Kozo Nashida
- Chris Churas
- Yasir Demirtaş

Pull requests merged in this release
------------------------------------

None
