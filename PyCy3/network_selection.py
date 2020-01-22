# -*- coding: utf-8 -*-

from . import commands
from . import networks
from .pycy3_utils import DEFAULT_BASE_URL, node_suid_to_node_name
from PyCy3.decorators import debug

def get_selected_node_count(network=None, base_url=DEFAULT_BASE_URL):
    net_suid = networks.get_network_suid(network, base_url=base_url)
    res = commands.cyrest_get('networks/' + str(net_suid) + '/nodes', parameters={'column': 'selected', 'query': 'true'}, base_url=base_url)
    return len(res)

def get_selected_nodes(node_suids=False, network=None, base_url=DEFAULT_BASE_URL):
    net_suid = networks.get_network_suid(network, base_url=base_url)

    if get_selected_node_count(net_suid, base_url=base_url) == 0:
        print('No nodes selected.')
        return None
    else:
        selected_node_suids = commands.cyrest_get('networks/' + str(net_suid) + '/nodes', parameters={'column': 'selected', 'query': 'true'})
        if node_suids:
            return selected_node_suids
        else:
            selected_node_names = node_suid_to_node_name(selected_node_suids, net_suid, base_url=base_url)
            return selected_node_names
