import networkx as nx
import LogicFormula as Logic
import SatParser
import math
import Preprocessing as preproc
from BaseColoring import ColoringModel

class ASS_SAT(ColoringModel):
    def __init__(self):
        self.type = "ASS"
        self.x = {}
    def k_coloring_formula(self,G: nx.Graph, k: int):
        sat_formulation = Logic.LogicFormula()
        x = {}
        for v in G.nodes():
            x.update({(v, i): sat_formulation.addVar() for i in range(k)})
            Logic.at_least_1_const([x[v, i] for i in range(k)], sat_formulation)

        for v, w in G.edges():
            for i in range(k):
                Logic.at_most_1_const([x[v, i], x[w, i]], sat_formulation)
        self.x = x.copy()

        if self.clq is not None:
            preproc.precolorClique(self,sat_formulation,self.clq)


        with open("SAT.cnf", "w") as f:
            f.write(sat_formulation.parseAsString())


        return x

    def coloring_from_vars(self,vars):

        #for v in range(max(self.x.keys(),key=lambda x: x[0])[0]):
        #    print(v,[vars[self.x[v, i]] for i in range(max(self.x.keys(), key=lambda x: x[1])[1] + 1)])
        #    print(v, [self.x[v, i] for i in range(max(self.x.keys(), key=lambda x: x[1])[1] + 1)])
        return SatParser.varsToColor(vars,self.x)


class POP_SAT(ColoringModel):
    def __init__(self):
        self.type = "POP"
        self.x = {}

    def k_coloring_formula(self,G: nx.Graph, k: int):
        sat_formulation = Logic.LogicFormula()
        y = {}
        for v in G.nodes():
            y.update({(v, i): sat_formulation.addVar() for i in range(k)})
            sat_formulation.addClause([-y[v, k - 1]])
            for i in range(1, k):
                Logic.at_least_1_const([y[v, i - 1], -y[v, i]], sat_formulation)

        for v, w in G.edges():
            Logic.at_least_1_const([y[v, 0], y[w, 0]], sat_formulation)
            for i in range(1, k):
                Logic.at_most_1_const([y[v, i - 1], -y[v, i], y[w, i - 1], -y[w, i]], sat_formulation)
        self.x = y.copy()
        if self.clq is not None:
            preproc.precolorClique(self,sat_formulation,self.clq)
        with open("SAT.cnf", "w") as f:
            f.write(sat_formulation.parseAsString())

        return y

    def coloring_from_vars(self,vars):
        #for v in range(max(self.x.keys(),key=lambda x: x[0])[0]):
        #    print(v,[vars[self.x[v, i]] for i in range(max(self.x.keys(), key=lambda x: x[1])[1] + 1)])
        #    print(v, [self.x[v, i] for i in range(max(self.x.keys(), key=lambda x: x[1])[1] + 1)])
        return SatParser.varsToColor_POP(vars,self.x)
class POPHyb_SAT(ColoringModel):
    def __init__(self):
        self.type = "POPH"
        self.x = {}
        self.y = {}
    def k_coloring_formula(self,G: nx.Graph, k: int,clique = None):
        sat_formulation = Logic.LogicFormula()
        y = {}
        x = {}
        for v in G.nodes():
            y.update({(v, i): sat_formulation.addVar() for i in range(k)})
            sat_formulation.addClause([-y[v, k - 1]])
            x.update({(v, i): sat_formulation.addVar() for i in range(k)})
            sat_formulation.addClauses([[x[v,0],y[v,0]],[-x[v,0],-y[v,0]]])
            for i in range(1, k):
                Logic.at_least_1_const([y[v, i - 1], -y[v, i]], sat_formulation)
                sat_formulation.addClauses([
                    [-x[v, i], y[v, i-1]],
                    [-x[v, i], -y[v, i]],
                    [x[v, i], -y[v, i-1],y[v,i]]
                ])

        for v, w in G.edges():
            for i in range(k):
                Logic.at_most_1_const([x[v, i], x[w, i]], sat_formulation)

        self.y = y.copy()
        self.x = x.copy()

        if self.clq is not None:
            preproc.precolorClique(self,sat_formulation,self.clq)

        with open("SAT.cnf", "w") as f:
            f.write(sat_formulation.parseAsString())


        return y,x

    def coloring_from_vars(self,vars):
        return SatParser.varsToColor(vars,self.x)
def k_colorability(G: nx.Graph, k: int):
    n = G.number_of_nodes()
    m = G.number_of_edges()
    sat_formulation = Logic.LogicFormula()
    x = {}
    for v in G.nodes():
        x.update({(v,i):sat_formulation.addVar() for i in range(k)})
        Logic.at_least_1_const([x[v,i] for i in range(k)],sat_formulation)

    for v,w in G.edges():
        for i in range(k):
            Logic.at_most_1_const([x[v,i],x[w,i]],sat_formulation)
    with open("SAT.cnf", "w") as f:
        f.write(sat_formulation.parseAsString())

    return x

def k_colorability_pop(G: nx.Graph, k: int):
    sat_formulation = Logic.LogicFormula()
    y = {}
    for v in G.nodes():
        y.update({(v,i):sat_formulation.addVar() for i in range(k)})
        sat_formulation.addClause([-y[v,k-1]])
        for i in range(2,k):
            Logic.at_least_1_const([y[v,i-1],-y[v,i]],sat_formulation)

    for v,w in G.edges():
        Logic.at_least_1_const([y[v,0],y[w,0]],sat_formulation)
        for i in range(1,k):
            Logic.at_most_1_const([y[v,i-1],-y[v,i],y[w,i-1],-y[w,i]],sat_formulation)
    with open("SAT.cnf", "w") as f:
        f.write(sat_formulation.parseAsString())


    return y


def exact_k_coloring_equit(G: nx.Graph, k: int):
    n = G.number_of_nodes()
    sat_formulation = Logic.LogicFormula()
    x = {}
    for v in G.nodes():
        x.update({(v, i): sat_formulation.addVar() for i in range(k)})
        Logic.at_least_1_const([x[v, i] for i in range(k)], sat_formulation)

    for v, w in G.edges():
        for i in range(k):
            Logic.at_most_1_const([x[v, i], x[w, i]], sat_formulation)
    for i in range(k):
        Logic.k_card_const([x[v,i] for v in G.nodes()],sat_formulation,int(math.floor(n/k)),atmost=False)
        Logic.k_card_const([x[v, i] for v in G.nodes()],sat_formulation, int(math.ceil(n / k)), atmost=True)
    with open("SAT.cnf", "w") as f:
        f.write(sat_formulation.parseAsString())

    return x


def precolorSAT():
    pass