# py4cytoscape

This project recreates the [R-based RCy3 Cytoscape Automation library](https://github.com/cytoscape/RCy3) as a Python package. The idea is to allow a Cytoscape workflow to be written in one language (R or Python) and translated to another language (Python or R) without having to learn different Cytoscape interfaces. The current Cytoscape Python interface ([Py2Cytoscape](https://github.com/cytoscape/py2cytoscape)) has different features than the Cytoscape R library, and therefore doesn't fit my purpose.

Additionally, this project attempts to maintain the same function signatures, return values, function implementation and module structure as the RCy3, thereby enabling smooth maintenance and evolution of both RCy3 and py4cytoscape.

This project uses PyCharm because of its excellent code management and debugging features.

Over time, py4cytoscape functionality should match RCy3 functionality. Once that occurs, novel Py2Cytoscape functions will be added to both as appropriate.

An overall scorecard comparing Py2Cytoscape, RCy3 and py4cytoscape can be found [here](https://docs.google.com/spreadsheets/d/1uhBTbOMI4QMKUpLaOTuf6BP5wgqU6-pOzkj6BNmC4CY/edit?usp=sharing). Pay close attention to columns E and F, which show how much of RCy3 is reflected in py4cytoscape.
 
## How to install

```shell
pip install python-igraph requests pandas networkx
git clone git://github.com/bdemchak/py4cytoscape
cd py4cytoscape
python setup.py install # or python setup.py install --user
```

## How to use (from within a Python command shell)

```python
import py4cytoscape
dir(py4cytoscape)
py4cytoscape.import_network_from_file("galfiltered.sif") # Before running this, save galfiltered.sif in the current directory.
```

## How to use (from within a Jupyter Notebook on the same machine as Cytoscape)

```shell
# Install the current py4cytoscape package
!pip install git+https://github.com/bdemchak/py4cytoscape

# Manually start Cytoscape (using your mouse/keyboard and operating system)

# Verify that Cytoscape is started and reachable
!curl localhost:1234
```
```python
# Import py4cytoscape and verify its connection to Cytoscape
import py4cytoscape as p4c
p4c.cytoscape_ping()
p4c.cytoscape_version_info()
```

## How to test (in Windows)

First, start Cytoscape.

```shell
rem Assuming the current directory is the py4cytoscape project directory
cd tests 
set PYTHONPATH=..

rem To execute a single set of tests ...
python -m unittest test_apps.py

rem To execute two sets of tests ...
python -m unittest test_apps.py test_filters.py

rem To execute all tests ...
python -m unittest

rem To execute a single test out of a set ...
python -m unittest test_apps.AppsTests.test_get_app_information

rem Pro Tip: To send test output to a file, redirect stderr ...
python -m unittest 2>myfile.log

rem Pro Tip: To execute tests with less console debug output,
rem set this environment variable before executing tests ...
set PY4CYTOSCAPE_SUMMARY_LOGGER=FALSE

rem Pro Tip: To execute tests that don't even show the names
rem tests being executed, set this environment variable before
rem executing tests
set PY4CYTOSCAPE_SHOW_TEST_PROGRESS=FALSE

rem Pro Tip: To skip execution of tests that require user input,
rem set this environment variable before executing tests ...
set PY4CYTOSCAPE_SKIP_UI_TESTS=TRUE

rem When executing all tests, we recommend the following 
rem that all three environment variables be set as described above.

rem Pro Tip: When executing tests in PyCharm, you can set 
rem environment variables using the 'Run | Edit Configurations...' 
rem menu item. 
```

## How to configure logging

py4cytoscape logging is based on the Python ``logging`` package, which is based on ``JUnit``. 

For an explanation of log configuration and use, see the [LOGGING.rst](LOGGING.rst) file.

## License

Released under the MIT License (see [LICENSE.rst](LICENSE.rst) file):

```
    Copyright (c) 2018-2020 The Cytoscape Consortium
    Barry Demchak <bdemchak@ucsd.edu>
```
