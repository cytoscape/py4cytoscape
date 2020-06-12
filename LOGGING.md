Logging
=======

py4cytoscape logging is based on the Python ``logging`` package, which is based on ``JUnit``. 
py4cytoscape emits log entries in SysLog format. For example::

   [INFO] py4...S:  ǀHTTP DELETE(http://localhost:1234/v1/networks)
   [INFO] py4...S:  ǀOK[200]  

``[INFO]`` is the priority level.

``py4...S`` the name of the py4cytoscape package.

The count of ``|`` indicates the nesting level of the currently executing code, where ``||`` indicates log entries called from code at the ``|`` level. 

The remainder of the message contains the logged information. In the example above, an HTTP DELETE call is logged along with the HTTP server's reply.
 
Logger configuration is available in the ``py4cytoscape_logger_settings.py`` module. py4cytoscape emits two independent logging streams: Summary (to the console) and Detail (to a file in the ``logs`` directory).

By default, Summary logging is the short form (priority ``INFO``), which shows HTTP calls and results. You can disable Summary logging by setting ``_SUMMARY_LOG_LEVEL`` to ``NOTSET``, and you can enable full logging by setting it to ``DEBUG``.

By default, Detail logging is the long form (priority ``DEBUG``), and is controlled by the ``_DETAIL_LOG_LEVEL`` setting.

Here is an example of Detail logging involving nested calls::

   2020-06-06 15:29:55,721 [DEBUG] py4...: ǀCalling cytoscape_version_info(base_url='http://localhost:1234/v1')
   2020-06-06 15:29:55,721 [DEBUG] py4...: ǀǀCalling cyrest_get('version', base_url='http://localhost:1234/v1')
   2020-06-06 15:29:55,721 [DEBUG] py4...: ǀǀHTTP GET(http://localhost:1234/v1/version)
   2020-06-06 15:29:55,737 [DEBUG] py4...: ǀǀOK[200], content: {"apiVersion":"v1","cytoscapeVersion":"3.9.0-SNAPSHOT"}
   2020-06-06 15:29:55,738 [DEBUG] py4...: ǀǀReturning 'cyrest_get': {'apiVersion': 'v1', 'cytoscapeVersion': '3.9.0-SNAPSHOT'}
   2020-06-06 15:29:55,738 [DEBUG] py4...: ǀReturning 'cytoscape_version_info': {'apiVersion': 'v1', 'cytoscapeVersion': '3.9.0-SNAPSHOT'}

Runtime Control
---------------
   
For convenience, Summary logging can be controlled using an environment variable or at execution time. By default, Summary logging is enabled, but can be disabled::

   set PY4CYTOSCAPE_SUMMARY_LOGGER=False

At execution time, it can be disabled by calling ``set_summary_logger()``. This is handy within a busy code block or when running in a Notebook environment. For example::

   old_state = set_summary_logger(False)
     # ... make several py4cytoscape calls ...
   set_summary_logger(old_state)

