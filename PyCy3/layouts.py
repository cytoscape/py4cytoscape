# -*- coding: utf-8 -*-

from . import commands
from . import networks
from .pycy3_utils import DEFAULT_BASE_URL

def layoutNetwork(layout_name=None, network=None, base_url=DEFAULT_BASE_URL):
    suid = networks.get_network_suid(network, base_url=base_url)
    if layout_name is None:
        res = commands.commands_post('layout apply preferred networkSelected="SUID:' + str(suid) + '"', base_url=base_url)
        return res
    else:
        res = commands.commands_post('layout ' + layout_name + ' network="SUID:' + str(suid) + '"', base_url=base_url)
        return res
