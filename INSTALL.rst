Install
=======

``py4cytoscape`` requires Python 3.6, 3.7, or 3.8.  If you do not already
have a Python environment configured on your computer, please see the
instructions for installing the full `scientific Python stack
<https://scipy.org/install.html>`_.

.. note::
   If you are on Windows and want to install optional packages (e.g., `scipy`),
   then you will need to install a Python distributions such as
   `Anaconda <https://www.anaconda.com/download/>`_,
   `Enthought Canopy <https://www.enthought.com/product/canopy>`_,
   `Python(x,y) <http://python-xy.github.io/>`_,
   `WinPython <https://winpython.github.io/>`_, or
   `Pyzo <http://www.pyzo.org/>`_.
   If you use one of these Python distribution, please refer to their online
   documentation.

   `PyCharm <https://www.jetbrains.com/pycharm/>`_ and other integrated development
   environments often install their own Python distributions.

Below we assume you have the default Python environment already configured on
your computer and you intend to install ``py4cytoscape`` inside of it.  If you want
to create and work with Python virtual environments, please follow instructions
on `venv <https://docs.python.org/3/library/venv.html>`_ and `virtual
environments <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_.

First, make sure you have the latest version of ``pip`` (the Python package manager)
installed. If you do not, refer to the `Pip documentation
<https://pip.pypa.io/en/stable/installing/>`_ and install ``pip`` first.

Cytoscape Prerequisite
----------------------

To exercise ``py4cytoscape``, you must first have downloaded, installed, and
executed Cytoscape. If you have not already done this, please refer to the `Launching
Cytoscape <http://manual.cytoscape.org/en/stable/Launching_Cytoscape.html#launching-cytoscape>`_
instructions.

.. note::
   Cytoscape and ``py4cytoscape`` must be running on the same workstation or
   virtual machine. ``py4cytoscape`` communicates with Cytoscape via a localhost
   connection, which precludes ``py4cytoscape`` from accessing Cytoscape
   remotely. While this limitation can be overcome by configuring ``py4cytoscape`` or
   supplying the Cytoscape URL in ``py4cytoscape`` calls, this can become a complex
   networking problem if firewalls and routers are present on the network.

Install the development version (Python Console)
------------------------------------------------

Install the current release of ``py4cytoscape`` with ``pip``::

   pip install python-igraph requests pandas networkx
   git clone git://github.com/bdemchak/py4cytoscape
   cd py4cytoscape
   python setup.py install # or python setup.py install --user

Install the development version (Jupyter Notebook)
--------------------------------------------------

Install the current release of ``py4cytoscape`` with ``pip``::

   !pip install python-igraph requests pandas networkx
   !pip install git+https://github.com/bdemchak/py4cytoscape
   !curl localhost:1234

Verify Cytoscape connection
---------------------------

To verify that ``py4cytoscape`` is properly installed and able to communicate with
Cytoscape, execute the following in a Python Console or Jupyter Notebook
(after starting Cytoscape)::

   import py4cytoscape as py4
   dir(py4)
   py4.cytoscape_ping()
   py4.cytoscape_version_info()
   py4.import_network_from_file("tests\data\galfiltered.sif")

This will import ``py4cytoscape`` into the Python namespace, print a (long) list
of ``py4cytoscape`` entrypoints, and then demonstrate a connection to Cytoscape
by collecting Cytoscape information and loading a demonstration
network.

Testing
-------

``py4cytoscape`` uses the Python ``unittest`` testing package. You can learn more
about ``unittest`` on its `homepage <https://docs.python.org/3/library/unittest.html>`_.

To execute tests from an OS command line, set the current directory to
the ``py4cytoscape`` package directory. Then, establish the execution environment::

   cd tests
   set PYTHONPATH=..

The ``py4cytoscape`` test suite consists of a number of sub-suites. Executing one
or two of them is relatively quick. To execute a single sub-suite
(e.g., ``test_apps.py``)::

   python -m unittest test_apps.py

To execute more than one sub-suite (e.g., ``test_apps.py`` and ``test_filters.py``)::

   python -m unittest test_apps.py test_filters.py

To execute the entire test suite::

   python -m unittest

To execute a single test (e.g., test_get_app_information) in a single test suite::

   python -m unittest test_apps.AppsTests.test_get_app_information

.. note::
   To send test output to a file, redirect stderr and console::

      python -m unittest 2>stderr.log 1>cons.log

   Some tests require console input, and without console prompts, the tests will
   appear to stall. To avoid executing such tests, set the PY4CYTOSCAPE_SKIP_UI_TESTS
   environment variable described below.

.. note::
   To execute tests with less console debug output, set this environment
   variable before executing tests::

      set PY4CYTOSCAPE_SUMMARY_LOGGER=FALSE

   To further configure logging, see the :ref:`Logging` file.

.. note::
   To execute tests without showing test names as tests execute, set this
   environment variable before executing the tests::

      set PY4CYTOSCAPE_SHOW_TEST_PROGRESS=FALSE

.. note::
   To skip execution of tests that require user input, set this environment
   variable before executing tests::

      set PY4CYTOSCAPE_SKIP_UI_TESTS=TRUE

.. note::
    When executing a large number of tests, we recommend that all three
    environment variables be set as described above.

.. note::
    When executing tests in PyCharm, you can set environment
    variables using the ``Run | Edit Configurations...`` menu item.

