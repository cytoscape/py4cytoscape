.. Look here for code block commenting examples: http://www.sphinx-doc.org/en/master/usage/extensions/example_google.html#example-google
.. Look here for a general discussion of directives: https://docutils.sourceforge.io/docs/ref/rst/directives.html
.. Common formatting options: https://dockramer.com.au/creating-manuals-using-rst-and-sphinx-text-formatting/#:~:text=To%20designate%20%2A%2Abold%20text%2A%2A%2C%20use%20two%20asterisks%20before,before%20and%20after%20the%20text%20to%20be%20bolded.

.. _contents:

Overview of py4cytoscape
========================

py4cytoscape is a Python package that communicates with `Cytoscape <https://cytoscape.org>`_
via its `REST API <https://pubmed.ncbi.nlm.nih.gov/31477170/>`_, providing access to a set over 250 functions that
enable control of Cytoscape from within standalone and Notebook Python programming environments. It provides
nearly identical functionality to `RCy3 <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6880260/>`_, an R package in
Bioconductor available to R programmers.

py4cytoscape provides:

-  functions that can be leveraged from Python code to implement network biology-oriented workflows;
-  access to user-written `Cytoscape Apps <http://apps.cytoscape.org/>`_ that implement `Cytoscape Automation <https://pubmed.ncbi.nlm.nih.gov/31477170/>`_ protocols;
-  logging and debugging facilities that enable rapid development, maintenance, and auditing of Python-based workflow;
-  two-way conversion between the `igraph <https://igraph.org/python/>`_ and `NetworkX <https://networkx.github.io/documentation/stable/>`_ graph packages, which enables interoperability with popular packages available in public repositories (e.g., `PyPI <https://pypi.org/>`_); and
-  the ability to painlessly work with large data sets generated within Python or available on public repositories (e.g., `STRING <https://string-db.org/>`_ and `NDEx <http://ndexbio.org>`_);
-  execute Python code on the Cytoscape workstation or in Jupyter Notebooks on local or remote servers.

