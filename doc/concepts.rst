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

This section discusses conceptual and miscellaneous issues relating to py4cytoscape use.

:ref:`here<Missing Functions>`


:ref:`here<Calling Cytoscape Apps>`


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
