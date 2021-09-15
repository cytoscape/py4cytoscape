# py4cytoscape

This project recreates the [R-based ``RCy3`` Cytoscape Automation library](https://github.com/cytoscape/RCy3) as a Python package. The idea is to allow a Cytoscape workflow to be written in one language (R or Python) and translated to another language (Python or R) without having to learn different Cytoscape interfaces. The previous Cytoscape Python interface ([Py2Cytoscape](https://github.com/cytoscape/py2cytoscape)) has different features than the Cytoscape R library, and is therefore deprecated.

Additionally, this project attempts to maintain the same [function signatures](https://docs.google.com/spreadsheets/d/1XLWsKxGLqcBWLzoW2y6HyAUU2jMXaEaWw7QLn3NE5nY/edit#gid=1999503690), return values, function implementation and module structure as the RCy3, thereby enabling smooth maintenance and evolution of both ``RCy3`` and ``py4cytoscape``.

This project uses PyCharm because of its excellent code management and debugging features.

Over time, py4cytoscape functionality should match RCy3 functionality. Once that occurs, novel Py2Cytoscape functions will be added to both as appropriate. The official Automation API definition met by both RCy3 and py4cytoscape is [here](https://docs.google.com/spreadsheets/d/1XLWsKxGLqcBWLzoW2y6HyAUU2jMXaEaWw7QLn3NE5nY/edit?usp=sharing). The API is versioned, and you can see which API version RCy3 or py4cytoscape implements by executing the cytoscape_version_info() or cytoscapeVersionInfo() function.

An overall scorecard comparing Py2Cytoscape, ``RCy3`` and ``py4cytoscape`` can be found [here](https://docs.google.com/spreadsheets/d/1uhBTbOMI4QMKUpLaOTuf6BP5wgqU6-pOzkj6BNmC4CY/edit?usp=sharing). Pay close attention to columns E and F, which show how much of RCy3 is reflected in py4cytoscape.


# Documentation

To understand the API structure and see calling examples, see the ``py4cytoscape`` [documentation](https://py4cytoscape.readthedocs.io/en/latest/).
 
## How to install and test

For an explanation of ``py4cytoscape`` installation and testing, see the [INSTALL.rst](INSTALL.rst) file.

## How to run a simple workflow

For a quick tutorial on how to build a workflow in Python and using ``py4cytoscape``, see
https://py4cytoscape.readthedocs.io/en/latest/tutorials/index.html.
You can try ``py4cytoscape`` with a web browser only, without installing anything in your local environment.

## How to configure logging

``py4cytoscape`` logging is based on the Python ``logging`` package, which is based on the Java ``logging`` framework. 

For an explanation of log configuration and use, see the [LOGGING.rst](LOGGING.rst) file.

## How to build and release
1. Create a new release file in doc/release to match the version number (e.g., release_0.0.1.rst) 
1. Update the theme list in doc/release_log.rst and reference the release file you just created
1. Update the version number in both py4cytoscape/_version.py and build.bat
1. If any API changes were made, be sure to update the [Automation API Definition](https://docs.google.com/spreadsheets/d/1XLWsKxGLqcBWLzoW2y6HyAUU2jMXaEaWw7QLn3NE5nY/edit#gid=1999503690) and change the Automation API version in py4cytoscape/_version.py
1. If any functions were added, be sure to add them to the appropriate .rst file in the References section of the document.
1. Verify that the requirements.txt file in the docs directory correctly identifies all external dependencies.
1. Verify that the setup.py file correctly identifies all external dependencies.
1. Check all sources (including documents and tests) into Github, merge them into the Master branch, and make Master the current branch
1. Successfully execute all tests by using the tests/runalltests.bat file
1. Execute liveness test (e.g., [Sanity Test](https://github.com/bdemchak/cytoscape-jupyter/tree/main/sanity-test)) on Google Colab
1. Execute GangSu workflows (e.g., [Workflow1](https://colab.research.google.com/github/bdemchak/cytoscape-jupyter/blob/main/gangsu/basic%20protocol%201.ipynb) and [Workflow2](https://colab.research.google.com/github/bdemchak/cytoscape-jupyter/blob/main/gangsu/basic_protocol_2.ipynb#scrollTo=cZ9Gr2Pjnapm)) on Google Colab
1. Execute build.bat to check into PyPI __... be sure you updated the version number in build.bat first__
1. Again, successfully execute all tests by using the tests/runalltests.bat file, Gang Su workflows and the Sanity Test. (Change Sanity Test to fetch ``py4cytoscape`` from PyPI instead of Github.)
1. Check any/all changes to the [user manual](https://py4cytoscape.readthedocs.io/en/latest/) and fix them now. (Note that the manual is automatically re-compiled when changes are made to the Master branch in Github.)
1. Create a new Github tag (in the Releases section on the far right of the Github GUI)
1. Start a branch to contain the next round of py4cytoscape changes.

## Test Suites

``py4cytoscape`` is supported by extensive test suites that benefit ``py4cytoscape`` users as follows:
* Verify that all API functionality operates as documented
* Verify that changes to ``py4cytoscape`` don't break working functionality

These test suites are not intended to verify Cytoscape or CyREST operation, though they may have that side effect. 
Their main purpose is to verify that ``py4cytoscape`` functions either properly call CyREST or pre/post-process CyREST data. So, they test
that each function parameter has an intended affect in the context of one or more CyREST calls. The payoff is confidence 
in ``py4cytoscape`` functions over both the immediate and long term. 

Single tests or groups of tests can be executed from the command line per the [``py4cytoscape`` Installation instructions](INSTALL.rst).

Surprising (but true!) general rules of thumb:

* Creating a test for a ``py4cytoscape`` function may take between 2x and 5x the effort
needed to create the function itself. Combined with the effort to document ``py4cytoscape`` functions, the overall time 
needed to create the function itself may be only 30% of the total effort.

* Unless code is tested, it can reasonably assumed to be buggy ... either in its definition or
execution. **Untested code is essentially buggy code.**

* For a function or capability to be useful to a user, it must be documented in a place where a user can find it. In addition to testing functions, there
must be appropriate function documentation (in the function's header and in the .rst files in the _docs_ directory). Test cases are a
rich source for documentation and examples.

### Test Suite Construction

The ``py4cytoscape`` test suite is created under the rules of the Python [unittest](https://docs.python.org/3/library/unittest.html) framework, 
and exists in the `tests` directory. Just as each ``py4cytoscape`` Python module contains a collection of ``py4cytoscape`` functions, there
are corresponding test case files that contain tests for individual functions. For example, the `networks` module (`networks.py`) contains over 20
functions; the corresponding test case is `tests_networks.py`, and it contains individual tests that validate each `networks` function.

An individual test creates a testing environment and then verifies that each
variant of a specific function produces an expected result (i.e., some change in the network, its properties, or the file system). 
For example, the `test_networks.test_get_network_list` test loads the `galFiltered` network and calls `networks.get_network_list` with
various combinations of parameters. 

At heart, an individual test:

* Captures the state (_pre-state_) before the function is executed
* Executes the function with a particular combination of parameters and may return a value
* Verifies that the value is what is expected
* Captures the state (_post-state_) after the function is executed
* Verifies that the _post-state_ is different than the _pre-state_, and is the state that's expected

Note that these tests also verify that functions return expected results (e.g., exceptions) when _incorrect_ parameters are passed.

### Test Suite Usage

The test suite can be used in the following circumstances:

* During function development ... especially when [Test Driven Development](https://en.wikipedia.org/wiki/Test-driven_development) is practiced
* To verify that changes to a function don't break existing functionality
* To verify that new versions of Cytoscape don't cause functions to return incorrect results 
 
 To support this, any changes to a function must be followed up with new tests as appropriate. For example, changes in the
 `networks.get_network_list` function should be reflected by appropriate tests added/changed/removed in the `test_networks.test_get_network_list` function.
 
 


## License

``py4cytoscape`` is released under the MIT License (see [LICENSE.rst](LICENSE.rst) file):

```
    Copyright (c) 2018-2020 The Cytoscape Consortium
    Barry Demchak <bdemchak@ucsd.edu>
```
