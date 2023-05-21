#Author: Daniel Faber

import gurobipy as gb
from gurobipy import GRB
import networkx as nx
import math
import Parser as prs

#Dieses Modul konstruiert die ganzzahligen Programme für das equitable Färbungsproblem
#Bemerkung: Einige Modelle benötigen bestimmtes Preprocessing(z.b. benötigt das asymmetrische POP-Modell bestimmtes Relabeling)
#Die Funktionen sollten deshalb nicht direkt benutzt sondern nur über die Funktionen in "Evaluation" benutzt werden
def createASSOld(g:nx.Graph,H,equit = True):#(Veraltete Funktion)
    M = gb.Model("ASS")
    n = g.number_of_nodes()
    m = g.number_of_edges()
    w = []
    x = {}

    for v in g.nodes:

        node_sum = 0

        for i in range(H):
            variable = M.addVar(vtype = GRB.BINARY)
            x[(v,i)] = variable
            node_sum += variable

        M.addConstr(node_sum == 1)
        print("\r Adding variables: "+str(v/n), sep=' ', end='')

    for i in range(H):
        w_i = M.addVar(obj=1, vtype=GRB.BINARY)
        w.append(w_i)
        if i >= 1:
            M.addConstr(w[i] <= w[i-1])

        M.addConstrs(x[(u, i)] + x[(v, i)] <= w_i for u, v in g.edges)

        print("\r Adding edge constraints: " + str((i+1)/(H)), sep=' ', end='')

    for i in range(equit*H-1):

        floor_sum = sum(x[(v,i)] for v in g.nodes)

        ceil_sum = floor_sum.copy()

        floor_sum -= sum(math.floor(n / (j + 1)) * (w[j] - w[j + 1]) for j in range(i, H-1))

        ceil_sum -= sum(math.ceil(n / (j + 1)) * (w[j] - w[j + 1]) for j in range(i, H-1))

        floor_sum -= math.floor(n/H)*w[H - 1]
        ceil_sum -= math.ceil(n/H)*w[H - 1]
        M.addConstr(floor_sum >= 0)
        M.addConstr(ceil_sum <= 0)
        print("\r Adding equitability constraints: " + str(i / H), sep=' ', end='')

    M._H = H
    M._G = g
    M._type = "ASS"
    M.update()
    return M,x,w

def createASS(g:nx.Graph,H,equit=True,symm=False,equitConst=0):#Konstruiert das Assignment-Modell. Die Parameter bestimmen die Variante des Modells
    #equit: Equitables oder klassiches Modell, symm:Asymmetriebedingungen, EquitConst: Variante der Equitability Constraints

    M = gb.Model("ASS")
    n = g.number_of_nodes()

    w = []
    x = {}

    for v in g.nodes:

        node_sum = 0

        for i in range(H):
            variable = M.addVar(vtype = GRB.BINARY)
            x[(v,i)] = variable
            node_sum += variable

        M.addConstr(node_sum == 1)
        print("\r Adding variables: " + str(v / n), sep=' ', end='')

    for i in range(H):
        w_i = M.addVar(obj=1, vtype=GRB.BINARY)
        w.append(w_i)
        if i >= 1:
            M.addConstr(w[i] <= w[i-1])

        M.addConstrs(x[(u, i)] + x[(v, i)] <= w_i for u, v in g.edges)

        print("\r Adding edge constraints: " + str((i + 1) / (H)), sep=' ', end='')
    if equitConst == 0:
        for i in range(-1 + H * equit):
            floor_sum = sum(x[(v, i)] for v in g.nodes)

            ceil_sum = floor_sum.copy()

            floor_sum -= sum(math.floor(n / (j + 1)) * (w[j] - w[j + 1]) for j in range(i, H - 1))

            ceil_sum -= sum(math.ceil(n / (j + 1)) * (w[j] - w[j + 1]) for j in range(i, H - 1))

            floor_sum -= math.floor(n / H) * w[H - 1]
            ceil_sum -= math.ceil(n / H) * w[H - 1]
            M.addConstr(floor_sum >= 0)
            M.addConstr(ceil_sum <= 0)
            print("\r Adding equitability constraints: " + str(i / H), sep=' ', end='')
    else:
        s = []
        for i in range(-1+H*equit):


            s.append(M.addVar(vtype = GRB.BINARY,lb=0,ub=1))

            floor_sum = sum(x[(v,i)] for v in g.nodes)

            floor_sum -= sum(math.floor(n / (j + 1)) * (w[j] - w[j + 1]) for j in range(i, H-1))

            floor_sum -= (math.floor(n/H)*w[H - 1] + s[i])

            M.addConstr(floor_sum == 0)
            print("\r Adding equitability constraints: " + str(i / H), sep=' ', end='')

    if symm:
        for v in range(H):

            for i in range(v+1,H):
                M.addConstr(x[(v,i)] == 0)
            print("\r Adding symmetry-breaking constraints: " + str((v + 1) / n), sep=' ', end='')
    M._H = H
    M._G = g
    M._type = "ASS"
    M.update()
    return M,x,w

def createRep(g:nx.Graph, H,symm = True,lowBound=1):#Konstruiert das Assignment-Modell. Die Parameter bestimmen die Variante des Modells
   #symm:Asymmetriebedingungen
    M = gb.Model("Rep")
    n = g.number_of_nodes()
    x = {}
    for v in g.nodes:
        x[(v,v)] = M.addVar(vtype=GRB.BINARY, obj=1.0)
        node_sum = x[(v,v)]
        for u in nx.non_neighbors(g,v):
            if u < v or (u != v and not symm):
                variable = M.addVar(vtype=GRB.BINARY)
                x[(u,v)] = variable
                node_sum += variable

        M.addConstr(node_sum == 1)
        print("\r Adding variables: " + str(v / n), sep=' ', end='')
    M.update()
    for u in g.nodes:

        M.addConstrs(x[(u,v)] + x[(u,w)] <= x[(u,u)]
                     for v,w in g.subgraph(nx.non_neighbors(g,u)).edges if (v > u and w > u) or not symm)
        print("\r Adding edge constraints: " + str((u+1) / n), sep=' ', end='')
    Lw = math.floor(n/H)
    Uw = math.ceil(n/lowBound)
    ysum = 0
    y = {}
    z = {}
    for i in range(Lw,Uw+1):
        y[i] = M.addVar(vtype=GRB.BINARY)
        ysum += y[i]
        for u in g.nodes:
            z[(u,i)] = M.addVar(vtype=GRB.BINARY)
            M.addConstr(z[(u,i)] <= x[(u,u)])
            M.addConstr(z[(u, i)] <= y[i])
            M.addConstr(z[(u, i)] >= x[(u,u)]+y[i]-1)
    M.addConstr(ysum == 1)

    for u in g.nodes:

        ceil_sum = 0
        ceil_sum+=x[(u,u)]
        for v in nx.non_neighbors(g,u):
            if v > u or (v != u and not symm):
                ceil_sum += x[(u, v)]

        for i in range(Lw,Uw+1):
            ceil_sum -= i * z[(u,i)]


        floor_sum = ceil_sum.copy()
        floor_sum += 1

        M.addConstr(floor_sum >= 0)
        M.addConstr(ceil_sum <= 0)
        print("\r Adding equitability constraints: " + str(u / n), sep=' ', end='')

    M._H = H
    M._G = g
    M._type = "REP"
    M.update()
    return M,x


def createPOPOld(g:nx.graph, H,q=0):#(veraltete Funktion)
    M = gb.Model("POP")
    n = g.number_of_nodes()
    y = {}
    z = {}

    for i in range(H):
        y[(q, i)] = M.addVar(vtype=GRB.BINARY, obj=1)
        z[(q, i)] = M.addVar(vtype=GRB.BINARY)
    for v in g.nodes:
        if v != q:
            y[(v,0)] = M.addVar(vtype=GRB.BINARY)
            z[(v,0)] = M.addVar(vtype=GRB.BINARY)

        for i in range(1,H):
            if v != q:
                y[(v,i)] = M.addVar(vtype=GRB.BINARY)
                z[(v, i)] = M.addVar(vtype=GRB.BINARY)
            M.addConstr(y[(v,i-1)]-y[(v,i)] >= 0)
            M.addConstr(y[(v,i-1)]+z[(v,i)] == 1)
            M.addConstr(y[(q, i - 1)] - y[(v, i-1)] >= 0)

        M.addConstr(y[(v, H-1)] == 0)
        M.addConstr(z[(v, 0)] == 0)


    for u,v in g.edges:
        for i in range(H):
            M.addConstr(y[(u,i)]+y[(v,i)]+z[(u,i)]+z[(v,i)] >= 1)

    for i in range(H-1):

        floor_sum = n

        for v in g.nodes:

            floor_sum -= y[(v,i)]+z[(v,i)]

        ceil_sum = floor_sum.copy()

        for j in range(i,H):
            floor_sum -= math.floor(n/(j+1))*((y[(0,j-1)] if j > 0 else 1)-y[(q,j)])

            ceil_sum -= math.ceil(n/(j+1))*((y[(0,j-1)] if j > 0 else 1)-y[(q,j)])


        M.addConstr(floor_sum >= 0)
        M.addConstr(ceil_sum <= 0)

    M._H = H
    M._G = g
    M._q = q
    M._type = "POP"
    M.setAttr("ObjCon", 1)
    M.update()
    return M,y,z


def createPOPImpOld(g:nx.graph,H,q=0,equit=True,strength = True):#(veraltete Funktion)
    M = gb.Model("POPImp")
    n = g.number_of_nodes()

    y = {}

    for i in range(H):
        y[(q,i)] = M.addVar(vtype=GRB.BINARY,obj = 1)
        print("\r Adding variables: " + str(i / (H*n)), sep=' ', end='')
    for v in g.nodes:
        if v != q:
            y[(v,0)] = M.addVar(vtype=GRB.BINARY)


        for i in range(1,H):
            if v != q:
                y[(v,i)] = M.addVar(vtype=GRB.BINARY)
            M.addConstr(y[(v,i-1)]-y[(v,i)] >= 0)
            M.addConstr(y[(q, i - 1)] - y[(v, i-1)] >= 0)

        M.addConstr(y[(v, H-1)] == 0)
        print("\r Adding variables: " + str((i+1) / n), sep=' ', end='')



    M.addConstrs(y[(u, 0)] + y[(v, 0)] >= 2 - (y[(q, 0)] if strength else 1) for u,v in g.edges)
    print("\r Adding edge constraints: " + str(1 / H), sep=' ', end='')
    for i in range(1, H):
        M.addConstrs(y[(u, i - 1)] - y[(u, i)] + y[(v, i - 1)] - y[(v, i)] <= (y[(q, i - 1)] if strength else 1) for u,v in g.edges)
        print("\r Adding edge constraints: " + str((i + 1) / H), sep=' ', end='')

    if strength:
        for v in nx.neighbors(g,q):

            M.addConstrs(y[(q,i+1)] - y[(v,i)] >= 0 for i in range(H-1))

    for i in range(H*equit):

        floor_sum = sum((y[(v,i-1)] if i > 0 else 1)-y[(v,i)] for v in g.nodes)


        ceil_sum = floor_sum.copy()


        floor_sum -= sum(math.floor(n / (j + 1)) * ((y[(q, j - 1)] if j > 0 else 1) - y[(q, j)]) for j in range(i,H))
        ceil_sum -= sum(math.ceil(n/(j+1))*((y[(q,j-1)] if j > 0 else 1)-y[(q,j)]) for j in range(i,H))


        t1 = M.addConstr(floor_sum >= 0)
        t2 = M.addConstr(ceil_sum <= 0)
        print("\r Adding equitability constraints: " + str((i+1) / H), sep=' ', end='')


    M._H = H
    M._G = g
    M._q = q
    M._type = "POP"
    M.setAttr("ObjCon", 1)
    M.update()
    return M,y

def createPOP(g:nx.graph,H,q=0,equit=True,strength = True,symm = True, equitConst = 0):#Konstruiert das POP-Modell. Die Parameter bestimmen die Variante des Modells
    #equit: Equitables oder klassiches Modell, symm:Asymmetriebedingungen, EquitConst: Variante der Equitability Constraints, Strength: Verstäktes Modell
    M = gb.Model("POPImp")
    n = g.number_of_nodes()

    y = {}

    for i in range(H):
        y[(q,i)] = M.addVar(vtype=GRB.BINARY,obj = 1)
        print("\r Adding variables: " + str(i / (H*n)), sep=' ', end='')
    for v in g.nodes:
        if v != q:
            y[(v,0)] = M.addVar(vtype=GRB.BINARY)


        for i in range(1,H):
            if v != q:
                y[(v,i)] = M.addVar(vtype=GRB.BINARY)
            M.addConstr(y[(v,i-1)]-y[(v,i)] >= 0)
            M.addConstr(y[(q, i - 1)] - y[(v, i-1)] >= 0)

        M.addConstr(y[(v, H-1)] == 0)
        print("\r Adding variables: " + str((i+1) / n), sep=' ', end='')



    M.addConstrs(y[(u, 0)] + y[(v, 0)] >= 2 - (y[(q, 0)] if strength else 1) for u,v in g.edges)
    print("\r Adding edge constraints: " + str(1 / H), sep=' ', end='')
    for i in range(1, H):
        M.addConstrs(y[(u, i - 1)] - y[(u, i)] + y[(v, i - 1)] - y[(v, i)] <= (y[(q, i - 1)] if strength else 1) for u,v in g.edges)
        print("\r Adding edge constraints: " + str((i + 1) / H), sep=' ', end='')

    if strength:
        for v in nx.neighbors(g,q):

            M.addConstrs(y[(q,i+1)] - y[(v,i)] >= 0 for i in range(H-1))
    if equitConst == 0:

        for i in range(-1+H*equit):

            floor_sum = sum((y[(v,i-1)] if i > 0 else 1)-y[(v,i)] for v in g.nodes)


            ceil_sum = floor_sum.copy()


            floor_sum -= sum(math.floor(n / (j + 1)) * ((y[(q, j - 1)] if j > 0 else 1) - y[(q, j)]) for j in range(i,H))
            ceil_sum -= sum(math.ceil(n/(j+1))*((y[(q,j-1)] if j > 0 else 1)-y[(q,j)]) for j in range(i,H))


            t1 = M.addConstr(floor_sum >= 0)
            t2 = M.addConstr(ceil_sum <= 0)
            print("\r Adding equitability constraints: " + str((i+1) / H), sep=' ', end='')
    else:
        s = []
        for i in range(-1+H * equit):
            floor_sum = sum((y[(v, i - 1)] if i > 0 else 1) - y[(v, i)] for v in g.nodes)
            s.append(M.addVar(vtype=GRB.BINARY, lb=0, ub=1))


            floor_sum -= sum(
                math.floor(n / (j + 1)) * ((y[(q, j - 1)] if j > 0 else 1) - y[(q, j)]) for j in range(i, H))


            M.addConstr(floor_sum-s[i] == 0)

            print("\r Adding equitability constraints: " + str((i + 1) / H), sep=' ', end='')

    if symm:
        #for v in range(1,H):

            #M.addConstr(y[(v,v-1)] >= y[(q,v)])
            #print("\r Adding symmetry-breaking constraints: " + str((v + 1) / n), sep=' ', end='')
        for v in range(H):
            if v == q:continue
            M.addConstr(y[(v,v)] == 0)
            print("\r Adding symmetry-breaking constraints: " + str((v + 1) / n), sep=' ', end='')

    M._H = H
    M._G = g
    M._q = q
    M._type = "POP"
    M.setAttr("ObjCon", 1)
    M.update()
    return M,y

def createPOPHybOld(g: nx.graph, H, q=0, equit = True,strength = True):#(veraltete Funktion)
    M = gb.Model("POPHyb")
    n = g.number_of_nodes()
    y = {}
    for i in range(H):
        y[(q,i)] = M.addVar(vtype=GRB.BINARY,obj=1)
        print("\r Adding variables: " + str(i / (2 *H * n)), sep=' ', end='')
    for v in g.nodes:

        if v != q:
            y[(v, 0)] = M.addVar(vtype=GRB.BINARY)

        for i in range(1, H):
            if v != q:
                y[(v, i)] = M.addVar(vtype=GRB.BINARY)
            M.addConstr(y[(v, i - 1)] - y[(v, i)] >= 0)
            M.addConstr(y[(q, i - 1)] - y[(v, i - 1)] >= 0)

        M.addConstr(y[(v, H - 1)] == 0)
        print("\r Adding variables: " + str((i + 1) / (2*n)), sep=' ', end='')
    x = {}
    for v in g.nodes:
        x[(v,0)] = M.addVar(vtype=GRB.BINARY)
        M.addConstr(x[(v,0)] == 1-y[(v,0)])
        for i in range(1,H):
            x[(v, i)] = M.addVar(vtype=GRB.BINARY)
            M.addConstr(x[(v, i)] == y[(v, i-1)] - y[(v, i)])
        print("\r Adding variables: " + str((i + n + 1) / (2 * n)), sep=' ', end='')



    M.addConstrs(x[(u, 0)] + x[(v, 0)] <= (y[(q, 0)] if strength else 1) for u,v in g.edges)
    print("\r Adding edge constraints: " + str(1 / H), sep=' ', end='')
    for i in range(1, H):
        M.addConstrs(x[(u, i)] + x[(v, i)] <= (y[(q, 0)] if strength else 1) for u,v in g.edges)
        print("\r Adding edge constraints: " + str((i + 1) / H), sep=' ', end='')

    if strength:
        for v in nx.neighbors(g, q):
            for i in range(H - 1):
                M.addConstr(y[(q, i+1)] - y[(v, i)] >= 0)

    for i in range(H* equit):

        floor_sum = 0

        for v in g.nodes:

            floor_sum += x[(v,i)]

        ceil_sum = floor_sum.copy()

        for j in range(i,H):
            #floor_sum -= math.floor(n/(j+1))*((y[(q,j-1)] if j > 0 else 1)-y[(q,j)])
            floor_sum -= math.floor(n / (j + 1)) * x[(q, j)]
            #ceil_sum -= math.ceil(n/(j+1))*((y[(q,j-1)] if j > 0 else 1)-y[(q,j)])
            ceil_sum -= math.ceil(n / (j + 1)) * x[(q, j)]

        M.addConstr(floor_sum >= 0)
        M.addConstr(ceil_sum <= 0)
        print("\r Adding equitability constraints: " + str((i + 1) / H), sep=' ', end='')




    M._H = H
    M._G = g
    M._q = q
    M._type = "POP"
    M.setAttr("ObjCon",1)
    M.update()
    return M, y, x

def createPOPHyb(g: nx.graph, H, q=0, equit = True, strength = False,symm = False,equitConst = 0):#Konstruiert das hybride POP-Modell. Die Parameter bestimmen die Variante des Modells
    #equit: Equitables oder klassiches Modell, symm:Asymmetriebedingungen, EquitConst: Variante der Equitability Constraints, Strength: Verstäktes Modell
    M = gb.Model("POPHyb")
    n = g.number_of_nodes()
    y = {}
    for i in range(H):
        y[(q, i)] = M.addVar(vtype=GRB.BINARY, obj=1)
        print("\r Adding variables: " + str(i / (2 * H * n)), sep=' ', end='')
    for v in g.nodes:

        if v != q:
            y[(v, 0)] = M.addVar(vtype=GRB.BINARY)

        for i in range(1, H):
            if v != q:
                y[(v, i)] = M.addVar(vtype=GRB.BINARY)
            M.addConstr(y[(v, i - 1)] - y[(v, i)] >= 0)
            M.addConstr(y[(q, i - 1)] - y[(v, i - 1)] >= 0)

        M.addConstr(y[(v, H - 1)] == 0)

        print("\r Adding variables: " + str((i + 1) / (2 * n)), sep=' ', end='')
    x = {}
    for v in g.nodes:
        x[(v, 0)] = M.addVar(vtype=GRB.BINARY)
        M.addConstr(x[(v, 0)] == 1 - y[(v, 0)])
        for i in range(1, H):
            x[(v, i)] = M.addVar(vtype=GRB.BINARY)
            M.addConstr(x[(v, i)] == y[(v, i - 1)] - y[(v, i)])
        print("\r Adding variables: " + str((i + n + 1) / (2 * n)), sep=' ', end='')

    M.addConstrs(x[(u, 0)] + x[(v, 0)] <= (y[(q, 0)] if strength else 1) for u, v in g.edges)
    print("\r Adding edge constraints: " + str(1 / H), sep=' ', end='')
    for i in range(1, H):
        M.addConstrs(x[(u, i)] + x[(v, i)] <= (y[(q, 0)] if strength else 1) for u, v in g.edges)
        print("\r Adding edge constraints: " + str((i + 1) / H), sep=' ', end='')

    if strength:
        for v in nx.neighbors(g, q):
            for i in range(H - 1):
                M.addConstr(y[(q, i + 1)] - y[(v, i)] >= 0)

    #for v in nx.neighbors(g, q):
    #    for i in range(H - 1):
    #        M.addConstr(y[(q, i+1)] - y[(v, i)] >= 0)

    if equitConst == 0:
        for i in range(-1+H * equit):

            floor_sum = 0

            for v in g.nodes:
                floor_sum += x[(v, i)]

            ceil_sum = floor_sum.copy()

            for j in range(i, H):
                # floor_sum -= math.floor(n/(j+1))*((y[(q,j-1)] if j > 0 else 1)-y[(q,j)])
                floor_sum -= math.floor(n / (j + 1)) * x[(q, j)]
                # ceil_sum -= math.ceil(n/(j+1))*((y[(q,j-1)] if j > 0 else 1)-y[(q,j)])
                ceil_sum -= math.ceil(n / (j + 1)) * x[(q, j)]

            M.addConstr(floor_sum >= 0)
            M.addConstr(ceil_sum <= 0)
            print("\r Adding equitability constraints: " + str((i + 1) / H), sep=' ', end='')
    else:

        s = []
        for i in range(-1 + H * equit):

            floor_sum = 0
            s.append(M.addVar(vtype=GRB.BINARY, lb=0, ub=1))
            for v in g.nodes:

                floor_sum += x[(v,i)]



            for j in range(i,H):
                #floor_sum -= math.floor(n/(j+1))*((y[(q,j-1)] if j > 0 else 1)-y[(q,j)])
                floor_sum -= math.floor(n / (j + 1)) * x[(q, j)]
                #ceil_sum -= math.ceil(n/(j+1))*((y[(q,j-1)] if j > 0 else 1)-y[(q,j)])


            M.addConstr(floor_sum-s[i] == 0)

            print("\r Adding equitability constraints: " + str((i + 1) / H), sep=' ', end='')

    if symm:
        #for v in range(1,H):

            #M.addConstr(y[(v,v-1)] >= y[(q,v)])
            #print("\r Adding symmetry-breaking constraints: " + str((v + 1) / n), sep=' ', end='')
        for v in range(H):
            if v == q: continue
            M.addConstr(y[(v,v)] == 0)
            print("\r Adding symmetry-breaking constraints: " + str((v + 1) / n), sep=' ', end='')

    M._H = H
    M._G = g
    M._q = q
    M._type = "POP"
    M.setAttr("ObjCon",1)
    M.update()
    return M, y, x

def precolorClique(M, var,max_clique): #Vorfärbung der Clique


    match M._type:
        case "POP":
            y = var
            q = M._q
            if q in max_clique:
                max_clique = max_clique.copy()
                max_clique.remove(q)

            for i, v in enumerate(max_clique):

                M.addConstr(y[(v, i)] == 0)

                if i > 0:
                    M.addConstr(y[(v, i - 1)] == 1)
            M.addConstr(y[(q, len(max_clique)-1)] == 1)
        case "ASS":
            x = var

            for i, v in enumerate(max_clique):
                M.addConstr(x[(v, i)] == 1)

        case "REP":

            x = var

            for v in max_clique:
                M.addConstr(x[(v, v)] == 1)




