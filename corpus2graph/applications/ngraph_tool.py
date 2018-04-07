import time
from corpus2graph.applications import wordpair_generator, graph_tool_wrapper, graph_generator
from corpus2graph import FileParser, WordPreprocessor, Tokenizer, WordProcessing, \
    SentenceProcessing, WordPairsProcessing, util

import configparser
config = configparser.ConfigParser()
config.read('../test/config.ini')

print(config)

data_folder = '../test/unittest_data/tmp_dir/'

file_extension = '.txt'
max_window_size = 5
process_num = 1
data_type = 'txt'
min_count = 0
max_vocab_size = 'None'

output_folder = '../test/output/'
dicts_folder = output_folder + 'dicts_and_encoded_texts/'
edges_folder = output_folder + 'edges/'
graph_folder = output_folder + 'graph/'

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

# igt = networkx_wrapper.IGraphWrapper('Test')
# igt.add_edges_from_file(path=graph_folder+'encoded_edges_count_window_size_5.txt')
print('[corpus2graph] time in seconds:', util.count_time(start_time))
gtw = graph_tool_wrapper.GraphToolWrapper('Test')
gtw.addEdgesFromFile(path=graph_folder+'encoded_edges_count_window_size_5.txt')
print('[corpus2graph] time in seconds:', util.count_time(start_time))