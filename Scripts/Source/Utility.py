import networkx as nx
import gurobipy as gb

def getColoringFromModel(M:gb.Model,m_vars:dict):
    coloring = {}
    for (i,j),val in m_vars.items():

        if M._type == "ASS" or M._type == "REP":
            if val.X == 1:
                if j not in coloring:
                    coloring[j] = []
                coloring[j].append(i)

        else:
            if (j == 0 and val.X == 0) or (j > 0 and m_vars[(i,j-1)].X-val.X == 1):
                if j not in coloring:
                    coloring[j] = []
                coloring[j].append(i)
    return coloring







def checkColoringEq(G:nx.Graph,c_groups:dict,eqCheck = True)->bool: #Überprüft ob die Färbung eine gültige equitable Färbung ist
    if eqCheck:
        frequencies = [len(c) for c in c_groups.values()]
        frequencies.sort()
        if frequencies[0]+1 < frequencies[-1]:
            print("Not balanced:", frequencies)
            return False
    coloring = [0]*G.number_of_nodes()
    colored = set()
    for c in c_groups.values():
        for v in c:
            coloring[v] = c
            colored.add(v)
    if len(colored) < G.number_of_nodes():
        print("Not all nodes colored")
        return False

    for u,v in G.edges:
        if coloring[u] == coloring[v]:
            print("Conflict:",u,",",v)
            return False
    return True
