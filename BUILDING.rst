Building ``py4cytoscape``

(This list assumes you're already working on the Github branch for the new release, and that you'll be merging it into Master.)

1. Verify the version number in both py4cytoscape/_version.py and build.bat
2. If any API changes were made, be sure to update the [Automation API Definition](https://docs.google.com/spreadsheets/d/1XLWsKxGLqcBWLzoW2y6HyAUU2jMXaEaWw7QLn3NE5nY/edit#gid=1999503690) and change the Automation API version in py4cytoscape/_version.py
3. If any functions were added, be sure to add them to the appropriate .rst file in the References section of the document.
4. Verify that the requirements.txt file in the docs directory correctly identifies all external dependencies.
5. Verify that the setup.py file correctly identifies all external dependencies. If any dependencies have changed, be sure to update the Install.rst file, too.
6. Verify that changes to the [user manual]() are correct. Be sure to activate automatic ReadTheDocs [building](https://readthedocs.org/projects/py4cytoscape/versions/) for this new version.
7. Check all sources (including documents and tests) into Github, make Master the current branch, merge changes into the Master branch, commit to GitHub
8. Successfully execute all tests by using the tests/runalltests.bat and tests/runsanitytests.bat files
9. Execute liveness test (e.g., [Sanity Test](https://github.com/bdemchak/cytoscape-jupyter/tree/main/sanity-test)) on Google Colab
10. Execute both local and remote GangSu workflows (e.g., [Workflow1](https://colab.research.google.com/github/bdemchak/cytoscape-jupyter/blob/main/gangsu/basic%20protocol%201.ipynb) and [Workflow2](https://colab.research.google.com/github/bdemchak/cytoscape-jupyter/blob/main/gangsu/basic_protocol_2.ipynb#scrollTo=cZ9Gr2Pjnapm)) on Google Colab
11. Execute build.bat to check into PyPI __... be sure you updated the version number in build.bat first__
12. Again, successfully execute all tests by using the tests/runalltests.bat file, Gang Su workflows and the Sanity Test. (Change Sanity Test to fetch ``py4cytoscape`` from PyPI instead of Github.)
13. Check any/all changes to the [user manual](https://py4cytoscape.readthedocs.io/en/latest/) and fix them now. (Note that the manual is automatically re-compiled when changes are made to the Master branch in Github.)
14. Create a new Github tag (in the Releases section on the far right of the Github GUI)
15. Start a branch to contain the next round of py4cytoscape changes.
16. Update the version number in both py4cytoscape/_version.py and build.bat
17. Create a new release file in doc/release to match the version number (e.g., release_0.0.1.rst)
18. Update the theme list in doc/release_log.rst and reference the release file you just created
19. Check all changes into github
20. Activate the new branch in ReadTheDocs.org(https://readthedocs.org/projects/py4cytoscape/versions/)
