__author__ = 'Ruiqing YIN'

from igraph import *


class IGraphWrapper(object):
    """
    graph.union does not handle edge attributes
    """

    def __init__(self, Name='Graph'):
        self.name = Name
        self.idx = {}
        self.curr_id = 0
        self.graph = Graph()
        self.graph.vs["word"] = []  # vertice property: store the corresponding word
        self.graph.es["weight"] = []  # edge weight property: store the cooccurrence

    def vertex_exist(self, w):
        '''
        :param w: string
        :return: int word id
        if word is in graph, return its id
        else add word to the graph (generate a new int id and add it to graph
        then set its property to word) return the corresponding id
        '''
        if w in self.idx:
            return True
        else:
            self.idx[w] = self.curr_id
            self.curr_id += 1
            return False

    def addPair(self, w1, w2):
        '''
        :param w1: str
        :param w2: str
        :return: None
        if edge(w1,w2) not in graph, add the edge and set its property weight to 1
        else update the weight by add 1
        '''
        w1_exist = self.vertex_exist(w1)
        w2_exist = self.vertex_exist(w2)
        if w1_exist and w2_exist:
            e = self.graph.get_eid(w1, w2, error=False)
            if e != -1:
                self.graph.es[e]["weight"] += 1
            else:
                self.graph.add_edge(w1, w2, weight=1)
        else:
            if not w1_exist:
                self.graph.add_vertex(w1)
            if not w2_exist:
                self.graph.add_vertex(w2)
            self.graph.add_edge(w1, w2, weight=1)

    def getGraph(self):
        return self.graph
