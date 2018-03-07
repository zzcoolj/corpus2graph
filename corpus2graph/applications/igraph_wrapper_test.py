import unittest
from corpus2graph.applications import wordpair_generator, igraph_wrapper
from corpus2graph import FileParser, WordPreprocessor, Tokenizer, WordProcessing, \
    SentenceProcessing, WordPairsProcessing

import configparser
config = configparser.ConfigParser()
config.read('config.ini')


class TestIGraph(unittest.TestCase):
    """
    Undirected graph
    """

    data_folder = '../test/unittest_data/'

    file_extension = '.txt'
    max_window_size = 6
    process_num = 3
    data_type = 'txt'
    min_count = 5
    max_vocab_size = 3

    def test_igraph_wrapper_wrapper(self):
        wg = wordpair_generator.WordsGenerator(window_size=3, file_parser=self.data_type,
                                               xml_node_path=None, word_tokenizer='WordPunct',
                                               remove_numbers=True, remove_punctuations=True,
                                               stem_word=True, lowercase=True)

        igt = igraph_wrapper.IGraphWrapper('Test')
        print('in2')
        for w1, w2 in wg(self.data_folder):
            print(w1, w2)
            igt.addPairs(w1, w2)

        graph = igt.getGraph()
        print(graph.vs["word"])
        print(graph.es)
        print(graph.es["weight"])