__author__ = 'Ruiqing YIN'

import unittest
import time
from corpus2graph.applications import wordpair_generator, graph_tool_wrapper, graph_generator
from corpus2graph import FileParser, WordPreprocessor, Tokenizer, WordProcessing, \
    SentenceProcessing, WordPairsProcessing, util

import configparser
config = configparser.ConfigParser()
config.read('config.ini')


class TestGraphTool(unittest.TestCase):
    """ ATTENTION
    Normally, data_folder and output_folder should be user defined paths (absolute paths).
    For unittest, as input and output folders locations are fixed, these two paths are exceptionally relative paths.
    """
    data_folder = '../test/unittest_data/'

    file_extension = '.txt'
    max_window_size = 5
    process_num = 1
    data_type = 'txt'
    min_count = 0
    max_vocab_size = 'None'

    def test_graph_tool_wrapper(self):
        start_time = time.time()
        wg = wordpair_generator.WordsGenerator(window_size=self.max_window_size, file_parser='txt',
                     xml_node_path=None, word_tokenizer='', wtokenizer=Tokenizer.mytok,
                     remove_numbers=False, remove_punctuations=False,
                     stem_word=False, lowercase=False)

        gtw = graph_tool_wrapper.GraphToolWrapper('Test')
        for w1,w2 in wg(self.data_folder+'/tmp_dir/'):
            gtw.addPairs(w1, w2)
        print(util.count_time(start_time))
        # graph = gtw.getGraph()
        # print('---- vertice ----')
        # print([gtw.vname[v] for v in graph.vertices()])
        # print('---- edge ----')
        # print([gtw.eweight[e] for e in graph.edges()])

    # def test_add_edges(self):
    #     gg = graph_generator.GraphGenerator(window_size=3, file_parser='txt',
    #                                         xml_node_path=None, word_tokenizer='WordPunct',
    #                                         remove_numbers=True, remove_punctuations=True,
    #                                         stem_word=True, lowercase=True)
    #     pl, wl = gg.fromfile(self.data_folder + 'AA/wiki_03.txt')
    #     gtw = graph_tool_wrapper.GraphToolWrapper('Test')
    #     gtw.addEdgesFromList(pl,wl)
    #
    #     graph = gtw.getGraph()
    #     print('---- vertice ----')
    #     print([gtw.vname[v] for v in graph.vertices()])
    #     print('---- edge ----')
    #     print([gtw.eweight[e] for e in graph.edges()])
    #
    # def test_our_method(self):
    #     gtw = graph_tool_wrapper.GraphToolWrapper('Test')
    #     gtw.addEdgesFromFile(
    #         path='../test/output/keep/encoded_edges_count_window_size_6_vocab_size_none_undirected_for_unittest.txt')
    #
    #     graph = gtw.getGraph()
    #     print('---- vertice ----')
    #     print([gtw.vname[v] for v in graph.vertices()])
    #     print('---- edge ----')
    #     print([gtw.eweight[e] for e in graph.edges()])
