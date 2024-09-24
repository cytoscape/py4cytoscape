
py4cytoscape 1.10.0
-------------------
Release date: 24 Sep 2024

We're happy to announce the release of py4cytoscape 1.10.0!

py4cytoscape is a Python package that communicates with `Cytoscape <https://cytoscape.org>`_
via its `REST API <https://pubmed.ncbi.nlm.nih.gov/31477170/>`_, providing access to a set over 250 functions that
enable control of Cytoscape from within standalone and Notebook Python programming environments. It provides
nearly identical functionality to `RCy3 <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6880260/>`_, an R package in
Bioconductor available to R programmers.

The themes for this release are:

* Add missing parameters to enable non-default base_url
* Add documentation & checks for large commands
* Speed improvement on many functions that convert node or edge names to SUIDs


Release notes
~~~~~~~~~~~~~

* Added base_url parameter propagation in filters, networks and tables functions
* Add documentation & check for outsize commands_run and commands_get requests
* Speed improvement on functions that convert node or edge names to SUIDs

    edge_name_to_edge_suid
        convert_edge_name_to_edge_info

        create_network_from_data_frames

        clear_edge_property_bypass

        set_edge_property_bypass

        get_edge_property

        get_table_value

    node_name_to_name_suid
        add_cy_edges

        get_first_neighbors

        clear_node_property_bypass

        set_node_property_bypass

        get_node_property

        get_table_value


API Changes
-----------

Added:

None



Deprecations
------------

None


Contributors to this release
----------------------------

- Barry Demchak
- Harsh Sharma


Pull requests merged in this release
------------------------------------

- #139 by Harsh Sharma
- #140 by Barry Demchak
- #141 by Harsh Sharma

Issues closed in this release
------------------------------------

- #137 by Harsh Sharma
- #135 by Minghao Gong
- #127 by Athina Gavriilidou
- #94  by Harsh Sharma

