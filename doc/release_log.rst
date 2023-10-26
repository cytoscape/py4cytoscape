.. currentmodule:: py4cytoscape

Release Log
===========


py4cytoscape 1.9.0
-------------------
Release date: dd mmm yyyy

* Removed value validation warning from set_visual_property_default()
* Fixed missing URL parameter in create_network_from_data_frames() and create_network_from_networkx()
* Added style functions for node_position and node_label_position


Release notes
~~~~~~~~~~~~~

.. include:: release/release_1.9.0.rst



py4cytoscape 1.8.0
-------------------
Release date: 21 Jul 2023

* Allowed load_table_data() to handle lists containing float, int and bool instead of just str
* Fixed base_url= not recognized for update_style_defaults() and set_visual_property_default()
* Update python-igraph name to igraph
* Clean up property value warnings for set_node_property_bypass() and set_edge_property_bypass()


Release notes
~~~~~~~~~~~~~

.. include:: release/release_1.8.0.rst


py4cytoscape 1.7.0
-------------------
Release date: 12 Mar 2023

* Updated annotations.ungroup() to call Cytoscape via GET instead of POST, per document
* Fixed networks.create_network_from_data_frames() to allow key column different than 'id'
* Documented how to include a comma in a node name
* Fixed timing issue in merge_networks() where network wasn't stable before returning


Release notes
~~~~~~~~~~~~~

.. include:: release/release_1.7.0.rst


py4cytoscape 1.6.0
-------------------
Release date: 12 Jan 2023

* Now supporting Metascape migration from py2cytoscape to py4cytoscape
* Added sandbox support when Cytoscape is at URL different than 127.0.0.1
* Fixed bugs for calling Cytoscape at URL different than 127.0.0.1
* Removed slow n^2 algorithm from get_table_columns()
* For failed connections to Cytoscape, use exponential backoff retry
* Updated support for Python's improved comparison semantics and treatment of NANs (e.g., style_auto_mappings(), create_column_filter())
* Added Alternate IP Address section to Concepts.rst
* Allow text colors (e.g., "red") in addition to hex colors when setting color properties
* Allow log directory to be set via PY4CYTOSCAPE_DETAIL_LOGGER environment variable
* Allow execution delays to be set via environment variable (PY4CYTOSCAPE_CATCHUP_FILTER_SECS, PY4CYTOSCAPE_MODEL_PROPAGATION_SECS, PY4CYTOSCAPE_CATCHUP_NETWORK_SECS, PY4CYTOSCAPE_CATCHUP_NETWORK_TIMEOUT_SECS)
* Disallow string as value when setting opacity properties
* Added value syntax checks for map_visual_property(), set_node_property_bypass(), set_edge_property_bypass(), set_network_property_bypass(), set_visual_property_default(), update_style_defaults() & set_visual_property_default()
* Added ability to use old property names in all property functions
* Fixed occasional status 404 in cytoscape_api_versions()
* Fixed apps functions to support Cytoscape 3.10 (get_app_information())
* Added set_catchup_network_merge_secs() and PY4CYTOSCAPE_CATCHUP_NETWORK_MERGE_SECS environment variable to control post-merge delay
* Eliminated futures warning for load_table_data() for use of .iteritems()
* Added select_edges_adjacent_to_nodes()


Release notes
~~~~~~~~~~~~~

.. include:: release/release_1.6.0.rst


py4cytoscape 1.5.0
-------------------
Release date: 28 Jun 2022

* Removed dependence on Enum package due to build errors


Release notes
~~~~~~~~~~~~~

.. include:: release/release_1.5.0.rst

py4cytoscape 1.4.0
-------------------
Release date: 28 Jun 2022

* Supported Metascape migration from py2cytoscape to py4cytoscape
* Added names= to get_network_list
* Added create_cytoscapejs_from_network and create_network_from_cytoscapejs
* Added get_visual_style_JSON
* Added delete_all_visual_styles
* Added sandbox support when Cytoscape is at URL different than 127.0.0.1
* Fixed bugs for calling Cytoscape at URL different than 127.0.0.1


Release notes
~~~~~~~~~~~~~

.. include:: release/release_1.4.0.rst

py4cytoscape 1.3.0
-------------------
Release date: 22 May 2022

* Added import_file_from_url() function to improve cloud file download
* Added Gang Su basic protocol 1 & 2 Jupyter Notebook demonstrations
* Added network enrichment demonstration in local & remote Gang Su basic protocol 1
* Moved tutorials to https://github.com/cytoscape/cytoscape-automation/wiki


Release notes
~~~~~~~~~~~~~

.. include:: release/release_1.3.0.rst

py4cytoscape 1.2.0
-------------------
Release date: 30 Apr 2022

* Added annotation functions (mirroring new Cytoscape Annotation features)
* When running Notebook on Cytoscape workstation, files now resolved to local file system (instead of automatic sandbox)
* Added create_view and select_all functions, updated get_network_view_suid() and get_network_views() to coordinate
* Sped up select_all_nodes, select_all_edges



Release notes
~~~~~~~~~~~~~

.. include:: release/release_1.2.0.rst

py4cytoscape 0.0.11
-------------------
Release date: 11 Oct 2021

* Updated documentation and tutorials
* Made set_*_property_bypass more resilient to null node/edge lists
* For Notebook support, improved startup code and added notebook_show_image(), notebook_export_show_image() functions
* For color generators, added reverse= parameter and made divergent palettes automatically reversed
* Fixed filter and style bypass functions to not crash when there are no selected nodes


Release notes
~~~~~~~~~~~~~

.. include:: release/release_0.0.11.rst


py4cytoscape 0.0.10
-------------------

Cancelled

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




