import graph_data_provider
import nltk.data

nltk.data.path = ['/vol/datailes/tools/nlp/nltk_data/2016']

# graph_data_provider.prepare_intermediate_data(
#     data_folder='/vol/corpusiles/open/Wikipedia-Dumps/en/20170420/prep/',
#     file_extension='.txt',
#     max_window_size=10,
#     process_num=50)

# graph_data_provider.multiprocessing_merge_edges_count_of_a_specific_window_size(window_size=10, process_num=50, already_existed_window_size=7)

# get undirected edges count for all file
for i in range(2, 11):
    file_path = 'output/intermediate data/graph/encoded_edges_count_window_size_' + str(i) + '.txt'
    graph_data_provider.merge_encoded_edges_count_for_undirected_graph(file_path)
