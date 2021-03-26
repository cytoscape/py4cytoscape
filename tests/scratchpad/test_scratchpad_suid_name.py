import py4cytoscape as p4c
import pandas as pd
from igraph import *

def test_1():
    x = pd.read_csv('nodes_for_Cytoscape_test.txt', sep='\t')
    y = pd.read_csv('edges_for_Cytoscape_test.txt', sep='\t')
    print("OK")

def test_2a():
    graph_1 = Graph([(0, 1), (0, 1)], directed=True)
    graph_1.vs['name'] = ['A', 'B']
    graph_1.es['type'] = ['E1', 'E2']
    print(graph_1)

    p4c.create_network_from_igraph(graph_1)

# test_1()
test_2a()
