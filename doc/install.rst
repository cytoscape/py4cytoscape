Install
=======

NetworkX requires Python 3.6, 3.7, or 3.8.  If you do not already
have a Python environment configured on your computer, please see the
instructions for installing the full `scientific Python stack
<https://scipy.org/install.html>`_.

.. note::
   If you are on Windows and want to install optional packages (e.g., `scipy`),
   then you will need to install a Python distribution such as
   `Anaconda <https://www.anaconda.com/download/>`_,
   `Enthought Canopy <https://www.enthought.com/product/canopy>`_,
   `Python(x,y) <http://python-xy.github.io/>`_,
   `WinPython <https://winpython.github.io/>`_, or
   `Pyzo <http://www.pyzo.org/>`_.
   If you use one of these Python distribution, please refer to their online
   documentation.

   `PyCharm <https://www.jetbrains.com/pycharm/>`_ and other integrated development
   environment often install their own Python distributions.

Below we assume you have the default Python environment already configured on
your computer and you intend to install ``py4cytoscape`` inside of it.  If you want
to create and work with Python virtual environments, please follow instructions
on `venv <https://docs.python.org/3/library/venv.html>`_ and `virtual
environments <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_.

First, make sure you have the latest version of ``pip`` (the Python package manager)
installed. If you do not, refer to the `Pip documentation
<https://pip.pypa.io/en/stable/installing/>`_ and install ``pip`` first.

Install the development version
-------------------------------

Install the current release of ``py4cytoscape`` with ``pip``::

    $ pip install python-igraph requests pandas networkx
    $ git clone git://github.com/bdemchak/py4cytoscape
    $ cd py4cytoscape
    $ python setup.py install # or python setup.py install --user

To exercise ``py4cytoscape``, you must first have downloaded, installed, and
executed Cytoscape. If you have not already done this, please refer to the `Launching
Cytoscape <http://manual.cytoscape.org/en/stable/Launching_Cytoscape.html#launching-cytoscape>'_
instructions.

Trying ``py4cytoscape`` (Python Console)
----------------------------------------

To verify that ``py4cytoscape`` is properly installed and able to communicate with
Cytoscape, execute the following in a Python Console::

   import py4cytoscape as py4
   dir(py4)
   py4.import_network_from_file("tests\data\galfiltered.sif")

This will import ``py4cytoscape`` into the Python namespace, then print a (long) list
of ``py4cytoscape`` entrypoints, and then direct Cytoscape to load a demonstration
network.

Note that
# Before running this, save galfiltered.sif in the current directory



Install the development version
-------------------------------

If you have `Git <https://git-scm.com/>`_ installed on your system, it is also
possible to install the development version of ``networkx``.

Before installing the development version, you may need to uninstall the
standard version of ``networkx`` using ``pip``::

    $ pip uninstall networkx

Then do::

    $ git clone https://github.com/networkx/networkx.git
    $ cd networkx
    $ pip install -e .

The ``pip install -e .`` command allows you to follow the development branch as
it changes by creating links in the right places and installing the command
line scripts to the appropriate locations.

Then, if you want to update ``networkx`` at any time, in the same directory do::

    $ git pull

Optional packages
-----------------

.. note::
   Some optional packages (e.g., `scipy`, `gdal`) may require compiling
   C or C++ code.  If you have difficulty installing these packages
   with `pip`, please review the instructions for installing
   the full `scientific Python stack <https://scipy.org/install.html>`_.

The following optional packages provide additional functionality.

- `NumPy <http://www.numpy.org/>`_ (>= 1.15.4) provides matrix representation of
  graphs and is used in some graph algorithms for high-performance matrix
  computations.
- `SciPy <http://scipy.org/>`_ (>= 1.1.0) provides sparse matrix representation
  of graphs and many numerical scientific tools.
- `pandas <http://pandas.pydata.org/>`_ (>= 0.23.3) provides a DataFrame, which
  is a tabular data structure with labeled axes.
- `Matplotlib <http://matplotlib.org/>`_ (>= 3.0.2) provides flexible drawing of
  graphs.
- `PyGraphviz <http://pygraphviz.github.io/>`_ (>= 1.5) and
  `pydot <https://github.com/erocarrera/pydot>`_ (>= 1.2.4) provide graph drawing
  and graph layout algorithms via `GraphViz <http://graphviz.org/>`_.
- `PyYAML <http://pyyaml.org/>`_ provides YAML format reading and writing.
- `gdal <http://www.gdal.org/>`_ provides shapefile format reading and writing.
- `lxml <http://lxml.de/>`_ used for GraphML XML format.

To install ``networkx`` and all optional packages, do::

    $ pip install networkx[all]

To explicitly install all optional packages, do::

    $ pip install numpy scipy pandas matplotlib pygraphviz pydot pyyaml gdal

Or, install any optional package (e.g., ``numpy``) individually::

    $ pip install numpy

Testing
-------

NetworkX uses the Python ``pytest`` testing package.  You can learn more
about pytest on their `homepage <https://pytest.org>`_.

Test a source distribution
^^^^^^^^^^^^^^^^^^^^^^^^^^

You can test the complete package from the unpacked source directory with::

    pytest networkx

Test an installed package
^^^^^^^^^^^^^^^^^^^^^^^^^

From a shell command prompt you can test the installed package with::

   pytest --pyargs networkx

If you have a file-based (not a Python egg) installation you can test the
installed package with::

    >>> import networkx as nx
    >>> nx.test()

or::

    python -c "import networkx as nx; nx.test()"

