import unittest
import warnings
from corpus2graph.applications import graph_generator
from corpus2graph import FileParser, WordPreprocessor, Tokenizer, WordProcessing, \
    SentenceProcessing, WordPairsProcessing

import configparser
config = configparser.ConfigParser()
config.read('config.ini')


class TestGenerator(unittest.TestCase):
    """ ATTENTION
    Normally, data_folder and output_folder should be user defined paths (absolute paths).
    For unittest, as input and output folders locations are fixed, these two paths are exceptionally relative paths.
    """
    data_folder = '../test/unittest_data/'

    file_extension = '.txt'
    max_window_size = 6
    process_num = 3
    data_type = 'txt'
    min_count = 5
    max_vocab_size = 3

    def test_graph_generator(self):
        gg = graph_generator.GraphGenerator(window_size=3, file_parser='txt',
                                               xml_node_path=None, word_tokenizer='WordPunct',
                                               remove_numbers=True, remove_punctuations=True,
                                               stem_word=True, lowercase=True)
        print('-----Test sentence based generator-----')
        print(gg.fromsent([1, 2, 3]))

        print('-----Test file based generator-----')
        p = gg.fromfile(self.data_folder + 'AA/wiki_03.txt')
        print(p[0])
        print(p[1])

        print('-----Test folder based generator-----')
        for p in gg(self.data_folder):
            print(p[0])
            print(p[1])
