.. _networks:
********
Networks
********

.. automodule:: py4cytoscape.networks

Nodes
-----
.. autosummary::
   :toctree: generated/

   add_cy_nodes
   get_all_nodes
   get_first_neighbors
   get_node_count

Edges
-----
.. autosummary::
   :toctree: generated/

   add_cy_edges
   get_all_edges
   get_edge_count
   get_edge_info

Networks
--------
.. autosummary::
   :toctree: generated/

   clone_network
   create_subnetwork
   delete_all_networks
   delete_network
   get_network_count
   get_network_list
   get_network_name
   get_network_suid
   rename_network
   set_current_network

Import/Export
-------------
.. autosummary::
   :toctree: generated/

   create_igraph_from_network
   create_network_from_data_frames
   create_network_from_igraph
   create_network_from_networkx
   create_networkx_from_network
   export_network
   import_network_from_file


.. _networkselection:
Network Selection
-----------------

.. automodule:: py4cytoscape.network_selection

Nodes
=====
.. autosummary::
   :toctree: generated/

   clear_selection
   delete_selected_nodes
   get_selected_node_count
   get_selected_nodes
   invert_node_selection
   select_all_nodes
   select_first_neighbors
   select_nodes
   select_nodes_connected_by_selected_edges

Edges
=====
.. autosummary::
   :toctree: generated/

   clear_selection
   delete_duplicate_edges
   delete_selected_edges
   delete_self_loops
   get_selected_edge_count
   get_selected_edges
   invert_edge_selection
   select_all_edges
   select_edges
   select_edges_adjacent_to_selected_nodes
   select_edges_connecting_selected_nodes

.. _networkviews:
Network Views
-------------

.. automodule:: py4cytoscape.network_views

Views
=====
.. autosummary::
   :toctree: generated/

   export_image
   fit_content
   get_network_view_suid
   get_network_views
   set_current_view
   toggle_graphics_details