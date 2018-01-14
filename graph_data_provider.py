__author__ = 'Zheng ZHANG'

import string
import os
from collections import Counter
import configparser
from multiprocessing import Pool
from itertools import repeat
import sys
sys.path.insert(0, '../common/')
import common
import multi_processing

config = configparser.ConfigParser()
config.read('config.ini')

""" Attention
Each time we create a local dictionary, word order will not be the same (word id is identical).
So each time the merged dictionary will be different: Each time a word may have different id in the merged dictionary.
"""

""" Meaning of local and transferred
local: (dict and encoded_text)
    Based on the original file, different local files may have different token id for the same token. 
    Because local files have never "communicate" with each other.
transferred: (word_count and encoded edges)
    Based on the merged dict (which is universal across all local dicts.), for the same token, all transferred files 
    have same id for it.
"""

""" When we lost some original information?
Remove rare tokens:
    In the 3rd (final) multiprocessing of merging transferred edges files to get a specific window size edges count.
    So information of all tokens are kept in transferred edges files and transferred word count files.
    We just ignore the information about invalid vocabulary in the final stage.
"""


def write_encoded_text_and_local_dict_for_xml(file_path, output_folder):
    """For data in /vol/corpusiles/restricted/ldc/ldc2008t25/data/xin_eng
    """
    print('Processing file %s (%s)...' % (file_path, multi_processing.get_pid()))

    word2id = dict()  # key: word <-> value: index
    id2word = dict()
    encoded_text = []
    puncs = set(string.punctuation)

    for paragraph in common.search_all_specific_nodes_in_xml_known_node_path(file_path,
                                                                             config['input data']['xml_node_path']):
        for sent in common.tokenize_informal_paragraph_into_sentences(paragraph):
            encoded_sent = []

            # update the dictionary
            for word in common.tokenize_text_into_words(sent, "WordPunct"):

                # Remove numbers
                if word.isnumeric():
                    # TODO LATER Maybe distinguish some meaningful numbers, like year
                    continue

                # Remove punctuations
                # if all(j.isdigit() or j in puncs for j in word):
                if all(c in puncs for c in word):
                    continue

                # Stem word
                word = common.stem_word(word)

                # Make all words in lowercase
                word = word.lower()

                if word not in word2id:
                    id = len(word2id)
                    word2id[word] = id
                    id2word[id] = word
                encoded_sent.append(word2id[word])
            encoded_text.append(encoded_sent)

    file_basename = multi_processing.get_file_name(file_path)
    # Write the encoded_text
    if not output_folder.endswith('/'):
        output_folder += '/'
    common.write_to_pickle(encoded_text, output_folder + "encoded_text_" + file_basename + ".pickle")
    # Write the dictionary
    common.write_dict_to_file(output_folder + "dict_" + file_basename + ".dicloc", word2id, 'str')


def write_encoded_text_and_local_dict_for_txt(file_path, output_folder):
    """For data in /vol/corpusiles/open/Wikipedia-Dumps/en/20170420/prep/ (Each line of txt file is one sentence.)
    """

    def sentences():
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                yield line

    print('Processing file %s (%s)...' % (file_path, multi_processing.get_pid()))

    word2id = dict()  # key: word <-> value: index
    id2word = dict()
    encoded_text = []
    puncs = set(string.punctuation)

    if config.getboolean("input data", "preprocessing_word"):
        for sent in sentences():
            encoded_sent = []
            # update the dictionary
            for word in common.tokenize_text_into_words(sent, "WordPunct"):
                # Remove numbers
                if config.getboolean("input data", "remove_numbers") and word.isnumeric():
                    # TODO LATER Maybe distinguish some meaningful numbers, like year
                    continue
                # Remove punctuations
                # if all(j.isdigit() or j in puncs for j in word):
                if config.getboolean("input data", "remove_punctuations"):
                    if all(c in puncs for c in word):
                        continue
                # Stem word
                if config.getboolean("input data", "stem_word"):
                    word = common.stem_word(word)
                # Make all words in lowercase
                if config.getboolean("input data", "lowercase"):
                    word = word.lower()
                if word not in word2id:
                    id = len(word2id)
                    word2id[word] = id
                    id2word[id] = word
                encoded_sent.append(word2id[word])
            encoded_text.append(encoded_sent)
    else:
        for sent in sentences():
            encoded_sent = []
            # update the dictionary
            for word in sent.strip().split(' '):
                if word not in word2id:
                    id = len(word2id)
                    word2id[word] = id
                    id2word[id] = word
                encoded_sent.append(word2id[word])
            encoded_text.append(encoded_sent)

    file_basename = multi_processing.get_file_name(file_path)
    # names like "AA", "AB", ...
    parent_folder_name = multi_processing.get_file_folder(file_path).split('/')[-1]
    # Write the encoded_text
    if not output_folder.endswith('/'):
        output_folder += '/'
    common.write_to_pickle(encoded_text,
                           output_folder + "encoded_text_" + parent_folder_name + "_" + file_basename + ".pickle")
    # Write the dictionary
    write_dict_to_file(output_folder + "dict_" + parent_folder_name + "_" + file_basename + ".dicloc", word2id)


def multiprocessing_write_local_encoded_text_and_local_dict(data_folder, file_extension, dicts_folder, process_num):
    """1st multiprocessing
    Get dictionary and encoded text of each origin file
    """
    kw = {'output_folder': dicts_folder}
    if file_extension == '.txt':
        multi_processing.master(files_getter=multi_processing.get_files_endswith_in_all_subfolders,
                                data_folder=data_folder,
                                file_extension=file_extension,
                                worker=write_encoded_text_and_local_dict_for_txt,
                                process_num=process_num,
                                **kw)
    elif file_extension == '.xml':
        multi_processing.master(files_getter=multi_processing.get_files_endswith_in_all_subfolders,
                                data_folder=data_folder,
                                file_extension=file_extension,
                                worker=write_encoded_text_and_local_dict_for_xml,
                                process_num=process_num,
                                **kw)


def merge_local_dict(dict_folder, output_folder):
    def read_first_column_file_to_build_set(file):
        d = set()
        with open(file, encoding='utf-8') as f:
            for line in f:
                (key, val) = line.rstrip('\n').split("\t")
                d.add(key)
        return d

    # Take all files in the folder starting with "dict_"
    files = [os.path.join(dict_folder, name) for name in os.listdir(dict_folder)
             if (os.path.isfile(os.path.join(dict_folder, name))
                 and name.startswith("dict_") and (name != 'dict_merged.txt'))]
    all_keys = set()
    for file in files:
        all_keys |= read_first_column_file_to_build_set(file)

    result = dict(zip(all_keys, range(len(all_keys))))
    write_dict_to_file(output_folder + 'dict_merged.txt', result)
    return result


def get_transferred_edges_files_and_transferred_word_count(local_dict_file_path, output_folder, max_window_size):
    def word_count(encoded_text, file_name):
        result = dict(Counter([item for sublist in encoded_text for item in sublist]))
        folder_name = multi_processing.get_file_folder(local_dict_file_path)
        common.write_dict_to_file(folder_name + "/word_count_" + file_name + ".txt", result, 'str')
        return result

    def get_transfer_dict_for_local_dict(local_dict, merged_dict):
        """
        local_dict:
            "hello": 37
        merged_dict:
            "hello": 52
        transfer_dict:
            37: 52
        """
        transfer_dict = {}
        for key, value in local_dict.items():
            transfer_dict[value] = merged_dict[key]
        return transfer_dict

    def write_edges_of_different_window_size(encoded_text, file_basename, output_folder, max_window_size):
        edges = {}

        # Construct edges
        for i in range(2, max_window_size + 1):
            edges[i] = []
        for encoded_sent in encoded_text:
            sentence_len = len(encoded_sent)
            for start_index in range(sentence_len - 1):
                if start_index + max_window_size < sentence_len:
                    max_range = max_window_size + start_index
                else:
                    max_range = sentence_len

                for end_index in range(1 + start_index, max_range):
                    current_window_size = end_index - start_index + 1
                    # encoded_edge = [encoded_sent[start_index], encoded_sent[end_index]]
                    encoded_edge = (encoded_sent[start_index], encoded_sent[end_index])
                    edges[current_window_size].append(encoded_edge)

        # Write edges to files
        if not output_folder.endswith('/'):
            output_folder += '/'
        for i in range(2, max_window_size + 1):
            common.write_list_to_file(
                output_folder + file_basename + "_encoded_edges_distance_{0}.txt".format(i), edges[i])

    print('Processing file %s (%s)...' % (local_dict_file_path, multi_processing.get_pid()))

    merged_dict = read_two_columns_file_to_build_dictionary_type_specified(
        file=multi_processing.get_file_folder(local_dict_file_path) + '/dict_merged.txt', key_type=str, value_type=int)
    local_dict = read_two_columns_file_to_build_dictionary_type_specified(local_dict_file_path, str, int)
    transfer_dict = get_transfer_dict_for_local_dict(local_dict, merged_dict)
    '''
    Local dict and local encoded text must be in the same folder,
    and their names should be look like below:
        local_dict_file_path:       dict_xin_eng_200410.txt
        local_encoded_text_pickle:  pickle_encoded_text_xin_eng_200410
    '''
    # Get encoded_text_pickle path according to local_dict_file_path
    local_encoded_text_pickle = local_dict_file_path.replace("dict_", "encoded_text_")[
                                :-len(config['graph']['local_dict_extension'])]
    local_encoded_text = common.read_pickle(local_encoded_text_pickle + ".pickle")
    # Translate the local encoded text with transfer_dict
    transferred_encoded_text = []
    for encoded_sent in local_encoded_text:
        transfered_encoded_sent = []
        for encoded_word in encoded_sent:
            transfered_encoded_sent.append(transfer_dict[encoded_word])
        transferred_encoded_text.append(transfered_encoded_sent)

    file_name = multi_processing.get_file_name(local_dict_file_path).replace("dict_", "")
    # Word count
    word_count(transferred_encoded_text, file_name)
    # Write edges files of different window size based on the transfered encoded text
    write_edges_of_different_window_size(transferred_encoded_text, file_name, output_folder, max_window_size)


def multiprocessing_write_transferred_edges_files_and_transferred_word_count(local_dicts_folder, edges_folder,
                                                                             max_window_size, process_num):
    """2nd multiprocessing
    Build a transfer dict (by local dictionary and merged dictionary)
    and write a new encoded text by using the transfer dict.
    """
    kw = {'output_folder': edges_folder, 'max_window_size': max_window_size}
    multi_processing.master(files_getter=multi_processing.get_files_endswith,
                            data_folder=local_dicts_folder,
                            file_extension=config['graph']['local_dict_extension'],
                            worker=get_transferred_edges_files_and_transferred_word_count,
                            process_num=process_num,
                            **kw)


def merge_transferred_word_count(word_count_folder, output_folder):
    # TODO LATER too slow, improve this part
    files = get_files_startswith(word_count_folder, "word_count_")
    c = Counter()
    for file in files:
        counter_temp = common.read_two_columns_file_to_build_dictionary_type_specified(file, int, int)
        c += counter_temp
    common.write_dict_to_file(output_folder + "word_count_all.txt", dict(c), 'str')
    return dict(c)


def write_valid_vocabulary(merged_word_count_path, output_path, min_count, max_vocab_size):
    # TODO valid_vocabulary should be a dict. No need to write as list and then read list changing to dict.
    # TODO LATER maybe it's not the fastest way to sort dict.
    merged_word_count = read_two_columns_file_to_build_dictionary_type_specified(file=merged_word_count_path,
                                                                                 key_type=str, value_type=int)

    valid_word_count = {}
    for word_id, count in merged_word_count.items():
        if count >= min_count:
            valid_word_count[word_id] = count
    if max_vocab_size and (max_vocab_size != 'None'):
        if int(max_vocab_size) < len(valid_word_count):
            valid_vocabulary = list(sorted(valid_word_count, key=valid_word_count.get, reverse=True))[
                               :int(max_vocab_size)]
        else:
            valid_vocabulary = list(valid_word_count.keys())
    else:
        valid_vocabulary = list(valid_word_count.keys())

    common.write_simple_list_to_file(output_path, valid_vocabulary)
    return valid_vocabulary


def get_counted_edges_worker(edges_files_paths, valid_vocabulary_path, output_folder):
    def counters_yielder():
        def read_edges_file_with_respect_to_valid_vocabulary(file_path, valid_vocabulary_dict):
            d = []
            with open(file_path) as f:
                for line in f:
                    (first, second) = line.rstrip('\n').split("\t")
                    if (first in valid_vocabulary_dict) and (second in valid_vocabulary_dict):
                        d.append((first, second))
            return d

        valid_vocabulary = dict.fromkeys(read_valid_vocabulary(file_path=valid_vocabulary_path))
        for file in edges_files_paths:
            yield Counter(dict(Counter(
                read_edges_file_with_respect_to_valid_vocabulary(file_path=file, valid_vocabulary_dict=valid_vocabulary))))


    total = len(edges_files_paths)
    print(total, "files to be counted.")
    count = 1
    counted_edges = Counter(dict())
    for c in counters_yielder():
        counted_edges += c
        print('%i/%i files processed.' % (count, total), end='\r', flush=True)
        count += 1
    # The result could be counted edges of several files (i.e. len(edges_files_paths) >= 1). Using the first file name
    # as part of the pickle file name is just to make sure the pickle name is unique (pickle file couldn't be
    # overwritten).
    common.write_to_pickle(counted_edges,
                           output_folder + multi_processing.get_file_name(edges_files_paths[0]) + ".pickle")


def multiprocessing_merge_edges_count_of_a_specific_window_size(window_size, process_num,
                                                                min_count=config['graph']['min_count'],
                                                                dicts_folder=config['graph'][
                                                                    'dicts_and_encoded_texts_folder'],
                                                                edges_folder=config['graph']['edges_folder'],
                                                                output_folder=config['graph']['graph_folder'],
                                                                max_vocab_size=config['graph']['max_vocab_size'],
                                                                already_existed_window_size=None):
    def counted_edges_from_worker_yielder(paths):
        for path in paths:
            yield Counter(common.read_pickle(path))

    def get_counted_edges(files, process_num=process_num):
        # Each thread processes several target edges files and save their counted_edges.
        files_size = len(files)
        num_tasks = files_size // int(config['graph']['safe_files_number_per_processor'])
        if num_tasks < process_num:
            num_tasks = process_num
        if files_size <= num_tasks:  # extreme case: #files less than #tasks => use only one processor to handle all.
            num_tasks = 1
            process_num = 1
        files_list = multi_processing.chunkify(lst=files, n=num_tasks)
        p = Pool(process_num)
        if (max_vocab_size == 'None') or (not max_vocab_size):
            worker_valid_vocabulary_path = dicts_folder + 'valid_vocabulary_min_count_' + str(min_count) + '.txt'
        else:
            worker_valid_vocabulary_path = dicts_folder + 'valid_vocabulary_min_count_' + str(
                min_count) + '_vocab_size_' + str(
                max_vocab_size) + '.txt'
        worker_output_path = edges_folder
        p.starmap(get_counted_edges_worker,
                  zip(files_list, repeat(worker_valid_vocabulary_path), repeat(worker_output_path)))
        p.close()
        p.join()
        print('All sub-processes done.')

        # Merge all counted_edges from workers and get the final result.
        counted_edges_paths = multi_processing.get_files_endswith(data_folder=edges_folder, file_extension='.pickle')
        count = 1
        counted_edges = Counter(dict())
        for c in counted_edges_from_worker_yielder(paths=counted_edges_paths):
            counted_edges += c
            print('%i/%i files processed.' % (count, len(files_list)), end='\r', flush=True)
            count += 1

        # Remove all counted_edges from workers.
        for file_path in counted_edges_paths:
            print('Remove file %s' % file_path)
            os.remove(file_path)

        return counted_edges

    # Get all target edges files' paths to be merged and counted.
    files = {}
    for i in range(2, window_size + 1):
        files_of_specific_distance = multi_processing.get_files_endswith(edges_folder,
                                                                         "_encoded_edges_distance_{0}.txt".format(i))
        if not files_of_specific_distance:
            print('No encoded edges file of window size ' + str(window_size) + '. Reset window size to ' + str(
                i - 1) + '.')
            window_size = i - 1
            break
        else:
            files[i] = files_of_specific_distance

    # Generate counted edges of different window sizes in a stepwise way.
    if not already_existed_window_size:
        # No encoded edges count already existed, calculate them from distance 2 to distance size.
        counted_edges_of_specific_window_size = None
        start_distance = 2
    else:
        already_existed_counted_edges_path = output_folder + "encoded_edges_count_window_size_" \
                                             + str(already_existed_window_size) + ".txt"
        d = {}
        with open(already_existed_counted_edges_path) as f:
            for line in f:
                (first, second, count) = line.rstrip('\n').split("\t")
                d[(first, second)] = int(count)
        counted_edges_of_specific_window_size = Counter(d)
        start_distance = already_existed_window_size + 1
    for i in range(start_distance, window_size + 1):
        counted_edges_of_distance_i = get_counted_edges(files[i])
        if i == 2:
            # counted edges of window size 2 = counted edges of distance 2
            counted_edges_of_specific_window_size = counted_edges_of_distance_i
        else:
            # counted edges of window size n (n>=3) = counted edges of window size n-1 + counted edges of distance n
            counted_edges_of_specific_window_size += counted_edges_of_distance_i
        common.write_dict_to_file(output_folder + "encoded_edges_count_window_size_" + str(i) + ".txt",
                                  counted_edges_of_specific_window_size, 'tuple')

    return counted_edges_of_specific_window_size


def write_dict_to_file(file_path, dictionary):
    with open(file_path, 'w', encoding='utf-8') as f:
        for key, value in dictionary.items():
            f.write('%s\t%s\n' % (key, value))


def read_two_columns_file_to_build_dictionary_type_specified(file, key_type, value_type):
    d = {}
    with open(file, encoding='utf-8') as f:
        for line in f:
            (key, val) = line.rstrip('\n').split("\t")
            d[key_type(key)] = value_type(val)
        return d


def get_index2word(file, key_type=int, value_type=str):
    """ATTENTION
    This function is different from what in graph_data_provider.
    Here, key is id and token is value, while in graph_data_provider, token is key and id is value.
    """
    d = {}
    with open(file, encoding='utf-8') as f:
        for line in f:
            (key, val) = line.rstrip('\n').split("\t")
            d[key_type(val)] = value_type(key)
        return d


def get_files_startswith(data_folder, starting):
    # Reason to add the third condition to verify files' names are not equal to 'word_count_all.txt': In case before
    # executing the code, dicts_and_encoded_texts_folder folder already has 'word_count_all.txt' file, this function
    # considers the previous word_count_all file as a normal local dict file.
    files = [os.path.join(data_folder, name) for name in os.listdir(data_folder)
             if (os.path.isfile(os.path.join(data_folder, name))
                 and name.startswith(starting)
                 and (name != 'word_count_all.txt'))]
    return files


def read_valid_vocabulary(file_path):
    result = []
    with open(file_path) as f:
        for line in f:
            line_element = line.rstrip('\n')
            result.append(line_element)
    return result


def prepare_intermediate_data(data_folder, file_extension,
                              max_window_size,
                              process_num,
                              dicts_folder=config['graph']['dicts_and_encoded_texts_folder'],
                              edges_folder=config['graph']['edges_folder'],
                              min_count=config['graph']['min_count'],
                              max_vocab_size=config['graph']['max_vocab_size']):
    multiprocessing_write_local_encoded_text_and_local_dict(data_folder, file_extension, dicts_folder, process_num)
    merge_local_dict(dict_folder=dicts_folder, output_folder=dicts_folder)
    multiprocessing_write_transferred_edges_files_and_transferred_word_count(dicts_folder, edges_folder,
                                                                             max_window_size, process_num)
    merge_transferred_word_count(word_count_folder=dicts_folder, output_folder=dicts_folder)
    if (max_vocab_size == 'None') or (not max_vocab_size):
        valid_vocabulary_name = dicts_folder + 'valid_vocabulary_min_count_' + min_count + '.txt'
    else:
        valid_vocabulary_name = dicts_folder + 'valid_vocabulary_min_count_' + str(min_count) + '_vocab_size_' + str(
            max_vocab_size) + '.txt'
    write_valid_vocabulary(
        merged_word_count_path=dicts_folder + 'word_count_all.txt',
        output_path=valid_vocabulary_name,
        min_count=int(min_count),
        max_vocab_size=max_vocab_size)


def filter_edges(min_count,
                 old_encoded_edges_count_path,
                 max_vocab_size=config['graph']['max_vocab_size'],
                 new_valid_vocabulary_folder=config['graph']['dicts_and_encoded_texts_folder'],
                 merged_word_count_path=config['graph']['dicts_and_encoded_texts_folder'] + 'word_count_all.txt',
                 output_folder=config['graph']['graph_folder']):
    """
    ATTENTION 1:
    This function should only be used when 'encoded_edges_count_window_size_n.txt' already exists (But when calculating
    this, 'max_vocab_size' has been set to 'None' in 'write_valid_vocabulary' function).
    If 'max_vocab_size' has already been well set, there's no need to use this function.
    Because 'encoded_edges_count_window_size_n.txt' has been generated with considering 'min_count' and 'max_vocab_size'

    ATTENTION 2:
    'min_count' should be no bigger than the previous one.
    """
    new_valid_vocabulary_path = new_valid_vocabulary_folder + 'valid_vocabulary_min_count_' + str(
        min_count) + '_vocab_size_' + str(max_vocab_size) + '.txt'
    write_valid_vocabulary(
        merged_word_count_path=merged_word_count_path,
        output_path=new_valid_vocabulary_path,
        min_count=min_count,
        max_vocab_size=max_vocab_size)

    valid_vocabulary = dict.fromkeys(read_valid_vocabulary(file_path=new_valid_vocabulary_path))
    filtered_edges = {}
    for line in common.read_file_line_yielder(old_encoded_edges_count_path):
        (source, target, weight) = line.split("\t")
        if (source in valid_vocabulary) and (target in valid_vocabulary):
            filtered_edges[(source, target)] = int(weight)
    common.write_dict_to_file(output_folder + "encoded_edges_count_filtered.txt", filtered_edges, 'tuple')
    return filtered_edges


def reciprocal_for_edges_weight(old_encoded_edges_count_path, output_folder=config['graph']['graph_folder']):
    reciprocal_weight_edges = {}
    for line in common.read_file_line_yielder(old_encoded_edges_count_path):
        (source, target, weight) = line.split("\t")
        # reciprocal_weight_edges[(source, target)] = 1./int(weight)
        reciprocal_weight_edges[(source, target)] = 1
    # output_name = multi_processing.get_file_name(old_encoded_edges_count_path).split('.txt')[0]+'_reciprocal.txt'
    output_name = multi_processing.get_file_name(old_encoded_edges_count_path).split('.txt')[0]+'_allONE.txt'
    common.write_dict_to_file(output_folder + output_name, reciprocal_weight_edges, 'tuple')
    return reciprocal_weight_edges


def merge_encoded_edges_count_for_undirected_graph(old_encoded_edges_count_path,
                                                   output_folder=config['graph']['graph_folder']):
    """e.g.
    In old encoded edges count file:
        17  57  8
        ...
        57  17  2
    return:
        17  57  10 or 57   17  10 (only one of them will appear in the file.)
    """
    merged_weight_edges = {}
    for line in common.read_file_line_yielder(old_encoded_edges_count_path):
        (source, target, weight) = line.split("\t")
        if (target, source) in merged_weight_edges:
            # edge[source][target] inverse edge edge[target][source] already put into the merged_weight_edges
            merged_weight_edges[(target, source)] += int(weight)
        else:
            # The first time merged_weight_edges meets edge[source][target] or its inverse edge edge[target][source]
            merged_weight_edges[(source, target)] = int(weight)
    output_name = multi_processing.get_file_name(old_encoded_edges_count_path).split('.txt')[0] + '_undirected.txt'
    common.write_dict_to_file(output_folder + output_name, merged_weight_edges, 'tuple')
    return merged_weight_edges


if __name__ == '__main__':
    # # One core test (local dictionaries ready)
    # # xml
    # write_encoded_text_and_local_dict_for_xml("data/test_input_data/test_for_graph_builder_igraph_multiprocessing.xml", 'data/dicts_and_encoded_texts/', "./DOC/TEXT/P")
    # merged_dict = merge_local_dict(dict_folder='data/dicts_and_encoded_texts/', output_folder='data/dicts_and_encoded_texts/')
    # get_local_edges_files_and_local_word_count('data/dicts_and_encoded_texts/dict_test_for_graph_builder_igraph_multiprocessing.dicloc',
    #                                            merged_dict, 'data/edges/', max_window_size=10, local_dict_extension='.dicloc')
    # merge_transferred_word_count(word_count_folder='data/dicts_and_encoded_texts/', output_folder='data/dicts_and_encoded_texts/')
    # multiprocessing_merge_edges_count_of_a_specific_window_size(edges_folder='data/edges/', window_size=4, output_folder='data/')

    # # txt
    # write_encoded_text_and_local_dict_for_txt(
    #     file_path="data/training data/Wikipedia-Dumps_en_20170420_prep/AA/wiki_01.txt",
    #     output_folder='output/intermediate data/dicts_and_encoded_texts')


    # # Multiprocessing test
    # # xml
    # prepare_intermediate_data(xml_data_folder='/Users/zzcoolj/Code/GoW/data/test_input_data/xin_eng_for_test',
    #                     xml_file_extension='.xml',
    #                     xml_node_path='./DOC/TEXT/P',
    #                     dicts_folder='data/dicts_and_encoded_texts/',
    #                     local_dict_extension='.dicloc',
    #                     edges_folder='data/edges/',
    #                     max_window_size=3,
    #                     process_num=3)
    # merge_transferred_word_count(word_count_folder='data/dicts_and_encoded_texts/', output_folder='data/dicts_and_encoded_texts/')
    # multiprocessing_merge_edges_count_of_a_specific_window_size(edges_folder='data/edges/', window_size=4, output_folder='data/')

    # txt
    # TODO NOW check the guess below
    '''
    If intermediate data remains unchanged, running multiprocessing_merge_edges_count_of_a_specific_window_size several
    times won't change the result: only the line order in the encoded edges file changed.
    
    If intermediate data changed, running multiprocessing_merge_edges_count_of_a_specific_window_size won't get the same
    result, even the number of lines in encoded edges file changes. It's normal that the value of lines changes because
    of the different merged_dict (the id for the same token changes each time). But it's abnormal that #lines changes.
    The guess is that, #lines won't change if we set max_vocab_size to None. But it changes when we set it to a 
    specific value (e.g. 10000). Because if we order the tokens by their frequency, around that value's position, there
    are more than one token which has the same frequency. Each time, the "last" several valid tokens are different.
    '''
    # prepare_intermediate_data(data_folder='data/training data/Wikipedia-Dumps_en_20170420_prep/',
    #                           file_extension='.txt',
    #                           max_window_size=10,
    #                           process_num=4,
    #                           max_vocab_size=10000)

    # multiprocessing_merge_edges_count_of_a_specific_window_size(window_size=10, process_num=4, max_vocab_size=10000, already_existed_window_size=7)

    # get undirected edges count for all file
    for i in range(2, 11):
        file_path = config['graph']['graph_folder'] + 'encoded_edges_count_window_size_' + str(i) + '.txt'
        merge_encoded_edges_count_for_undirected_graph(old_encoded_edges_count_path=file_path)

# TODO LATER Add weight according to word pair distance in write_edges_of_different_window_size function
# TODO NOW This program now allows self-loop, add one option for that.
