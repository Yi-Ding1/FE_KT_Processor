import json
import csv

DEPTH = 4
IDX_CONTENT_TAG = -2
IDX_YEAR_LEVEL = -1
IDX_SUBTOPIC = 1
FNAME_STRUCT = "structure"
FNAME_DISPLAY = "struct_year_level"
FNAME_PROCESS = "detailed_tree"
FNAME = "rawData.csv"

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

        sub_content = row[all_fields[-1]]
        if sub_content not in track[next_node]:
            track[next_node].append(sub_content)

    return output


def construct_tree_json(data):

    output = {}
    all_fields = data.fieldnames
    cur_idx = -1
    dis_idx = 0
    year_level_dict = {"All levels": set()}

    for row in data:
        track = output
        next_tag = row[all_fields[IDX_CONTENT_TAG]]
        year_level = row[all_fields[IDX_YEAR_LEVEL]]
        subtopic = row[all_fields[IDX_SUBTOPIC]]
        entry = f"Y{year_level} {next_tag}"

        if subtopic not in year_level_dict:
            year_level_dict[subtopic] = set()
        year_level_dict[subtopic].add(f"Y{year_level}")
        year_level_dict['All levels'].add(f'Y{year_level}')

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
        track = track[next_node]
        field = all_fields[DEPTH]
        next_node = row[field]

        if next_node not in track:
            track[next_node] = f"{dis_idx}"
        else:
            track[next_node] += f" {dis_idx}"
        dis_idx += 1

    track = output
    for key, val in year_level_dict.items():
        sorted_val = sorted(list(val))
        track[key] = ' '.join(sorted_val)

    return output


def detailed_tree(data, depth):
    
    output = {}
    all_fields = data.fieldnames

    for row in data:
        track = output

        for field in all_fields[:depth]:
            next_node = row[field]
            if next_node not in track:
                track[next_node] = {}
            track = track[next_node]

        year_level = f"Y{row[all_fields[-1]]}"
        if year_level not in track:
            track[year_level] = []
        track[year_level].append(row[all_fields[-2]])

    return output

def write_json(data, fname):
    with open(f"{fname}.json", 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))


with open(FNAME, 'r', encoding='utf-8') as csvf:

    csvReader = csv.DictReader(csvf)
    struct_json = construct_json(csvReader, DEPTH)
    write_json(struct_json, FNAME_STRUCT)

with open(FNAME, 'r', encoding='utf-8') as csvf:

    csvReader = csv.DictReader(csvf)
    struct_with_tag_json = construct_tree_json(csvReader)
    write_json(struct_with_tag_json, FNAME_DISPLAY)

with open(FNAME, 'r', encoding='utf-8') as csvf:

    csvReader = csv.DictReader(csvf)
    detailed_tree_json = detailed_tree(csvReader, DEPTH)
    write_json(detailed_tree_json, FNAME_PROCESS)


print("ta daa!!!")