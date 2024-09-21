import json
import csv

DEPTH = 4
PADDING = 30
IDX_CONTENT_TAG = -2
IDX_YEAR_LEVEL = -1
FNAME_STRUCT = "structure"
FNAME_DISPLAY = "display"

def construct_json(data, depth):

    output = {}
    all_fields = data.fieldnames[:depth]

    for row in data:
        track = output

        for field in all_fields[:-2]:
            next_node = row[field]
            if next_node not in track:
                track[next_node] = {}
            track = track[next_node]

        next_node = row[all_fields[-2]]
        if next_node not in track:
            track[next_node] = []
        track[next_node].append(row[all_fields[-1]])

    return output


def construct_tree_json(data):

    output = {}
    all_fields = data.fieldnames
    cur_idx = -1
    dis_idx = 1

    for row in data:
        track = output
        next_tag = row[all_fields[IDX_CONTENT_TAG]]
        year_level = row[all_fields[IDX_YEAR_LEVEL]]
        entry = f"Y{year_level}: {next_tag: ^PADDING}"

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
        
        field = all_fields[DEPTH-1]
        next_node = row[field]
        if cur_idx == -1 or next_node not in track[cur_idx]:
            temp_cont = {next_node: {}}
            track.append(temp_cont)
            dis_idx = 1
            cur_idx += 1

        track = track[cur_idx]
        track[dis_idx] = entry
        track = track[next_node]
        field = all_fields[DEPTH]
        next_node = row[field]

        if next_node not in track:
            track[next_node] = f"{dis_idx}"
        else:
            track[next_node] += f" {dis_idx}"
        dis_idx += 1

    return output


def write_json(data, fname):
    with open(f"{fname}.json", 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))


fname = input("Enter file name: ")
with open(f"{fname}.csv", encoding='utf-8') as csvf:

    csvReader = csv.DictReader(csvf)
    struct_json = construct_json(csvReader, DEPTH)
    write_json(struct_json, FNAME_STRUCT)

with open(f"{fname}.csv", encoding='utf-8') as csvf:

    csvReader = csv.DictReader(csvf)
    tree_json = construct_tree_json(csvReader)
    write_json(tree_json, FNAME_DISPLAY)
