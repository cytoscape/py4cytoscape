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

With py4cytoscape, you can leverage Cytoscape to:

-  load and store networks in standard and nonstandard data formats;
-  visualize molecular interaction networks and biological pathways;
-  integrate these networks with annotations, gene expression profiles and other state data;
-  analyze, profile, and cluster these networks based on integrated data, using new and existing algorithms.

py4cytoscape enables an agile collaboration between powerful Cytoscape, Python libraries, and novel Python code
so as to realize auditable, reproducible and sharable workflows.

Look to the :doc:`Tutorials <tutorials/index>` section to get started with py4cytoscape.

Look to the :doc:`Install <install>` section for installation instructions.

Look to the :doc:`Reference <reference/index>` section to see details on py4cytoscape functions.

Look to the :doc:`Concepts <concepts>` section to see read about important py4cytoscape topics.

Look to the :doc:`Jupyter Notebook <concepts>` section to learn how to use py4cytoscape from a Jupyter Notebook running on a remote server.

Note that py4cytoscape and RCy3 functions implement a common interface called the `Cytoscape Automation API Definition <https://docs.google.com/spreadsheets/d/1XLWsKxGLqcBWLzoW2y6HyAUU2jMXaEaWw7QLn3NE5nY/edit?usp=sharing>`_.

Audience
--------

The audience for py4cytoscape includes biologists, mathematicians, physicists, biologists,
computer scientists, and social scientists. A running sample of research based on Cytoscape can be found on
`Tumblr <https://cytoscape-publications.tumblr.com/>`_. Cytoscape provides `tutorials <https://github.com/cytoscape/cytoscape-tutorials/wiki>`_,
`videos <https://www.youtube.com/channel/UCv6auk9FK4NgXiXiqrDLccw>`_, and `automation vignettes <https://github.com/cytoscape/cytoscape-automation/wiki>`_.

Google Scholar reports that Cytoscape was cited in over 10,000 in academic papers
in `2019 <https://scholar.google.com/scholar?start=0&q=cytoscape&hl=en&as_sdt=0,5&as_ylo=2019&as_yhi=2019>`_, most of
which executed Cytoscape via the traditional mouse and keyboard. py4cytoscape can automate these results as a means of
achieving `reproducible science <https://www.nature.com/articles/s41562-016-0021>`_.

Python
------

Python is a powerful programming language that allows simple and flexible
representations of networks as well as clear and concise expressions of network
algorithms. Python has a vibrant and growing ecosystem of packages that can be used in combination with
py4cytoscape to integrate with traditional workflow engines (e.g., `Gene Pattern <https://www.genepattern.org/>`_
and `Galaxy <https://galaxyproject.org/>`_) to produce robust
end-to-end workflows.

In order to make the most out of py4cytoscape you should know how
to write basic programs in Python.  Among the many guides to Python, we
recommend the `Python documentation <https://docs.python.org/3/>`_
and `Python in a Nutshell <https://www.amazon.com/Python-Nutshell-Second-Alex-Martelli/dp/0596100469>`_.

Free Software
-------------

py4cytoscape is free software; you can redistribute it and/or modify it under the
terms of the :ref:`License`.  We welcome contributions. Join us on `GitHub <https://github.com/bdemchak/py4cytoscape>`_.

History
-------

The original Python libraries for Cytoscape were written by `Keiichiro Ono <https://f1000research.com/articles/4-478>`_ in
2015 as an interface to the then-new CyREST automation interface. Its original name was
`py2cytoscape <https://pypi.org/project/py2cytoscape/>`_. It was further evolved through 2019 by Kozo Nishida and Jorge Bouças.

In late 2019, py4cytoscape was undertaken by Barry Demchak as a replacement for py2cytoscape. It implemented the API defined by RCy3,
an R package in Bioconductor developed by a Cytoscape Automation working group consisting of Alex Pico (primary author),
Mark Grimes, Julia Gustavsen, Shraddha Pai, Ruth Isserlin, and Barry Demchak. RCy3 was based on prior work contributed by
Paul Shannon, Tanja Muetze, Georgi Kolishkovski and Keiichiro Ono.

We intend to keep the function definitions available through py4cytoscape and RCy3 consistent and synchronized going forward,
and to re-integrate unique features found only in py2cytoscape.

Documentation
-------------

.. only:: html

    :Release: |version|
    :Date: |today|

.. toctree::
   :maxdepth: 1

   install
   tutorials/index
   concepts
   reference/index
   logging
   release_log
   license
   credits
   citing

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

