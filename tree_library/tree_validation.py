'''
This program will generate a report that describes potential errors
in the knowledge tree.
Author: Yi Ding
Version: 1.0
'''

import csv

SIM_THRESHOLD = 0.5  # control the standard for similarity
DEPTH = 4
COURSES = {
    "Mathematics": "",
    "Mathematics (General Level)": " GM",
    "Mathematics (Standard Level)": " MM",
    "Mathematics (Advanced Level)": " SM"
}


def compare(master_data, compared_data, all_nodes, fpath_output):
    """ make comparison between current study design and knowledge tree
    """

    # count frequency of content tags and search for differences
    master_freq = {x: master_data.count(x) for x in master_data}
    compared_freq = {x: compared_data.count(x) for x in compared_data}
    missing_data = set(master_data) - set(compared_data)
    extra_data = set(compared_data) - set(master_data)
    common_data = set(master_data) & set(compared_data)
    discrepancy = {}

    # calculate similarity score for nodes' names
    suggestions = get_similarity_pairs(list(missing_data), list(extra_data))
    sus_nodes = find_sus_nodes(all_nodes)
    
    # search for discrepancies that is content appeared more than once
    for item in common_data:
        diff = compared_freq[item] - master_freq[item]
        if diff:
            discrepancy[item] = diff

    # generate an output report for all the errors
    generate_report(missing_data, extra_data, discrepancy, suggestions, sus_nodes, fpath_output)


def levenshtein_distance(str1, str2):
    """ compute the distance for two strings
    """
    # Create a matrix to hold the distances
    len_str1 = len(str1)
    len_str2 = len(str2)
    
    # Initialize matrix of zeros with dimensions (len_str1+1) x (len_str2+1)
    dp = [[0 for _ in range(len_str2 + 1)] for _ in range(len_str1 + 1)]
    
    # Initialize the matrix with base case values
    for i in range(len_str1 + 1):
        dp[i][0] = i  # The cost of converting str1[:i] to an empty string
    for j in range(len_str2 + 1):
        dp[0][j] = j  # The cost of converting an empty string to str2[:j]

    # Fill the matrix with Levenshtein distances
    for i in range(1, len_str1 + 1):
        for j in range(1, len_str2 + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]  # No cost if characters match
            else:
                dp[i][j] = min(
                    dp[i - 1][j],    # Deletion
                    dp[i][j - 1],    # Insertion
                    dp[i - 1][j - 1] # Substitution
                ) + 1
    
    return dp[len_str1][len_str2]


def levenshtein_ratio(str1, str2):
    """ compute a normalized similarity score for two strings
    """
    # Calculate the Levenshtein distance
    lev_distance = levenshtein_distance(str1, str2)
    
    # Calculate the ratio (normalized similarity score)
    max_len = max(len(str1), len(str2))
    
    if max_len == 0:
        return 1.0  # Both strings are empty, considered identical
    
    return 1 - lev_distance / max_len


def get_similarity_pairs(list1, list2, threshold=SIM_THRESHOLD):
    """ go through all pairs of nodes and find content tags with similar names.
    Note: this would only give the closest content tag.
    """
    pairs = []
    used_list1 = set()
    used_list2 = set()

    # iterate through all pairs of nodes
    while len(used_list1) < len(list1) and len(used_list2) < len(list2):
        best_pair = None
        best_score = 0
        
        for i, (key1, str1) in enumerate(list1):
            if i in used_list1:
                continue
            for j, (key2, str2) in enumerate(list2):
                if j in used_list2:
                    continue
                
                # First check if the keys (str1 part) match exactly
                if key1 == key2:
                    # If the keys match, compare str2 for similarity
                    score = levenshtein_ratio(str1, str2)
                    
                    if score > best_score and score >= threshold:
                        best_score = score
                        best_pair = (i, j)
        
        if best_pair:
            i, j = best_pair
            # Append the matching pair from both lists
            pairs.append((list1[i], list2[j]))
            used_list1.add(i)
            used_list2.add(j)
        else:
            # If no pair meets the threshold, break the loop
            break
    
    return pairs


def find_similar(node_lst, threshold=SIM_THRESHOLD):
    """ find nodes with similar names to prevent miss spelling.
    Return pair of nodes with similar names.
    """
    len_row = len(node_lst)
    all_sus_nodes = []

    # find node names with high similarity
    for i in range(len_row):
        for j in range(i+1, len_row):
            if levenshtein_ratio(node_lst[i][1], node_lst[j][1]) >= threshold:
                all_sus_nodes.append((node_lst[i], node_lst[j]))

    return all_sus_nodes


def find_sus_nodes(all_nodes):
    """ iterate through each layer of the knowledge tree
    and then find nodes with similar names. Return the
    pairs of similar nodes in each layer.
    """

    sus_node_pairs = []
    node_storage = [set() for _ in range(DEPTH)]
    
    # store all nodes in their respective layer
    for row in all_nodes:
        for i in range(DEPTH):
            node_storage[i].add((i, row[i]))
    
    # iterate through each layer to find similar nodes
    for node_set in node_storage:
        node_lst = list(node_set)
        suggestions = find_similar(node_lst, 0.9)
        sus_node_pairs += suggestions

    return sus_node_pairs


def generate_report(missing_data, extra_data, discrepancy, suggestions, sus_nodes, fpath_output):
    """ produce a .txt report that reports the errors in the knowledge tree
    """
    f = open(fpath_output, "w")
    if suggestions:
        N_LENGTH = len(max(suggestions, key=lambda x: len(x[1][1]))[1][1]) * 2 + 12
    else:
        N_LENGTH = 100

    # output tags that are missing from the knowledge tree
    f.write("-" * N_LENGTH + '\n')
    if missing_data:
        f.write(f"{len(missing_data)} content tags are missing from the knowledge tree:" + '\n')
        for key, value in list(missing_data):
            f.write("{:<8}{}".format(key, value) + '\n')
    else:
        f.write("No missing data found." + '\n')
    
    # output tags that did not appear in the knowledge tree
    f.write("-" * N_LENGTH + '\n')
    if extra_data:
        f.write(f"{len(extra_data)} content tags did not appear in current study design:" + '\n')
        for key, value in list(extra_data):
            f.write("{:<8}{}".format(key, value) + '\n')
    else:
        f.write("No extra data found." + '\n')
    
    # output tags that appeared more than once
    f.write("-" * N_LENGTH + '\n')
    if discrepancy:
        f.write(f"{len(discrepancy)} content tags appeared more than once." + '\n')
        for content, freq in discrepancy.items():
            f.write("{:<8}{}".format(content[0], content[1]) + '\n')
    else:
        f.write("No more discrepancies found." + '\n')

    # output suggestions for fixes
    f.write("-" * N_LENGTH + '\n')
    if suggestions:
        padding = len(max(suggestions, key=lambda x: len(x[1][1]))[1][1])
        f.write(f"Below are some suggestions for fixes:" + '\n')
        for str1, str2 in suggestions:
            f.write(f"{str1[0]}: {str2[1].ljust(padding)} --> {str1[1]}" + '\n')
    else:
        f.write("No available suggestions." + '\n')

    # output warnings for nodes with high level of similarity for name
    f.write("-" * N_LENGTH + '\n')
    if sus_nodes:
        padding = len(max(sus_nodes, key=lambda x: len(x[1][1]))[1][1])
        f.write(f"Below are some nodes with similar names:" + '\n')
        for node1, node2 in sus_nodes:
            f.write(f"Depth {node1[0]}: {node1[1].ljust(padding)} <--> {node2[1]}" + '\n')
    else:
        f.write("All nodes seemed to be alright." + '\n')
    
    f.write("-" * N_LENGTH + '\n')
    f.close()


def validate_tree(fpath_keys, fpath_master, fpath_compared, fpath_output):
    """ driver program for validation the design of the JSON tree
    """
    master_data = []
    compared_data = []
    all_nodes = set()
    keys = []

    # find all the topics the user is working on
    with open(fpath_keys, 'r', encoding='utf-8') as csvf:

        csvReader = csv.DictReader(csvf)
        year_level, topic = csvReader.fieldnames
        for row in csvReader:
            keys.append((row[year_level], row[topic]))

    # read the given current study design
    with open(fpath_master, 'r', encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        course, rawgrade, area, topic, sub_topic, content = csvReader.fieldnames[:6]
        for row in csvReader:
            grade = f"{row[rawgrade]}{COURSES[row[course]]}"
            row_key = (grade, row[topic])
            if row_key in keys:
                master_data.append((grade, row[content]))
    
    # read the knowledge tree design file
    with open(fpath_compared, 'r', encoding='utf-8') as csvf:
        
        csvReader = csv.DictReader(csvf)
        fields = csvReader.fieldnames
        
        for row in csvReader:
            compared_data.append((row[fields[-1]], row[fields[-2]]))
            all_nodes.add(tuple(row[fields[x]] for x in range(DEPTH)))

    # compare the current study design and knowledge tree design
    compare(master_data, compared_data, all_nodes, fpath_output)

