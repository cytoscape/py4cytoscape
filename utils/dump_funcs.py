import py4cytoscape
import inspect
import re
import csv

SKIP_MODULES = {'py4cytoscape.decorator',
                'py4cytoscape.decorators',
                'py4cytoscape.py4cytoscape_logger',
                'py4cytoscape.py4cytoscape_notebook',
                'py4cytoscape.py4cytoscape_sandbox'}


def sort_key(e):
    return f'{e[0]}:{e[1]}'  # return sub-module and function in tuple


# Collect all of the callable functions in this package
callable_funcs = [y for y in inspect.getmembers(py4cytoscape, callable)]

# Collect (sub-module, funcname, params) in a list

func_signatures = [[re.sub(r'^py4cytoscape\.', '', y[1].__module__), y[0], str(inspect.signature(y[1]))]
                   for y in callable_funcs if not y[1].__module__ in SKIP_MODULES]
func_signatures.sort(key=sort_key)  # Group according to sub-module and then function name

with open('py4cytoscape_funcs.csv', 'w', newline='') as f:
    write = csv.writer(f)
    write.writerow(['Sub-Module', 'FuncName', 'Params'])
    write.writerows(func_signatures)

print(f'Done ... {len(func_signatures)} rows')
