import py4cytoscape as p4c
import pandas as pd

df = pd.read_csv('a.csv')

b = p4c.create_network_from_data_frames(df, edges=None, title="My first network", collection="DataFrame Example")


