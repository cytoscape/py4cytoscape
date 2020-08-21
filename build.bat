rem ... from https://packaging.python.org/tutorials/packaging-projects/
rem ... remember to bump the version number in setup.py before uploading

python3 -m pip install --user --upgrade setuptools wheel twine
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*


