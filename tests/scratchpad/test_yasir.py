# -*- coding: utf-8 -*-

""" Test functions in style_mappings.py.
"""

import unittest
import pandas as df
import time
import urllib.request
import uuid

from requests import RequestException

from test_utils import *


class MyTestCase(unittest.TestCase):
    def setUp(self):
        try:
            delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    @print_entry_exit
    def test_ui(self):
        load_test_session('c:/Program Files/Cytoscape_v3.8.1/sampleData/sessions/Affinity Purification.cys')
        edges = get_all_edges()
        sources = [re.match('(\S*) \(.*\) (\S*)', edge).group(1)   for edge in edges]
        targets = [re.match('(\S*) \(.*\) (\S*)', edge).group(2)   for edge in edges]
        edge_data = {'source': sources, 'target': targets}

        edges_frame = df.DataFrame(data=edge_data, columns=['source', 'target'])

        network_name = uuid.uuid4().hex
        network_suid = networks.create_network_from_data_frames(edges=edges_frame, title=network_name, collection=network_name + '_collection')

        analyze = commands.commands_post('analyzer/analyze')
        mcode = commands.commands_post('mcode cluster degreeCutoff=2 fluff=false fluffNodeDensityCutoff=0.1 haircut=true includeLoops=false kCore=2 maxDepthFromStart=100 network=current nodeScoreCutoff=0.2 scope=NETWORK')
        big_clusters = [i for i in range(len(mcode['clusters'])) if len(mcode['clusters'][i]['nodes']) > 3]
        clusters = []
        for i in range(len(big_clusters)):
            view_id = commands.commands_post('mcode view id=1 rank=' + str(i+1) )
            clusters.append( tables.get_table_columns()
                             .drop(columns=['id','name','selected','MCODE_Cluster','SUID'])
                             .sort_values(by=['MCODE_Score'], ascending=False)
                             .reset_index(drop=True) )
            network_views.get_network_view_suid()
            img_name = str(i) #uuid.uuid4().hex
            export_image(str(img_name))
            # Image(img_name+'.png')
            #img_name
        # sleep(3)


if __name__ == '__main__':
    unittest.main()
