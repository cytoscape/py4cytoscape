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
