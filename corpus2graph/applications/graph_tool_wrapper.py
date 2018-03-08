__author__ = 'Ruiqing YIN'

from graph_tool.all import *
import numpy as np
class GraphToolWrapper(object):
    def __init__(self,
                 Name='Graph'):
        self.name = Name
        self.idx ={}
        self.curr_id = 0
        self.graph = Graph(directed=True)
        self.vname = self.graph.new_vertex_property("string")  # vertice property: store the corresponding word
        self.eweight = self.graph.new_edge_property("int64_t") # edge weight property: store the cooccurrence

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
            v = self.graph.add_vertex()
            self.vname[v] = w
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
        e = self.graph.edge(id1, id2)
        if e is None:
            s = self.graph.vertex(id1)
            t = self.graph.vertex(id2)
            e = self.graph.add_edge(s, t)
            self.eweight[e] = 1

        else:
            self.eweight[e] += 1

    def addEdgesFromFile(self, path):
        # used by our method
        file = open(path, 'r')
        edges = [[triple.split()[0], triple.split()[1], triple.split()[2]] for triple in file]
        self.vname = self.graph.add_edge_list(edges, hashed=True, string_vals=True, eprops=[self.eweight])

    def addEdgesFromList(self, pl, wl):
        #self.idx = { word: ind for ind, word in enumerate(wl)}
        #edges = np.array([[self.idx[s],self.idx[t], w] for s,t,w in pl])
        # self.graph.add_vertex(len(wl))
        # self.graph.add_edge_list(edges, eprops=[self.eweight])
        edges = [[s, t, w] for s, t, w in pl]
        self.vname = self.graph.add_edge_list(edges, hashed=True, string_vals=True, eprops=[self.eweight])


    def getGraph(self):
        return self.graph




