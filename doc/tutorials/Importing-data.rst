Importing data
==============

**by Kozo Nishida, Alexander Pico, Barry Demchak**

**2021-04-04**

**Package** py4cytoscape 0.0.8

This notebook will show you how to import a pandas.DataFrame of node
attributes into Cytoscape as Node Table columns. The same approach works
for edge and network attriubutes.

Installation
------------

.. code:: python

    %%capture
    !python3 -m pip install python-igraph requests pandas networkx
    !python3 -m pip install py4cytoscape

Required Software
-----------------

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

.. code:: python

    p4c.cytoscape_ping()

Always Start with a Network
---------------------------

When importing data, you are actually performing a merge function of
sorts, appending columns to nodes (or edges) that are present in the
referenced network. Data that do not match elements in the network are
effectively discarded upon import.

So, in order to demonstrate data import, we first need to have a
network. This command will import network files in any of the supported
formats (e.g., SIF, GML, XGMML, etc).

In order to import the “SIF” file into Cytoscape, it must be on the
local machine where Cytoscape installed, not on Colab. So use the
FileTransfer App to send the SIF file to your local file system from
Colab.

This operation is necessary even if you are using a local Jupyter
Notebook instead of Colab. (This prevents reproducibility problems
depending on the file path.)

.. code:: python

    p4c.sandbox_url_to("https://raw.githubusercontent.com/cytoscape/cytoscape-automation/master/for-scripters/Python/data/galFiltered.sif", "galFiltered.sif")


If you are using py4cytoscape in Jupyter Notebook,
``import_network_from_file`` will always try to read the file under the
sandbox filepath.

.. code:: python

    p4c.import_network_from_file("galFiltered.sif")

You should now see a network with just over 300 nodes. If you look at
the Node Table, you’ll see that there are no attributes other than node
names. Let’s fix that…

Import Data
-----------

You can import data into Cytoscape from any pandas.DataFrame in Python
as long as it contains row names (or an arbitrary column) that match a
Node Table column in Cytoscape. In this example, we are starting with a
network with yeast identifiers in the “name” column. We also have a CSV
file with gene expression data values keyed by yeast identifiers here:

.. code:: python

    import pandas as pd
    data = pd.read_csv("https://raw.githubusercontent.com/cytoscape/RCy3/master/inst/extdata/galExpData.csv")

.. code:: python

    data

**Note: there may be times where your network and data identifers are of
different types. This calls for identifier mapping. py4cytoscape
provides a function to perform ID mapping in Cytoscape:**

.. code:: python

    ?p4c.map_table_column

Check out the Identifier mapping notebook for detailed examples.

Now we have a pandas.DataFrame that includes our identifiers in a column
called “name”, plus a bunch of data columns. Knowing our key columns, we
can now perform the import:

.. code:: python

    p4c.load_table_data(data, data_key_column="name")

If you look back at the Node Table, you’ll now see that the
corresponding rows of our pandas.DataFrame have been imported as new
columns.

**Note: we relied on the default values for table (“node”) and
table_key_column (“name”), but these can be specified as well. See help
docs for parameter details.**

.. code:: python

    ?p4c.load_table_data
