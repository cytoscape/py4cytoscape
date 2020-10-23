# py4cytoscape

This project recreates the [R-based ``RCy3`` Cytoscape Automation library](https://github.com/cytoscape/RCy3) as a Python package. The idea is to allow a Cytoscape workflow to be written in one language (R or Python) and translated to another language (Python or R) without having to learn different Cytoscape interfaces. The previous Cytoscape Python interface ([Py2Cytoscape](https://github.com/cytoscape/py2cytoscape)) has different features than the Cytoscape R library, and is therefore deprecated.

Additionally, this project attempts to maintain the same function signatures, return values, function implementation and module structure as the RCy3, thereby enabling smooth maintenance and evolution of both ``RCy3`` and ``py4cytoscape``.

This project uses PyCharm because of its excellent code management and debugging features.

Over time, py4cytoscape functionality should match RCy3 functionality. Once that occurs, novel Py2Cytoscape functions will be added to both as appropriate. The official Automation API definition met by both RCy3 and py4cytoscape is [here](https://docs.google.com/spreadsheets/d/1XLWsKxGLqcBWLzoW2y6HyAUU2jMXaEaWw7QLn3NE5nY/edit?usp=sharing). The API is versioned, and you can see which API version RCy3 or py4cytoscape implements by executing the cytoscape_version_info() or cytoscapeVersionInfo() function.

An overall scorecard comparing Py2Cytoscape, ``RCy3`` and ``py4cytoscape`` can be found [here](https://docs.google.com/spreadsheets/d/1uhBTbOMI4QMKUpLaOTuf6BP5wgqU6-pOzkj6BNmC4CY/edit?usp=sharing). Pay close attention to columns E and F, which show how much of RCy3 is reflected in py4cytoscape.


# Documentation

To understand the API structure and see calling examples, see the ``py4cytoscape`` [documentation](https://py4cytoscape.readthedocs.io/en/latest/).
 
## How to install and test

For an explanation of ``py4cytoscape`` installation and testing, see the [INSTALL.rst](INSTALL.rst) file.

## How run a simple workflow

For a quick tutorial on how to build a workflow in Python and using ``py4cytoscape``, see
https://py4cytoscape.readthedocs.io/en/latest/tutorials/index.html.
You can try ``py4cytoscape`` with a web browser only, without installing anything in your local environment.

## How to configure logging

``py4cytoscape`` logging is based on the Python ``logging`` package, which is based on the Java ``logging`` framework. 

For an explanation of log configuration and use, see the [LOGGING.rst](LOGGING.rst) file.

## How to build and release
1. Check all sources (including tests) into Github, merge them into the Master branch, and make Master the current branch
1. Update the version number in both py4cytoscape/_version.py and build.bat
1. Successfully execute all tests by using the tests/runalltests.bat file
1. Create a new release file in doc/release to match the version number (e.g., release_0.0.1.rst) 
1. Update the theme list in doc/release_log.rst and reference the release file you just created
1. Create a new Github tag (in the Releases section on the far right of the Github GUI)
1. Execute build.bat to check into PyPI __... be sure you updated the version number in build.bat first__ 

Note that the user manual is automatically updated when Master files changes. You can find the manual [here](https://py4cytoscape.readthedocs.io/en/latest/).


## License

``py4cytoscape`` is released under the MIT License (see [LICENSE.rst](LICENSE.rst) file):

```
    Copyright (c) 2018-2020 The Cytoscape Consortium
    Barry Demchak <bdemchak@ucsd.edu>
```
