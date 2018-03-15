from corpus2graph import Tokenizer, WordProcessing, SentenceProcessing, WordPairsProcessing, util

# from ..word_processor import FileParser, WordPreprocessor, Tokenizer
# from ..word_processing import WordProcessing
# from ..wordpair_processing import WordPairsProcessing
# from ..sentence_processing import SentenceProcessing
# from ..util import count_time

import time
import configparser

config = configparser.ConfigParser()
config.read('corpus2graph/test/config.ini')

"""run command below in Code/corpus2graph folder
python -m corpus2graph.server_test.py
"""

# data_folder = '/Users/zzcoolj/Code/GoW/data/training data/Wikipedia-Dumps_en_20170420_prep/'
data_folder = '/dev/shm/zzheng-tmp/prep/'

output_folder = 'server_output/'
dicts_folder = output_folder + 'dicts_and_encoded_texts/'
edges_folder = output_folder + 'edges/'
graph_folder = output_folder + 'graph/'

max_window_size = 5
process_num = 50
min_count = 5
max_vocab_size = 10000

# start_time = time.time()
# wp = WordProcessing(output_folder=dicts_folder, word_tokenizer='', wtokenizer=Tokenizer.mytok,
#                     remove_numbers=False, remove_punctuations=False, stem_word=False, lowercase=False)
# merged_dict = wp.apply(data_folder=data_folder, process_num=process_num)
# print('time in seconds:', util.count_time(start_time))
#
# start_time = time.time()
# sp = SentenceProcessing(dicts_folder=dicts_folder, output_folder=edges_folder,
#                         max_window_size=max_window_size, local_dict_extension=config['graph']['local_dict_extension'])
# word_count_all = sp.apply(data_folder=dicts_folder, process_num=process_num)
# print('time in seconds:', util.count_time(start_time))

start_time = time.time()
wpp = WordPairsProcessing(max_vocab_size=max_vocab_size, min_count=min_count,
                          dicts_folder=dicts_folder, window_size=max_window_size,
                          edges_folder=edges_folder, graph_folder=graph_folder,
                          safe_files_number_per_processor=config['graph']['safe_files_number_per_processor'])
result = wpp.apply(process_num=process_num)
# wpp.multiprocessing_merge_edges_count_of_a_specific_window_size(process_num=process_num, already_existed_window_size=4)
print('time in seconds:', util.count_time(start_time))

# # convert edges for undirected graph
# wpp.convert_encoded_edges_count_for_undirected_graph(
#     old_encoded_edges_count_path=graph_folder + 'encoded_edges_count_window_size_5.txt')


# from corpus2graph.applications import graph_builder as gb
#
# # load into NoGraph and calculate stochastic matrix
# start_time = time.time()
# no_graph = gb.NoGraph(graph_folder + 'encoded_edges_count_window_size_5_undirected.txt',
#                       valid_vocabulary_path=dicts_folder + 'valid_vocabulary_min_count_5_vocab_size_10000.txt')
# print('[load into NoGraph] time in seconds:', util.count_time(start_time))
# start_time = time.time()
# matrix = no_graph.get_stochastic_matrix(remove_self_loops=False)
# print('[calculate stochastic matrix] time in seconds:', util.count_time(start_time))
#
#
# # load into NetworkX and calculate stochastic matrix
# start_time = time.time()
# graph = gb.NXGraph.from_encoded_edges_count_file(path=graph_folder + 'encoded_edges_count_window_size_5_undirected.txt',
#                                                  directed=False)
# print('[load into NXGraph] time in seconds:', util.count_time(start_time))
# start_time = time.time()
# matrix = graph.get_stochastic_matrix(remove_self_loops=False)
# print('[calculate stochastic matrix] time in seconds:', util.count_time(start_time))
