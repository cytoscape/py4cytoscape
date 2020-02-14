from . import commands
from .pycy3_utils import DEFAULT_BASE_URL

def cytoscape_ping(base_url=DEFAULT_BASE_URL):
    try:
        res = commands.cyrest_get('version')
        if 'cytoscapeVersion' in res:
            print('You are connected to Cytoscape!')
    except:
        print('CyREST connection problem. PyCy3 can not continue!')
