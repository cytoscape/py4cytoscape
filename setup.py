import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bdemchak", # Replace with your own username
    version="0.0.1",
    author="Barry Demchak",
    author_email="bdemchak@ucsd.edu",
    description="Cytoscape Automation API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bdemchak/PyCy3",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

# How to build distribution: https://packaging.python.org/tutorials/packaging-projects/
# print('Packages:')
# print(setuptools.find_packages())