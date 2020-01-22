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

def get_table_column_types(table='node', namespace='default', network=None, base_url=DEFAULT_BASE_URL):
    suid = networks.get_network_suid(network, base_url=base_url)
    cmd = 'networks/' + str(suid) + '/tables/' + namespace + table + '/columns'
    res = commands.cyrest_get(cmd, base_url=base_url)
    col_types = {x['name']: x['type'] for x in res}

    return col_types


