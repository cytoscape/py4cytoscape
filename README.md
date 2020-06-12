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
py4cytoscape emits log entries in SysLog format. For example:

```
[INFO] py4...S:  ǀHTTP DELETE(http://localhost:1234/v1/networks)
[INFO] py4...S:  ǀOK[200]
```  

``[INFO]`` is the priority level.

``py4...S`` the name of the py4cytoscape package.

The count of ``|`` indicates the nesting level of the currently executing code, where ``||`` indicates log entries nested in code at the ``|`` level. 

The remainder of the message contains the logged information. In the example above, an HTTP DELETE call is logged along with the HTTP server's reply.
 
Logger configuration is available in the ``py4cytoscape_logger_settings.py`` module. py4cytoscape emits two independent logging streams: Summary (to the console) and Detail (to a file in the ``logs`` directory).

By default, Summary logging is the short form, which shows HTTP calls and results. You can disable Summary logging by setting ``_SUMMARY_LOG_LEVEL`` to ``NOTSET``, and you can enable full logging by setting it to ``DEBUG``.

By default, Detail logging is the long form, and is controlled by the ``_DETAIL_LOG_LEVEL`` setting.

For convenience, Summary logging can be controlled using an environment variable or at execution time. By default, Summary logging is enabled, but can be disabled:

```shell
set PY4CYTOSCAPE_SUMMARY_LOGGER=False
```

At execution time, it can be disabled by calling ``set_summary_logger()``. For example:

```
old_state = set_summary_logger(False)
# ... make several py4cytoscape calls ...
set_summary_logger(old_state)
```

``set_summary_logger()`` can also be called from a Python Console.

Here is an example of detailed logging involving nested calls:

```
2020-06-06 15:29:55,721 [DEBUG] py4...: ǀCalling cytoscape_version_info(base_url='http://localhost:1234/v1')
2020-06-06 15:29:55,721 [DEBUG] py4...: ǀǀCalling cyrest_get('version', base_url='http://localhost:1234/v1')
2020-06-06 15:29:55,721 [DEBUG] py4...: ǀǀHTTP GET(http://localhost:1234/v1/version)
2020-06-06 15:29:55,737 [DEBUG] py4...: ǀǀOK[200], content: {"apiVersion":"v1","cytoscapeVersion":"3.9.0-SNAPSHOT"}
2020-06-06 15:29:55,738 [DEBUG] py4...: ǀǀReturning 'cyrest_get': {'apiVersion': 'v1', 'cytoscapeVersion': '3.9.0-SNAPSHOT'}
2020-06-06 15:29:55,738 [DEBUG] py4...: ǀReturning 'cytoscape_version_info': {'apiVersion': 'v1', 'cytoscapeVersion': '3.9.0-SNAPSHOT'}
```

License
-------

Released under the MIT License (see `LICENSE` file)::

    Copyright (c) 2018-2020 The Cytoscape Consortium
    Barry Demchak (bdemchak@ucsd.edu)
