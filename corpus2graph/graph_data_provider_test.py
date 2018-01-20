"""ATTENTION
1. All results are based on setting preprocessing_word=False in config.ini.
2. The execution order follows ASCII order of function names, so add number after 'test_' to make sure the execution
   order.
"""

import unittest
import graph_data_provider as gdp


class TestGraphDataProvider(unittest.TestCase):
    data_folder = 'data/training data/unittest_data/'
    file_extension = '.txt'
    max_window_size = 6
    process_num = 4
    data_type = 'txt'
    dicts_folder = 'output/intermediate data for unittest/dicts_and_encoded_texts/'
    edges_folder = 'output/intermediate data for unittest/edges/'
    graph_folder = 'output/intermediate data for unittest/graph/'
    min_count = 5
    max_vocab_size = 3

    def test_1_merge_local_dict(self):
        gdp.multiprocessing_write_local_encoded_text_and_local_dict(self.data_folder, self.file_extension,
                                                                    self.dicts_folder, self.process_num)
        result = gdp.merge_local_dict(dict_folder=self.dicts_folder, output_folder=self.dicts_folder)
        self.assertEqual(len(result), 94)

    def test_2_merge_transferred_word_count(self):
        gdp.multiprocessing_write_transferred_edges_files_and_transferred_word_count(self.dicts_folder,
                                                                                     self.edges_folder,
                                                                                     self.max_window_size,
                                                                                     self.process_num)
        result = gdp.merge_transferred_word_count(word_count_folder=self.dicts_folder, output_folder=self.dicts_folder)
        self.assertEqual(len(result), 94)
        merged_dict = gdp.read_two_columns_file_to_build_dictionary_type_specified(
            file=self.dicts_folder + 'dict_merged.txt', key_type=str,
            value_type=int)
        self.assertEqual(result[merged_dict['on']], 2)
        self.assertEqual(result[merged_dict['00']], 3)
        self.assertEqual(result[merged_dict[',']], 5)

    def get_3_id2word(self):
        word2id = gdp.read_two_columns_file_to_build_dictionary_type_specified(
            file=self.dicts_folder + 'dict_merged.txt', key_type=str,
            value_type=int)
        id2word = dict()
        for word, id in word2id.items():
            id2word[id] = word
        return id2word

    def test_4_write_valid_vocabulary(self):
        result = gdp.write_valid_vocabulary(merged_word_count_path=self.dicts_folder + 'word_count_all.txt',
                                            output_path=self.dicts_folder + 'valid_vocabulary_min_count_' + str(
                                                self.min_count) + '.txt',
                                            min_count=self.min_count,
                                            max_vocab_size=None)
        self.assertEqual(len(result), 6)

        result = gdp.write_valid_vocabulary(merged_word_count_path=self.dicts_folder + 'word_count_all.txt',
                                            output_path=self.dicts_folder + 'valid_vocabulary_min_count_1.txt',
                                            min_count=1,
                                            max_vocab_size=None)
        self.assertEqual(len(result), 94)

        result = gdp.write_valid_vocabulary(merged_word_count_path=self.dicts_folder + 'word_count_all.txt',
                                            output_path=self.dicts_folder + 'valid_vocabulary_min_count_3.txt',
                                            min_count=3,
                                            max_vocab_size=None)
        self.assertEqual(len(result), 9)

        result = gdp.write_valid_vocabulary(merged_word_count_path=self.dicts_folder + 'word_count_all.txt',
                                            output_path=self.dicts_folder + 'valid_vocabulary_min_count_' + str(
                                                self.min_count) + '_vocab_size_' + str(self.max_vocab_size) + '.txt',
                                            min_count=self.min_count,
                                            max_vocab_size=self.max_vocab_size)
        self.assertEqual(len(result), self.max_vocab_size)

    def test_5_multiprocessing_merge_edges_count_of_a_specific_window_size(self):
        # max_vocab_size is None
        gdp.write_valid_vocabulary(merged_word_count_path=self.dicts_folder + 'word_count_all.txt',
                                   output_path=self.dicts_folder + 'valid_vocabulary_min_count_' + str(
                                       self.min_count) + '.txt',
                                   min_count=self.min_count,
                                   max_vocab_size=None)
        result = gdp.multiprocessing_merge_edges_count_of_a_specific_window_size(window_size=50, process_num=5,
                                                                                 min_count=self.min_count,
                                                                                 dicts_folder=self.dicts_folder,
                                                                                 edges_folder=self.edges_folder,
                                                                                 output_folder=self.graph_folder,
                                                                                 max_vocab_size=None)
        word2id = gdp.read_two_columns_file_to_build_dictionary_type_specified(
            file=self.dicts_folder + 'dict_merged.txt', key_type=str,
            value_type=int)

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

        # max_vocab_size is set to 3
        gdp.write_valid_vocabulary(merged_word_count_path=self.dicts_folder + 'word_count_all.txt',
                                   output_path=self.dicts_folder + 'valid_vocabulary_min_count_' + str(
                                       self.min_count) + '_vocab_size_' + str(
                                       self.max_vocab_size) + '.txt',
                                   min_count=self.min_count,
                                   max_vocab_size=self.max_vocab_size)
        result = gdp.multiprocessing_merge_edges_count_of_a_specific_window_size(window_size=50, process_num=5,
                                                                                 min_count=self.min_count,
                                                                                 dicts_folder=self.dicts_folder,
                                                                                 edges_folder=self.edges_folder,
                                                                                 output_folder=self.graph_folder,
                                                                                 max_vocab_size=self.max_vocab_size)
        word2id = gdp.read_two_columns_file_to_build_dictionary_type_specified(
            file=self.dicts_folder + 'dict_merged.txt', key_type=str,
            value_type=int)

        self.assertEqual(result[(str(word2id['and']), str(word2id['the']))], 1)

        self.assertEqual(result[(str(word2id['the']), str(word2id['of']))], 6)
        self.assertEqual(result[(str(word2id['the']), str(word2id['and']))], 3)

        self.assertEqual(result[(str(word2id['of']), str(word2id['the']))], 2)
        self.assertEqual(result[(str(word2id['of']), str(word2id['and']))], 3)

        self.assertEqual(len(result), 5 + 2)  # 2 self loops

    def test_6_filter_edges(self):
        gdp.write_valid_vocabulary(merged_word_count_path=self.dicts_folder + 'word_count_all.txt',
                                   output_path=self.dicts_folder + 'valid_vocabulary_min_count_' + str(
                                       self.min_count) + '.txt',
                                   min_count=self.min_count,
                                   max_vocab_size=None)
        gdp.multiprocessing_merge_edges_count_of_a_specific_window_size(window_size=50, process_num=5,
                                                                        min_count=self.min_count,
                                                                        dicts_folder=self.dicts_folder,
                                                                        edges_folder=self.edges_folder,
                                                                        output_folder=self.graph_folder,
                                                                        max_vocab_size=None)
        filtered_edges = gdp.filter_edges(min_count=self.min_count,
                                          old_encoded_edges_count_path=
                                          self.graph_folder + 'encoded_edges_count_window_size_6.txt',
                                          max_vocab_size=self.max_vocab_size,
                                          new_valid_vocabulary_folder=self.dicts_folder,
                                          merged_word_count_path=self.dicts_folder + 'word_count_all.txt',
                                          output_folder=self.graph_folder)

        word2id = gdp.read_two_columns_file_to_build_dictionary_type_specified(
            file=self.dicts_folder + 'dict_merged.txt', key_type=str,
            value_type=int)

        self.assertEqual(filtered_edges[(str(word2id['and']), str(word2id['the']))], 1)

        self.assertEqual(filtered_edges[(str(word2id['the']), str(word2id['of']))], 6)
        self.assertEqual(filtered_edges[(str(word2id['the']), str(word2id['and']))], 3)

        self.assertEqual(filtered_edges[(str(word2id['of']), str(word2id['the']))], 2)
        self.assertEqual(filtered_edges[(str(word2id['of']), str(word2id['and']))], 3)

        self.assertEqual(len(filtered_edges), 5 + 2)  # 2 self loops

    def test_7_merge_encoded_edges_count_for_undirected_graph(self):
        gdp.write_valid_vocabulary(merged_word_count_path=self.dicts_folder + 'word_count_all.txt',
                                   output_path=self.dicts_folder + 'valid_vocabulary_min_count_' + str(
                                       self.min_count) + '.txt',
                                   min_count=self.min_count,
                                   max_vocab_size=None)
        directed = gdp.multiprocessing_merge_edges_count_of_a_specific_window_size(window_size=50, process_num=5,
                                                                                   min_count=self.min_count,
                                                                                   dicts_folder=self.dicts_folder,
                                                                                   edges_folder=self.edges_folder,
                                                                                   output_folder=self.graph_folder,
                                                                                   max_vocab_size=None)
        word2id = gdp.read_two_columns_file_to_build_dictionary_type_specified(
            file=self.dicts_folder + 'dict_merged.txt', key_type=str,
            value_type=int)

        undirected = gdp.merge_encoded_edges_count_for_undirected_graph(
            old_encoded_edges_count_path=
            self.graph_folder + "encoded_edges_count_window_size_" + str(self.max_window_size) + ".txt",
            output_folder=self.graph_folder)

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

        equal_test('and', ',')
        equal_test('the', '.')
        equal_test('and', '.')
        equal_test('and', 'of')
        equal_test('in', 'of')
        equal_test('.', 'in')
        equal_test('.', ',')  # . and , are not directly connected.


if __name__ == '__main__':
    unittest.main()
