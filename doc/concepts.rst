Concepts
========

py4cytoscape is a Python module that interfaces with Cytoscape to enable
researchers to write reproducible sequences of network manipulations, visualizations
and analyses. py4cytoscape includes functions that accomplish network operations
common to many kinds of workflows. Using py4cytoscape, a Python application can:

* load a network (from a file, from the NDEx or STRING repositories, or from local Python variables)
* operate on the network
* retrieve results

The Python application can perform several rounds of network analysis and results retrieval,
and mix visualization and analyses with existing Python libraries. Finally, it can
repeat the process for one network after another.

.. _FullPaper: https://pubmed.ncbi.nlm.nih.gov/31477170/
.. _WikiPages: https://github.com/cytoscape/cytoscape-automation/wiki/Trying-Automation/

py4cytoscape works by connecting to Cytoscape's CyREST feature, which is the
foundation of Cytoscape Automation (FullPaper_ or WikiPages_). The
connection is based on standard HTTP networking protocols. For py4cytoscape to
work, you must have Cytoscape running on your workstation.

Your Python application can be run in several modes:

* Standalone on the workstation that's already running Cytoscape
* In a Jupyter Notebook running on the same workstation as your Cytoscape
* In a Jupyter Notebook running on a remote server (e.g., Google Colab or GenePattern Notebook)

This section discusses conceptual and miscellaneous topics relating to py4cytoscape use:

* `Missing Functions`_ shows how to call Cytoscape functions not covered in py4cytoscape.

* `Calling Cytoscape Apps`_ shows how to call Cytoscape apps that support automation.

* `Jupyter Notebook`_ shows how to use py4cytoscape from within a Jupyter Notebook.

* `Sandboxing`_ shows how to limit Cytoscape to accessing files in particular directories.

* `Value Generators`_ shows how to automatically generate colors, sizes, shapes, etc. for style mappings.


Missing Functions
-----------------

While py4cytoscape provides hundreds of functions, there are still many Cytoscape
operations for which py4cytoscape does not provide an equivalent function. However,
it *does* provide mechanisms for you to write your own functions that can invoke many of these
Cytoscape operations.

The complete list of invokable Cytoscape operations (either in py4cytoscape or not)
is spread across two web pages, differing by the mechanism you would use to
invoke them. Using the Cytoscape menus:

* **Help | Automation | CyREST API**
* **Help | Automation | CyREST Commands API**

Both pages enable you to try Cytoscape operations out directly from the web page
(via the Swagger interface). Additionally, the Commands panel
(**View | Show Commands Panel**) contains the same material as the CyREST
Commands API page, but uses a command line oriented interface for
experimentation.

For example, there is no py4cytoscape function for finding the name of
the Cytoscape session. However, the CyREST API page lists this function under the
``Session`` heading as ``GET /v1/session/name``. You can
try this function under Swagger by clicking the **Try it now!** button.

For operations on the CyREST API page, you can write your own Python functions by
using one of the following py4cytoscape functions, according to the label on the CyREST API
Swagger page:

* ``commands.cyrest_get()``
* ``commands.cyrest_post()``
* ``commands.cyrest_put()``
* ``commands.cyrest_delete()``

For the session rename operation, the py4cytoscape call would be:

.. code:: python

    commands.cyrest_get('session/name', {})

The {} value reflects that there are no parameters to the ``session/name`` operation.
If there were parameters, they would be passed as Python dictionary values (e.g.,
``{'param1': 'value1', 'param2': 'value2'}``).

As another example, there is no py4cytoscape function for renaming a filter.
However, the CyREST Commands API page lists this operation under the ``filter`` heading as
``POST /v1/commands/filter/rename``. You can try this operation yourself
on the CyREST Commands API page by using Swagger to specify the ``container``,
``name`` and ``newName`` parameters and clicking the
**Try it now!** button. You can do the same thing in the Commands panel by first
entering ``help filter rename`` to find the parameter names and then something like:

.. code:: python

    filter rename container='filter' name='affinity' newName='myAffinity'

For operations on the CyREST Commands API page, you can write your own Python functions by
using one of the following py4cytoscape functions, according to the label on the CyREST Commands API
Swagger page:

* ``commands.commands_get()``
* ``commands.commands_post()``

For the filter rename operation, the py4cytoscape call would be:

.. code:: python

    commands.commands_post('filter rename container="filter" name="affinity" newName="myAffinity"')

For commands.cyrest* and commands.commands* functions, you can determine the return
result by trying the equivalent Cytoscape operation using Swagger's **Try it now!** button.

.. _calling-cytoscape-apps:

Calling Cytoscape Apps
----------------------

py4cytoscape includes operations corresponding to functions in a number of
apps delivered with Cytoscape. However, there are many more App Store apps for
which py4cytoscape provides no function. You can still call these
apps' functions using the techniques described in the `Missing Functions`_ section.

To find out which apps are automation-enabled, you can visit
the `App Store <http://apps.cytoscape.org/>`_ and click on the *automation* category
on the left. At this writing, there are over 40 apps, only a few of which are
delivered with Cytoscape -- see the end of this section for a list.

You can also determine whether a specific app (e.g., MCODE) is enabled for
automation by viewing its App Store page
(e.g., http://apps.cytoscape.org/apps/mcode). If the gear icon appears below
the page title, the app has functions callable via CyREST.

To determine which functions and parameters an app offers, first install the
app in Cytoscape (using the **Apps | App Manager** menu), and then look for the app's category
in either the CyREST Commands API or the Commands panel as described in the
`Missing Functions`_ section.

For example, to call the MCODE cluster function:

.. code:: python

    commands.commands_post('mcode cluster degreeCutoff=2 fluff=true fluffNodeDensityCutoff=0.1 haircut=true includeLoops=false kCore=2 maxDepthFromStart=100 network=current nodeScoreCutoff=0.2 scope=NETWORK')

Automation-enabled apps::

    aMatReader
    Analyzer
    AutoAnnotate
    autoHGPEC
    cddApp
    chemViz2
    ClueGO
    clusterMaker2
    copycatLayout
    CyAnimator
    cyBrowser
    cyChart
    cyNDEx-2
    Cyni Toolbox
    Cyrface
    CyTargetLinker
    CytoCopteR
    Diffusion
    enhancedGraphics
    EnrichmentMap
    eXamine
    GeneMANIA
    ID Mapper
    KEGGscape
    MCODE
    Motif-Discovery
    Omics Visualizer
    PathLinker
    PSFC
    ReactomeFIPlugin
    RINalyzer
    RINspector
    RWRMTN
    scNetViz
    setsApp
    stringApp
    structureViz2
    Synapse Client
    WikiPathways
    wk-shell-decomposition
    WordCloud


Jupyter Notebook
----------------

Jupyter Notebooks can be executed on a number of platforms, including:

* Your Cytoscape workstation (via `PyCharm <https://www.jetbrains.com/pycharm/>`_, `Anaconda <https://www.anaconda.com/>`_, and others)
* Private Notebook servers (e.g., `GenePattern Notebook <https://notebook.genepattern.org>`_)
* Public Notebook servers (e.g., `Google Collaboratory <https://colab.research.google.com/>`_ and `JetBrains Datalore <https://datalore.jetbrains.com/>`_)

In each case, your Jupyter Notebook can call py4cytoscape functions that are executed
by Cytoscape running on your own workstation.

Note that when a Notebook executes on a server, the file system accessible to it is likely different from the file system Cytoscape can access. We highly
recommend that your server-based Notebook code use *sandboxing* techniques built into py4cytoscape when sharing files to be read by
Cytoscape or created by Cytoscape. See the `Sandboxing`_ section (below) for an explanation of the file sharing protocol.

See the `Sanity Test <https://github.com/bdemchak/cytoscape-jupyter/tree/main/sanity-test>`_ examples to see how to
use sandboxing in different situations.

.. note:: In all cases, py4cytoscape calls the Cytoscape running on your *private workstation*. Cytoscape is not a full server, and can support exactly one Notebook running at a time -- multiple simultaneous Notebooks are not supported.


Local Jupyter Notebooks
~~~~~~~~~~~~~~~~~~~~~~~

To call py4cytoscape from a Notebook running on your Cytoscape workstation (a so-called
*local* Notebook), simply use your Python environment to install the py4cytoscape library,
then create a Notebook cell that imports the py4cytoscape library and calls a py4cytoscape
function:

.. code:: python

    import py4cytoscape as p4c
    p4c.cytoscape_version_info()

Alternatively, you can create a Notebook cell to install the py4cytoscape library, and then
import it and call a test function:

.. code:: python

    import sys
    !{sys.executable} -m pip uninstall -y py4cytoscape
    !{sys.executable} -m pip install py4cytoscape

    import py4cytoscape as p4c
    p4c.cytoscape_version_info()

Alternatively, you can create a Notebook cell to load an unreleased version of the
py4cytoscape library:

.. code:: python

    import sys
    !{sys.executable} -m pip uninstall -y py4cytoscape
    !{sys.executable} -m pip install git+https://github.com/cytoscape/py4cytoscape

    import py4cytoscape as p4c
    p4c.cytoscape_version_info()

.. note:: To get Jupyter to recognize a py4cytoscape library different from the one first used by your Notebook, you may need to restart the Python kernel -- see your Jupyter Notebook documentation.

If you intend to develop your Notebook on your Cytoscape workstation but deploy it on a *remote* Jupyter server
(including Google Colab), you may want to use the Jupyter initialization strategy described in the next
section instead of simply importing py4cytoscape directly.

Remote Jupyter Notebooks
~~~~~~~~~~~~~~~~~~~~~~~~

Jupyter Notebooks (including Google Colab or JetBrains Datalore) that run on *remote* (private or public)
servers can use py4cytoscape to execute Cytoscape functions on your workstation via
the `Jupyter-Bridge <https://github.com/cytoscape/jupyter-bridge>`_. To use the Jupyter-Bridge,
you must create and execute an initialization cell at the beginning of your Notebook:

.. code:: python

    import requests

    exec(requests.get("https://raw.githubusercontent.com/cytoscape/jupyter-bridge/master/client/p4c_init.py").text)

    IPython.display.Javascript(_PY4CYTOSCAPE_BROWSER_CLIENT_JS) # Start browser client

.. warning:: The ``IPython.display.Javascript()`` call must be the last line in the initialization cell. It cannot be part of a if-then or try-except block, and no other line can follow it.

By default, this loads py4cytoscape from the PyPI repository. You can specify a different version of py4cytoscape by
setting the _PY4CYTOSCAPE variable *before* the ``exec()`` call. For example, to load the most recent unreleased py4cytoscape
or the py4cytoscape in Github branch 0.0.11, use the following:

.. code:: python

    _PY4CYTOSCAPE = 'git+https://github.com/cytoscape/py4cytoscape'

or

.. code:: python

    _PY4CYTOSCAPE = 'git+https://github.com/cytoscape/py4cytoscape@1.2.0'

.. note:: The Jupyter-Bridge can reach your Cytoscape workstation whether or not it's behind a firewall.

.. note:: The Jupyter-Bridge can be used for Notebooks running on the same workstation as Cytoscape, which enables local development of workflows that will execute remotely, though at the cost of some execution speed.

Note that remotely executing Notebooks can create files for Cytoscape to read, or
can read files written by Cytoscape, but only by using the sandboxing functions
described below.

Sandboxing
----------

If you use py4cytoscape to create and run a Python workflow on the same workstation as
your Cytoscape instance (either from the command line or in a Jupyter Notebook), you may not need sandbox features.
If you use py4cytoscape from a Jupyter Notebook
running on a remote server or on your Cytoscape workstation, you very likely **need** sandboxing.

For context, py4cytoscape functions (e.g., ``open_session()``, ``save_session()``
and ``export_image()``) access files in either Cytoscape's current working directory or
in a location given by a full path. When a Python workflow starts on the Cytoscape workstation, its working directory
is the Python kernel's working directory, which may contain user data files. Calls to py4cytoscape functions
may contain paths relative to this directory, or may be full paths on the Cytoscape workstation.

Full paths work well only as long as the workflow executes on the same workstation as
it was written. It raises a number of problems:

* Workflows with hard-coded paths are not likely to be portable to other Cytoscape workstations,
  which may have their own (different) file system layouts. This applies equally to both
  to workflows running on other Cytoscape workstations and those running in a remote Jupyter
  Notebook server. (For example: C:\users\Bob\CyFiles may be a valid path on Bob's Windows workstation,
  but may not be valid on Carol's Windows or Mac workstation.)

* To enable collaboration, workflows running on a remote Jupyter Notebook server likely
  prefer to store Cytoscape data and output on the Notebook server. As the server's file
  system is inaccessible to the Cytoscape running on your workstation, there is no path the
  workflow can pass to make Cytoscape read or write those files.

Sandboxing solves these problems by defining a dedicated folder on the Cytoscape workstation (in the
user's ``CytoscapeConfiguration/filetransfer`` folder); files
read and written by Cytoscape are all contained with the folder (aka sandbox).
Sandboxing functions allow files to be transferred
between the Jupyter Notebook server's native file system
and the sandbox. Thus, a remotely executing Notebook-based workflow can maintain Cytoscape files on the
Notebook server, and transfer them to/from the Cytoscape workstation (in the sandbox) at
will.

A sandbox can contain both files and directories (which can contain files and directories, too).

Sandboxing applies to a notebook running on a remote Jupyter server, but can be used by notebooks
running on the Cytoscape workstation. Thus, workflows written for one environment can work
seamlessly on the other.

A useful side effect of sandboxing is that workflows that use them stand little chance of
inadvertantly (or maliciously) corrupting the Cytoscape workstation's file system. This
safety further encourages sharing of workflows between collaboratating researchers.

Notebook workflows that execute remotely are automatically provisioned with a default sandbox (called
``default_sandbox``). To get the same effect with Python running on the
Cytoscape workstation, you can explicitly create the default sandbox. (See vignettes below.)

.. note::
    By default, a sandbox is pre-loaded with a copy of Cytoscape's ``sampleData``
    files. This makes it easy for workflow writers to experiment on sample data. For example,
    calling ``open_session('sampleData/sessions/Affinity Purification')`` opens a sandbox-based sample session
    provided with Cytoscape.

A workflow can define any number of sandboxes and even switch between them.
This promotes modularity by facilitating the creation of different sub-workflows with
some certainty that a sub-workflow's files aren't accidentally corrupted by other
sub-workflows over time.

See the `Sanity Test <https://github.com/bdemchak/cytoscape-jupyter/tree/main/sanity-test>`_ examples to see how to
use sandboxing in different situations.

**Vignette 1**: A workstation-based Python workflow (as notebook or command-line) calling Cytoscape to load a session and create a network image.

Without sandboxing, the workflow must specify Cytoscape files as either relative to the Python kernel's
current directory or as full (non-portable) paths.

.. code:: python

    open_session('mySession')
    # ...
    export_image('myImage.png')
    # ... use Python to do something with the .png

or

.. code:: python

    open_session('C:\Users\Me\Documents\CyFiles\mySession')
    # ...
    export_image('C:\Users\Me\Documents\CyFiles\myImage.png')
    # ... use Python to do something with the .png

When using full paths, this workflow is portable only to workstations that have their Cytoscape files in the
``C:\Users\Me\Documents\CyFiles``, which doesn't seem like a good assumption for many workstations. Best to use
either relative paths or sandboxing (see below) in this situation.

.. note::
    If you have a Cytoscape file on a cloud resource (e.g., Dropbox), you can use the
    import_file_from_url() function to fetch it onto your Cytoscape workstation and then
    have Cytoscape read it. You don't need sandbox functions for this.

**Vignette 2**: A remotely executing Notebook-based version of Vignette 1 ... data files are on a Jupyter server.

A sandbox is automatically created for remote workflows. The workflow must transfer
a session file from the Notebook's remote file system
to the sandbox, call Cytoscape, and then transfer the result back to the Notebook's remote file
system for further processing.

.. code:: python

    sandbox_send_to('./mySession.cys') # copy session file from Notebook directory to workstation
    open_session('mySession')
    # ...
    export_image('myImage.png')
    sandbox_get_from('myImage.png', './myImage.png') # copy image file to Notebook directory
    # ... do something with the .png

This workflow can run on any Notebook server and Cytoscape workstation without knowledge of
or risk to the workstation's file system. Various Python-based libraries can process the
.png after it is copied back to the Notebook's file system.

When calling sandbox functions, if you don't specify the name of a sandbox, the operation
is performed on the "current sandbox", which is the ``default_sandbox`` folder or whatever sandbox you
set by calling the ``sandbox_set()`` function.

Sandbox functions don't accept full paths for files, as they
would create non-portable code and pose a security risk to the Cytoscape workstation.

**Vignette 3**: A remotely executing Notebook-based version of Vignette 1 ... data files are on a cloud service.

This vignette is the same as Vignette 2, except the session file resides on a cloud service (i.e.,
GitHub, Dropbox, OneDrive, Google Drive, or elsewhere). In this case, the workflow must transfer
the file from the cloud service (instead of the Notebook's file system) to the sandbox, and then proceed
as in Vignette 2.

.. code:: python

    # copy session file from cloud service to workstation
    sandbox_url_to('https://www.dropbox.com/s/r15azh0xb534mu1/mySession.cys?dl=0')
    open_session('mySession')
    # ...
    export_image('myImage.png')
    sandbox_get_from('myImage.png', './myImage.png') # copy image file to Notebook directory
    # ... do something with the .png

.. note::
    If your Notebook is executing on the local Cytoscape workstation instead of a remote server,
    you can use the import_file_from_url() function to fetch it onto your Cytoscape workstation and then
    have Cytoscape read it. You don't need sandbox functions for this.

**Vignette 4**: A workstation-based non-Notebook Python workflow accesses sandbox-based files

Sandboxes are stored as directories under the user's ``CytoscapeConfiguration/filetransfer`` folder. You can
choose to maintain your Cytoscape files in a sandbox folder (instead of elsewhere in the
Cytoscape workstation file system). If you do this, you get all of the benefits of sandboxing without having to specify non-portable
file paths.

.. code:: python

    sandbox_set('mySandbox', copy_samples=False, reinitialize=False)
    open_session('mySession')
    # ...
    export_image('myImage.png')
    # ... do something with the .png

If Cytoscape files reside in the sandbox *a priori*, no ``sandbox_send_to()`` or
``sandbox_get_from()`` calls are needed. Note that to make a standalone Python workflow run in a remote
Notebook, you'll have to add sandbox calls (as in Vignette 2). Why not start by using sandboxes in anticipation
of publishing a workflow as a Notebook?

.. warning:: The ``reinitialize=False`` parameter is needed to prevent the ``sandbox_set()`` call from erasing the sandbox folder's contents, which is its default behavior.

.. note::
    Sandbox functions allow the following operations on files and sandboxes:
        * ``sandbox_set()``: Create a new sandbox or makes another sandbox the "current sandbox"
        * ``sandbox_remove()``: Delete a sandbox and its files and directories
        * ``sandbox_send_to()``: Transfer a Notebook file to a sandbox
        * ``sandbox_url_to()``: Transfer for a cloud-based file to a sandbox
        * ``sandbox_get_from()``: Transfer a sandbox file to the Notebook file system
        * ``sandbox_get_file_info()``: Get sandbox file metadata
        * ``sandbox_remove_file()``: Remove a sandbox file

Value Generators
----------------

You can set visual graph attributes (e.g., color, size, opacity and shapes) according to attribute data assigned to
nodes or edges by using Style Mapping functions such as ``set_node_color_mapping()`` or ``set_node_size_mapping()``.
As described in the `Cytoscape Manual <http://manual.cytoscape.org/en/stable/Styles.html#how-mappings-work>`_, there
are three different ways to map node or edge attributes to visual attributes.

Briefly:

* *continuous* mappings map a range of values to a color gradient or a range of sizes, opacities et al
* *discrete* mappings allow specific values to map to specific colors, sizes, opacities et al
* *passthrough* mappings allow node or edge labels to be taken from node or edge attributes

A `value generator <http://manual.cytoscape.org/en/stable/Styles.html#automatic-value-generators>`_ makes
*discrete* or *continuous* mappings more convenient by automatically mapping attribute data values to visual attributes.
It first determines the unique data values for a given node or edge attribute, then allows you to choose
a mapping to colors, sizes, opacities or shapes. For example, you can use a value generator to map a node with
a `Degree` attribute having values 1, 10 and 20 to node fill colors of Red, Blue or Green ... or to a node size
of 100, 150 or 200 ... or to circle, square or diamond shapes.

Essentially, a *value generator* spares you from having to know both the specific values of a node or edge attribute and
the specifics of the visual attributes to display ... it lets you focus on whether to render the attribute as a color,
size, opacity or shape.

For example, to set a node's fill color based on its `Degree` attribute using a *discrete* style mapping function, you could use the
longhand (without value generator) where you know the unique `Degree` values in advance and choose specific colors to
represent them:

.. code:: python

    set_node_color_mapping('Degree',
                           ['1', '10', '20'],
                           ['#FF0000', '#00FF00', '#0000FF],
                           mapping_type='d',
                           style_name='galFiltered Style')

Instead, you could use a color value generator that determines the unique `Degree` values and assigns
each to a different color in a `Brewer palette <https://colorbrewer2.org>`_:

.. code:: python

    set_node_color_mapping(**gen_node_color_map('Degree',
                                                mapping_type='d',
                                                style_name='galFiltered Style'))
    set_node_color_mapping(**gen_node_color_map('Degree',
                                                palette_color_brewer_q_Accent(),
                                                mapping_type='d',
                                                style_name='galFiltered Style'))

The first form uses a default Brewer palette (Set2), and the second form shows how you can choose a different Brewer palette (Accent).

.. note:: For color-oriented visual attributes, py4cytoscape offers a wide range of `Brewer palettes <https://colorbrewer2.org>`_, which are widely regarded as aesthetic and visually effective.

.. note:: Brewer palettes appropriate for *discrete* mappings are called *qualititive* palettes, and are distinguished in py4cytoscape by the "_q_" in the palette name.

To map attributes to a gradient of colors, sizes, opacities, etc, use *continuous* mapping:

.. code:: python

    set_node_color_mapping(**gen_node_color_map('Degree',
                                                style_name='galFiltered Style'))
    set_node_color_mapping(**gen_node_color_map('Degree',
                                                palette_color_brewer_s_YlGn(),
                                                style_name='galFiltered Style'))

The first form uses a default Brewer palette (GnBu), and the second form shows how you can choose a different Brewer palette (YlGn).

.. note:: Brewer palettes appropriate for *continuous* mappings of same-signed values are called *sequential* palettes, and are distinguished in py4cytoscape by the "_s_" in the palette name.

.. note:: Brewer palettes appropriate for *continuous* mappings of mixed-signed values are called *divergent* palettes, and are distinguished in py4cytoscape by the "_d_" in the palette name.

It's likely that the `Degree` attribute would have only positive values, so a *sequential* Brewer palette would be appropriate.
When the distribution of attribute data values isn't known in advance, you can provide both a sequential and divergent
palette and let py4cytoscape choose between them based on the data values it finds:

.. code:: python

    set_node_color_mapping(**gen_node_color_map('Expressed',
                                                style_name='galFiltered Style'))
    set_node_color_mapping(**gen_node_color_map('Expressed',
                                                (palette_color_brewer_s_YlGn(), palette_color_brewer_d_Spectral()),
                                                style_name='galFiltered Style'))

The first form uses default sequential and divergent palettes (GnBu and RdYlBu), and the second form shows how to use
a tuple to specify which sequential and divergent palettes to use.

The general methodology is to use the value generator (e.g., ``gen_node_color_map()``) as the sole parameter to a
style mapping function, binding it by using the Python ** operator. py4cytoscape provides color generators (for use with
color mapping functions (e.g., ``set_node_color_mapping()``), opacity generators (for use with opacity mapping
functions (e.g., ``set_node_opacity_mapping()``), and other generators (e.g., size, width, height, shapes).

Each generator accepts all of the same parameters as the corresponding style mapping functions, and provides the same
defaults for them. So,

.. code:: python

    set_node_color_mapping(**gen_node_color_map('Degree',
                                                 palette_color_brewer_q_Accent(),
                                                 mapping_type='d',
                                                 style_name='galFiltered Style'))

is the equivalent of:

.. code:: python

    set_node_color_mapping(table_column='Degree',
                           table_column_values=['8', '7', '6', '5', '4', '3', '2', '1'],
                           colors=['#7FC97F', '#BEAED4', '#FDC086', '#FFFF99', '#386CB0', '#F0027F', '#BF5B17', '#666666'],
                           mapping_type='d',
                           default_color=None,
                           style_name='galFiltered Style',
                           network=None,
                           base_url:'http://127.0.0.1:1234/v1')

py4cytoscape provides numerous automatic value generators for discrete mappings:

* 8 *qualitative* Brewer palettes (for color mappings)
* a random palette (``palette_color_random()``, for color mappings)
* node shapes, edge arrow shapes, and edge line styles
* ranges and random distributions

It also provides automatic value generators for continuous mappings:

* 18 *sequential* Brewer palettes (for color mappings for same-signed data)
* 9 *divergent* Brewer palettes (for color mappings for mixed-signed data)

Examples of non-color mappings that use ranges and random distributions include:

.. code:: python

    set_node_fill_opacity_mapping(**gen_node_opacity_map('Degree',
                                                         mapping_type='d',
                                                         style_name='galFiltered Style'))
    set_node_fill_opacity_mapping(**gen_node_opacity_map('Degree',
                                                         scheme_d_number_series(start_value=100, step=20),
                                                         mapping_type='d',
                                                         style_name='galFiltered Style'))
    set_node_fill_opacity_mapping(**gen_node_opacity_map('Degree',
                                                         scheme_d_number_random(min_value=10, max_value=120),
                                                         mapping_type='d',
                                                         style_name='galFiltered Style'))
    set_node_fill_opacity_mapping(**gen_node_opacity_map('Expressed',
                                                         scheme_c_number_continuous(start_value=50, end_value=200),
                                                         style_name='galFiltered Style'))

Note that the default value generator for a numeric attribute is scheme_d_number_series(start_value=0, step=10). The default
range for a random distribution is 0..255.

Note that the last form shows a *continuous* mapping where the node opacity is set to range from 50 to 200, depending on
the value of the `Expressed` attribute. The normal range defaults to 10..30.

Shape generators don't require a ``scheme`` parameter, and automatically have a ``mapping_type`` of 'd'. For example:

.. code:: python

    set_node_shape_mapping(**gen_node_shape_map('Degree',
                                                style_name='galFiltered Style'))

    set_edge_source_arrow_shape_mapping(**gen_edge_arrow_map('interaction',
                                                             style_name='galFiltered Style'))

    set_edge_target_arrow_shape_mapping(**gen_edge_arrow_map('interaction',
                                                             style_name='galFiltered Style'))

