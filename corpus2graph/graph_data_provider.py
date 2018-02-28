__author__ = 'Zheng ZHANG'

import string
import os
import warnings
from collections import Counter
from multiprocessing import Pool
from . import util
from . import multi_processing

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









# def get_index2word(file, key_type=int, value_type=str):
#     """ATTENTION
#     This function is different from what in graph_data_provider.
#     Here, key is id and token is value, while in graph_data_provider, token is key and id is value.
#     """
#     d = {}
#     with open(file, encoding='utf-8') as f:
#         for line in f:
#             (key, val) = line.rstrip('\n').split("\t")
#             d[key_type(val)] = value_type(key)
#         return d
#
#


# def merge_encoded_edges_count_for_undirected_graph(old_encoded_edges_count_path,
#                                                    output_folder=config['graph']['graph_folder']):
#     """e.g.
#     In old encoded edges count file:
#         17  57  8
#         ...
#         57  17  2
#     return:
#         17  57  10 or 57   17  10 (only one of them will appear in the file.)
#     """
#     merged_weight_edges = {}
#     for line in util.read_file_line_yielder(old_encoded_edges_count_path):
#         (source, target, weight) = line.split("\t")
#         if (target, source) in merged_weight_edges:
#             # edge[source][target] inverse edge edge[target][source] already put into the merged_weight_edges
#             merged_weight_edges[(target, source)] += int(weight)
#         else:
#             # The first time merged_weight_edges meets edge[source][target] or its inverse edge edge[target][source]
#             merged_weight_edges[(source, target)] = int(weight)
#     output_name = multi_processing.get_file_name(old_encoded_edges_count_path).split('.txt')[0] + '_undirected.txt'
#     util.write_dict_to_file(output_folder + output_name, merged_weight_edges, 'tuple')
#     return merged_weight_edges


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
    # TODO LATER Zheng check the guess below
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

# TODO LATER Zheng Add weight according to word pair distance in write_edges_of_different_window_size function
