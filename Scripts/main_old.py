import gurobipy as gb
from gurobipy import GRB
import networkx as nx
import colorsys
import math
import Parser as ps


def createAssign(g:nx.Graph):
    M = gb.Model("Assign")
    n = g.number_of_nodes()
    m = g.number_of_edges()
    H = max(g.degree, key = lambda x:x[1])[1]+1
    print("Upper Bound: ",H)
    w_vars = []
    v_vars = []



    for v in g.nodes:
        v_vars.append([])
        node_sum = 0

        for i in range(H):
            variable = M.addVar(vtype = GRB.BINARY, name = str(v)+","+str(i))
            v_vars[v].append(variable)
            node_sum += variable
            g.nodes[v][i] = variable
        M.addConstr(node_sum == 1)

    for i in range(H):
        w_i = M.addVar(obj = 1, vtype = GRB.BINARY, name = str(i))
        w_vars.append(w_i)
        if i >= 1:
            M.addConstr(w_vars[i] <= w_vars[i-1])

        for (u,v) in g.edges:
            M.addConstr(v_vars[u][i]+v_vars[v][i] <= w_i)


    for i in range(H-1):

        floor_sum = 0

        for v in g.nodes:
            print("Node",v)
            floor_sum += v_vars[v][i]

        ceil_sum = floor_sum.copy()

        for j in range(i,H-1):
            floor_sum -= math.floor(n/(j+1))*(w_vars[j]-w_vars[j+1])

            ceil_sum -= math.ceil(n/(j+1))*(w_vars[j]-w_vars[j+1])
        floor_sum -= math.floor(5 / H) * w_vars[H - 1]
        ceil_sum -= math.ceil(5 / H) * w_vars[H - 1]
        M.addConstr(floor_sum >= 0)
        M.addConstr(ceil_sum <= 0)

    M._H = H
    M._counter = 0
    #M.setParam("MIPFocus",2)
    return M,v_vars,w_vars

def createRep(g:nx.Graph):
    M = gb.Model("Representative")
    n = g.number_of_nodes()
    m = g.number_of_edges()


    for v in g.nodes:

        node_sum = 0
        for w in g.nodes:
            if not g.has_edge(v,w):
                variable = M.addVar(vtype=GRB.BINARY, name=str(w) + "," + str(v))
                node_sum += variable


        M.addConstr(node_sum >= 1)
    M.update()
    for u in g.nodes:
        M.getVarByName(str(u)+","+str(u)).setAttr("obj",1)

        for v,w in g.edges:
            if v not in g[u] and w not in g[u]:
                M.addConstr(M.getVarByName(str(u)+","+str(v)) + M.getVarByName(str(u)+","+str(w)) <= M.getVarByName(str(u)+","+str(u)))





    return M



def createPOP(g:nx.graph):
    M = gb.Model("Partial-Ordering")
    n = g.number_of_nodes()
    m = g.number_of_edges()
    H = 7#max(g.degree, key=lambda x: x[1])[1] + 1
    y = {}
    z = {}
    for v in g.nodes:

        y[(v,0)] = M.addVar(vtype=GRB.BINARY,obj=(v == 0))
        z[(v,0)] = M.addVar(vtype=GRB.BINARY)

        for i in range(1,H):
            y[(v,i)] = M.addVar(vtype=GRB.BINARY,obj=(v == 0))
            z[(v, i)] = M.addVar(vtype=GRB.BINARY)
            M.addConstr(y[(v,i-1)]-y[(v,i)] >= 0)
            M.addConstr(y[(v,i-1)]+z[(v,i)] == 1)
            M.addConstr(y[(0, i - 1)] - y[(v, i-1)] >= 0)

        M.addConstr(y[(v, H-1)] == 0)
        M.addConstr(z[(v, 0)] == 0)


    for u,v in g.edges:
        for i in range(H):
            M.addConstr(y[(u,i)]+y[(v,i)]+z[(u,i)]+z[(v,i)] >= 1)

    #M.setParam("MIPFocus",3)
    max_clique = nx.max_weight_clique(dimG,weight = None)[0]
    print(max_clique)
    for i, v in enumerate(max_clique):
        print("Farbe",i,"Knoten  ",v)
        M.addConstr(y[(v, i)] == 0)
        M.addConstr(z[(v, i)] == 0)

    return M,y,z

def createPOPRed(g:nx.graph):
    M = gb.Model("Partial-Ordering-Reduced")
    n = g.number_of_nodes()
    m = g.number_of_edges()
    H = 7 #max(g.degree, key=lambda x: x[1])[1] + 1
    y = {}

    for v in g.nodes:

        y[(v,0)] = M.addVar(vtype=GRB.BINARY,obj=(v == 0))


        for i in range(1,H):
            y[(v,i)] = M.addVar(vtype=GRB.BINARY,obj=(v == 0))
            M.addConstr(y[(v,i-1)]-y[(v,i)] >= 0)
            M.addConstr(y[(0, i - 1)] - y[(v, i-1)] >= 0)

        M.addConstr(y[(v, H-1)] == 0)



    for u,v in g.edges:
        M.addConstr(y[(u, 0)] + y[(v, 0)] >= 1)
        for i in range(1,H):
            M.addConstr(y[(u,i-1)]-y[(u,i)]+y[(v,i-1)]-y[(v,i)] <= 1)

    #M.setParam("MIPFocus",3)
    max_clique = nx.max_weight_clique(dimG,weight = None)[0]
    print(max_clique)
    for i, v in enumerate(max_clique):
        print("Farbe",i,"Knoten  ",v)
        M.addConstr(y[(v, i)] == 0)
        if i > 0:
            M.addConstr(y[(v, i-1)] == 1)
    M.setParam("cuts",3)
    return M,y

def createPOPDec(g:nx.graph):
    M = gb.Model("Partial-Ordering-Reduced")
    n = g.number_of_nodes()
    m = g.number_of_edges()
    H = 6
    y = {}

    for v in g.nodes:

        y[(v,0)] = M.addVar(vtype=GRB.BINARY)


        for i in range(1,H):
            y[(v,i)] = M.addVar(vtype=GRB.BINARY)
            M.addConstr(y[(v,i-1)]-y[(v,i)] >= 0)
            M.addConstr(y[(0, i - 1)] - y[(v, i-1)] >= 0)

        M.addConstr(y[(v, H-1)] == 0)

    M.addConstr(y[(0,H-2)] == 1)
    M.addConstr(y[(0, H -1)] == 0)
    for u,v in g.edges:
        M.addConstr(y[(u, 0)] + y[(v, 0)] >= 1)
        for i in range(1,H):
            M.addConstr(y[(u,i-1)]-y[(u,i)]+y[(v,i-1)]-y[(v,i)] <= 1)


    max_clique = nx.max_weight_clique(dimG,weight = None)[0]
    print(max_clique)
    for i, v in enumerate(max_clique):
        print("Farbe",i,"Knoten  ",v)
        M.addConstr(y[(v, i)] == 0)
        if i > 0:
            M.addConstr(y[(v, i-1)] == 1)

    return M,y

def createPOPLwBound(g:nx.graph):
    M = gb.Model("Partial-Ordering-Reduced")
    n = g.number_of_nodes()
    m = g.number_of_edges()
    H = 7 #max(g.degree, key=lambda x: x[1])[1] + 1
    y = {}

    for v in g.nodes:

        y[(v,0)] = M.addVar(vtype=GRB.BINARY,obj=(v == 0))


        for i in range(1,H):
            y[(v,i)] = M.addVar(vtype=GRB.BINARY,obj=(v == 0))
            M.addConstr(y[(v,i-1)]-y[(v,i)] >= 0)
            M.addConstr(y[(0, i - 1)] - y[(v, i-1)] >= 0)

        M.addConstr(y[(v, H-1)] == 0)



    for u,v in g.edges:
        M.addConstr(y[(u, 0)] + y[(v, 0)] >= 1)
        for i in range(1,H):
            M.addConstr(y[(u,i-1)]-y[(u,i)]+y[(v,i-1)]-y[(v,i)] <= 1)

    #M.setParam("MIPFocus",3)
    max_clique = nx.max_weight_clique(dimG,weight = None)[0]
    print(max_clique)
    for i, v in enumerate(max_clique):
        print("Farbe",i,"Knoten  ",v)
        M.addConstr(y[(v, i)] == 0)
        if i > 0:
            M.addConstr(y[(v, i-1)] == 1)

    return M,y

dimG = ps.readDimacs("../Instances/2-FullIns_5.col")
g = nx.fast_gnp_random_graph(200,0.08 , seed=12355)
colored = g.copy()


#M,v_vars,w_vars = createAssign(dimG)
MPOPRed,yRed = createPOPRed(dimG)
#MPOP,y,z = createPOP(dimG)
#MPOPDec = createPOPDec(dimG)[0]

#MRep = createRep(g)
def cliqueCuts(m,where):
    if where == GRB.Callback.MIPNODE and m.cbGet(GRB.Callback.MIPNODE_STATUS) == GRB.OPTIMAL:
        m._counter += 1
        if m._counter % 20 == 0:


            for i in range(m._H):
                for v,data in g.nodes(data=True):

                    if 1e-5 < m.cbGetNodeRel(data[i]) < 1-1e-5:

                        clique = max(list(nx.find_cliques(g,nodes=[v])),key=lambda x:len(x))

                        #cliqueList = list(nx.find_cliques(g,nodes=[v]))
                        #for clique in cliqueList:
                        if len(clique) >= 4:

                            for i in range(m._H):
                                ivars = 0
                                for vic in clique:
                                    ivars += g.nodes[vic][i]
                                m.cbCut(ivars <= 1)



MPOPRed.optimize()
#MPOPDec.optimize()
for v,i in y:
    if y[(v,i)].X + z[(v,i)].X == 0:
        print("Knoten",v,"Farbe",i)
def checkBal():
    for i in range(M._H-1):

        floor_sum = 0
        for v in g.nodes:
            floor_sum += v_vars[v][i].X
        ceil_sum = floor_sum
        for j in range(i, M._H-1):
            floor_sum -= math.floor(5 / (j + 1)) * (w_vars[j].X - w_vars[j + 1].X)

            ceil_sum -= math.ceil(5 / (j + 1)) * (w_vars[j].X - w_vars[j + 1].X)
        floor_sum -= math.floor(5 / M._H) * w_vars[M._H-1].X
        ceil_sum -= math.ceil(5 / M._H) * w_vars[M._H-1].X
        print("Floor: ",floor_sum)
        print("Ceil ",ceil_sum)

#checkBal()

def printColors():
    for v in range(len(v_vars)):
        for i in range(len(v_vars[0])):
            if v_vars[v][i].X == 1:
                print("Variable %d: %d" %(v,i))


def colorGraph():

    col = int(M.getObjective().getValue())
    for i in range(col):

        rgbcolor = '#%02x%02x%02x' % tuple([round(c*255) for c in colorsys.hsv_to_rgb(i/col,1,1)])
        print(rgbcolor)
        for v in range(len(v_vars)):
            if v_vars[v][i].X == 1:

                colored.nodes[v]["graphics"] = {"hasFill":True,"fill":rgbcolor}

    nx.write_gml(colored, "../coloring.gml")
#printColors()
#colorGraph()
#M.write("out.sol")
