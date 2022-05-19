# -*- coding: utf-8 -*-

"""Functions for working with FILTERS for the selection of nodes and edges in
networks, including operations to import and export filters. In the Cytoscape
user interface, filters are managed in the Select tab of the Control Panel.
"""

"""Copyright 2020-2022 The Cytoscape Consortium

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the 
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit 
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the 
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO 
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

# Internal module convenience imports
import time
import json
import warnings

# Internal module imports
from . import commands
from . import networks
from . import network_selection
from . import tables
from . import style_bypasses
from . import sandbox

# External library imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log, show_error
from .py4cytoscape_tuning import CATCHUP_FILTER_SECS
from .py4cytoscape_sandbox import get_abs_sandbox_path
from .py4cytoscape_notebook import running_remote

@cy_log
def apply_filter(filter_name='Default filter', hide=False, network=None, base_url=DEFAULT_BASE_URL):
    """Run an existing filter by supplying the filter name.

    Args:
        filter_name (str): Name of filter to apply. Default is "Default filter".
        hide (bool): Whether to hide filtered out nodes and edges. Default is FALSE.
            Ignored if all nodes or edges are filtered out. This is an alternative to filtering for node and edge selection.
        network (SUID or str or None): Name or SUID of the network. Default is the "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: {'nodes': <node list>, 'edges': <edge list>} returns list of nodes and edges selected after filter executes

    Raises:
        CyError: if filter doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> apply_filter('degree filter 1x')
        {'nodes': ['YDR395W', 'YLR362W', 'YPL248C', 'YGL035C'], 'edges': None}
        >>> apply_filter('degree filter 1x', hide=True, network='My Network')
        {'nodes': ['YDR395W', 'YLR362W', 'YPL248C', 'YGL035C'], 'edges': None}

    See Also:
        :meth:`unhide_all`
    """
    if not filter_name in get_filter_list(base_url=base_url):
        raise CyError(f'Filter "{filter_name}" does not exist.')

    net_suid = networks.get_network_suid(network, base_url=base_url)
    networks.set_current_network(net_suid, base_url=base_url)

    # TODO: It looks like R can't properly use filter_name with blank embedded, and doesn't wait for filter to be applied
    res = commands.commands_post(f'filter apply container="filter" name="{filter_name}" network=SUID:"{net_suid}"',
                                 base_url=base_url)
    return _check_selected(hide, net_suid, base_url)


@cy_log
def create_column_filter(filter_name, column, criterion, predicate, caseSensitive=False, anyMatch=True, type='nodes',
                         hide=False, network=None, base_url=DEFAULT_BASE_URL, *, apply=True):
    """Create Column Filter.

    Create a filter to control node or edge selection. Works on columns of boolean, string, numeric
    and lists. Note the unique restrictions for criterion and predicate depending on the type of column
    being filtered.

    Args:
        filter_name (str): Name for new filter.
        column (str): Table column to base filter upon.
        criterion (list, bool, str, int or float): For boolean columns: True or False. For string columns: a
            string value, e.g., "hello". If the predicate is REGEX then this can be a regular expression as
            accepted by the Java Pattern class (https://docs.oracle.com/javase/7/docs/api/java/util/regex/Pattern.html).
            For numeric columns: If the predicate is BETWEEN or IS_NOT_BETWEEN then this is a two-element list of
            numbers, example: [1,5], otherwise a single number.
        predicate (str):  For boolean columns: IS, IS_NOT. For string columns: IS, IS_NOT, CONTAINS, DOES_NOT_CONTAIN,
            REGEX. For numeric columns: IS, IS_NOT, GREATER_THAN, GREATER_THAN_OR_EQUAL, LESS_THAN, LESS_THAN_OR_EQUAL,
            BETWEEN, IS_NOT_BETWEEN.
        caseSensitive (bool): If string matching should be case sensitive. Default is FALSE.
        anyMatch (bool): Only applies to List columns. If true then at least one element in the list must pass the
            filter, if false then all the elements in the list must pass the filter. Default is TRUE.
        type (str): Apply filter to "nodes" (default) or "edges".
        hide (bool): Whether to hide filtered out nodes and edges. Default is FALSE.
            Ignored if all nodes or edges are filtered out. This is an alternative to filtering for node and edge selection.
        network (SUID or str or None): Name or SUID of the network. Default is the "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.
        apply (bool): True to execute filter immediately; False to define filter but not execute it

    Returns:
        dict: {'nodes': <node list>, 'edges': <edge list>} returns list of nodes and edges selected after filter executes; None if filter wasn't applied

    Raises:
        CyError: if column doesn't exist in the table named by ``type`` or filter couldn't be applied
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> create_column_filter('myFilter', 'log2FC', [-1,1], "IS_NOT_BETWEEN") # filter on numeric value log2FC
        {'nodes': ['YDR395W', 'YLR362W', 'YPL248C', 'YGL035C'], 'edges': None}
        >>> create_column_filter('myFilter', 'pValue', 0.05, "LESS_THAN") # Filter on floating point column pValue
        {'nodes': ['YDR395W', 'YLR362W', 'YPL248C', 'YGL035C'], 'edges': None}
        >>> create_column_filter('myFilter', 'function', "kinase", "CONTAINS", False) # Function on string column name
        {'nodes': ['YDR395W', 'YLR362W', 'YPL248C', 'YGL035C'], 'edges': None}
        >>> create_column_filter('myFilter', 'name', "^Y.*C$", "REGEX") # Filter on string column name
        {'nodes': ['YDR395W', 'YLR362W', 'YPL248C', 'YGL035C'], 'edges': None}
        >>> create_column_filter('myFilter', 'isTarget', True , "IS") # Filter on boolean column isTarget
        {'nodes': ['YDR395W', 'YLR362W', 'YPL248C', 'YGL035C'], 'edges': None}
        >>> create_column_filter('myFilter', 'isTarget', True , "IS", hide=True) # Filter on boolean column isTarget
        {'nodes': ['YDR395W', 'YLR362W', 'YPL248C', 'YGL035C'], 'edges': None}
        >>> create_column_filter('myFilter', 'Betweenness', [300, 600] , "BETWEEN", type='edges') # Filter edges
        {'nodes': None, 'edges': [{'YPR119W (pd) YMR043W', 'YDR412W (pp) YPR119W'}]}
        >>> create_column_filter('myFilter', 'Betweenness', [300, 600] , "BETWEEN", type='edges', apply=False) # Define filter
        {'nodes': None, 'edges': [{'YPR119W (pd) YMR043W', 'YDR412W (pp) YPR119W'}]}
    """
    networks.set_current_network(network, base_url=base_url)

    if column not in tables.get_table_column_names(type[:4], base_url=base_url):
        raise CyError('Column "%s" does not exist in the "%s" table' % (column, type[:4]))

    if predicate == "REGEX" and check_supported_versions(cytoscape='3.9'):
        show_error('Warning -- Cytoscape version pre-3.9 in use ... REGEX filter may hang forever')
    elif predicate in ['BETWEEN', 'IS_NOT_BETWEEN']:
        if not isinstance(criterion, list) or len(criterion) != 2:
            raise CyError('Criterion "{criterion}" must be a list of two numeric values, e.g., [0.5, 2.0]')
    elif predicate in ['GREATER_THAN', 'GREATER_THAN_OR_EQUAL']:
        #        # manually feed max bound so that UI is also correct ... UI doesn't show these predicates directly ... it uses BETWEEN, and doesn't distinguish between > and >=
        # TODO: Recommend that this check be limited to GREATER_THAN_OR_EQUAL because that's what the UI supports
        col_vals = tables.get_table_columns(type[:4], column, base_url=base_url)
        crit_max = col_vals[column].max()
        criterion = [criterion, crit_max]
        # same trick to fix UI does not work for LESS_THAN cases
        # } else if (predicate %in% c("LESS_THAN", "LESS_THAN_OR_EQUAL")){
        #     col.vals <- getTableColumns(substr(type,1,4), column, base.url = base.url)
        #     crit.max <- min(na.omit(col.vals))
        #     criterion <- c(crit.max,criterion[1])

        # TODO: Find out what range criterion should be for GREATER_THAN ... different than GREAT_THAN_OR_EQUAL
    elif isinstance(criterion, bool):
        if predicate == "IS_NOT": criterion = not criterion
    elif isinstance(criterion, int) or isinstance(criterion, float):
        if predicate == 'IS':
            criterion = [criterion, criterion]
            predicate = 'BETWEEN'
        elif predicate == 'IS_NOT':
            criterion = [criterion, criterion]
            predicate = 'IS_NOT_BETWEEN'

    # Actually create the filter
    cmd_json = {'id': 'ColumnFilter',
                'parameters': {'criterion': criterion, 'columnName': column, 'predicate': predicate,
                               'caseSensitive': caseSensitive, 'anyMatch': anyMatch, 'type': type}}
    cmd_body = {'name': filter_name, 'json': json.dumps(cmd_json)}
    return _create_filter_and_finish('commands/filter/create', cmd_body, hide, apply, network, base_url)


@cy_log
def create_degree_filter(filter_name, criterion, predicate='BETWEEN', edge_type='ANY', hide=False, network=None,
                         base_url=DEFAULT_BASE_URL, *, apply=True):
    """Create Degree Filter.

    Creates a filter to control node selection base on in/out degree.

    Args:
        filter_name (str): Name for new filter.
        criterion (list): A two-element vector of numbers, example: [1,5].
        predicate (str):  BETWEEN (default) or IS_NOT_BETWEEN
        edgeType (str): Type of edges to consider in degree count: ANY (default), UNDIRECTED, INCOMING, OUTGOING, DIRECTED
        hide (bool): Whether to hide filtered out nodes and edges. Default is FALSE.
            Ignored if all nodes or edges are filtered out. This is an alternative to filtering for node and edge selection.
        network (SUID or str or None): Name or SUID of the network. Default is the "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.
        apply (bool): True to execute filter immediately; False to define filter but not execute it

    Returns:
        dict: {'nodes': <node list>, 'edges': <edge list>} returns list of nodes and edges selected after filter executes; None if filter wasn't applied

    Raises:
        CyError: if criterion is not list of two values or filter couldn't be applied
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> create_degree_filter('myFilter', [2, 5]) # filter on any nodes having between 2 and 5 edges
        {'nodes': ['YDR395W', 'YLR362W', 'YPL248C', 'YGL035C'], 'edges': None}
        >>> create_degree_filter('myFilter', [2, 5], predicate='IS_NOT_BETWEEN') # filter for edges < 2 or > 5
        {'nodes': ['YDR395W', 'YLR362W', 'YPL248C', 'YGL035C'], 'edges': None}
        >>> create_column_filter('myFilter', [2, 5], edge_type='INCOMING') # filter for between 2 and 5 incoming edges
        {'nodes': ['YDR395W', 'YLR362W', 'YPL248C', 'YGL035C'], 'edges': None}
        >>> create_column_filter('myFilter', [2, 5], hide=True) # filter for between 2 and 5 edges, and hide them
        {'nodes': ['YDR395W', 'YLR362W', 'YPL248C', 'YGL035C'], 'edges': None}
        >>> create_column_filter('myFilter', [2, 5], apply=False) # define filter for between 2 and 5 edges, and hide them
        {'nodes': ['YDR395W', 'YLR362W', 'YPL248C', 'YGL035C'], 'edges': None}
    """
    networks.set_current_network(network, base_url=base_url)

    if not isinstance(criterion, list) or len(criterion) != 2:
        raise CyError(f'Criterion "{criterion}" must be a list of two numeric values, e.g., [0.5, 2.0]')

    cmd_json = {'id': 'DegreeFilter',
                'parameters': {'criterion': criterion, 'predicate': predicate, 'edgeType': edge_type}}
    cmd_body = {'name': filter_name, 'json': json.dumps(cmd_json)}
    return _create_filter_and_finish('commands/filter/create', cmd_body, hide, apply, network, base_url)


@cy_log
def create_composite_filter(filter_name, filter_list, type='ALL', hide=False, network=None, base_url=DEFAULT_BASE_URL, *, apply=True):
    """Combine filters to control node and edge selection based on previously created filters.

    Args:
        filter_name (str): Name for new filter.
        filter_list (list): List of names of filters to combine.
        type (str): Type of composition, requiring ALL (default) or ANY filters to pass for final node and edge selection.
        hide (bool): Whether to hide filtered out nodes and edges. Default is FALSE.
            Ignored if all nodes or edges are filtered out. This is an alternative to filtering for node and edge selection.
        network (SUID or str or None): Name or SUID of the network. Default is the "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.
        apply (bool): True to execute filter immediately; False to define filter but not execute it

    Returns:
        dict: {'nodes': <node list>, 'edges': <edge list>} returns list of nodes and edges selected after filter executes; None if filter wasn't applied

    Raises:
        CyError: if filter list contains less than one filter or has filters that don't exist, or filter couldn't be applied
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> create_composite_filter('New Filter', ['degree filter 1x', 'degree filter 2x'])
        {'nodes': ['YDR395W', 'YLR362W', 'YPL248C', 'YGL035C'], 'edges': None}
        >>> create_composite_filter('New Filter', ['degree filter 1x', 'column filter 10x'], type='ANY', network="My network")
        {'nodes': ['YDR395W', 'YLR362W', 'YPL248C', 'YGL035C'], 'edges': [{'YPR119W (pd) YMR043W', 'YDR412W (pp) YPR119W'}]}
        >>> create_composite_filter('New Filter', ['degree filter 1x', 'degree filter 2x'], hide=True)
        {'nodes': ['YDR395W', 'YLR362W', 'YPL248C', 'YGL035C'], 'edges': None}
        >>> create_composite_filter('New Filter', ['degree filter 1x', 'degree filter 2x'], apply=False)
        {'nodes': ['YDR395W', 'YLR362W', 'YPL248C', 'YGL035C'], 'edges': None}
    """
    networks.set_current_network(network, base_url=base_url)

    if len(filter_list) < 2:
        raise CyError(f'Filter list "{filter_list}" is invalid. Must provide a list of two or more filter names, e.g., ["filter1", "filter2"]')

    def fetch(x):
        return commands.commands_post('filter get name="' + x + '"', base_url=base_url)

    def extract(y):
        return y[0]['transformers'][0] if y else None

    trans_list = [extract(fetch(filter)) for filter in filter_list]

    if None in trans_list:
        raise CyError('Filter name "%s" does not exist' % (filter_list[trans_list.index(None)]))

    cmd_json = {'id': 'CompositeFilter', 'parameters': {'type': type}, 'transformers': trans_list}
    cmd_body = {'name': filter_name, 'json': json.dumps(cmd_json)}
    return _create_filter_and_finish('commands/filter/create', cmd_body, hide, apply, network, base_url)


@cy_log
def get_filter_list(base_url=DEFAULT_BASE_URL):
    """Retrieve list of named filters in current session

    Args:
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: returns list of available filter names

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_filter_list()
        ['degree filter 1x', 'degree filter 2x']
    """
    res = commands.commands_post('filter list', base_url=base_url)
    return res


@cy_log
def export_filters(filename='filters.json', base_url=DEFAULT_BASE_URL, *, overwrite_file=True):
    """Saves filters to file in JSON format.

    Args:
        filename (str): Full path or path relavtive to current working directory, in addition to the name of the file. Default is "filters.json".
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.
        overwrite_file (bool): False allows an error to be generated if the file already exists;
            True allows Cytoscape to overwrite it without asking
    Returns:
        list: []

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> export_filters() # Saves all filters in file 'filters.json'
        []
        >>> export_filters('test.json') # Saves all filters in file 'test.json'
        []
        >>> export_filters('test') # Saves all filters in file 'test.json'
        []
        >>> export_filters('test', overwrite_file=False) # Save filters only if test.json doesn't already exist
        []
    """
    ext = '.json'

    if re.search(ext + '$', filename) is None: filename += ext

    file_info = sandbox.sandbox_get_file_info(filename, base_url=base_url)
    if len(file_info['modifiedTime']) and file_info['isFile']:
        if overwrite_file:
            narrate('This file has been overwritten.')
        else:
            raise CyError(f'File "{filename}" already exists ... filters not saved.')
    full_filename = file_info['filePath']

    res = commands.commands_get(f'filter export file="{full_filename}"', base_url=base_url)
    return res


@cy_log
def import_filters(filename, base_url=DEFAULT_BASE_URL):
    """Loads filters from a file in JSON format.

    Adds filters to whatever filters already exist, and renames filters where names already exist. Also executes
    each filter.

    Note:
        To load a filter file from cloud storage, use the file's URL and the ``sandbox_url_to`` function to download
        the file to a sandbox, and then use ``import_filters`` to load it from there.

    Args:
        filename (str): Path and name of the filters file to load.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: []

    Raises:
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> import_filters('test.json') # Fetches filters in file 'test.json'
        []
        >>> import_filters('test') # Fetches filters in file 'test'
        []
    """

    res = commands.commands_get(f'filter import file="{get_abs_sandbox_path(filename)}"', base_url=base_url)
    time.sleep(
        CATCHUP_FILTER_SECS)  # give the filters time to finish executing ... this race condition is a Cytoscape bug
    return res


def _create_filter_and_finish(cmd, cmd_body, hide, apply, network, base_url):
    AUTO_APPLY_THRESHOLD = 100000
    if check_supported_versions(cytoscape='3.9') is None:
        cmd_body['apply'] = apply
        res = commands.cyrest_post(cmd, body=cmd_body, base_url=base_url)
    else:
        # Before Cytoscape 3.9, the filter was automatically applied when it was created unless
        # the total of nodes and edges was 100,000 or more. So, we create the filter and then
        # consider applying it if it wasn't automatically applied already.
        res = commands.cyrest_post(cmd, body=cmd_body, base_url=base_url)
        if networks.get_node_count(network=network, base_url=base_url) \
           + networks.get_edge_count(network=network, base_url=base_url) > AUTO_APPLY_THRESHOLD:
            if apply:
                show_error('Warning -- Cytoscape version pre-3.9 in use ... explicitly applying filter')
                res = commands.commands_post(
                    f'filter apply container="filter" name="{cmd_body["name"]}" network="{network}"',
                    base_url=base_url)
        elif not apply:
            raise CyError('Attempt to create but not apply filter in Cytoscape version pre-3.9 is not supported')

    return _check_selected(hide, network, base_url)


def _check_selected(hide, network, base_url):
    if check_supported_versions(cytoscape='3.9'):
    # This delay became unnecessary in Cytoscape 3.9
        show_error('Warning -- Cytoscape version pre-3.9 in use ... settling delay inserted after filter execution')
        time.sleep(CATCHUP_FILTER_SECS)  # Yikes! Have to wait a second for selection to settle!

    sel_nodes = network_selection.get_selected_nodes(network=network, base_url=base_url)
    sel_edges = network_selection.get_selected_edges(network=network, base_url=base_url)

    if hide:
        res = style_bypasses.unhide_all(network=network, base_url=base_url)
        # TODO: Ignore return result res??
        if sel_nodes is not None and len(sel_nodes) != 0:
            res= style_bypasses.hide_nodes(network_selection.invert_node_selection(network=network, base_url=base_url)['nodes'])
        if sel_edges is not None and len(sel_edges) != 0:
            res = style_bypasses.hide_edges(network_selection.invert_edge_selection(network=network, base_url=base_url)['edges'])

    return {'nodes': sel_nodes, 'edges': sel_edges}

# TODO: Need to add Topological filter, too.
# TODO: Need to add rename/remove filter
# TODO: Need to add filter chaining
# TODO: Need to fetch existing filter???
