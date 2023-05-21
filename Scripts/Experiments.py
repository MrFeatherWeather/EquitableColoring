import os

import networkx as nx
import random
import Parser as prs
import gurobipy as gb
from gurobipy import GRB
import ModelConstructors as models
import math
import Heuristiken as heur
import Relabeling as relab
import itertools
def partitonMin(G:nx.graph):
    minCutVal = G.number_of_edges()
    minCut = None
    n = G.number_of_nodes()
    for i in range(100):
        newCut = random.sample(range(n), int(n/2))
        newVal = nx.cut_size(G,newCut)
        if newVal < minCutVal:
            minCut = newCut
            minCutVal = newVal
    print(minCutVal)
    return minCut

#D = prs.readDimacs("../Instances/DSJC250.1.col")

#print(nx.cut_size(D,ModelConstructors.maxCutClique(D,10)))
#print(nx.cut_size(D,nx.max_weight_clique(D,weight=None)))
def setStartSol(yMod:dict,xMod:dict, y:dict,x:dict):

    for key, value in y.items():
        if key[0] == 0:
            continue
        yMod[key].Start = value


    for key, value in x.items():
        if key[0] == 0:
            continue
        xMod[key].Start = value


def createPOPCont(g:nx.graph,H,q=0,equit=True):
    M = gb.Model("POPImp")
    n = g.number_of_nodes()

    y = {}

    for i in range(H):
        y[(q,i)] = M.addVar(vtype=GRB.CONTINUOUS,obj = 1)

    for v in g.nodes:
        if v != q:
            y[(v,0)] = M.addVar(vtype=GRB.CONTINUOUS)


        for i in range(1,H):
            if v != q:
                y[(v,i)] = M.addVar(vtype=GRB.CONTINUOUS)
            M.addConstr(y[(v,i-1)]-y[(v,i)] >= 0)
            M.addConstr(y[(q, i - 1)] - y[(v, i-1)] >= 0)

        M.addConstr(y[(v, H-1)] == 0)


    for u,v in g.edges:
        M.addConstr(y[(u, 0)] + y[(v, 0)] >=  1)#2-y[(q,0)])
        for i in range(1,H):
            M.addConstr(y[(u,i-1)]-y[(u,i)]+y[(v,i-1)]-y[(v,i)] <= 1)#y[(q,i-1)])

    #for v in nx.neighbors(g,q):
    #    for i in range(H-1):
    #        M.addConstr(y[(q,i+1)] - y[(v,i)] >= 0)

    for i in range(H*equit):

        floor_sum = 0

        for v in g.nodes:

            floor_sum += (y[(v,i-1)] if i > 0 else 1)-y[(v,i)]

        ceil_sum = floor_sum.copy()

        for j in range(i,H):
            floor_sum -= math.floor(n/(j+1))*((y[(q,j-1)] if j > 0 else 1)-y[(q,j)])

            ceil_sum -= math.ceil(n/(j+1))*((y[(q,j-1)] if j > 0 else 1)-y[(q,j)])


        t1 = M.addConstr(floor_sum >= 0)
        t2 = M.addConstr(ceil_sum <= 0)


    #M.addConstr(y[(q,0)] == 0.9)
    #for i in range(H):
    #    for v in g.nodes:
    #        if v !=q and v != g.number_of_nodes()-1:
    #            M.addConstr(y[(v,i)] == y[(v+1,i)])
    M._H = H
    M._G = g
    M._q = q
    M._type = "POP"
    M.setAttr("ObjCon", 1)
    M.update()
    return M,y

def createASSCont(g:nx.Graph,H):
    M = gb.Model("ASS")
    n = g.number_of_nodes()

    w = []
    x = {}

    for v in g.nodes:

        node_sum = 0

        for i in range(H):
            variable = M.addVar(vtype = GRB.CONTINUOUS)
            x[(v,i)] = variable
            node_sum += variable

        M.addConstr(node_sum == 1)

    for i in range(H):
        w_i = M.addVar(obj=1, vtype=GRB.CONTINUOUS)
        w.append(w_i)
        if i >= 1:
            M.addConstr(w[i] <= w[i-1])

        for u, v in g.edges:
            M.addConstr(x[(u,i)]+x[(v,i)] <= w_i)

    for i in range(H-1):

        floor_sum = 0

        for v in g.nodes:

            floor_sum += x[(v,i)]

        ceil_sum = floor_sum.copy()

        for j in range(i,H-1):
            floor_sum -= math.floor(n/(j+1))*(w[j]-w[j+1])

            ceil_sum -= math.ceil(n/(j+1))*(w[j]-w[j+1])

        floor_sum -= w[H - 1]
        ceil_sum -= w[H - 1]
        M.addConstr(floor_sum >= 0)
        M.addConstr(ceil_sum <= 0)

    M._H = H
    M._G = g
    M._type = "ASS"
    M.update()
    return M,x,w


#for i, f in enumerate(os.listdir("../Instances/Reserve")):
#    if not f.endswith(".col"):
#        continue
#    G = prs.readDimacs("../Instances/Reserve/"+f)
#
#    H = max(heur.FJK3(G, nx.greedy_color(G, "DSATUR")).keys()) + 1
#    print(H)


def InstanceTester(modelList,G):
    modelMap = {
        "ASS":models.createASS,
        "POP":models.createPOP,
        "POPHyb":models.createPOPHyb,
        "REP":models.createRep
    }
    results = []



    print("Caclulate heuristic solution")
    H = max(heur.FJK3(G,nx.greedy_color(G,strategy="DSATUR")).keys())+1

    print(H)
    print("Calculate Clique Bound")
    cl,clRep = models.maxCutClique(G,H)
    print("CL1:",len(cl),nx.cut_size(G,cl))
    print("CL2:", len(clRep), nx.cut_size(G, clRep))
    print(clRep)
    #cl = clRep
    print("Construct Model")
    #print(G.degree(cl))
    #G, cl = relab.relabelModel(G, cl, True, H)
    #UPDATE NECESSARY FROM MODELTESTER
    for MStr in modelList:
        if "POP" in MStr:
            # max(G.degree,key=lambda x: x[1])[0]max(cl,key=G.degree)

            M, var ,*other = modelMap[MStr](G, H, q=cl[0], strength=False,symm = False,equit=True)

        elif "ASS" in MStr:
            M, var, *other = modelMap[MStr](G, H,symm = False,equit = True)
        else:
            G, clRep = relab.relabelModel(G, clRep)
            M, var, *other = modelMap[MStr](G, H, lowBound=len(clRep),symm = True)

        models.precolorClique(M,var,clRep if "REP" in MStr else cl)
        M.setParam("TimeLimit",3600)
        M.setParam("Seed",0)
        M.setParam("Threads", 1)



        M.optimize()


for i in range(-1):
    #G = nx.fast_gnp_random_graph(120,0.1,seed=i)
    #G: nx.Graph = prs.readDimacs("../Instances/Error/le450_15a.col")
    G: nx.Graph = nx.fast_gnp_random_graph(200,0.1)
    G.add_edges_from((u,v) for u,v in itertools.combinations(range(6),2))
    numbCliq = 0
    for i in range(1,numbCliq+1):

        G.add_edges_from((u,v) for u,v in itertools.combinations(range(i*int(300/(numbCliq+1)),i*int(300/(numbCliq+1))+7),2))

    InstanceTester(["POP"],G)

#G = prs.readDimacs("../Instances/le450_25c.col")
#H = max(heur.FJK3(G,nx.greedy_color(G,"DSATUR")).keys())+1
#models.maxCutClique(G,H)

G = nx.complete_graph(3)
M,vars = createPOPCont(G,3)
M.optimize()
print(vars)