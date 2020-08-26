import setuptools

# Nasty but effective way to set __version__
exec(open("py4cytoscape/_version.py").read())

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py4cytoscape",
    version=__version__,
    author="Barry Demchak",
    author_email="bdemchak@ucsd.edu",
    maintainer='Barry Demchak',
    maintainer_email='bdemchak@ucsd.edu',
    description="Cytoscape Automation API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bdemchak/py4cytoscape",
    license='MIT License',
    keywords=['data visualization', 'visualization', 'cytoscape',
              'bioinformatics', 'graph', 'network'],
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'pandas',
        'networkx',
        'requests',
        'python-igraph',
    ],
    classifiers=[
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Visualization'
    ],
    python_requires='>=3.6',
    test_suite='tests',
)

# How to build distribution: https://packaging.python.org/tutorials/packaging-projects/
# print('Packages:')
# print(setuptools.find_packages())

