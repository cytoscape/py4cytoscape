rem ... from https://packaging.python.org/tutorials/packaging-projects/
rem ... remember to update twine command (below) to contain new version
rem ... remember to bump the version number in _version.py before uploading

python3 -m pip install --user --upgrade setuptools wheel twine
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/py4cytoscape-0.0.9*


