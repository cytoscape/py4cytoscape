.. currentmodule:: py4cytoscape

Release Log
===========

py4cytoscape 0.0.6
------------------
Release date: 30 Oct 2020

* Made default directory for standalone Python the same as the Python kernel directory
* Shortened delays that wait for Cytoscape to stabilize, removed NDEx function delays
* Began docker support
* Improved sandboxing and Jupyter Notebook documentation
* Added shorter test (test_sanity) for quick installation verification


Release notes
~~~~~~~~~~~~~

.. include:: release/release_0.0.6.rst


py4cytoscape 0.0.5
------------------
Release date: 15 Oct 2020

* Referenced Concepts:Sandboxing from documentation for sandbox functions
* Updated installation and logging documentation
* Updated test to detect Colab shell


Release notes
~~~~~~~~~~~~~

.. include:: release/release_0.0.5.rst


py4cytoscape 0.0.4
------------------
Release date: 05 Oct 2020

* Corrected a build problem that stopped 0.0.3 from initializing

Release notes
~~~~~~~~~~~~~

.. include:: release/release_0.0.4.rst


py4cytoscape 0.0.3
------------------
Release date: 05 Oct 2020

* Conform to `Cytoscape Automation API Definition <https://docs.google.com/spreadsheets/d/1XLWsKxGLqcBWLzoW2y6HyAUU2jMXaEaWw7QLn3NE5nY/edit?usp=sharing>`_
* Change CyError logger to write exceptions to stderr
* Add `Sandboxing` interface and functions
* Add merge_network() and analyze_network()
* Add Jupyter-bridge, Cytoscape Automation API, py4cytoscape versions to cytoscape_version_info
* Add support for Jupyter-bridge
* Add Concepts section to documentation

Release notes
~~~~~~~~~~~~~

.. include:: release/release_0.0.3.rst



py4cytoscape 0.0.1
------------------
Release date: 21 Aug 2020

Initial release, matches API signatures for RCy3

Release notes
~~~~~~~~~~~~~

.. include:: release/release_0.0.1.rst




