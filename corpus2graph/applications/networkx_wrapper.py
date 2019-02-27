__author__ = 'Zheng ZHANG'

import networkx as nx


class IGraphWrapper(object):
    """
    graph.union does not handle edge attributes
    """

    def __init__(self, Name='Graph'):
        self.name = Name
        self.graph = nx.DiGraph()

    def addPair(self, w1, w2):
        # used by wordpair_generator.py
        # Naive way of generating word co-occurrence network, DO NOT USE IT!
        """
        :param w1: str
        :param w2: str
        :return: None
        if edge(w1,w2) not in graph, add the edge and set its property weight to 1
        else update the weight by add 1
        """
        if self.graph.has_edge(w1, w2):
            self.graph[w1][w2]['weight'] += 1
        else:
            self.graph.add_edge(w1, w2, weight=1)

    def add_edges_from_file(self, path):
        # used by our method
        self.graph = nx.read_weighted_edgelist(path, create_using=nx.DiGraph(), nodetype=int)

    def add_edges_from_list(self, edges):
        # used by graph_generator.py
        # A little bit better naive way of generating word co-occurrence network, DO NOT USE IT!
        # edges: [(k.split()[0], k.split()[1], d[k]) for k in d]
        self.graph.add_weighted_edges_from(edges)

    def getGraph(self):
        return self.graph
