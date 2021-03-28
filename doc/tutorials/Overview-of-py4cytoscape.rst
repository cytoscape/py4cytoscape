Overview of py4cytoscape
========================

by Kozo Nishida, Alexander Pico, Tanja Muetze, Georgi Kolishovski, Paul
Shannon, Barry Demchak

**Package**

py4cytoscape 0.0.8

Cytoscape is a well-known bioinformatics tool for displaying and
exploring biological networks. Python is a powerful programming language
and environment for statistical and exploratory data analysis.
*py4cytoscape* uses CyREST to communicate between **Python** and
Cytoscape, allowing any graphs (e.g., igraph or dataframes) to be
viewed, explored and manipulated with the Cytoscape point-and-click
visual interface. Thus, via py4cytoscape, these two quite different,
quite useful bioinformatics software environments are connected,
mutually enhancing each other, providing new possibilities for exploring
biological data.

Installation
------------

.. code:: python

    %%capture
    !python3 -m pip install python-igraph requests pandas networkx
    !python3 -m pip install py4cytoscape

Prerequisites
-------------

In addition to this package (py4cytoscape), you will need:

Cytoscape 3.8.1 or greater + `FileTransfer
App <https://apps.cytoscape.org/apps/filetransfer>`__, which can be
downloaded from http://www.cytoscape.org/download.php. Simply follow the
installation instructions on screen.

Once you have Cytoscape installed in your desktop environment, launch
Cytoscape and keep it running whenever using py4cytoscape.

In addition to that, if you are now running this Notebook on Google
Colab, you need to run the code below. (If you’re running this notebook
on your local Jupyter, you don’t need to.)

.. code:: python

    import IPython
    import py4cytoscape as p4c
    print(f'Loading Javascript client ... {p4c.get_browser_client_channel()} on {p4c.get_jupyter_bridge_url()}')
    browser_client_js = p4c.get_browser_client_js()
    IPython.display.Javascript(browser_client_js) # Start browser client

Getting started
---------------

First, confirm that you have everything installed and running:

.. code:: python

    p4c.cytoscape_ping()

.. code:: python

    p4c.cytoscape_version_info()

My first network
----------------

Let’s create a Cytoscape network from some basic Python objects

.. code:: python

    import pandas as pd
    nodes = pd.DataFrame(data={'id': ["node 0","node 1","node 2","node 3"], 'group': ["A","A","B","B"], 'score': [20,10,15,5]})
    edges = pd.DataFrame(data={'source': ["node 0","node 0","node 0","node 2"], 'target': ["node 1","node 2","node 3","node 3"], 'interaction': ["inhibits","interacts","activates","interacts"], 'weight': [5.1,3.0,5.2,9.9]})
    
    p4c.create_network_from_data_frames(nodes, edges, title="my first network", collection="DataFrame Example")

Switch styles
~~~~~~~~~~~~~

Check out the marquee style!

.. code:: python

    p4c.set_visual_style('Marquee')

My own style
~~~~~~~~~~~~

Create your own style with node attribute fill mappings and some
defaults

.. code:: python

    style_name = "myStyle"
    defaults = {'NODE_SHAPE': "diamond", 'NODE_SIZE': 30, 'EDGE_TRANSPARENCY': 120, 'NODE_LABEL_POSITION': "W,E,c,0.00,0.00"}
    nodeLabels = p4c.map_visual_property('node label','id','p')
    nodeFills = p4c.map_visual_property('node fill color','group','d',["A","B"], ["#FF9900","#66AAAA"])
    arrowShapes = p4c.map_visual_property('Edge Target Arrow Shape','interaction','d',["activates","inhibits","interacts"],["Arrow","T","None"])
    edgeWidth = p4c.map_visual_property('edge width','weight','p')
    
    p4c.create_visual_style(style_name, defaults, [nodeLabels,nodeFills,arrowShapes,edgeWidth])
    p4c.set_visual_style(style_name)

*Pro-tip: if you want to set NODE_WIDTH and NODE_HEIGHT independently,
you also need to unlock the node dimensions with…*

.. code:: python

    p4c.lock_node_dimensions(False, style_name)

Biological graph example
------------------------

Here we create a 4-node graph in Python, send it to Cytoscape for
display and layout. For the sake of simplicity, no node attributes and
no visual styles are included; those topics are covered in subsequent
steps.

.. code:: python

    nodes = pd.DataFrame(data={'id': ["A", "B", "C", "D"]})
    edges = pd.DataFrame(data={'source': ["C", "B", "B", "B"], 'target': ["D", "A", "D", "C"]})
    
    p4c.create_network_from_data_frames(nodes, edges, title="simple network", collection="Biological Example")

You should now have the structure of this 4-node graph with a basic,
default style. Fortunately, Cytoscape has some built-in rendering rules
in which (and unless instructed otherwise) nodes and edges are rendered
and a default (user-preference) layout algorithm is applied.

Add node attributes
~~~~~~~~~~~~~~~~~~~

We often know quite a lot about the nodes and edges in our graphs. By
conveying this information visually, the graph will be easier to
explore. For instance, we may know that protein A phosphorylates protein
B, that A is a kinase and B a transcription factor, and that their mRNA
expression (compared to a control) is a log2 fold change of 1.8 and 3.2
respectively. One of the core features of Cytoscape is visual styles,
which allow you to specify how data values (e.g., kinase,transcription
factor; expression ratios) should be conveyed in the visual properties
of the graph (e.g., node shape, node color or size).

We continue with the simple 4-node graph, adding two kinds data values
(moleculeType and log2fc). The easiest way to do this is via pandas
DataFrame s. However, you can also include attributes together with the
original graph models as igraph s or pandas DataFrame s and then use the
provided create functions to create and load in a single step (see
*p4c.create_network_from_igraph() and
p4c.create_network_from_data_frames()* functions). Check out the other
Notebooks for more examples.

.. code:: python

    df = pd.DataFrame(data={'moleculeType': ['kinase','TF','cytokine','cytokine'], 'log2fc': [1.8,3.0,-1.2,-2.5]})
    df.index = ['A','B','C','D']

.. code:: python

    p4c.load_table_data(df)

Note that adding the attributes does not in itself cause the appearance
of the graph to change. Such a change requires that you specify and
apply visual style mappings, which will be explained in the *next*
section. You can, however, examine these attributes in Cytoscape, using
Cytoscape’s the **Data Panel** to display data values associated with
selected nodes immediately below the Cytoscape window.

Modifying the display: defaults and mappings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

py4cytoscape provides an easy way to not only change the default styles,
but more interestingly, py4cytoscape also provides easy access to
*mapping* your data to visual styles, e.g., allowing the size, shape and
color of nodes and edges to be determined by the data you have
associated with those nodes and edges.

First, let’s change the the defaults.

.. code:: python

    p4c.set_node_shape_default('OCTAGON')

.. code:: python

    p4c.set_node_color_default('#AAFF88')

.. code:: python

    p4c.set_node_size_default(60)

.. code:: python

    p4c.set_node_font_size_default(30)

Now we will add some visual mappings. Let’s map \`moleculeType’ to node
shapes. First, we can see which shapes are available in Cytoscape, then
we can define the mapping with paired lists.

.. code:: python

    p4c.get_node_shapes()

.. code:: python

    column = 'moleculeType'
    values = ['kinase', 'TF', 'cytokine']
    shapes = ['DIAMOND', 'TRIANGLE', 'RECTANGLE']
    
    p4c.set_node_shape_mapping(column, values, shapes)

The node shape mapping is an example of a *discrete* mapping, where a
style is defined for each, discrete value. This is useful for
categorical data (like type) where there is only a limited set of
possible values. This is in contast to the other two other types of
mappings: *continuous* and *passthrough*. In the case of expression
values, for example, we will want to use *continuous* mapping (e.g., to
node color), defining a small set of control points, rather than an
explicit color for each possible data value. Cytoscape will simply
interpolate between the control points to provide a gradient of colors.
Let’s try that one now

.. code:: python

    column = 'log2fc'
    control_points = [-3.0, 0.0, 3.0]
    colors = ['#5588DD', '#FFFFFF', '#DD8855']
    
    p4c.set_node_color_mapping(column, control_points, colors)

Note that there are three colors and three control points. However, you
can also specify *two additional* colors beyond the number of control
points if you want to set extreme (or out-of-bounds) colors for values
less than or greater than your control points.

.. code:: python

    control_points = [-2.0, 0.0, 2.0]
    colors = ['#2255CC', '#5588DD', '#FFFFFF', '#DD8855', '#CC5522']
    
    p4c.set_node_color_mapping(column, control_points, colors)

Now, add a node size rule, using *log2fc* again as controlling node
values.

.. code:: python

    control_points = [-3.0, 2.0, 3.0]
    sizes = [20, 80, 90]
    p4c.set_node_size_mapping(column, control_points, sizes)

If you recall the third type of mapping, *passthrough*, we can see it
already working in our current network example. The node labels! By
default, the *name* column is mapped to the node label property using
*passthrough* logic: the value is passed directly to the style property.

Selecting nodes
~~~~~~~~~~~~~~~

Let us now try selecting nodes in Cytoscape from Python. Select the C
node by name:

.. code:: python

    p4c.select_nodes('C', 'name')

.. code:: python

    p4c.get_selected_nodes()

Now we wish to extend the selected nodes to include the first neighbors
of the already-selected node B. This is a common operation: for
instance, after selecting one or more nodes based on experimental data
or annotation, you may want to explore these in the context of
interaction partners (in a protein-protein network) or in relation to
upstream and downstream partners in a signaling or metabolic network.
Type:

.. code:: python

    p4c.select_first_neighbors()

You will see that three nodes are now selected. Get their names back to
Python as a list:

.. code:: python

    node_names = p4c.get_selected_nodes()

.. code:: python

    node_names

And, finally, deselection works as you’d expect by means of a general
*p4c.clearSelection()* function:

.. code:: python

    p4c.clear_selection()

.. code:: python

    ?p4c.clear_selection

Browse available functions, commands and arguments
--------------------------------------------------

py4cytoscape functions

.. code:: python

    help(p4c)

.. code:: python

    dir(p4c)

+-----------------------+-----------------------+-----------------------+
| Category              | Description           | Examples              |
+=======================+=======================+=======================+
| apps                  | Inspecting and        | *install_app          |
|                       | managing apps for     | disable_app           |
|                       | Cytoscape.            | get_installed_apps*   |
+-----------------------+-----------------------+-----------------------+
| collections           | Getting information   | *get_collection_list  |
|                       | about network         | get                   |
|                       | collections.          | _collection_networks* |
+-----------------------+-----------------------+-----------------------+
| commands              | Constructing any      | *cyrest_get           |
|                       | arbitrary CyREST API  | commands_post         |
|                       | or Commands API       | cyrest_api            |
|                       | method via standard   | commands_run*         |
|                       | GET, PUT, POST and    |                       |
|                       | DELETE protocols.     |                       |
+-----------------------+-----------------------+-----------------------+
| cy_ndex               | Communicating with    | *imp                  |
|                       | NDEx from within      | ort_network_from_ndex |
|                       | Cytoscape.            | ex                    |
|                       |                       | port_network_to_ndex* |
+-----------------------+-----------------------+-----------------------+
| cytoscape_system      | Checking Cytoscape    | *cytoscape_ping       |
|                       | System information,   | cy                    |
|                       | including versions    | toscape_version_info* |
|                       | and memory usage.     |                       |
+-----------------------+-----------------------+-----------------------+
| filters               | Selecting nodes and   | *create_degree_filter |
|                       | edges based on filter | create_column_filter* |
|                       | criteria.             |                       |
+-----------------------+-----------------------+-----------------------+
| groups                | Working with groups   | *create_group         |
|                       | in Cytoscape.         | collapse_group*       |
+-----------------------+-----------------------+-----------------------+
| layouts               | Performing layouts in | *layout_network       |
|                       | addition to getting   | get_layout_names*     |
|                       | and setting layout    |                       |
|                       | properties.           |                       |
+-----------------------+-----------------------+-----------------------+
| networks              | Creating and managing | \                     |
|                       | networks and          | *create_network_from… |
|                       | retrieving            | create…_from_network  |
|                       | information on        | get_network_suid      |
|                       | networks, nodes and   | export_network        |
|                       | edges.                | get_all_nodes         |
|                       |                       | get_edge_count        |
|                       |                       | get_first_neighbors\* |
+-----------------------+-----------------------+-----------------------+
| network_selection     | Manipulating          | *select_nodes         |
|                       | selection of nodes    | invert_node_selection |
|                       | and edges in          | se                    |
|                       | networks.             | lect_first_neighbors* |
+-----------------------+-----------------------+-----------------------+
| network_views         | Performing view       | *fit_content          |
|                       | operations in         | export_image          |
|                       | addition to getting   | tog                   |
|                       | and setting view      | gle_graphics_details* |
|                       | properties.           |                       |
+-----------------------+-----------------------+-----------------------+
| session               | Managing Cytoscape    | *open_session         |
|                       | sessions, including   | save_session          |
|                       | save, open and close. | close_session*        |
+-----------------------+-----------------------+-----------------------+
| style_bypasses        | Setting and clearing  | *                     |
|                       | bypass values for     | set_node_color_bypass |
|                       | visual properties.    | set_e                 |
|                       |                       | dge_line_style_bypass |
|                       |                       | hide_nodes*           |
+-----------------------+-----------------------+-----------------------+
| style_defaults        | Getting and setting   | *s                    |
|                       | default values for    | et_node_shape_default |
|                       | visual properties.    | set_edg               |
|                       |                       | e_line_width_default* |
+-----------------------+-----------------------+-----------------------+
| style_dependencies    | Getting and setting   | *                     |
|                       | style dependencies.   | lock_node_dimensions* |
+-----------------------+-----------------------+-----------------------+
| style_mappings        | Defining mappings     | *map_visual_property  |
|                       | between table column  | update_style_mapping  |
|                       | values and visual     | set_node_size_mapping |
|                       | properties.           | se                    |
|                       |                       | t_edge_color_mapping* |
+-----------------------+-----------------------+-----------------------+
| styles                | Managing styles and   | *create_visual_style  |
|                       | retrieving general    | set_visual_style      |
|                       | lists of properties   | export_visual_styles  |
|                       | relevant to multiple  | get_arrow_shapes*     |
|                       | style modes.          |                       |
+-----------------------+-----------------------+-----------------------+
| style_values          | Retrieving current    | *get_node_width       |
|                       | values for visual     | get_edge_color        |
|                       | properties.           | get_network_zoom*     |
+-----------------------+-----------------------+-----------------------+
| tables                | Managing table        | *get_table_columns    |
|                       | columns and table     | rename_table_column   |
|                       | column functions,     | load_table_data       |
|                       | like map and rename,  | map_table_column*     |
|                       | as well as loading    |                       |
|                       | and extracting table  |                       |
|                       | data in Cytoscape.    |                       |
+-----------------------+-----------------------+-----------------------+
| tools                 | Performing actions    | *cybrowser_dialog     |
|                       | found in the Tools    | diffusion_basic*      |
|                       | Menu in Cytoscape.    |                       |
+-----------------------+-----------------------+-----------------------+
| user_interface        | Controling the panels | *hide_panel           |
|                       | in the Cytoscape user | float_panel           |
|                       | interface.            | dock_panel*           |
+-----------------------+-----------------------+-----------------------+

Open swagger docs for live instances of CyREST API and Commands API:

.. code:: python

    p4c.cyrest_api()

.. code:: python

    p4c.commands_api()

List available commands and arguments in Python. Use “help” to list top
level:

.. code:: python

    p4c.commands_help("help")

List **network** commands. Note that “help” is optional:

.. code:: python

    p4c.commands_help("help network")

List arguments for the **network select** command:

.. code:: python

    p4c.commands_help("help network select")

That covers the basics of network manipulation. Check out the other
vignettes for additional amd more complex examples. And when you are
ready to work with some real data, check out the other basic and
advanced R tutorials,
https://github.com/cytoscape/cytoscape-automation/tree/master/for-scripters/Python.

More examples
-------------

The Cytoscape team is collecting scripts from the community in a public
GitHub repository at
https://github.com/cytoscape/cytoscape-automation/tree/master/for-scripters/Python.

Development
-----------

The py4cytoscape project code and documentation is maintained at GitHub:
https://github.com/cytoscape/py4cytoscape. All bugs and feature requests
are tracked as Issues, https://github.com/cytoscape/py4cytoscape/issues.

Credits
-------

-  Paul Shannon’s generous advice and mentorship was very important for
   transforming this package from using XMLRPC and CytoscapeRPC to using
   CyREST.
-  David Otasek, Keiichiro Ono and Barry Demchak kindly provided CyREST
   as well as help and support for new functionalities and changes.
-  Mark Grimes and Ruth Isserlin kindly provided helpful user feedback.
-  Julia Gustavsen generously developed various use cases/examples for
   using RCy3 with biological data during GSOC 2016,
   https://github.com/jooolia/gsoc_Rcy3_vignettes/blob/master/blog_post_drafts/final_work_submission.md.
-  Tanja Muetze provided many years of development, design, maintenance
   and documentation for the RCy3 project.
-  All contributors, new and old, are dynamically acknowledged in our
   Contributor Graph,
   https://github.com/cytoscape/py4cytoscape/graphs/contributors

References
----------

1. Shannon P, Markiel A, Ozier O, Baliga NS, Wang JT, Ramage D, Amin N,
   Schwikowski B, Ideker T. 2003. Cytoscape: a software environment for
   integrated models of biomolecular interaction networks. Genome Res.
   Nov;13(11):2498-504
2. Huber W, Carey VJ, Long L, Falcon S, Gentleman R. 2007. Graphs in
   molecular biology. BMC Bioinformatics. 2007 Sep 27;8.
3. Ono K, Muetze T, Kolishovski G, Shannon P, Demchak, B. CyREST:
   Turbocharging Cytoscape Access for External Tools via a RESTful API
   [version 1; referees: 2 approved]. F1000Research 2015, 4:478.

