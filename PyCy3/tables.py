# -*- coding: utf-8 -*-

from . import commands
from . import networks
from .pycy3_utils import DEFAULT_BASE_URL

from .decorators import debug
import pandas as pd
import numpy as np

def __init__(self):
    pass

def get_table_columns(table='node', columns=None, namespace='default', network=None, base_url=DEFAULT_BASE_URL):
    suid = networks.get_network_suid(network, base_url)

    # column information (names and types)
    table_col_info = get_table_column_types(table, namespace=namespace, network=network, base_url=base_url)
    table_col_list = list(table_col_info.keys())

    # all columns ... handle comma separated lists and list objects
    if columns is None:
        col_list = table_col_list
    elif isinstance(columns, str):
        col_list = columns.split(',')
    else:
        col_list = columns

    # get suid column first and make a dataframe with SUID as index
    res_names = commands.cyrest_get('networks/' + str(suid) + '/tables/' + namespace + table + '/columns/SUID', base_url=base_url)
    suid_list = res_names['values']
    df = pd.DataFrame(index=suid_list, columns=col_list)

    # then fill in each requested column
    for col in col_list:
        if not col in table_col_list:
            print('Error: Column ' + col + ' not found in ' + table + ' table\n')
            break

        # fetch all values for the column
        res_col = commands.cyrest_get('networks/' + str(suid) + '/tables/' + namespace + table + '/columns/' + col, base_url=base_url)

        # the R version of this function replaces missing values with the constant NA, which
        # doesn't exist in Python. Pandas authority discusses this situation, but doesn't
        # make a clear recommendation, so we'll leave None as None for non-numerics and nan for
        # numerics.
        # https://pandas.pydata.org/pandas-docs/stable/user_guide/missing_data.html
        table_col_type = table_col_info[col]
        if table_col_type in ['Double']:
            f = lambda x: np.nan if (x is None) else float(x)
        elif table_col_type in ['Long', 'Integer']:
            f = lambda x: np.nan if (x is None) else int(x)
        elif table_col_type in ['Boolean']:
            f = lambda x: None if (x is None) else bool(x)
        else:
            f = lambda x: x
        cvv = [f(x) for x in res_col['values']]

        if len(suid_list) != len(cvv):
            print('Error: Column ' + col + ' has only ' + str(len(cvv)) + ' elements, but should have ' + str(len(suid_list)))
            break
        # TODO: Consider assigning entire column all at once instead of iterating ... should be OK
        for val, suid_val in zip(cvv, suid_list):
            df.at[suid_val, col] = val

    return df

def get_table_column_names(table='node', namespace='default', network=None, base_url=DEFAULT_BASE_URL):
    suid = networks.get_network_suid(network, base_url=base_url)
    tbl = namespace + table
    res = commands.cyrest_get('networks/' + str(suid) + '/tables/' + tbl + '/columns', base_url=base_url)
    col_names = [x['name']   for x in res]
    return col_names

def get_table_column_types(table='node', namespace='default', network=None, base_url=DEFAULT_BASE_URL):
    suid = networks.get_network_suid(network, base_url=base_url)
    cmd = 'networks/' + str(suid) + '/tables/' + namespace + table + '/columns'
    res = commands.cyrest_get(cmd, base_url=base_url)
    col_types = {x['name']: x['type'] for x in res}

    return col_types

def load_table_data(data, data_key_column='row.names', table='node', table_key_column='name', namespace='default', network=None, base_url=DEFAULT_BASE_URL):
    net_suid = networks.get_network_suid(network, base_url=base_url)
    table_key_column_values = get_table_columns(table=table, columns=table_key_column, network=net_suid, base_url=base_url)

    if table_key_column_values.columns is None:
        return "Failed to load data: Please check table.key.column"

    if data_key_column == 'row.names':
        data['row.names'] = data.index

    if not data_key_column in data.columns:
        return "Failed to load data: Please check data.key.column"

    # verify that there is at least one key in the Cytoscape table that matches a key in the data
    table_keys = table_key_column_values[table_key_column].values
    filter = [key in table_keys    for key in data[data_key_column]]
    if not True in filter:
        return "Failed to load data: Provided key columns do not contain any matches"

    # create table containing columns present in data and already present in Cytoscape table
    data_subset = data[filter]

    # look for elements that are lists (instead of scalars) and turn them into comma-separated strings.
    # Note that CyREST doesn't accept lists or create columns of type list, but comma-separated strings is
    # the best we can do for the user at this time.
    for col in data_subset.columns:
        col_val = [','.join(val) if isinstance(val, list) else val    for val in data_subset[col]]
        data_subset[col] = col_val

    # TODO: Find out whether "factors" are an issue in Python, and why factors could be troublesome in R
    # TODO: Verify that this gives the right answer for list of str, int, etc

    data_list = _df_to_attr_dict_list(data_subset) # convert DataFrame to dicts that are easy to convert to JSON

    tbl = namespace + table # calculate fully qualified table name

    # if there are any columns that aren't in the Cytoscape table and they're going to be Int, add them explicitly now so
    # they don't default to float
    def create_col(x):
        return commands.cyrest_post('networks/' + str(net_suid) + '/tables/' + tbl + '/columns', body={'name':x, 'type':'Integer'}, require_json=False, base_url=base_url)
    existing_cols = get_table_column_names(table, namespace, net_suid, base_url=base_url)
    [create_col(x[0]) if x[1] == 'int64' and not x[0] in existing_cols else None     for x in data_subset.dtypes.iteritems()]

    # finally, add the values for whatever columns we have (and create new columns as needed)
    res = commands.cyrest_put('networks/' + str(net_suid) + '/tables/' + tbl, body={'key': table_key_column, 'dataKey': data_key_column, 'data': data_list}, require_json=False, base_url=base_url)

    return 'Success: Data loaded in ' + tbl + ' table'

# TODO: Check to see if this is needed in RCy3
def _nan_to_none(original_df, attr_dict_list):
    # convert missing numbers from 'nan' to None, which will cause the JSON converter to properly emit null
    # First, determine whether any floating point values are missing
    if original_df.isnull().any().any():
        # yes ... find out which rows contain null values
        data_subset_nans = original_df.isnull() # map out missing floating point in all cells
        data_subset_nans_indexes = [True in set(data_subset_nans.loc[i,:])    for i in data_subset_nans.index] # find rows containing missing floating point
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

