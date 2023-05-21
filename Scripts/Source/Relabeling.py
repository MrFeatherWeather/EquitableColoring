#Author: Daniel Faber

import networkx as nx
import numpy as np
import Heuristiken as heur

#Umindexierung der Knoten, die für manche Modelle benötigt wird
def relabelModel(G:nx.Graph,cl,H=0,POP=False): #Umindexiert Knoten eines Graphen abhängig vom Modell und der Clique
    #for the POP models, q = maxColor, so we need to guarantee that 1...H-1 are neighbours of q
    if POP:
        print("POP Relabel")
        if H == 0:
            print("No upper bound")
            return None,None
        mDegInd = np.argmax([G.degree(cl[i]) for i in range(len(cl))])

        cl[-1],cl[mDegInd] = cl[mDegInd],cl[-1]
        print(G.degree(cl))
    #because we precolor clique, with 1...Clq, the indices of the clique must be 1...Clq
    mapping1 = relabelMapping(cl,range(len(cl)))

    cl = list(range(len(cl)))
    G = nx.relabel_nodes(G, mapping1, copy=True)
    if POP and H > len(cl):
        if len(list(G.neighbors(cl[-1]))) < H-len(cl):
            print("Not enough neighbours")
            return None,None
        mapping2 = relabelMapping(list(G.neighbors(cl[-1]))[:H-len(cl)],range(len(cl),H))

        G = nx.relabel_nodes(G, mapping2, copy=True)

    return G,cl




def relabelMapping(nds:list,rng:range):#Nimmt eine Liste von Knotenindizes und ein Intevall als Paramter und vertauscht die Indizes im Graphen so, dass die Knoten mit den Indizes aus der Liste danach die Indizes aus dem Intervall besitzen
    a,b = rng[0],rng[-1]
    if b-a+1 != len(nds):
        print("Wrong range size")
        return
    missing1 = list(rng)
    missing2 = []
    for v in nds:
        if a <= v <= b:
            missing1.remove(v)
        else:
            missing2.append(v)
    listA = nds+missing1
    listB = list(rng)+missing2

    mapping = {listA[i]:listB[i] for i in range(len(listA))}
    return mapping
def relabelNodes(G:nx.Graph,cl):#Umindexiert die Knoten in einer Clique
    cl.sort()
    missing = []
    lastInd = 0
    for i,v in enumerate(cl):

        if v >= len(cl):
            lastInd = i
            break
        if i == 0:
            missing += list(range(v))
        else:
            missing += list(range(cl[i-1]+1,v))


    missing += list(range(cl[lastInd-1]+1 if lastInd > 0 else 0,len(cl)))

    mapping = {missing[i]:cl[lastInd+i] for i in range(len(missing))}
    mapping.update({cl[lastInd+i]:missing[i] for i in range(len(missing))})
    G_relabel = nx.relabel_nodes(G,mapping,copy=True)

    return G_relabel,list(range(len(cl)))


