from corpus2graph import Tokenizer, WordProcessing, SentenceProcessing, WordPairsProcessing, util
from corpus2graph.applications import wordpair_generator, graph_generator, networkx_wrapper

import time
import configparser
config = configparser.ConfigParser()
config.read('corpus2graph/test/config.ini')

"""run command below in Code/corpus2graph folder
python -m corpus2graph.server_test_one_file.py
"""

# data_folder = '/Users/zzcoolj/Code/GoW/data/training data/Wikipedia-Dumps_en_20170420_prep/'

data_folder = '/dev/shm/zzheng-tmp/prep_one_file/'

output_folder = 'server_one_file_output/'
dicts_folder = output_folder + 'dicts_and_encoded_texts/'
edges_folder = output_folder + 'edges/'
graph_folder = output_folder + 'graph/'

data_type = 'txt'
max_window_size = 5
process_num = 1
min_count = 0
max_vocab_size = 'None'


# NetworkX: corpus2graph
start_time = time.time()
wp = WordProcessing(output_folder=dicts_folder, word_tokenizer='', wtokenizer=Tokenizer.mytok,
                    remove_numbers=False, remove_punctuations=False, stem_word=False, lowercase=False)
merged_dict = wp.apply(data_folder=data_folder, process_num=process_num)

sp = SentenceProcessing(dicts_folder=dicts_folder, output_folder=edges_folder,
                        max_window_size=max_window_size, local_dict_extension=config['graph']['local_dict_extension'])
word_count_all = sp.apply(data_folder=dicts_folder, process_num=process_num)

wpp = WordPairsProcessing(max_vocab_size=max_vocab_size, min_count=min_count,
                          dicts_folder=dicts_folder, window_size=max_window_size,
                          edges_folder=edges_folder, graph_folder=graph_folder,
                          safe_files_number_per_processor=config['graph']['safe_files_number_per_processor'])
result = wpp.apply(process_num=process_num)
print('[corpus2graph] time in seconds:', util.count_time(start_time))
# igt = networkx_wrapper.IGraphWrapper('Test')
# igt.add_edges_from_file(path=graph_folder+'encoded_edges_count_window_size_5.txt')
# print('[corpus2graph] time in seconds:', util.count_time(start_time))
#
# # NetworkX: naive
# start_time = time.time()
# igt = networkx_wrapper.IGraphWrapper('Test')
# wg = wordpair_generator.WordsGenerator(window_size=max_window_size, file_parser=data_type,
#                                        xml_node_path=None, word_tokenizer='', wtokenizer=Tokenizer.mytok,
#                                        remove_numbers=False, remove_punctuations=False,
#                                        stem_word=False, lowercase=False)
# for w1, w2 in wg(data_folder):
#     igt.addPair(w1, w2)
# print('[naive] time in seconds:', util.count_time(start_time))
#
# # NetworkX: advanced naive
# start_time = time.time()
# igt = networkx_wrapper.IGraphWrapper('Test')
# gg = graph_generator.GraphGenerator(window_size=max_window_size, file_parser=data_type,
#                                     xml_node_path=None, word_tokenizer='', wtokenizer=Tokenizer.mytok,
#                                     remove_numbers=False, remove_punctuations=False,
#                                     stem_word=False, lowercase=False)
# edges, nodes = gg.fromfile(data_folder + 'AA/wiki_00.txt')
# igt.add_edges_from_list(edges)
# print('[advanced naive] time in seconds:', util.count_time(start_time))


# from corpus2graph.applications import igraph_wrapper
# # igraph: corpus2graph
# start_time = time.time()
# wp = WordProcessing(output_folder=dicts_folder, word_tokenizer='', wtokenizer=Tokenizer.mytok,
#                     remove_numbers=False, remove_punctuations=False, stem_word=False, lowercase=False)
# merged_dict = wp.apply(data_folder=data_folder, process_num=process_num)
#
# sp = SentenceProcessing(dicts_folder=dicts_folder, output_folder=edges_folder,
#                         max_window_size=max_window_size, local_dict_extension=config['graph']['local_dict_extension'])
# word_count_all = sp.apply(data_folder=dicts_folder, process_num=process_num)
#
# wpp = WordPairsProcessing(max_vocab_size=max_vocab_size, min_count=min_count,
#                           dicts_folder=dicts_folder, window_size=max_window_size,
#                           edges_folder=edges_folder, graph_folder=graph_folder,
#                           safe_files_number_per_processor=config['graph']['safe_files_number_per_processor'])
# result = wpp.apply(process_num=process_num)
#
# print('[corpus2graph prepared] time in seconds:', util.count_time(start_time))
# igt = igraph_wrapper.IGraphWrapper('Test')
# igt.add_edges_from_file(path=graph_folder+'encoded_edges_count_window_size_5.txt')
# print('[corpus2graph] time in seconds:', util.count_time(start_time))

# # igraph: naive
# start_time = time.time()
# wg = wordpair_generator.WordsGenerator(window_size=max_window_size,
#                                        xml_node_path=None, word_tokenizer='', wtokenizer=Tokenizer.mytok,
#                                        remove_numbers=False, remove_punctuations=False,
#                                        stem_word=False, lowercase=False)
# igt = igraph_wrapper.IGraphWrapper('Test')
# for w1, w2 in wg(data_folder):
#     igt.addPair(w1, w2)
# graph = igt.getGraph()
# print('[naive] time in seconds:', util.count_time(start_time))
