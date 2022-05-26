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