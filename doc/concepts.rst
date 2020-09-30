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

* `Sandboxing`_ shows how to limit Cytoscape to accessing files in particular directories.



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

Sandboxing
----------

If you use py4cytoscape to create and run a Python workflow on the same workstation as
your Cytoscape instance, you may not need sandbox features (but they may make your Python
coding simpler). If you use py4cytoscape from a Jupyter Notebook running on a remote server,
you very likely **need** sandboxing.

For context, py4cytoscape functions (e.g., ``open_session()``, ``save_session()``
and ``export_image()``) access files in either Cytoscape's current working directory or
in a location given by a full path. When Cytoscape starts, its working directory is the
Cytoscape install directory, which has no write permissions and likely contains no user
data files. Very quickly, a Python workflow author learns to pass file names
qualified by full paths that are unique to the workstation.

This situation works well only as long as the workflow executes on the same workstation as
it was written. However, it raises a number of problems:

* Workflows with hard-coded paths are not likely to be portable to other Cytoscape workstations,
  which are likely to have their own (different) file system layouts. This applies equally to both
  to workflows running on other Cytoscape workstations and those running in a remote Jupyter
  Notebook server.


* To enable collaboration, workflows running on a remote Jupyter Notebook server likely
  prefer to store Cytoscape data and output on the Notebook server. As the server's file
  system is inaccessible to the Cytoscape running on your workstation, there is no path the
  workflow can pass to make Cytoscape read or write those files.

Sandboxing solves this by defining a subdirectory on the Cytoscape workstation (in the
user's ``CytoscapeConfiguration/filetransfer`` folder); files
read and written by Cytoscape are all contained with the subdirectory (aka sandbox).
Sandboxing functions allow files to be transferred
between the workflow's native file system (e.g., on the Jupyter Notebook server)
and the sandbox. Thus, a Notebook-based workflow can maintain Cytoscape files on the
Notebook server, and transfer them to/from the Cytoscape workstation (in the sandbox) at
will.

A sandbox can contain both files and directories (which can contain files and directories, too).

A useful side effect of sandboxing is that workflows that use them stand no chance of
inadvertantly (or maliciously) corrupting the Cytoscape workstation's file system. This
safety further encourages sharing of workflows between collaboratating researchers.

Notebook workflows are automatically provisioned with a default sandbox (called
``default_sandbox``). To get the same effect with Python running standalone on the
Cytoscape workstation, you can explicitly create the default sandbox. (See vignettes below.)

.. note::
    By default, a sandbox is pre-loaded with a copy of Cytoscape's ``sampleData``
    files. This makes it easy for workflow writers to experiment on sample data.

A workflow can define any number of sandboxes and even switch between them.
This promotes modularity by facilitating the creation of different sub-workflows with
some certainty that a sub-workflow's files aren't accidentally corrupted by other
sub-workflows over time.

**Vignette 1**: A workstation-based Python workflow loading a session and creating a network image.

Without sandboxing, the workflow must provide full paths to Cytoscape files.

.. code:: python

    open_session('C:\Users\Me\Documents\CyFiles\mySession')
    # ...
    export_image('C:\Users\Me\Documents\CyFiles\myImage.png')
    # ... do something with the .png

This workflow is portable only to workstations that have their Cytoscape files in the
``C:\Users\Me\Documents\CyFiles``, which doesn't seem likely.

**Vignette 2**: A Notebook-based version of Vignette 1.

A sandbox is automatically created for Notebook-bsed workflows. The workflow must transfer
a session file from the Notebook's file system
to the sandbox, call Cytoscape, and then transfer the result back to the Notebook's file
system for further processing.

.. code:: python

    sandbox_send_to('data/mySession.cys') # copy session file from Notebook server to workstation
    open_session('mySession')
    # ...
    export_image('myImage.png')
    sandbox_get_from('myImage.png', 'data/myImage.png') # copy image file to Notebook server
    # ... do something with the .png

This workflow can run on any Notebook server and Cytoscape workstation without knowledge of
or risk to the workstation's file system. Various Python-based libraries can process the
.png after it is copied to the Notebook's file system.

When calling sandbox functions, if you don't specify the name of a sandbox, the operation
is performed on the "current sandbox".

**Vignette 3**: A workstation-based Python workflow accesses sandbox-based files

Sandboxes are stored as directories under the user's ``CytoscapeConfiguration/filetransfer`` folder.
By always maintaining your Cytoscape files in a sandbox folder (instead of elsewhere in the file
system), you get all of the benefits of sandboxing without having to specify non-portable
file paths.

.. code:: python

    sandbox_set('mySandbox', copy_samples=False, reinitialize=False)
    open_session('mySession')
    # ...
    export_image('myImage.png')
    # ... do something with the .png

Because Cytoscape files reside in the sandbox *a priori*, no ``sandbox_send_to()`` or
``sandbox_get_from()`` calls are needed. Note that to make this workflow run in a remote
Notebook, you'll still have to add these calls (as in Vignette 2).

The ``reinitialize`` parameter is needed to prevent the ``sandbox_set()`` call from
erasing the sandbox folder's contents, which is its default behavior.

.. note::
    Sandbox functions allow the following operations on files and sandboxes:
        * ``sandbox_set()``: Create a new sandbox or makes another sandbox the "current sandbox"
        * ``sandbox_remove()``: Delete a sandbox and its files and directories
        * ``sandbox_send_to()``: Transfer a Notebook file to a sandbox
        * ``sandbox_get_from()``: Transfer a sandbox file to the Notebook file system
        * ``sandbox_get_file_info()``: Get sandbox file metadata
        * ``sandbox_remove_file()``: Remove a sandbox file

Jupyter Notebook
----------------

How to run from a Jupyter Notebook on a remote server.


