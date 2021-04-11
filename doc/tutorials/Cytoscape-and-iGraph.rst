Cytoscape and igraph
====================

**by Kozo Nishida, Alexander Pico, Barry Demchak**

**2021-04-11**

**Package**

py4cytoscape 0.0.9

This notebook will show you how to convert networks between igraph and
Cytoscape.

Installation
------------

.. code:: python

    %%capture
    !python3 -m pip install python-igraph requests pandas networkx
    !python3 -m pip install git+https://github.com/cytoscape/py4cytoscape.git@0.0.9

Required Software
-----------------

In addition to this package (py4cytoscape), you will need:

Cytoscape 3.8.2 or greater + `FileTransfer
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

.. code:: python

    p4c.cytoscape_ping()

From igraph to Cytoscape
------------------------

The igraph package is a popular network tool among Python users. With
py4cytoscape, you can easily translate igraph networks to Cytoscape
networks!

Here is a basic igraph network construction from the Graph.DataFrame
docs,
https://igraph.org/python/doc/tutorial/generation.html#from-pandas-dataframe-s

.. code:: python

    import pandas as pd
    from igraph import Graph
    
    actors = pd.DataFrame(data={'name': ["Alice", "Bob", "Cecil", "David", "Esmeralda"],
                                 'age': [48,33,45,34,21],
                                 'gender': ["F","M","F","M","F"]
                                 })
    
    relations = pd.DataFrame(data={'from': ["Bob", "Cecil", "Cecil", "David", "David", "Esmeralda"],
                                   'to': ["Alice", "Bob", "Alice", "Alice", "Bob", "Alice"],
                                   'same_dept': [False, False, True, False, False, True],
                                   'friendship': [4,5,5,2,1,1],
                                   'advice': [4,5,5,4,2,3]
                                   })
    
    ig = Graph.DataFrame(relations, directed=True, vertices=actors)

You now have an igraph network, ig. In order to translate the network
together with all vertex (node) and edge attributes over to Cytoscape,
simply use:

.. code:: python

    p4c.create_network_from_igraph(ig, "myIgraph")

From Cytoscape to igraph
------------------------

Inversely, you can use create_igraph_from_network() in py4cytoscape to
retrieve vertex (node) and edge data.frames to construct an igraph
network.

.. code:: python

    ig2 = p4c.create_igraph_from_network("myIgraph")

Compare the round-trip result for yourself…

.. code:: python

    print(ig)

.. code:: python

    print(ig2)

Note that a few additional attributes are present which are used by
Cytoscape to support node/edge selection and network collections.

**Also note: All networks in Cytoscape are implicitly modeled as
directed. This means that if you start with an undirected network in
igraph and then convert it round-trip (like described above), then you
will end up with a directed network.**

