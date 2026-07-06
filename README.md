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

# Cytoscape MCP Integration

Cytoscape can also be driven through a **Model Context Protocol (MCP)** server (`cytoscape-mcp`), which lets MCP-aware clients (agents, IDEs, or plain HTTP tooling) load and inspect networks in a running Cytoscape Desktop. The server speaks JSON-RPC 2.0 over the MCP *streamable HTTP* transport.

## Prerequisites

- Cytoscape Desktop is running.
- The `cytoscape-mcp` server is active and listening (default endpoint: `http://localhost:1234/mcp`).

> The endpoint accepts `POST`, `DELETE`, and `OPTIONS`. A plain `GET /mcp` returns `405 Method Not Allowed` — this is expected, not an error.

## Required headers

Every request must send:

- `Content-Type: application/json`
- `Accept: application/json, text/event-stream` (the server may reply with an SSE `event: message` stream)

After the handshake, include the session id returned by `initialize`:

- `Mcp-Session-Id: <session-id>`

## Integration steps

### 1. Initialize (handshake + connectivity test)

```bash
curl -sS -i -X POST http://localhost:1234/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"my-client","version":"0.0.1"}}}'
```

A successful response is `200 OK` and includes the session id in the response headers, e.g.:

```
Mcp-Session-Id: 2d28b700-e47e-47f5-88e3-c8da4d8c166a
```

and a body reporting the server info and capabilities:

```json
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"logging":{},"prompts":{"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"cytoscape-mcp","version":"1.0.2"}}}
```

Capture the `Mcp-Session-Id` value for all subsequent requests.

### 2. Complete the handshake

Send the `initialized` notification (no response body is returned):

```bash
SESSION="2d28b700-e47e-47f5-88e3-c8da4d8c166a"
curl -sS -X POST http://localhost:1234/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'
```

### 3. Discover available tools

```bash
curl -sS -X POST http://localhost:1234/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'
```

The server currently exposes one tool:

- **`load_cytoscape_network_view`** — creates a new Cytoscape network collection with a view from one of three sources:
  - `ndex` — an NDEx network id
  - `network-file` — a local network file (e.g. `.sif`, `.cys`)
  - `tabular-file` — a delimited file with column mapping

## Usage example: load a network from a file

Invoke the tool with a bundled Cytoscape sample network (`galFiltered.sif`):

```bash
curl -sS -X POST http://localhost:1234/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"load_cytoscape_network_view","arguments":{"source":"network-file","file_path":"/Applications/Cytoscape_v3.10.4/sampleData/galFiltered.sif"}}}'
```

The result arrives on the SSE stream and reports the new network:

```json
{"status":"success","network_suid":578,"node_count":330,"edge_count":359,"network_name":"galFiltered"}
```

## Usage example: load a network from NDEx

```bash
curl -sS -X POST http://localhost:1234/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"load_cytoscape_network_view","arguments":{"source":"ndex","network_id":"a7e43e3d-c7f8-11ec-8d17-005056ae23aa"}}}'
```

## Troubleshooting

- **`405 Method Not Allowed`** — you used `GET`; the MCP endpoint requires `POST`.
- **`406 Not Acceptable`** — add `text/event-stream` to the `Accept` header.
- **Missing/invalid session** — ensure `Mcp-Session-Id` matches the value returned by `initialize`; re-run the handshake if the server was restarted.
- **Tool call fails to create a network** — confirm Cytoscape Desktop is running and the `file_path` is accessible to the machine hosting Cytoscape.

## License

``py4cytoscape`` is released under the MIT License (see [LICENSE.rst](LICENSE.rst) file):

```
    Copyright (c) 2018-2022 The Cytoscape Consortium
    Barry Demchak <bdemchak@ucsd.edu>
```
