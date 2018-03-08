__author__ = 'Zheng ZHANG'

"""
graph_builder is used by negative_samples_generator.py to get what is needed to build the negative samples.
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import corpus2graph.util as util
import corpus2graph.multi_processing


class NoGraph:
    def __init__(self, encoded_edges_count_file_path, valid_vocabulary_path):
        """
        Theoretically valid_vocabulary file is not necessary. We could build a graph_index2wordId dict by going through
        encoded_edges_count_file_path and getting all wordIds. But it's not efficient.

        valid_wordId's order is really important and should be static, because:
            1. graph_index2wordId is built on this
            2. graph_wordId2index (temp var), on which cooccurrence_matrix element's order is based, is built on this.
            3. graph_index2wordId represents cooccurrence_matrix element's order
        """
        self.name_prefix = corpus2graph.multi_processing.get_file_name(encoded_edges_count_file_path).split('.')[0]
        valid_wordId = list(set(util.read_valid_vocabulary(valid_vocabulary_path)))  # make sure no duplication
        # ATTENTION: graph_index2wordId should be a list of which the index order is from 0 to vocab_size-1
        # TODO LATER No need to make graph_index2wordId an int list. Find where graph_index2wordId is needed and changed them.
        self.graph_index2wordId = list(map(int, valid_wordId))
        vocab_size = len(valid_wordId)
        # ATTENTION: the index is of the type int, while the wordId is of the type str
        graph_wordId2index = dict(zip(valid_wordId, range(vocab_size)))
        # initialize numpy 2d array
        cooccurrence_matrix = np.zeros((vocab_size, vocab_size))
        # read encoded_edges_count_file
        for line in corpus2graph.util.read_file_line_yielder(encoded_edges_count_file_path):
            # ATTENTION: line e.g. '17'  '57'  '10' or '57'   '17'  '10' (only one of them will appear in the file.)
            (source, target, weight) = line.split("\t")
            cooccurrence_matrix[graph_wordId2index[source]][graph_wordId2index[target]] = weight
            # undirected graph
            cooccurrence_matrix[graph_wordId2index[target]][graph_wordId2index[source]] = weight
        self.cooccurrence_matrix = cooccurrence_matrix

    def get_stochastic_matrix(self, remove_self_loops, power=None):
        """
        A replacement of get_stochastic_matrix function NXGraph class.
        """
        vocab_size = self.cooccurrence_matrix.shape[0]
        stochastic_matrix = self.cooccurrence_matrix.copy()
        # power co-occurrence if needed.
        if power:
            stochastic_matrix = np.power(stochastic_matrix, power)
        # remove self loop
        if remove_self_loops:
            for i in range(vocab_size):
                stochastic_matrix[i][i] = 0
        # calculate percentage
        matrix_sum_row = np.sum(stochastic_matrix, axis=1, keepdims=True)  # sum of each row and preserve the dimension
        stochastic_matrix /= matrix_sum_row
        return stochastic_matrix

    def one_to_t_step_random_walk_stochastic_matrix_yielder(self, t, remove_self_loops):
        """
        Instead of getting a specific t step random walk result, this method gets a dict of result from 1 step random
        walk to t step random walk. This method should be used for grid search.
        """
        transition_matrix = self.get_stochastic_matrix(remove_self_loops)
        result = transition_matrix
        for t in range(1, t+1):
            if t != 1:
                result = np.matmul(result, transition_matrix)
            yield result, t

    def get_t_step_random_walk_stochastic_matrix(self, t, remove_self_loops, output_folder=None):
        # TODO NOW not the same result from 1 step random walk
        transition_matrix = self.get_stochastic_matrix(remove_self_loops)
        result = transition_matrix
        while t > 1:
            result = np.matmul(result, transition_matrix)
            t -= 1
        if output_folder:
            file_prefix = output_folder + self.name_prefix + '_' + str(t)
            np.save(file_prefix + '_step_rw_matrix.npy', result, fix_imports=False)
            corpus2graph.util.write_to_pickle(self.graph_index2wordId, file_prefix + '_step_rw_nodes.pickle')
        return self.graph_index2wordId, result


class NXGraph:
    def __init__(self, graph, name_prefix, directed):
        # name_prefix = encoded_edges_count file's name - '.txt' => encoded_edges_count file names must be unique.
        self.name_prefix = name_prefix
        self.graph = graph
        self.directed = directed

    @classmethod
    def from_gpickle(cls, path):
        name_prefix = corpus2graph.multi_processing.get_file_name(path).split('.')[0]
        graph = nx.read_gpickle(path)
        return cls(graph, name_prefix, nx.is_directed(graph))

    @classmethod
    def from_encoded_edges_count_file(cls, path, directed):
        name_prefix = corpus2graph.multi_processing.get_file_name(path).split('.')[0]
        if directed:
            graph = nx.read_weighted_edgelist(path, create_using=nx.DiGraph(), nodetype=int)
        else:
            graph = nx.read_weighted_edgelist(path, create_using=nx.Graph(), nodetype=int)
        # nx.write_gpickle(graph, output_folder + name_prefix + '.gpickle')
        return cls(graph, name_prefix, directed)

    def draw_graph(self):
        """
        Takes too much time with big data.
        """
        nx.draw(self.graph, with_labels=True)
        plt.show()

    def print_graph_information(self):
        print('\n###################### Graph Information ######################')
        number_of_edges = self.graph.number_of_edges()
        number_of_selfloops = nx.number_of_selfloops(self.graph)
        number_of_nodes = self.graph.number_of_nodes()
        if nx.is_directed(self.graph):
            print('The graph is directed.')
            connected_edges_proportion = round(
                (number_of_edges - number_of_selfloops) / (number_of_nodes * (number_of_nodes - 1)) * 100, 2)
        else:
            print('The graph is undirected.')
            connected_edges_proportion = round(
                (number_of_edges - number_of_selfloops) / ((number_of_nodes * (number_of_nodes - 1)) / 2) * 100, 2)
        print("#nodes:", number_of_nodes, "#edges:",  number_of_edges, "#selfloops:", number_of_selfloops)
        print(str(connected_edges_proportion) + '% of the node pairs are connected via edges.')
        # TODO LATER: Code below takes long time to calculate for big graphs.
        # print('Average shortest path length (weight=None):', str(round(nx.average_shortest_path_length(self.graph), 2)))
        # TODO LATER: average_clustering has not implemented for undirected graph yet.
        if not nx.is_directed(self.graph):
            # For unweighted graphs, the clustering of a node
            # is the fraction of possible triangles through that node that exist
            print('The clustering coefficient for the graph is ' + str(
                round(nx.average_clustering(self.graph, weight=None), 2)))
        print('###############################################################\n')

    def get_stochastic_matrix(self, remove_self_loops):
        # ATTENTION: for a big graph, this method consumes too much memory and calculation time.
        # ATTENTION: it's really important to copy copy graph. If not, in remove_self_loops=True situation, self-loops
        # will be permanently deleted.
        graph_copy = self.graph.copy()
        if remove_self_loops:
            graph_copy.remove_edges_from(list(nx.selfloop_edges(graph_copy)))  # remove self loop
        if self.directed:
            directed_graph = graph_copy
        else:
            directed_graph = graph_copy.to_directed()
        # this function only works with directed graph
        stochastic_graph = nx.stochastic_graph(directed_graph, weight='weight')
        return nx.to_numpy_matrix(stochastic_graph)

    def get_t_step_random_walk_stochastic_matrix(self, t, remove_self_loops, output_folder=None):
        transition_matrix = self.get_stochastic_matrix(remove_self_loops=remove_self_loops)
        result = transition_matrix
        while t > 1:
            result = np.matmul(result, transition_matrix)
            t -= 1
        if output_folder:
            file_prefix = output_folder + self.name_prefix + '_' + str(t)
            np.save(file_prefix + '_step_rw_matrix.npy', result, fix_imports=False)
            corpus2graph.util.write_to_pickle(self.graph.nodes(), file_prefix + '_step_rw_nodes.pickle')
        return self.graph.nodes(), result

    def one_to_t_step_random_walk_stochastic_matrix_yielder(self, t, remove_self_loops):
        """
        Instead of getting a specific t step random walk result, this method gets a dict of result from 1 step random
        walk to t step random walk. This method should be used for grid search.
        """
        transition_matrix = self.get_stochastic_matrix(remove_self_loops)
        result = transition_matrix
        for t in range(1, t+1):
            if t != 1:
                result = np.matmul(result, transition_matrix)
            yield result, t

    # def get_shortest_path_lengths_between_all_nodes(self, output_folder):
    #     """
    #     From test, these three algorithms below take more than 20 hours (processes have been killed after 20 hours) to
    #     calculate.
    #     'floyd_warshall_numpy' takes around 100 minutes to get the result.
    #
    #     # length1 = dict(nx.all_pairs_dijkstra_path_length(g))
    #     # length2 = dict(nx.all_pairs_bellman_ford_path_length(g))
    #     # length3 = nx.johnson(g, weight='weight')
    #     # for node in [0, 1, 2, 3, 4]:
    #     #     print('1 - {}: {}'.format(node, length2[1][node]))
    #     """
    #     """ ATTENTION
    #     'floyd_warshall_numpy' has already considered situations below:
    #     1. If there's no path between source and target node, matrix will put 'inf'
    #     2. No matter how much the weight is between node and node itself(self loop), the shortest path will always be 0.
    #     """
    #     matrix = nx.floyd_warshall_numpy(self.graph)  # ATTENTION: return type is NumPy matrix not NumPy ndarray.
    #     # ATTENTION: after saving, NumPy matrix has been changed to 2darray.
    #     np.save(output_folder + self.name_prefix + '_matrix.npy', matrix, fix_imports=False)
    #     corpus2graph.util.write_to_pickle(self.graph.nodes(), output_folder + self.name_prefix + '_nodes.pickle')
    #     return self.graph.nodes(), matrix
