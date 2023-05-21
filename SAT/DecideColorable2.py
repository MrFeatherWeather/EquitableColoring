import networkx as nx
import LogicFormula as Logic



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





