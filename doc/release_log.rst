.. currentmodule:: py4cytoscape

Release Log
===========


py4cytoscape 0.0.10
-------------------
Release date: 13 Sep 2021

* Updated documentation and tutorials
* Made set_*_property_bypass more resilient to null node/edge lists
* For Notebook support, improved startup code and added notebook_show_image(), notebook_export_show_image() functions
* For color generators, added reverse= parameter and made divergent palettes automatically reversed
* Fixed filter and style bypass functions to not crash when there are no selected nodes


Release notes
~~~~~~~~~~~~~

.. include:: release/release_0.0.10.rst


py4cytoscape 0.0.9
------------------
Release date: 3 Jun 2021

* Updated documentation and tutorials
* Reworked iGraph support to track RCy3 implementation
* Added iGraph support for Graph, DiGraph, MultiGraph, MultiDiGraph
* Updated node/edge-to-suid functions to allow detection of multiple copies of a node/edge
* Enabled delete_duplicate_edges to ignore edge direction
* Added support for discrete and continuous value generators (as gen* functions in new style_auto_mappers module)


Release notes
~~~~~~~~~~~~~

.. include:: release/release_0.0.9.rst


py4cytoscape 0.0.8
------------------
Release date: 26 Mar 2021

* Added parameters in CyNDEX functions to support subdomains
* Added apply= parameter in filter definition functions to support Cytoscape v3.9.0 separating apply from definition
* Added overwrite_file parameter to export functions
* Added Sandbox direct download from URL
* Added functions for import network from tabular file & get current style, etc
* Fixes that allow commands_help to work


Release notes
~~~~~~~~~~~~~

.. include:: release/release_0.0.8.rst


py4cytoscape 0.0.7
------------------
Release date: 08 Jan 2021

* Compatibility of node, edge and group parameter with RCy3 formats
* Improved verify_supported_versions parsing for Cytoscape 3.10 and beyond


Release notes
~~~~~~~~~~~~~

.. include:: release/release_0.0.7.rst


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




