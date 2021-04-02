# -*- coding: utf-8 -*-

"""Functions for managing TABLE columns and table column functions, like map and rename, as well as loading and
extracting table data in Cytoscape.
"""

"""Copyright 2020 The Cytoscape Consortium

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

# External library imports
import pandas as pd
import numpy as np

# Internal module imports
from . import commands
from . import networks

# Internal module convenience imports
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log, narrate
from .exceptions import CyError
from .py4cytoscape_sandbox import get_abs_sandbox_path

def __init__(self):
    pass


@cy_log
def delete_table_column(column, table='node', namespace='default', network=None, base_url=DEFAULT_BASE_URL):
    """Delete a column from node, edge or network tables.

    Args:
        column (str): Name of the column to delete
        table (str): Name of table, e.g., node (default), edge, network
        namespace (str): Namespace of table. Default is "default".
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Note:
        No error is returned if the column doesn't exist in the table

    Raises:
        HTTPError: if table or namespace doesn't exist in network
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> delete_table_column('BetweennessCentrality')
        ''
        >>> delete_table_column('EdgeBetweenness', table='edge')
        ''
        >>> delete_table_column('BetweennessCentrality', network='My Network')
        ''
    """
    # TODO: Fix R's documentation ... the return value is wrong
    net_suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.cyrest_delete(f'networks/{net_suid}/tables/{namespace}{table}/columns/{column}',
                                 base_url=base_url, require_json=False)
    return res


@cy_log
def get_table_columns(table='node', columns=None, namespace='default', network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve one or more columns of data from node, edge or network tables.

    The 'SUID' column is always retrieved along with specified columns. The 'SUID' values are used as ``index`` in
    the returned ``dataframe``.

    Args:
        table (str): Name of table, e.g., node (default), edge, network
        columns (str or list or None): Names of columns to retrieve values from as list object or comma-separated list;
            default is all columns
        namespace (str): Namespace of table. Default is "default".
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dataframe: requested columns (including SUID), and rows for each node/edge or network.

    Raises:
        HTTPError: if table or namespace doesn't exist in network
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_table_columns()
              SUID shared name     name  ...   gal4RGsig   gal80Rsig isExcludedFromPaths
        3072  3072     YDL081C  YDL081C  ...    0.048133  5.9631e-06               False
        3073  3073     YGL166W  YGL166W  ...   0.0012181    0.032147               False
        ...
        >>> get_table_columns(columns='name')
              SUID shared name     name  ...   gal4RGsig   gal80Rsig isExcludedFromPaths
        3072  3072     YDL081C  YDL081C  ...    0.048133  5.9631e-06               False
        3073  3073     YGL166W  YGL166W  ...   0.0012181    0.032147               False
        ...
        >>> get_table_columns(columns=['gal1RGexp', 'Eccentricity', 'Stress'])
            gal1RGexp Eccentricity  Stress
        4608    -0.262           17       0
        4609    -0.704           17    2092
        ...
        >>> get_table_columns(columns='Stress, NumberOfDirectedEdges')
                Stress NumberOfDirectedEdges
        4608       0                     1
        4609    2092                     2
        ...
        >>> get_table_columns(columns='Stress, bogus')
              Stress bogus
        4608       0   NaN
        4609    2092   NaN
        ...

    Note:
        For requested columns not present in the table, the column is still returned but is full of ``nan`` values.
    """
    suid = networks.get_network_suid(network, base_url)

    # column information (names and types)
    table_col_info = get_table_column_types(table, namespace=namespace, network=network, base_url=base_url)
    table_col_list = list(table_col_info.keys())

    # all columns ... handle comma separated lists and list objects
    if columns is None:
        col_list = table_col_list
    elif isinstance(columns, str):
        col_list = [col.strip() for col in columns.split(',')]
    else:
        col_list = columns

    # get suid column first and make a dataframe with SUID as index
    res_names = commands.cyrest_get(f'networks/{suid}/tables/{namespace}{table}/columns/SUID', base_url=base_url)
    suid_list = res_names['values']
    df = pd.DataFrame(index=suid_list, columns=col_list)

    # then fill in each requested column
    for col in col_list:
        if not col in table_col_list:
            narrate(f'Column "{col}" not found in "{table}" table')
            # TODO: Is this really the behavior we want?
            break

        # fetch all values for the column
        res_col = commands.cyrest_get(f'networks/{suid}/tables/{namespace}{table}/columns/{col}', base_url=base_url)

        # the R version of this function replaces missing values with the constant NA, which
        # doesn't exist in Python. Pandas authority discusses this situation, but doesn't
        # make a clear recommendation, so we'll leave None as None for non-numerics and nan for
        # numerics.
        # https://pandas.pydata.org/pandas-docs/stable/user_guide/missing_data.html
        table_col_type = table_col_info[col]
        if table_col_type in ['Double']:
            def f(x):
                return np.nan if x is None else float(x)
        elif table_col_type in ['Long', 'Integer']:
            def f(x):
                return np.nan if x is None else int(x)
        elif table_col_type in ['Boolean']:
            def f(x):
                return None if x is None else bool(x)
        else:
            def f(x):
                return x
        cvv = [f(x) for x in res_col['values']]

        if len(suid_list) != len(cvv):
            narrate('Column "%s" has only %d elements, but should have %d' % (col, len(cvv), len(suid_list)))
            break  # TODO: Is this the right response?
        # TODO: Consider assigning entire column all at once instead of iterating ... should be OK
        for val, suid_val in zip(cvv, suid_list):
            df.at[suid_val, col] = val

    return df


@cy_log
def get_table_value(table, row_name, column, namespace='default', network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the value from a specific row and column from node, edge or network tables.

    Args:
        table (str): Name of table, e.g., node (default), edge, network
        row_name (str): Node, edge or network name, i.e., the value in the "name" column
        column (str): Name of column to retrieve values from
        namespace (str): Namespace of table. Default is "default".
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        obj: the value of the table cell, cast to float, int, bool or str depending on column type

    Raises:
        HTTPError: if table or namespace doesn't exist in network or if cell contains a numeric type but no number
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_table_value('node', 'YDL194W', 'COMMON')
        'SNF3'
        >>> get_table_value('edge', 'YLR197W (pp) YOR310C', 'EdgeBetweenness', network='My Network')
        2.0
        >>> get_table_value('node', 'YDL194W', 'IsSingleNode')
        False
    """
    suid = networks.get_network_suid(network, base_url=base_url)

    # column type
    table_col_info = get_table_column_types(table, namespace, network, base_url=base_url)
    table_col_type = table_col_info[column]

    # which row
    row_key = None
    from .py4cytoscape_utils import node_name_to_node_suid
    from .py4cytoscape_utils import edge_name_to_edge_suid
    if table == 'node':
        row_key = node_name_to_node_suid(row_name, network, base_url=base_url)[0]
    elif table == 'edge':
        row_key = edge_name_to_edge_suid(row_name, network, base_url=base_url)[0]
    elif table == 'network':
        row_key = networks.get_network_suid(row_name,
                                            base_url=base_url)  # TODO: R implementation looks wrong because of == and use of row_name
    else:
        row_key = None

    # get row/column value
    res = commands.cyrest_get(f'networks/{suid}/tables/{namespace}{table}/rows/{row_key}/{column}', base_url=base_url,
                              require_json=False)
    if not res: return None
    # TODO: This "not res" can't happen for numbers because CyREST returns HTTPError if a value doesn't exist ... is this what we want?
    # TODO: For strings, a '' is returned ... do we want to return None for this?

    if table_col_type == 'Double':
        return float(res)
    elif table_col_type == 'Long':
        return int(res)
    elif table_col_type == 'Integer':
        return int(res)
    elif table_col_type == 'Boolean':
        return bool(res)
    else:
        return str(res)


@cy_log
def get_table_column_names(table='node', namespace='default', network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the names of all columns in a table.

    Args:
        table (str): Name of table, e.g., node, edge, network; default is "node"
        namespace (str): Namespace of table. Default is "default".
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: list of column names

    Raises:
        HTTPError: if table or namespace or table doesn't exist in network
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_table_column_names()
        ['SUID', 'shared name', 'name', 'selected', 'AverageShortestPathLength', ... ]
        >>> get_table_column_names('edge')
        ['SUID', 'shared name', 'shared interaction', 'name', 'selected', 'interaction', 'EdgeBetweenness']
        >>> get_table_column_names('network', network='My Network')
        ['SUID', 'shared name', 'name', 'selected', '__Annotations', 'publication', 'Dataset Name', 'Dataset URL']
    """
    suid = networks.get_network_suid(network, base_url=base_url)
    tbl = namespace + table
    res = commands.cyrest_get(f'networks/{suid}/tables/{tbl}/columns', base_url=base_url)
    col_names = [x['name'] for x in res]
    return col_names


@cy_log
def get_table_column_types(table='node', namespace='default', network=None, base_url=DEFAULT_BASE_URL):
    """Retrieve the types of all columns in a table.

    Args:
        table (str): Name of table, e.g., node, edge, network; default is "node"
        namespace (str): Namespace of table. Default is "default".
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: where the column name is the key and the data type is the value

    Raises:
        HTTPError: if table or namespace or table doesn't exist in network
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_table_column_types()
        {'SUID': 'Long', 'shared name': 'String', 'name': 'String', 'selected': 'Boolean', 'AverageShortestPathLength': 'Double', ...}
        >>> get_table_column_types('edge')
        {'SUID': 'Long', 'shared name': 'String', 'shared interaction': 'String', 'name': 'String', ... }
        >>> get_table_column_types('network', network='My Network')
        {'SUID': 'Long', 'shared name': 'String', 'name': 'String', 'selected': 'Boolean', '__Annotations': 'List', ...}
    """
    suid = networks.get_network_suid(network, base_url=base_url)
    cmd = f'networks/{suid}/tables/{namespace}{table}/columns'
    res = commands.cyrest_get(cmd, base_url=base_url)
    col_types = {x['name']: x['type'] for x in res}

    return col_types

@cy_log
def load_table_data_from_file(file, first_row_as_column_names=False, start_load_row=1, delimiters='\\,,\t', data_key_column_index=1, table='node', table_key_column='shared name', network=None, base_url=DEFAULT_BASE_URL):
    """Loads data into Cytoscape tables from a tabular file.

    This function loads data into Cytoscape node/edge/network
    tables provided a common key, e.g., name. The tabular file
    may or may not contain a list of column names as the first
    row of the file. If not, Cytoscape will pick a name for each
    column. The data rows can start right after the column name
    row, or can be offset by some number of lines (which will be
    ignored). The delimiter that separates column names or data
    values can be specified. Existing columns with the same
    names will keep original type but values will be overwritten.
    Note that because the columns may or may not be named, the
    column used as a key is specified by its ordinal position
    amongst the other columns (i.e., the leftmost column is 1).

    Note:
        To load a table file from cloud storage, use the file's URL and the ``sandbox_url_to`` function to download
        the file to a sandbox, and then use ``load_table_data_from_file`` to load it from there.

    Args:
        file (str): Name of tabular file in any of the supported formats (e.g., .txt, .csv, .xls, .tsv, etc)
        first_row_as_column_names (bool): True if first row contributes column names but no data values; defaults to False
        start_load_row (int): 1-based row to start reading data ... after column name row, if present; defaults to 1
        delimiters (str): comma-separated list of characters that can separate columns ... \\, is a comma, \t is a tab; defaults to '\\,,\t'
        data_key_column_index (int): 1-based column number in tabular file to use a merge key
        table (str): name of Cytoscape table to load data into, e.g., node, edge or network; default is "node"
        table_key_column (str): name of column in Cytoscape table to use as merge key ... must be a column in the root network (i.e., global to all networks in the collection)
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        list: SUIDs of tables merged into

    Raises:
        CyError: if network name or SUID doesn't exist, file doesn't exist, or other parameters are incorrect
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> load_table_data_from_file('data/defaultnode_table.xlsx', first_row_as_column_names=True)
        {'mappedTables': [460222, 460260]}
        >>> load_table_data_from_file('data/defaultedge_table.csv', first_row_as_column_names=True, table='edge')
        {'mappedTables': [460222, 460260]}
        >>> load_table_data_from_file('data/defaultnode_table.txt', first_row_as_column_names=True, data_key_column_index=2, table_key_column='COMMON')
        {'mappedTables': [460222, 460260]}
    """
    file = get_abs_sandbox_path(file)

    table = table.lower()
    if table == 'node':
        table = 'Node Table Columns'
    elif table == 'edge':
        table = 'Edge Table Columns'
    elif table == 'network':
        table = 'Network Table Columns'
    else:
        raise CyError(f'Unknown table type {table}; must be either "node", "edge" or "network"')

    res = commands.commands_post(
        f'table import file file="{file}" firstRowAsColumnNames="{first_row_as_column_names}" startLoadRow="{start_load_row}" delimiters="{delimiters}" keyColumnIndex="{data_key_column_index}" dataTypeTargetForNetworkCollection="{table}" keyColumnForMapping="{table_key_column}"',
        base_url=base_url)
    return res

@cy_log
def load_table_data(data, data_key_column='row.names', table='node', table_key_column='name', namespace='default',
                    network=None, base_url=DEFAULT_BASE_URL):
    """Loads data into Cytoscape tables keyed by row.

    This function loads data into Cytoscape node/edge/network
    tables provided a common key, e.g., name. Data.frame column names will be
    used to set Cytoscape table column names.
    Numeric values will be stored as Doubles in Cytoscape tables.
    Integer values will be stored as Integers. Character or mixed values will be
    stored as Strings. Logical values will be stored as Boolean. Lists are
    stored as Lists by CyREST v3.9+. Existing columns with the same names will
    keep original type but values will be overwritten.

    Args:
        data (dataframe): each row is a node and columns contain node attributes
        data_key_column (str): name of data.frame column to use as key; ' default is "row.names"
        table (str): name of Cytoscape table to load data into, e.g., node, edge or network; default is "node"
        namespace (str): Namespace of table. Default is "default".
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: 'Success: Data loaded in <table name> table' or 'Failed to load data: <reason>'

    Raises:
        HTTPError: if table or namespace or table doesn't exist in network
        CyError: if network name or SUID doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> data = df.DataFrame(data={'id':['New1','New2','New3'], 'newcol':[1,2,3]})
        >>> load_table_data(data, data_key_column='id', table='node', table_key_column='name')
        'Failed to load data: Provided key columns do not contain any matches'
        >>> data = df.DataFrame(data={'id':['YDL194W','YDR277C','YBR043C'], 'newcol':[1,2,3]})
        >>> load_table_data(data, data_key_column='id', table='node', table_key_column='name', network='galfiltered.sif')
        'Success: Data loaded in defaultnode table'
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    table_key_column_values = get_table_columns(table=table, namespace=namespace, columns=table_key_column,
                                                network=net_suid, base_url=base_url)
    # TODO: Shouldn't namespace be in this parameter list? R doesn't have it ... I added it

    if table_key_column_values.columns is None:
        raise CyError('Failed to load data. Please check table_key_column.')

    if data_key_column == 'row.names':
        data['row.names'] = data.index

    if not data_key_column in data.columns:
        raise CyError('Failed to load data. Please check data_key_column.')

    # verify that there is at least one key in the Cytoscape table that matches a key in the data
    table_keys = table_key_column_values[table_key_column].astype(str).values
    filter = [str(key) in table_keys     for key in data[data_key_column]]
    if not True in filter:
        raise CyError(f'Provided table key column "{table_key_column}" and data key column "{data_key_column}" do not contain any matches')

    # create table containing columns present in data and already present in Cytoscape table
    data_subset = data[filter]

    # look for elements that are lists (instead of scalars) and turn them into comma-separated strings.
    # Note that CyREST doesn't accept lists or create columns of type list, but comma-separated strings is
    # the best we can do for the user at this time.
    for col in data_subset.columns:
        col_val = [','.join(val) if isinstance(val, list) else val for val in data_subset[col]]
        data_subset[col] = col_val

    # TODO: Find out whether "factors" are an issue in Python, and why factors could be troublesome in R
    # TODO: Verify that this gives the right answer for list of str, int, etc

    data_list = _df_to_attr_dict_list(data_subset)  # convert DataFrame to dicts that are easy to convert to JSON

    tbl = namespace + table  # calculate fully qualified table name

    # if there are any columns that aren't in the Cytoscape table and they're going to be Int, add them explicitly now so
    # they don't default to float
    def create_col(x):
        return commands.cyrest_post(f'networks/{net_suid}/tables/{tbl}/columns',
                                    body={'name': x, 'type': 'Integer'}, require_json=False, base_url=base_url)

    existing_cols = get_table_column_names(table, namespace, net_suid, base_url=base_url)
    [create_col(x[0]) if x[1] == 'int64' and not x[0] in existing_cols else None for x in
     data_subset.dtypes.iteritems()]

    # finally, add the values for whatever columns we have (and create new columns as needed)
    res = commands.cyrest_put(f'networks/{net_suid}/tables/{tbl}',
                              body={'key': table_key_column, 'dataKey': data_key_column, 'data': data_list},
                              require_json=False, base_url=base_url)

    return f'Success: Data loaded in {tbl} table'
    # TODO: This is a difficult result to test for ... are we able to change it?


@cy_log
def map_table_column(column, species, map_from, map_to, force_single=True, table='node', namespace='default',
                     network=None, base_url=DEFAULT_BASE_URL):
    """Map Table Column.

    Perform identifier mapping using an existing column of supported identifiers to populate a new column with
    identifiers mapped to the originals.

    Supported species: Human, Mouse, Rat, Frog, Zebrafish, Fruit fly, Mosquito, Worm, Arabidopsis thaliana, Yeast,
    E. coli, Tuberculosis. Supported identifier types (depending on species): Ensembl, Entrez Gene, Uniprot-TrEMBL,
    miRBase, UniGene,  HGNC (symbols), MGI, RGD, SGD, ZFIN, FlyBase, WormBase, TAIR.

    Args:
        column (str): Name of column containing identifiers of type specified by ``map.from``
        species (str): Common name for species associated with identifiers, e.g., Human. See details.
        map_from (str): Type of identifier found in specified ``column``. See details.
        map.to (str): Type of identifier to populate in new column. See details.
        force.single (bool): Whether to return only first result in cases of one-to-many mappings; otherwise
            the new column will hold lists of identifiers. Default is TRUE.
        table (str): name of Cytoscape table to load data into, e.g., node, edge or network; default is "node"
        namespace (str): Namespace of table. Default is "default".
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dataframe: contains map_from and map_to columns.

    Warnings:
        If map_to is not unique, it will be suffixed with an incrementing number in parentheses, e.g.,
        if mapIdentifiers is repeated on the same network. However, the original map_to column will be returned regardless.

    Raises:
        HTTPError: if table or namespace or table doesn't exist in network
        CyError: if network name or SUID doesn't exist, or if mapping parameter is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> map_table_column('name','Yeast','Ensembl','SGD')
                  name        SGD
        17920  YER145C S000000947
        17921  YMR058W S000004662
        17922  YJL190C S000003726
        ...
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)
    tbl = str(net_suid) + ' ' + namespace + ' ' + table

    fs = 'true' if force_single else 'false'

    all_cols = get_table_column_names(table, namespace, network, base_url=base_url)
    if not column in all_cols: raise CyError(f'Column "{column}" does not exist')

    res_map = commands.commands_post(
        f'idmapper map column columnName="{column}" forceSingle="{fs}" mapFrom="{map_from}" mapTo="{map_to}" species="{species}" table="{tbl}"',
        base_url=base_url)
    if res_map['new column'] == 'null ': raise CyError('No mappings returned')
    # TODO: Do we really mean to throw this result away?? R does ... if the 'new column' value returns null, something went wrong ... I added check

    res = get_table_columns(table=table, columns=[column, map_to], namespace=namespace, network=network,
                            base_url=base_url)
    return res


@cy_log
def rename_table_column(column, new_name, table='node', namespace='default', network=None, base_url=DEFAULT_BASE_URL):
    """Set a new name for a column.

    Args:
        column (str): Name of the column to rename
        new_name (str): New name for the specified column
        table (str): name of Cytoscape table to load data into, e.g., node, edge or network; default is "node"
        namespace (str): Namespace of table. Default is "default".
        network (SUID or str or None): Name or SUID of a network. Default is the
            "current" network active in Cytoscape.
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://127.0.0.1:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        str: ''

    Raises:
        HTTPError: if table or namespace or table doesn't exist in network, or if column doesn't exist in table, or new_name already exists
        CyError: if network name or SUID doesn't exist, or if mapping parameter is invalid
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> rename_table_column('AverageShortestPathLength', 'xAveragex')
        ''
        >>> rename_table_column('AverageShortestPathLength', 'xAveragex', table='edge', namespace='default', network='My Network')
        ''
    """
    net_suid = networks.get_network_suid(network, base_url=base_url)

    res = commands.cyrest_put(f'networks/{net_suid}/tables/{namespace}{table}/columns',
                              body={'oldName': column, 'newName': new_name},
                              base_url=base_url, require_json=False)
    return res


# TODO: Check to see if this is needed in RCy3
def _nan_to_none(original_df, attr_dict_list):
    # convert missing numbers from 'nan' to None, which will cause the JSON converter to properly emit null
    # First, determine whether any floating point values are missing
    if original_df.isnull().any().any():
        # yes ... find out which rows contain null values
        data_subset_nans = original_df.isnull()  # map out missing floating point in all cells
        data_subset_nans_indexes = [True in set(data_subset_nans.loc[i, :]) for i in
                                    data_subset_nans.index]  # find rows containing missing floating point
        for has_missing, row_contents in zip(data_subset_nans_indexes, attr_dict_list):
            # for each row in data_list, if it has missing values, find them and replace them with 'None'
            # Note that this could not have been done with data_subset because it's a DataFrame, which only outputs 'nan'
            if has_missing:
                for key, value in row_contents.items():
                    if type(value) is float and np.isnan(value): row_contents[key] = None
    return attr_dict_list


def _df_to_attr_dict_list(df):
    # convert whole data table to dictionary suitable for JSON encoding
    data_list = df.to_dict(orient='records')
    return _nan_to_none(df, data_list)
