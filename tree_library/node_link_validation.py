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
    """ outputs a .txt report that explains all the errors in the node links file
    """
    
    f = open(f"{fpath_output}/{FNAME_REP}", "w")
    if method == SERNUM:
        f.write("Method: conversion for serial to string." + '\n')
    elif method == STRLNK:
        f.write("Method: check validity of node names." + '\n')
    
    # output the pairs of nodes that do not match with content in the tree design
    f.write('-'*N_LENGTH + '\n')
    if invalid_nodes:
        f.write(f"{len(invalid_nodes)} pairs of nodes were not found in the tree." + '\n')
        f.write("from_node   to_node     weight" + '\n')
        for node in invalid_nodes:
            f.write("{:<11s} {:<11s} {}".format(node[0], node[1], node[2]) + '\n')
    else:
        f.write("All nodes seem to be valid." + '\n')
    
    # output the weightings that are not within the range (0,1]
    f.write('-'*N_LENGTH + '\n')
    if invalid_weight:
        f.write(f"{len(invalid_weight)} weightings were unreasonable." + '\n')
        f.write("from_node   to_node     weight" + '\n')
        for node in invalid_weight:
            f.write("{:<11s} {:<11s} {}".format(node[0], node[1], node[2]) + '\n ')
    else:
        f.write("All weightings seem to be valid." + '\n')
    
    # output the loops found
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
    """ This function produces a linkage dictionary structure based
    on the given serial number file. Return the list of nodes with
    invalid names and list of nodes with invalid weightings.
    """
    invalid_nodes = []
    invalid_weight = []

    with open(fpath_link, 'r', encoding='utf-8') as csvf:

        csvReader = csv.DictReader(csvf)
        for row in csvReader:

            # store linkages that are valid
            from_node, to_node, weight = row.values()
            is_valid = [False, False]

            # range check for weighting
            if float(weight) <= 0 or float(weight) > 1:
                invalid_weight.append(tuple(row.values()))
                continue

            # existence check for node serial number
            for node, val in all_nodes_down.items():
                if from_node == val['id']:
                    from_node_mod = (node[0], weight)
                    is_valid[0] = True
                elif to_node == val['id']:
                    to_node_mod = node
                    is_valid[1] = True
            
            # store nodes with invalid names
            if not is_valid[0] or not is_valid[1]:
                invalid_nodes.append(tuple(row.values()))
                continue

            # create the linkages dictionary structure
            if to_node_mod not in linkages:
                linkages[to_node_mod] = []
            linkages[to_node_mod].append(from_node_mod)
            
    return invalid_nodes, invalid_weight


def linkage_struct_adjust(linkages):
    """ This function adjusts the linkage file for the
    serial number method.
    """
    for key, val in linkages.items():
        # change the value from weighting to depth
        depth = key[1]
        temp = [(x[0], depth) for x in val]
        linkages[key] = temp


def save_linkage(linkages, fpath_output):
    """ This function saves all the linkages to .csv file when
    serial number method is used.
    """
    header = ['node_depth', 'from_node', 'to_node', 'weight']
    data = [header]

    # create a 2d array for the csv file
    for to_node, from_nodes in linkages.items():
        tn_name, tn_depth = to_node
        for from_node in from_nodes:
            fn_name, weight = from_node
            new_row = [tn_depth, fn_name, tn_name, weight]
            data.append(new_row)

    # output the csv file
    with open(f"{fpath_output}/{FNAME_LNK}", 'w', encoding='utf-8', newline='') as csvf:
        csvwriter = csv.writer(csvf)
        csvwriter.writerows(data)


def check_loop(next_node, current_path):
    """ Algorithm for checking whether a path contains
    any loops. Return a status that represents
    what needs to be done for the current path.
    """
    loop = None

    # case for when a new node is added to path
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
            # compute how many nodes are at the lowest depths
            if item[1] != lowest_depth:
                on_same_level = False
            else:
                count_same_level += 1

            # detect sharp turns
            if item[1] > prev_depth:
                rise = True
            elif item[1] < prev_depth and rise:
                return TERMINATE, None
            else:
                rise = False
        
        # positive when the loop is formed when the lowest depth has > 1 nodes
        if on_same_level or count_same_level > 1:
            status = HAS_LOOP
        else:
            status = TERMINATE
    
    return status, loop


def recursive_search_loop(invalid_paths, current_path, linkages,
                    all_nodes_down, all_nodes_up, node_queue):
    """ Recursively searches for any loops in the a path.
    """
    last_explored = current_path[-1]

    # base case where the root node is reached
    if last_explored[1] == HOME_DEPTH:
        return

    # create a list of all nodes to search for
    next_nodes = all_nodes_down[last_explored]['children'] + all_nodes_up[last_explored]['parent']
    if last_explored in linkages:
        next_nodes += linkages[last_explored]

    for next_node in next_nodes:
        # check whether a loop forms
        status, loop = check_loop(next_node, current_path)
        if next_node in node_queue:
            node_queue.remove(next_node)
        
        # decide the action for the current path that is being searched
        if status == TERMINATE:
            continue
        if status == HAS_LOOP:
            invalid_paths.append(loop)
        if status == NO_LOOP:
            recursive_search_loop(invalid_paths, current_path + [next_node],
                    linkages, all_nodes_down, all_nodes_up, node_queue)


def get_nodes(fpath_tree, all_nodes_down, all_nodes_up):
    """ gets all the parent, children node relationships based
    on the a given tree design file
    """
    with open(fpath_tree, 'r', encoding='utf-8') as csvf:
        id_lst = [1 for _ in range(DEPTH)]
        csvReader = csv.DictReader(csvf)
        fields = csvReader.fieldnames
        
        # create a dictionary of parent: children relationship
        for row in csvReader:
            for i in range(DEPTH):
                from_node = (row[fields[i]], i+1)
                if i < DEPTH - 1:
                    to_node = (row[fields[i+1]], i+2)
                else:
                    to_node = None

                # initialize nodes to have id
                if from_node not in all_nodes_down:
                    all_nodes_down[from_node] = {}
                    from_node_id = f"{i+1}.{id_lst[i]}"
                    all_nodes_down[from_node]['id'] = from_node_id
                    all_nodes_down[from_node]['children'] = []
                    id_lst[i] += 1

                # allocate child node
                if to_node and to_node not in all_nodes_down[from_node]['children']:
                    all_nodes_down[from_node]['children'].append(to_node)

        # reverse the all nodes down to create a dictionary of child: parent relationship
        for node, val in all_nodes_down.items():
            for child in val['children']:
                all_nodes_up[child] = {
                    'id': all_nodes_down[child]['id'],
                    'parent': [node]
                }


def get_str_link(fpath_link, linkages, all_nodes_down):
    """ This function extracts the linkages from the given
    written string linkage file and then return the pairs
    of nodes with invalid names or weightings.
    """
    with open(fpath_link, 'r', encoding='utf-8') as csvf:

        invalid_nodes = []
        invalid_weight = []
        csvReader = csv.DictReader(csvf)

        for row in csvReader:
            depth, from_node, to_node, weight = row.values()
            is_valid = True

            # range check for weighting
            if float(weight) <= 0 or float(weight) > 1:
                invalid_weight.append(tuple(row.values()))
                is_valid = False

            # existence check for node names
            from_node_mod = (from_node, int(depth))
            to_node_mod = (to_node, int(depth))
            if from_node_mod not in all_nodes_down or to_node_mod not in all_nodes_down:
                invalid_nodes.append(tuple(row.values()))
                is_valid = False
            
            # skip the linkage construction if validity is false
            if not is_valid:
                continue
            
            # store the new linkages
            if to_node_mod not in linkages:
                linkages[to_node_mod] = []
            linkages[to_node_mod].append(from_node_mod)
    
    return invalid_nodes, invalid_weight


def validate_linkage(linkages, all_nodes_down, all_nodes_up):
    """ This funciton validates all the linkages by finding loops
    and then return a list of paths that create loops.
    """
    invalid_paths = []
    node_queue = [x for x in linkages]

    # inspect all the nodes that could form loops
    while (node_queue):
        current_path = [node_queue.pop()]
        recursive_search_loop(invalid_paths, current_path, linkages,
                        all_nodes_down, all_nodes_up, node_queue)

    # filter out same paths
    unique_sets = []
    invalid_paths_cleaned = []
    for loop in invalid_paths:
        if set(loop) not in unique_sets:
            unique_sets.append(set(loop))
            invalid_paths_cleaned.append(loop)

    return invalid_paths_cleaned


def process_linkage(method, fpath_tree, fpath_link, fpath_output):
    """ driver program for processing the node linkage files
    """

    all_nodes_down = {}
    all_nodes_up = {}
    linkages = {}
    get_nodes(fpath_tree, all_nodes_down, all_nodes_up)

    # if serial number is used, conversion of linkage file would be required
    if method == SERNUM:
        invalid_nodes, invalid_weight = convert_serial_to_string(fpath_link, linkages, all_nodes_down)
        save_linkage(linkages, fpath_output)
        linkage_struct_adjust(linkages)
    elif method == STRLNK:
        invalid_nodes, invalid_weight = get_str_link(fpath_link, linkages, all_nodes_down)

    # find loops and produce a report showing all errors
    invalid_paths = validate_linkage(linkages, all_nodes_down, all_nodes_up)
    generate_report(method, invalid_nodes, invalid_weight, invalid_paths, fpath_output)

