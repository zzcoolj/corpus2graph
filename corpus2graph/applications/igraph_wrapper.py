__author__ = 'Ruiqing YIN'

from igraph import *

class IGraphWrapper(object):
    def __init__(self,
                 Name='Graph'):
        self.name = Name
        self.idx ={}
        self.curr_id = 0
        self.graph = Graph()
        self.graph.vs["word"] = []  # vertice property: store the corresponding word
        self.graph.es["weight"] = [] # edge weight property: store the cooccurrence

    def getWordId(self,w):
        '''
        :param w: string
        :return: int word id
        if word is in graph, return its id
        else add word to the graph (generate a new int id and add it to graph
        then set its property to word) return the corresponding id
        '''
        if w in self.idx:
            return self.idx[w]
        else:
            self.idx[w] = self.curr_id
            self.curr_id += 1
            v = self.graph.add_vertices(1)
            self.graph.vs["word"].append(w)
            return self.idx[w]

    def addPairs(self, w1, w2):
        '''
        :param w1: str
        :param w2: str
        :return: None
        if edge(w1,w2) not in graph, add the edge and set its property weight to 1
        else update the weight by add 1
        '''
        id1 = self.getWordId(w1)
        id2 = self.getWordId(w2)
        e = self.graph.get_eid(id1, id2, error=False)
        if e == -1:
            e = self.graph.add_edges((id1, id2))
            self.graph.es["weight"].append[1]
        else:
            self.graph.es["weight"][e] += 1

    def getGraph(self):
        return self.graph




