# py4cytoscape

This project recreates the [R-based ``RCy3`` Cytoscape Automation library](https://github.com/cytoscape/RCy3) as a Python package. The idea is to allow a Cytoscape workflow to be written in one language (R or Python) and translated to another language (Python or R) without having to learn different Cytoscape interfaces. The previous Cytoscape Python interface ([Py2Cytoscape](https://github.com/cytoscape/py2cytoscape)) has different features than the Cytoscape R library, and is therefore deprecated.

Additionally, this project attempts to maintain the same [function signatures](https://docs.google.com/spreadsheets/d/1XLWsKxGLqcBWLzoW2y6HyAUU2jMXaEaWw7QLn3NE5nY/edit#gid=1999503690), return values, function implementation and module structure as the RCy3, thereby enabling smooth maintenance and evolution of both ``RCy3`` and ``py4cytoscape``.

This project uses PyCharm because of its excellent code management and debugging features.

Over time, py4cytoscape functionality should match RCy3 functionality. Once that occurs, novel Py2Cytoscape functions will be added to both as appropriate. The official Automation API definition met by both RCy3 and py4cytoscape is [here](https://docs.google.com/spreadsheets/d/1XLWsKxGLqcBWLzoW2y6HyAUU2jMXaEaWw7QLn3NE5nY/edit?usp=sharing). The API is versioned, and you can see which API version RCy3 or py4cytoscape implements by executing the cytoscape_version_info() or cytoscapeVersionInfo() function.

An overall scorecard comparing Py2Cytoscape, ``RCy3`` and ``py4cytoscape`` can be found [here](https://docs.google.com/spreadsheets/d/1uhBTbOMI4QMKUpLaOTuf6BP5wgqU6-pOzkj6BNmC4CY/edit?usp=sharing). Pay close attention to columns E and F, which show how much of RCy3 is reflected in py4cytoscape.


# Documentation

To understand the API structure and see calling examples, see the ``py4cytoscape`` [documentation](https://py4cytoscape.readthedocs.io/en/latest/).

# Quick Start

The quickest way to see ``py4cytoscape`` in action is via the [Overview of py4cytoscape](https://github.com/cytoscape/cytoscape-automation/blob/master/for-scripters/Python/Overview-of-py4cytoscape.ipynb) Jupyter-based workflow.

You can avoid installing Python or ``py4cytoscape`` by clicking on the *Open in Colab* button, and running the Python workflow in the Google Cloud, though you will still have to install Cytoscape on your workstation. 

You can follow the notes in the Jupyter Notebook as the workflow automates Cytoscape execution.
 
## How to install and test

For an explanation of ``py4cytoscape`` installation and testing, see the [INSTALL.rst](INSTALL.rst) file.

## How to learn more about ``py4cytoscape``

A broad set of Cytoscape Automation samples and tutorials is available on the [Cytoscape Automation Wiki](https://github.com/cytoscape/cytoscape-automation/wiki).

## How to configure logging

``py4cytoscape`` logging is based on the Python ``logging`` package, which is based on the Java ``logging`` framework. 

For an explanation of log configuration and use, see the [LOGGING.rst](LOGGING.rst) file.

## How to build and release

``py4cytoscape`` maintainers can build a new release using the process in [BUILDING.rst](BUILDING.rst).

## How to test

``py4cytoscape`` has extensive test suites. Maintainers can learn more about testing in the [TESTING.rst](TESTING.rst) file.

 
 


# Running the Enrichment Analysis Visualizer Appyter (Docker)

The [Enrichment Analysis Visualizer Appyter](https://appyters.maayanlab.cloud/) can be run locally as a Docker container to complement `py4cytoscape` analyses. It serves a Flask web app on container port `5000`.

## Prerequisites

- Docker is installed and the daemon is running (on macOS, start Docker Desktop: `open -a Docker`).

## Start the container

```bash
docker run -d --name appyter-eav \
  --device /dev/fuse --cap-add SYS_ADMIN --security-opt apparmor:unconfined \
  -p 5001:5000 \
  maayanlab/appyter-enrichment_analysis_visualizer:0.2.7-0.19.17 \
  appyter flask-app
```

Notes:

- **Start command is required.** The image's default command is `/bin/sh`, so it must be launched with `appyter flask-app` to start the web server. Running it without a command (or with only `-it`) drops you into a shell instead of serving the app.
- **Image tag.** Use a tag that exists on Docker Hub — `0.2.7-0.19.17` is the latest at time of writing. Verify current tags with:
  ```bash
  curl -s "https://hub.docker.com/v2/repositories/maayanlab/appyter-enrichment_analysis_visualizer/tags?page_size=25&ordering=last_updated"
  ```
- **FUSE flags.** `--device /dev/fuse --cap-add SYS_ADMIN --security-opt apparmor:unconfined` are required by the Appyter runtime for filesystem mounting.
- **Platform.** The image is `linux/amd64`; on Apple Silicon it runs under emulation (a harmless platform-mismatch warning is expected).

## Port mapping

The container listens on port `5000` internally (`APPYTER_PORT=5000`). Map it to a host port with `-p <host>:5000`.

- On macOS, host port `5000` is often already taken by the **Control Center / AirPlay Receiver** service, causing `bind: address already in use`. The example above maps to host port **`5001`** to avoid this. Check what holds a port with:
  ```bash
  lsof -nP -iTCP:5000 -sTCP:LISTEN
  ```
- To use host port `5000` instead, free it first (System Settings → General → AirDrop & Handoff → turn off **AirPlay Receiver**), then run with `-p 5000:5000`.

## Verify it is accessible

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5001/
```

A `200` response indicates the app is up (during startup you may briefly see `502`). Then open it in a browser:

```
http://localhost:5001
```

## Stop and remove

```bash
docker rm -f appyter-eav
```

## License

``py4cytoscape`` is released under the MIT License (see [LICENSE.rst](LICENSE.rst) file):

```
    Copyright (c) 2018-2022 The Cytoscape Consortium
    Barry Demchak <bdemchak@ucsd.edu>
```
