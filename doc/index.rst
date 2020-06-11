.. _contents

Overview of py4cytoscape
========================

py4cytoscape is a Python package that communicates with [Cytoscape](https://cytoscape.org)
via its [REST API](https://pubmed.ncbi.nlm.nih.gov/31477170/), providing access to a set over 250 functions that
enable control of Cytoscape from within standalone and Notebook Python programming environments. It provides
nearly identical functionality to [RCy3](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6880260/), an R package in
Bioconductor available to R programmers.

py4cytoscape provides:

-  functions that can be leveraged from Python code to implement network biology-oriented workflows;
-  access to user-written Cytoscape Apps that implement [Cytoscape Automation](https://pubmed.ncbi.nlm.nih.gov/31477170/) protocols;
-  logging and debugging facilities that enable rapid development, maintenance, and auditing of Python-based workflow;
-  two-way conversion between the [igraph](https://igraph.org/python/) and
[NetworkX](https://networkx.github.io/documentation/stable/) graph packages, which enables interoperability with popular
packages available in public repositories (e.g., [PyPI](https://pypi.org/)); and
-  the ability to painlessly work with large data sets generated within Python or available on public repositories
(e.g., [STRING](https://string-db.org/) and [NDEx](http://ndexbio.org)).

With py4cytoscape, you can leverage Cytoscape to:

-  load and store networks in standard and nonstandard data formats;
-  visualize molecular interaction networks and biological pathways;
-  integrate these networks with annotations, gene expression profiles and other state data;
-  analyze, profile, and cluster these networks based on integrated data, using new and existing algorithms.

py4cytoscape enables an agile collaboration between powerful Cytoscape, Python libraries, and novel Python code
so as to realize auditable, reproducible and sharable workflows.

Audience
--------

... see NetworkX verbage

Python
------

... see NetworkX verbage

Free Software
-------------

... see NetworkX verbage

History
-------

... see NetworkX verbage

Documentation
-------------

.. only:: html

    :Release: |version|
    :Date: |today|

.. toctree::
   :maxdepth: 1

   install
   tutorial
   reference/index
   release_log
   license
   credits
   citing
   py4cytoscape_package


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

