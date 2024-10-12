"""
This program validates the linkage file and checks for loops.
The input will be a user specified file, the linkage file and
the design file for the JSON tree.
Author: Yi Ding
Version: 1.0
"""

import csv

DEPTH = 4
HOME_DEPTH = 1
TERMINATE = 2
HAS_LOOP = 1
NO_LOOP = 0
SERNUM = "Option 1"
STRLNK = "Option 2"
FNAME_REP = "node_validation_report.txt"
FNAME_LNK = "converted_to_str.csv"
N_LENGTH = 100


def generate_report(method, invalid_nodes, invalid_weight, invalid_paths, fpath_output):

    f = open(f"{fpath_output}/{FNAME_REP}", "w")
    if method == SERNUM:
        f.write("Method: conversion for serial to string." + '\n')
    elif method == STRLNK:
        f.write("Method: check validity of node names." + '\n')
    
    f.write('-'*N_LENGTH + '\n')
    if invalid_nodes:
        f.write(f"{len(invalid_nodes)} pairs of nodes were not found in the tree." + '\n')
        f.write("from_node   to_node     weight" + '\n')
        for node in invalid_nodes:
            f.write("{:<11s} {:<11s} {}".format(node[0], node[1], node[2]) + '\n')
    else:
        f.write("All nodes seem to be valid." + '\n')
    
    f.write('-'*N_LENGTH + '\n')
    if invalid_weight:
        f.write(f"{len(invalid_weight)} weightings were unreasonable." + '\n')
        f.write("from_node   to_node     weight" + '\n')
        for node in invalid_weight:
            f.write("{:<11s} {:<11s} {}".format(node[0], node[1], node[2]) + '\n ')
    else:
        f.write("All weightings seem to be valid." + '\n')
    
    f.write('-'*N_LENGTH + '\n')
    if invalid_paths:
        f.write(f"{len(invalid_paths)} loops were found." + '\n')
        idx = 1
        for path in invalid_paths:
            f.write(f"Loop {idx}:" + '\n')
            idx += 1
            for node in path:
                f.write(f"{'':7s}{node}" + '\n')
    else:
        f.write("There does not seem to be loops." + '\n')
    f.close()


def convert_serial_to_string(fpath_link, linkages, all_nodes_down):

    invalid_nodes = []
    invalid_weight = []
    with open(fpath_link, 'r', encoding='utf-8') as csvf:

        csvReader = csv.DictReader(csvf)
        for row in csvReader:
            from_node, to_node, weight = row.values()
            is_valid = [False, False]

            if float(weight) <= 0 or float(weight) > 1:
                invalid_weight.append(tuple(row.values()))
                continue

            for node, val in all_nodes_down.items():
                if from_node == val['id']:
                    from_node_mod = (node[0], weight)
                    is_valid[0] = True
                elif to_node == val['id']:
                    to_node_mod = node
                    is_valid[1] = True
            
            if not is_valid[0] or not is_valid[1]:
                invalid_nodes.append(tuple(row.values()))
                continue

            if to_node_mod not in linkages:
                linkages[to_node_mod] = []
            linkages[to_node_mod].append(from_node_mod)
            
    return invalid_nodes, invalid_weight


def linkage_struct_adjust(linkages):
    for key, val in linkages.items():
        depth = key[1]
        temp = [(x[0], depth) for x in val]
        linkages[key] = temp

def save_linkage(linkages, fpath_output):

    header = ['node_depth', 'from_node', 'to_node', 'weight']
    data = [header]
    for to_node, from_nodes in linkages.items():
        tn_name, tn_depth = to_node
        for from_node in from_nodes:
            fn_name, weight = from_node
            new_row = [tn_depth, fn_name, tn_name, weight]
            data.append(new_row)

    with open(f"{fpath_output}/{FNAME_LNK}", 'w', encoding='utf-8', newline='') as csvf:
        csvwriter = csv.writer(csvf)
        csvwriter.writerows(data)


def check_loop(next_node, current_path):

    loop = None
    
    if next_node not in current_path:
        status = NO_LOOP

    if next_node in current_path:
        rise = False
        prev_depth = next_node[1]
        on_same_level = True
        count_same_level = 0
        idx = current_path.index(next_node)
        loop = current_path[idx:]
        lowest_depth = min(loop, key=lambda x: x[1])[1]

        for item in loop:

            if item[1] != lowest_depth:
                on_same_level = False
            else:
                count_same_level += 1

            if item[1] > prev_depth:
                rise = True
            elif item[1] < prev_depth and rise:
                return TERMINATE, None
            else:
                rise = False
        
        if on_same_level or count_same_level > 1:
            status = HAS_LOOP
        else:
            status = TERMINATE
    
    return status, loop


def recursive_search_loop(invalid_paths, current_path, linkages,
                    all_nodes_down, all_nodes_up, node_queue):
    last_explored = current_path[-1]

    if last_explored[1] == HOME_DEPTH:
        return

    next_nodes = all_nodes_down[last_explored]['children'] + all_nodes_up[last_explored]['parent']
    if last_explored in linkages:
        next_nodes += linkages[last_explored]

    for next_node in next_nodes:
        status, loop = check_loop(next_node, current_path)
        if next_node in node_queue:
            node_queue.remove(next_node)
        
        if status == TERMINATE:
            continue
        if status == HAS_LOOP:
            invalid_paths.append(loop)
        if status == NO_LOOP:
            recursive_search_loop(invalid_paths, current_path + [next_node],
                    linkages, all_nodes_down, all_nodes_up, node_queue)


def get_nodes(fpath_tree, all_nodes_down, all_nodes_up):

    with open(fpath_tree, 'r', encoding='utf-8') as csvf:
        id_lst = [1 for _ in range(DEPTH)]
        csvReader = csv.DictReader(csvf)
        fields = csvReader.fieldnames

        for row in csvReader:
            for i in range(DEPTH):
                from_node = (row[fields[i]], i+1)
                if i < DEPTH - 1:
                    to_node = (row[fields[i+1]], i+2)
                else:
                    to_node = None

                if from_node not in all_nodes_down:
                    all_nodes_down[from_node] = {}
                    from_node_id = f"{i+1}.{id_lst[i]}"
                    all_nodes_down[from_node]['id'] = from_node_id
                    all_nodes_down[from_node]['children'] = []
                    id_lst[i] += 1

                if to_node and to_node not in all_nodes_down[from_node]['children']:
                    all_nodes_down[from_node]['children'].append(to_node)

        for node, val in all_nodes_down.items():
            for child in val['children']:
                all_nodes_up[child] = {
                    'id': all_nodes_down[child]['id'],
                    'parent': [node]
                }


def get_str_link(fpath_link, linkages, all_nodes_down):
    with open(fpath_link, 'r', encoding='utf-8') as csvf:

        invalid_nodes = []
        invalid_weight = []
        csvReader = csv.DictReader(csvf)

        for row in csvReader:
            
            depth, from_node, to_node, weight = row.values()
            is_valid = True
            if float(weight) <= 0 or float(weight) > 1:
                invalid_weight.append(tuple(row.values()))
                is_valid = False

            from_node_mod = (from_node, int(depth))
            to_node_mod = (to_node, int(depth))
            if from_node_mod not in all_nodes_down or to_node_mod not in all_nodes_down:
                invalid_nodes.append(tuple(row.values()))
                is_valid = False
            
            if not is_valid:
                continue

            if to_node_mod not in linkages:
                linkages[to_node_mod] = []
            
            linkages[to_node_mod].append(from_node_mod)
    
    return invalid_nodes, invalid_weight


def validate_linkage(linkages, all_nodes_down, all_nodes_up):
    invalid_paths = []
    node_queue = [x for x in linkages]

    while (node_queue):
        current_path = [node_queue.pop()]
        recursive_search_loop(invalid_paths, current_path, linkages,
                        all_nodes_down, all_nodes_up, node_queue)

    unique_sets = []
    invalid_paths_cleaned = []
    for loop in invalid_paths:
        if set(loop) not in unique_sets:
            unique_sets.append(set(loop))
            invalid_paths_cleaned.append(loop)

    return invalid_paths_cleaned


def process_linkage(method, fpath_tree, fpath_link, fpath_output):
     
    all_nodes_down = {}
    all_nodes_up = {}
    linkages = {}
    get_nodes(fpath_tree, all_nodes_down, all_nodes_up)
    if method == SERNUM:
        invalid_nodes, invalid_weight = convert_serial_to_string(fpath_link, linkages, all_nodes_down)
        save_linkage(linkages, fpath_output)
        linkage_struct_adjust(linkages)

    elif method == STRLNK:
        invalid_nodes, invalid_weight = get_str_link(fpath_link, linkages, all_nodes_down)

    invalid_paths = validate_linkage(linkages, all_nodes_down, all_nodes_up)
    generate_report(method, invalid_nodes, invalid_weight, invalid_paths, fpath_output)
