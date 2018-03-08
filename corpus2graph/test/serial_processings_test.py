import unittest
from corpus2graph import FileParser, WordPreprocessor, Tokenizer, WordProcessing, \
    SentenceProcessing, WordPairsProcessing, util
import configparser
config = configparser.ConfigParser()
config.read('config.ini')


class TestProcessings(unittest.TestCase):
    """ ATTENTION
    Normally, data_folder and output_folder should be user defined paths (absolute paths).
    For unittest, as input and output folders locations are fixed, these two paths are exceptionally relative paths.
    """
    data_folder = 'unittest_data/'
    output_folder = 'output/'
    # TODO create edges, dicts, graph folder based on output_folder, no need to define them below.
    dicts_folder = output_folder + 'dicts_and_encoded_texts/'
    edges_folder = output_folder + 'edges/'
    graph_folder = output_folder + 'graph/'

    max_window_size = 6
    process_num = 3
    min_count = 5
    max_vocab_size = 3

    def test_1_word_processing(self):
        wp = WordProcessing(output_folder=self.dicts_folder, word_tokenizer='', wtokenizer=Tokenizer.mytok,
                            remove_numbers=False, remove_punctuations=False, stem_word=False, lowercase=False)
        # wp.fromfile(self.data_folder + 'AA/wiki_03.txt')
        merged_dict = wp.apply(data_folder=self.data_folder, process_num=self.process_num)

        # test the merged dict (with global id)
        self.assertEqual(len(merged_dict), 94)

    def test_2_sentence_processing(self):
        sp = SentenceProcessing(dicts_folder=self.dicts_folder, output_folder=self.edges_folder,
                                max_window_size=self.max_window_size, local_dict_extension=config['graph']['local_dict_extension'])
        # sp.fromfile(self.dicts_folder + 'dict_AA_wiki_03.dicloc')
        word_count_all = sp.apply(data_folder=self.dicts_folder, process_num=self.process_num)

        # test the merged word count (with global id)
        merged_dict = util.read_two_columns_file_to_build_dictionary_type_specified(
            file=self.dicts_folder + 'dict_merged.txt', key_type=str, value_type=int)
        self.assertEqual(word_count_all[merged_dict['on']], 2)
        self.assertEqual(word_count_all[merged_dict['00']], 3)
        self.assertEqual(word_count_all[merged_dict[',']], 5)

    def test_3_word_pairs_processing(self):
        # test valid vocabulary
        wpp = WordPairsProcessing(max_vocab_size=None, min_count=1,
                                  dicts_folder=self.dicts_folder, window_size=self.max_window_size,
                                  edges_folder=self.edges_folder, graph_folder=self.graph_folder,
                                  safe_files_number_per_processor=config['graph']['safe_files_number_per_processor'])
        valid_vocab = wpp.write_valid_vocabulary()
        self.assertEqual(len(valid_vocab), 94)

        wpp = WordPairsProcessing(max_vocab_size=None, min_count=3,
                                  dicts_folder=self.dicts_folder, window_size=self.max_window_size,
                                  edges_folder=self.edges_folder, graph_folder=self.graph_folder,
                                  safe_files_number_per_processor=config['graph']['safe_files_number_per_processor'])
        valid_vocab = wpp.write_valid_vocabulary()
        self.assertEqual(len(valid_vocab), 9)

        wpp = WordPairsProcessing(max_vocab_size=self.max_vocab_size, min_count=self.min_count,
                                  dicts_folder=self.dicts_folder, window_size=self.max_window_size,
                                  edges_folder=self.edges_folder, graph_folder=self.graph_folder,
                                  safe_files_number_per_processor=config['graph']['safe_files_number_per_processor'])
        valid_vocab = wpp.write_valid_vocabulary()
        self.assertEqual(len(valid_vocab), self.max_vocab_size)

        wpp = WordPairsProcessing(max_vocab_size=None, min_count=self.min_count,
                                  dicts_folder=self.dicts_folder, window_size=self.max_window_size,
                                  edges_folder=self.edges_folder, graph_folder=self.graph_folder,
                                  safe_files_number_per_processor=config['graph']['safe_files_number_per_processor'])
        valid_vocab = wpp.write_valid_vocabulary()
        self.assertEqual(len(valid_vocab), 6)

        # test word pairs of a specific window size
        wpp = WordPairsProcessing(max_vocab_size=None, min_count=self.min_count,
                                  dicts_folder=self.dicts_folder, window_size=self.max_window_size,
                                  edges_folder=self.edges_folder, graph_folder=self.graph_folder,
                                  safe_files_number_per_processor=config['graph']['safe_files_number_per_processor'])
        result = wpp.apply(process_num=self.process_num)
        word2id = util.read_two_columns_file_to_build_dictionary_type_specified(
            file=self.dicts_folder + 'dict_merged.txt', key_type=str, value_type=int)

        self.assertEqual(result[(str(word2id['and']), str(word2id[',']))], 2)
        self.assertEqual(result[(str(word2id['and']), str(word2id['.']))], 2)
        self.assertEqual(result[(str(word2id['and']), str(word2id['the']))], 1)

        self.assertEqual(result[(str(word2id['the']), str(word2id['of']))], 6)
        self.assertEqual(result[(str(word2id['the']), str(word2id['.']))], 2)
        self.assertEqual(result[(str(word2id['the']), str(word2id['and']))], 3)
        self.assertEqual(result[(str(word2id['the']), str(word2id['in']))], 1)
        self.assertEqual(result[(str(word2id['the']), str(word2id[',']))], 2)

        self.assertEqual(result[(str(word2id['of']), str(word2id['.']))], 3)
        self.assertEqual(result[(str(word2id['of']), str(word2id['the']))], 2)
        self.assertEqual(result[(str(word2id['of']), str(word2id['and']))], 3)
        self.assertEqual(result[(str(word2id['of']), str(word2id['in']))], 2)
        self.assertEqual(result[(str(word2id['of']), str(word2id[',']))], 1)

        self.assertEqual(result[(str(word2id['in']), str(word2id['.']))], 1)
        self.assertEqual(result[(str(word2id['in']), str(word2id['the']))], 5)
        self.assertEqual(result[(str(word2id['in']), str(word2id['and']))], 1)
        self.assertEqual(result[(str(word2id['in']), str(word2id[',']))], 1)

        self.assertEqual(result[(str(word2id[',']), str(word2id['and']))], 2)
        self.assertEqual(result[(str(word2id[',']), str(word2id['in']))], 1)
        self.assertEqual(result[(str(word2id[',']), str(word2id['the']))], 1)

        self.assertEqual(len(result), 20 + 3)  # 3 self loops

        wpp = WordPairsProcessing(max_vocab_size=self.max_vocab_size, min_count=self.min_count,
                                  dicts_folder=self.dicts_folder, window_size=self.max_window_size,
                                  edges_folder=self.edges_folder, graph_folder=self.graph_folder,
                                  safe_files_number_per_processor=config['graph']['safe_files_number_per_processor'])
        result = wpp.apply(process_num=self.process_num)
        self.assertEqual(result[(str(word2id['and']), str(word2id['the']))], 1)

        self.assertEqual(result[(str(word2id['the']), str(word2id['of']))], 6)
        self.assertEqual(result[(str(word2id['the']), str(word2id['and']))], 3)

        self.assertEqual(result[(str(word2id['of']), str(word2id['the']))], 2)
        self.assertEqual(result[(str(word2id['of']), str(word2id['and']))], 3)

        self.assertEqual(len(result), 5 + 2)  # 2 self loops

    def test_4_convert_encoded_edges_count_for_undirected_graph(self):
        def equal_test(word1, word2):
            if directed[(str(word2id[word1]), str(word2id[word2]))] \
                    and directed[(str(word2id[word2]), str(word2id[word1]))]:
                sum_count = directed[(str(word2id[word1]), str(word2id[word2]))] \
                            + directed[(str(word2id[word2]), str(word2id[word1]))]
            elif directed[(str(word2id[word1]), str(word2id[word2]))]:
                sum_count = directed[(str(word2id[word1]), str(word2id[word2]))]
            elif directed[(str(word2id[word2]), str(word2id[word1]))]:
                sum_count = directed[(str(word2id[word2]), str(word2id[word1]))]
            else:
                sum_count = 0

            if (str(word2id[word1]), str(word2id[word2])) in undirected:
                self.assertEqual(sum_count, undirected[(str(word2id[word1]), str(word2id[word2]))])
            elif (str(word2id[word2]), str(word2id[word1])) in undirected:
                self.assertEqual(sum_count, undirected[(str(word2id[word2]), str(word2id[word1]))])
            else:
                print('No direct edge between ' + word1 + ' and ' + word2)
                self.assertEqual(sum_count, 0)

        wpp = WordPairsProcessing(max_vocab_size=None, min_count=self.min_count,
                                  dicts_folder=self.dicts_folder, window_size=50,
                                  edges_folder=self.edges_folder, graph_folder=self.graph_folder,
                                  safe_files_number_per_processor=config['graph']['safe_files_number_per_processor'])
        directed = wpp.apply(process_num=self.process_num)

        word2id = util.read_two_columns_file_to_build_dictionary_type_specified(
            file=self.dicts_folder + 'dict_merged.txt', key_type=str,
            value_type=int)

        undirected = wpp.convert_encoded_edges_count_for_undirected_graph(
            old_encoded_edges_count_path=
            self.graph_folder + "encoded_edges_count_window_size_" + str(self.max_window_size) + ".txt")

        equal_test('and', ',')
        equal_test('the', '.')
        equal_test('and', '.')
        equal_test('and', 'of')
        equal_test('in', 'of')
        equal_test('.', 'in')
        equal_test('.', ',')  # . and , are not directly connected.


if __name__ == '__main__':
    unittest.main()
