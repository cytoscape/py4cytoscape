export PY4CYTOSCAPE_SHOW_TEST_PROGRESS=TRUE
export PY4CYTOSCAPE_SKIP_UI_TESTS=TRUE
export PY4CYTOSCAPE_SUMMARY_LOGGER=FALSE
export PYTHONPATH=..

echo WARNING -- Tests that require user input will be skipped
echo WARNING -- Remember to execute user input tests with PY4CYTOSCAPE_SKIP_UI_TESTS=FALSE

date

python3 -m unittest 2>err

date


