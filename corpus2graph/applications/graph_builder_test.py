import unittest
import numpy as np
from corpus2graph.applications import graph_builder as gb
from corpus2graph.util import read_two_columns_file_to_build_dictionary_type_specified


class TestGraphBuilder(unittest.TestCase):
    """ ATTENTION
    Normally, data_folder and output_folder should be user defined paths (absolute paths).
    For unittest, as input and output folders locations are fixed, these two paths are exceptionally relative paths.
    """
    data_folder = '../test/output/keep/'

    # undirected paths
    encoded_edges_count_undirected_file = 'encoded_edges_count_window_size_6_vocab_size_none_undirected_for_unittest.txt'
    merged_dict_undirected_file = 'dict_merged_undirected_for_unittest.txt'
    word2wordId_undirected = read_two_columns_file_to_build_dictionary_type_specified(
        file=data_folder + merged_dict_undirected_file, key_type=str, value_type=int)
    valid_vocabulary_undirected_file = 'valid_vocabulary_min_count_5_undirected.txt'

    @staticmethod
    def get_matrix_value_by_token_xy(matrix, nodes, word2wordId, token_x, token_y):
        nodes = list(nodes)
        matrix_x = nodes.index(word2wordId[token_x])
        matrix_y = nodes.index(word2wordId[token_y])
        return matrix[matrix_x, matrix_y]

    def test_NoGraph_get_stochastic_matrix(self):
        no_graph = gb.NoGraph(self.data_folder + self.encoded_edges_count_undirected_file,
                              valid_vocabulary_path=self.data_folder + self.valid_vocabulary_undirected_file)
        matrix = no_graph.get_stochastic_matrix(remove_self_loops=True)

        self.assertTrue(self.get_matrix_value_by_token_xy(matrix, no_graph.graph_index2wordId,
                                                          self.word2wordId_undirected,
                                                          '.', 'the') == 2 / (2 + 2 + 3 + 1))
        self.assertTrue(self.get_matrix_value_by_token_xy(matrix, no_graph.graph_index2wordId,
                                                          self.word2wordId_undirected,
                                                          'and', 'the') == 4 / (2 + 1 + 4 + 3 + 4))
        self.assertTrue(self.get_matrix_value_by_token_xy(matrix, no_graph.graph_index2wordId,
                                                          self.word2wordId_undirected,
                                                          'the', ',') == 3 / (3 + 4 + 2 + 6 + 8))
        self.assertTrue(self.get_matrix_value_by_token_xy(matrix, no_graph.graph_index2wordId,
                                                          self.word2wordId_undirected,
                                                          ',', '.') == 0)
        self.assertTrue(self.get_matrix_value_by_token_xy(matrix, no_graph.graph_index2wordId,
                                                          self.word2wordId_undirected,
                                                          'in', ',') == 2 / (2 + 2 + 6 + 1 + 1))

    def test_NXGraph_get_stochastic_matrix(self):
        # Undirected
        graph = gb.NXGraph.from_encoded_edges_count_file(
            path=self.data_folder + self.encoded_edges_count_undirected_file, directed=False)
        graph.print_graph_information()

        matrix = graph.get_stochastic_matrix(remove_self_loops=True)
        graph_index2wordId = graph.graph.nodes()

        # check weight based transition probability
        self.assertTrue(self.get_matrix_value_by_token_xy(matrix, graph_index2wordId, self.word2wordId_undirected,
                                                          '.', 'the') == 2 / (2 + 2 + 3 + 1))
        self.assertTrue(self.get_matrix_value_by_token_xy(matrix, graph_index2wordId, self.word2wordId_undirected,
                                                          'and', 'the') == 4 / (2 + 1 + 4 + 3 + 4))
        self.assertTrue(self.get_matrix_value_by_token_xy(matrix, graph_index2wordId, self.word2wordId_undirected,
                                                          'the', ',') == 3 / (3 + 4 + 2 + 6 + 8))
        self.assertTrue(self.get_matrix_value_by_token_xy(matrix, graph_index2wordId, self.word2wordId_undirected,
                                                          ',', '.') == 0)
        self.assertTrue(self.get_matrix_value_by_token_xy(matrix, graph_index2wordId, self.word2wordId_undirected,
                                                          'in', ',') == 2 / (2 + 2 + 6 + 1 + 1))

    def test_NoGraph_t_step_random_walk(self):
        no_graph = gb.NoGraph(self.data_folder + self.encoded_edges_count_undirected_file,
                              valid_vocabulary_path=self.data_folder + self.valid_vocabulary_undirected_file)
        # t=1 step random walk (= stochastic matrix)
        _, matrix11 = no_graph.get_t_step_random_walk_stochastic_matrix(t=1, remove_self_loops=True)
        # t=2 steps random walk
        _, matrix22 = no_graph.get_t_step_random_walk_stochastic_matrix(t=2, remove_self_loops=True)

        # check the calculation of cell value.
        value_sum = 0
        for i in range(6):
            value_sum += matrix11[3, i] * matrix11[i, 5]
        np.testing.assert_array_almost_equal(value_sum, matrix22[3, 5])

        # t=3 steps random walk
        _, matrix33 = no_graph.get_t_step_random_walk_stochastic_matrix(t=3, remove_self_loops=True)

        # check the sum of each line in matrix equals to 1
        for i in range(0, matrix33.shape[0]):
            np.testing.assert_array_almost_equal(np.sum(matrix33[i]), 1)
        # check the calculation of cell value.
        value_sum = 0
        for i in range(6):
            value_sum += matrix22[3, i] * matrix11[i, 5]  # matrix1 is the transition matrix
        np.testing.assert_array_almost_equal(value_sum, matrix33[3, 5])

    def test_NXGraph_t_step_random_walk(self):
        graph = gb.NXGraph.from_encoded_edges_count_file(
            path=self.data_folder + self.encoded_edges_count_undirected_file, directed=False)
        # t=1 step random walk
        _, matrix1 = graph.get_t_step_random_walk_stochastic_matrix(t=1, remove_self_loops=True)
        # t=2 steps random walk
        _, matrix2 = graph.get_t_step_random_walk_stochastic_matrix(t=2, remove_self_loops=True)

        # check the calculation of cell value.
        value_sum = 0
        for i in range(6):
            value_sum += matrix1[3, i] * matrix1[i, 5]
        self.assertTrue(value_sum == matrix2[3, 5])

        # t=3 steps random walk
        _, matrix3 = graph.get_t_step_random_walk_stochastic_matrix(t=3, remove_self_loops=True)

        # check the sum of each line in matrix equals to 1
        for i in range(0, matrix3.shape[0]):
            self.assertTrue(np.sum(matrix3[i]) == 1.0)
        # check the calculation of cell value.
        value_sum = 0
        for i in range(6):
            value_sum += matrix2[3, i] * matrix1[i, 5]  # matrix1 is the transition matrix
        self.assertTrue(value_sum == matrix3[3, 5])
