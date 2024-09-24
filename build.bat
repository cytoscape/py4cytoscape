rem ... from https://packaging.python.org/tutorials/packaging-projects/
rem ... remember to update twine command (below) to contain new version
rem ... remember to bump the version number in _version.py before uploading

python -m pip install --upgrade setuptools wheel twine
python setup.py sdist bdist_wheel
python -m twine upload dist/py4cytoscape-1.11.0*


