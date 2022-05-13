class Node:
    def __init__(self, suid):
        self.parent = None
        self.suid = suid

def create_node_bag(node_order, node_tree):
    # Create tree where each node contains all SUIDs of its left and right children
    node_bag = {no['nodeName']: Node({no['suid']})   for no in node_order}
    assert len(node_bag) == len(node_order), 'Node list contained at least one duplicate'

    for nt in node_tree:
        assert nt['left'] in node_bag and nt['right'] in node_bag, f'{nt["name"]} has undefined child'
        left_node = node_bag[nt['left']]
        right_node = node_bag[nt['right']]

        left_node.parent = \
        right_node.parent = \
        node_bag[nt['name']] = Node(left_node.suid.union(right_node.suid))

    return node_bag

def find_node_set(node_to_find, node_set_size, node_order, node_bag):
    # Find set of nodes containing a particular node and a number of similar nodes
    suid_to_node = {str(no['suid']): node_bag[no['nodeName']] for no in node_order}
    assert node_to_find in suid_to_node, f'Node {node_to_find} is not a network node'
    cur_node = suid_to_node[node_to_find]
    parent_node = cur_node.parent

    # Find cur_node containing fewer SUIDs and parent_node containing more SUIDs
    while parent_node is not None and len(parent_node.suid) < node_set_size:
        temp = cur_node
        cur_node = parent_node
        parent_node = temp.parent

    # Choose enough SUIDs from parent node to fill out SUIDS in the cur_node
    parent_nodes = {}
    parent_nodes_needed = node_set_size - len(cur_node.suid)
    if parent_node is not None and parent_nodes_needed > 0:
        parent_nodes = parent_node.suid.difference(cur_node.suid)
        parent_nodes = set(list(parent_nodes)[:parent_nodes_needed])

    return cur_node.suid.union(parent_nodes)

#################################

import json

dend = json.load(open('C:\\Users\\CyDeveloper\\Desktop\\dend.json'))
node_order = dend[0]['nodeOrder']
node_tree = dend[0]['nodeTree']

node_bag = create_node_bag(node_order, node_tree)
select_nodes = find_node_set('5680188', 30, node_order, node_bag)

print(select_nodes)


