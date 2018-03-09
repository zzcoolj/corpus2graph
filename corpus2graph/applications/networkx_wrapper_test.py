import unittest
from corpus2graph.applications import wordpair_generator, networkx_wrapper, graph_generator
from corpus2graph import FileParser, WordPreprocessor, Tokenizer, WordProcessing, \
    SentenceProcessing, WordPairsProcessing

import configparser
config = configparser.ConfigParser()
config.read('config.ini')


class TestNetworkX(unittest.TestCase):
    """
    Undirected graph
    """

    data_folder = '../test/unittest_data/'

    file_extension = '.txt'
    max_window_size = 6
    process_num = 3
    data_type = 'txt'

    def test_naive_wrapper(self):
        igt = networkx_wrapper.IGraphWrapper('Test')
        wg = wordpair_generator.WordsGenerator(window_size=3, file_parser=self.data_type,
                                               xml_node_path=None, word_tokenizer='', wtokenizer=Tokenizer.mytok,
                                               remove_numbers=False, remove_punctuations=False,
                                               stem_word=False, lowercase=False)
        for w1, w2 in wg(self.data_folder):
            igt.addPair(w1, w2)
        graph = igt.getGraph()
        print(graph.nodes)
        print(graph.edges)

    def test_one_file_based_wrapper(self):
        igt = networkx_wrapper.IGraphWrapper('Test')
        gg = graph_generator.GraphGenerator(window_size=3, file_parser=self.data_type,
                                            xml_node_path=None, word_tokenizer='', wtokenizer=Tokenizer.mytok,
                                            remove_numbers=False, remove_punctuations=False,
                                            stem_word=False, lowercase=False)
        edges, nodes = gg.fromfile(self.data_folder + 'AA/wiki_03.txt')
        igt.add_edges_from_list(edges)
        graph = igt.getGraph()
        print(graph.nodes)
        print(graph.edges)

    def test_our_method(self):
        igt = networkx_wrapper.IGraphWrapper('Test')
        igt.add_edges_from_file(
            path='../test/output/keep/encoded_edges_count_window_size_6_vocab_size_none_undirected_for_unittest.txt')
        graph = igt.getGraph()
        print(graph.nodes)
        print(graph.edges)



    # def test_union_graphs(self):
    #     wg = wordpair_generator.WordsGenerator(window_size=3, file_parser=self.data_type,
    #                                            xml_node_path=None, word_tokenizer='', wtokenizer=Tokenizer.mytok,
    #                                            remove_numbers=False, remove_punctuations=False,
    #                                            stem_word=False, lowercase=False)
    #
    #     igt1 = igraph_wrapper.IGraphWrapper('graph1')
    #     igt2 = igraph_wrapper.IGraphWrapper('graph2')
    #
    #     graph_merged = igraph.Graph()
    #     graph_merged.vs["word"] = []  # vertice property: store the corresponding word
    #     graph_merged.es["weight"] = []  # edge weight property: store the cooccurrence
    #
    #     for w1, w2 in wg(self.data_folder):
    #         igt1.addPair(w1, w2)
    #         igt2.addPair(w1, w2)
    #     graph_merged.union([igt2.getGraph(), igt1.getGraph()])
    #
    #     print(igt1.getGraph().vs["name"])
    #     print(igt1.getGraph().es["weight"])
    #     print(igt2.getGraph().vs["name"])
    #     print(igt2.getGraph().es["weight"])
    #     print(graph_merged.vs["word"])
    #     print(graph_merged.es["weight"])
