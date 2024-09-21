'''
This program will generate 3 json files.
The input file must be "rawData.csv".
Author: Yi Ding
Version: 1.0
'''


import json
import csv

FNAME_STRUCT = "structure"
FNAME_DISPLAY = "struct_year_level"
FNAME_PROCESS = "detailed_tree"   
FNAME = "rawData.csv"   # input file name

DEPTH = 4
IDX_CONTENT_TAG = -2
IDX_YEAR_LEVEL = -1
IDX_SUBTOPIC = 1


def construct_json(data, depth):
    ''' construct a json file for the skeleton structure
    to be imported into the figma workspace. Input
    the rows of the csv file `data` and the level of depth for
    which the tree will be constructed.
    '''

    output = {}
    all_fields = data.fieldnames[:depth]

    for row in data:
        # track the current position in the output dictionary
        track = output

        # construct first two layers
        for field in all_fields[:-2]:
            next_node = row[field]
            if next_node not in track:
                track[next_node] = {}
            track = track[next_node]

        # construct the last two layers with the value
        # being an array of last level nodes.
        next_node = row[all_fields[-2]]
        if next_node not in track:
            track[next_node] = []

        sub_content = row[all_fields[-1]]
        if sub_content not in track[next_node]:
            track[next_node].append(sub_content)

    return output


def construct_with_yl(data):
    ''' construct a json file that documents and visualizes
    all content tags with the relevant year levels in
    a hierachical structure. Input the rows of the csv file `data`
    '''

    output = {}
    all_fields = data.fieldnames
    cur_idx = -1
    dis_idx = 0
    # document all year levels for the first two level nodes
    year_level_dict = {"All levels": set()}

    for row in data:
        # track the position in the output dictionary
        track = output
        next_tag = row[all_fields[IDX_CONTENT_TAG]]
        year_level = row[all_fields[IDX_YEAR_LEVEL]]
        subtopic = row[all_fields[IDX_SUBTOPIC]]
        entry = f"Y{year_level} {next_tag}"

        # record year level for first two levels
        if subtopic not in year_level_dict:
            year_level_dict[subtopic] = set()
        year_level_dict[subtopic].add(f"Y{year_level}")
        year_level_dict['All levels'].add(f'Y{year_level}')

        # construct first two levels of nodes
        for i in range(DEPTH-2):
            field = all_fields[i]
            next_node = row[field]
            if next_node not in track:
                if i == 0:
                    track[next_node] = {}
                elif i == 1:
                    track[next_node] = []
                    cur_idx = -1
            track = track[next_node]
        
        # construct the third level, which also includes content tags
        field = all_fields[DEPTH-1]
        next_node = row[field]
        node_exists = False
        for i in range(len(track)):
            node = track[i]
            if next_node in node:
                cur_idx = i
                node_exists = True

        if not node_exists:
            temp_cont = {next_node: {}}
            track.append(temp_cont)
            cur_idx = len(track) - 1

        track = track[cur_idx]
        dis_idx = len(track)
        track[dis_idx] = entry

        # construct last level of nodes with the relevant tag index
        track = track[next_node]
        field = all_fields[DEPTH]
        next_node = row[field]

        if next_node not in track:
            track[next_node] = f"{dis_idx}"
        else:
            track[next_node] += f" {dis_idx}"
        dis_idx += 1

    # report the overall year level distribution
    track = output
    for key, val in year_level_dict.items():
        sorted_val = sorted(list(val))
        track[key] = ' '.join(sorted_val)

    return output


def detailed_tree(data, depth):
    ''' construct a json file for the knowledge that
    is easy to process for the Realus XiAn Team. Input
    the rows of the csv file `data` and the level of depth
    for which the tree will be constructed.
    '''

    output = {}
    all_fields = data.fieldnames

    for row in data:
        # track the position in the output dictionary
        track = output

        # construct all the nodes
        for field in all_fields[:depth]:
            next_node = row[field]
            if next_node not in track:
                track[next_node] = {}
            track = track[next_node]

        # record the content tag with corresponding year level
        year_level = f"Y{row[all_fields[-1]]}"
        if year_level not in track:
            track[year_level] = []
        track[year_level].append(row[all_fields[-2]])

    return output


def write_json(data, fname):
    ''' produce a json file output based on the given data
    and a specified filename `fname`.
    '''
    with open(f"{fname}.json", 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))


# driver program
with open(FNAME, 'r', encoding='utf-8') as csvf:

    csvReader = csv.DictReader(csvf)
    struct_json = construct_json(csvReader, DEPTH)
    write_json(struct_json, FNAME_STRUCT)

with open(FNAME, 'r', encoding='utf-8') as csvf:

    csvReader = csv.DictReader(csvf)
    struct_with_tag_json = construct_with_yl(csvReader)
    write_json(struct_with_tag_json, FNAME_DISPLAY)

with open(FNAME, 'r', encoding='utf-8') as csvf:

    csvReader = csv.DictReader(csvf)
    detailed_tree_json = detailed_tree(csvReader, DEPTH)
    write_json(detailed_tree_json, FNAME_PROCESS)

# all done!
print("ta daa!!!")