.. _contents

Overview of py4cytoscape
========================

py4cytoscape is a Python package that communicates with `Cytoscape <https://cytoscape.org>`_
via its `REST API <https://pubmed.ncbi.nlm.nih.gov/31477170/>`_, providing access to a set over 250 functions that
enable control of Cytoscape from within standalone and Notebook Python programming environments. It provides
nearly identical functionality to `RCy3 <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6880260/>`_, an R package in
Bioconductor available to R programmers.

py4cytoscape provides:

-  functions that can be leveraged from Python code to implement network biology-oriented workflows;
-  access to user-written `Cytoscape Apps <http://apps.cytoscape.org/>`_ that
implement `Cytoscape Automation <https://pubmed.ncbi.nlm.nih.gov/31477170/>`_ protocols;
-  logging and debugging facilities that enable rapid development, maintenance, and auditing of Python-based workflow;
-  two-way conversion between the `igraph <https://igraph.org/python/>`_ and
`NetworkX <https://networkx.github.io/documentation/stable/>`_ graph packages, which enables interoperability with popular
packages available in public repositories (e.g., `PyPI <https://pypi.org/>`_); and
-  the ability to painlessly work with large data sets generated within Python or available on public repositories
(e.g., `STRING <https://string-db.org/>`_ and `NDEx <http://ndexbio.org>`_).

With py4cytoscape, you can leverage Cytoscape to:

-  load and store networks in standard and nonstandard data formats;
-  visualize molecular interaction networks and biological pathways;
-  integrate these networks with annotations, gene expression profiles and other state data;
-  analyze, profile, and cluster these networks based on integrated data, using new and existing algorithms.

py4cytoscape enables an agile collaboration between powerful Cytoscape, Python libraries, and novel Python code
so as to realize auditable, reproducible and sharable workflows.

Audience
--------

The audience for py4cytoscape includes biologists, mathematicians, physicists, biologists,
computer scientists, and social scientists. A running sample of research based on Cytoscape can be found on
`Tumblr <https://cytoscape-publications.tumblr.com/>`_. Google Scholar reports that Cytoscape was cited in over 10,000 in academic papers
in `2019 <https://scholar.google.com/scholar?start=0&q=cytoscape&hl=en&as_sdt=0,5&as_ylo=2019&as_yhi=2019>`_, most of
which executed Cytoscape via the traditional mouse and keyboard. py4cytoscape can automate these results as a means of
achieving `reproducible science <https://www.nature.com/articles/s41562-016-0021>`_.

Python
------

Python is a powerful programming language that allows simple and flexible
representations of networks as well as clear and concise expressions of network
algorithms.  Python has a vibrant and growing ecosystem of packages that can be used in combination with
py4cytoscape integrate with traditional workflow engines (e.g, `Galaxy <https://galaxyproject.org/>`_
and `Gene Pattern <https://www.genepattern.org/>`_) to produce robust
end-to-end workflows.

In order to make the most out of py4cytoscape you should know how
to write basic programs in Python.  Among the many guides to Python, we
recommend the `Python documentation <https://docs.python.org/3/>`_
and `Python in a Nutshell <https://www.amazon.com/Python-Nutshell-Second-Alex-Martelli/dp/0596100469>`_.

Free Software
-------------

py4cytoscape is free software; you can redistribute it and/or modify it under the
terms of the license_.  We welcome contributions. Join us on `GitHub <https://github.com/bdemchak/py4cytoscape>`_.

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

