#Author: Daniel Faber

import gurobipy as gb
from gurobipy import GRB
import networkx as nx
import math

#Dieses Modul konstruiert die ganzzahligen Programme für das equitable Färbungsproblem
#Bemerkung: Einige Modelle benötigen bestimmtes Preprocessing(z.b. benötigt das asymmetrische POP-Modell bestimmtes Relabeling)
#Die Funktionen sollten deshalb nicht direkt benutzt sondern nur über die Funktionen in "Evaluation" benutzt werden

def createASS(g:nx.Graph,H,symm=False,equitConst='standard'):#Konstruiert das Assignment-Modell. Die Parameter bestimmen die Variante des Modells
    #equit: Equitables oder klassiches Modell, symm:Asymmetriebedingungen, EquitConst: Variante der Equitability Constraints

    M = gb.Model("ASS")
    n = g.number_of_nodes()

    w = []
    x = {}

    for v in g.nodes:

        node_sum = 0

        #adding variables for every node and every color

        for i in range(H):
            variable = M.addVar(vtype = GRB.BINARY)
            x[(v,i)] = variable
            node_sum += variable

        M.addConstr(node_sum == 1)
        print("\r Adding variables: " + str(v / n), sep=' ', end='')

    #adding constraint for every color and every edge
    for i in range(H):
        w_i = M.addVar(obj=1, vtype=GRB.BINARY)
        w.append(w_i)
        if i >= 1:
            M.addConstr(w[i] <= w[i-1])

        M.addConstrs(x[(u, i)] + x[(v, i)] <= w_i for u, v in g.edges)

        print("\r Adding edge constraints: " + str((i + 1) / (H)), sep=' ', end='')

    #adding equitability constraints
    if equitConst == 'standard':
        for i in range(-1 + H):
            floor_sum = sum(x[(v, i)] for v in g.nodes)

            ceil_sum = floor_sum.copy()

            floor_sum -= sum(math.floor(n / (j + 1)) * (w[j] - w[j + 1]) for j in range(i, H - 1))

            ceil_sum -= sum(math.ceil(n / (j + 1)) * (w[j] - w[j + 1]) for j in range(i, H - 1))

            floor_sum -= math.floor(n / H) * w[H - 1]
            ceil_sum -= math.ceil(n / H) * w[H - 1]
            M.addConstr(floor_sum >= 0)
            M.addConstr(ceil_sum <= 0)
            print("\r Adding equitability constraints: " + str(i / H), sep=' ', end='')
    elif equitConst == 'addvars':
        s = []
        for i in range(-1+H):


            s.append(M.addVar(vtype = GRB.BINARY,lb=0,ub=1))

            floor_sum = sum(x[(v,i)] for v in g.nodes)

            floor_sum -= sum(math.floor(n / (j + 1)) * (w[j] - w[j + 1]) for j in range(i, H-1))

            floor_sum -= (math.floor(n/H)*w[H - 1] + s[i])

            M.addConstr(floor_sum == 0)
            print("\r Adding equitability constraints: " + str(i / H), sep=' ', end='')
    elif equitConst != 'none':
        print("Wrong Equitability specifier")
    #symmetry breaking
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

def createREP(g:nx.Graph, H,symm = True,lowBound=1):#Konstruiert das Representatives-Modell. Die Parameter bestimmen die Variante des Modells
   #symm:Asymmetriebedingungen
    M = gb.Model("REP")
    n = g.number_of_nodes()
    x = {}

   #add variable for u representing v if v is not in the neighbourhood of v
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

   #add edge constraints for every edge and every possible combinations of vertices represented by u
    for u in g.nodes:

        M.addConstrs(x[(u,v)] + x[(u,w)] <= x[(u,u)]
                     for v,w in g.subgraph(nx.non_neighbors(g,u)).edges if (v > u and w > u) or not symm)
        print("\r Adding edge constraints: " + str((u+1) / n), sep=' ', end='')

    #adding equitability constraints: first define the z variables as the products of y and x variables
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

    #then add equitability to every representative class
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


def createPOP(g:nx.graph,H,q=0,strength = True,symm = True, equitConst = 'standard'):#Konstruiert das POP-Modell. Die Parameter bestimmen die Variante des Modells
    #equit: Equitables oder klassiches Modell, symm:Asymmetriebedingungen, EquitConst: Variante der Equitability Constraints, Strength: Verstäktes Modell
    M = gb.Model("POP")
    n = g.number_of_nodes()

    y = {}
    # adding variables for the special vertex q for every color
    for i in range(H):
        y[(q,i)] = M.addVar(vtype=GRB.BINARY,obj = 1)
        print("\r Adding variables: " + str(i / (H*n)), sep=' ', end='')

    # adding variables for all other nodes and colors
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


    #adding constraints for every edge and color 0
    M.addConstrs(y[(u, 0)] + y[(v, 0)] >= 2 - (y[(q, 0)] if strength else 1) for u,v in g.edges)
    print("\r Adding edge constraints: " + str(1 / H), sep=' ', end='')

    # adding constraints for every edge and every other color
    for i in range(1, H):
        M.addConstrs(y[(u, i - 1)] - y[(u, i)] + y[(v, i - 1)] - y[(v, i)] <= (y[(q, i - 1)] if strength else 1) for u,v in g.edges)
        print("\r Adding edge constraints: " + str((i + 1) / H), sep=' ', end='')

    #add strengthening constraints
    if strength:
        for v in nx.neighbors(g,q):

            M.addConstrs(y[(q,i+1)] - y[(v,i)] >= 0 for i in range(H-1))

    # equitability constraints
    if equitConst == 'standard':

        for i in range(-1+H):

            floor_sum = sum((y[(v,i-1)] if i > 0 else 1)-y[(v,i)] for v in g.nodes)


            ceil_sum = floor_sum.copy()


            floor_sum -= sum(math.floor(n / (j + 1)) * ((y[(q, j - 1)] if j > 0 else 1) - y[(q, j)]) for j in range(i,H))
            ceil_sum -= sum(math.ceil(n/(j+1))*((y[(q,j-1)] if j > 0 else 1)-y[(q,j)]) for j in range(i,H))


            t1 = M.addConstr(floor_sum >= 0)
            t2 = M.addConstr(ceil_sum <= 0)
            print("\r Adding equitability constraints: " + str((i+1) / H), sep=' ', end='')
    elif equitConst == 'addvars':
        s = []
        for i in range(-1+H):
            floor_sum = sum((y[(v, i - 1)] if i > 0 else 1) - y[(v, i)] for v in g.nodes)
            s.append(M.addVar(vtype=GRB.BINARY, lb=0, ub=1))


            floor_sum -= sum(
                math.floor(n / (j + 1)) * ((y[(q, j - 1)] if j > 0 else 1) - y[(q, j)]) for j in range(i, H))


            M.addConstr(floor_sum-s[i] == 0)

            print("\r Adding equitability constraints: " + str((i + 1) / H), sep=' ', end='')
    elif equitConst != 'none':
        print("Wrong Equitability specifier")

    if symm:

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


def createPOPHyb(g: nx.graph, H, q=0, strength = False,symm = False,equitConst = 'standard'):#Konstruiert das hybride POP-Modell. Die Parameter bestimmen die Variante des Modells
    #equit: Equitables oder klassiches Modell, symm:Asymmetriebedingungen, EquitConst: Variante der Equitability Constraints, Strength: Verstäktes Modell
    M = gb.Model("POPHyb")
    n = g.number_of_nodes()
    y = {}

    # adding variables for the special vertex q for every color
    for i in range(H):
        y[(q, i)] = M.addVar(vtype=GRB.BINARY, obj=1)
        print("\r Adding variables: " + str(i / (2 * H * n)), sep=' ', end='')

    # adding variables for all other nodes and colors
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

    # adding  x variables that correspond to variables from ass model
    x = {}
    for v in g.nodes:
        x[(v, 0)] = M.addVar(vtype=GRB.BINARY)
        M.addConstr(x[(v, 0)] == 1 - y[(v, 0)])
        for i in range(1, H):
            x[(v, i)] = M.addVar(vtype=GRB.BINARY)
            M.addConstr(x[(v, i)] == y[(v, i - 1)] - y[(v, i)])
        print("\r Adding variables: " + str((i + n + 1) / (2 * n)), sep=' ', end='')

    #adding constraints for every edge andd color 0
    M.addConstrs(x[(u, 0)] + x[(v, 0)] <= (y[(q, 0)] if strength else 1) for u, v in g.edges)
    print("\r Adding edge constraints: " + str(1 / H), sep=' ', end='')

    # adding constraints for every edge and every other color
    for i in range(1, H):
        M.addConstrs(x[(u, i)] + x[(v, i)] <= (y[(q, 0)] if strength else 1) for u, v in g.edges)
        print("\r Adding edge constraints: " + str((i + 1) / H), sep=' ', end='')

    # adding strenghtening constraints
    if strength:
        for v in nx.neighbors(g, q):
            for i in range(H - 1):
                M.addConstr(y[(q, i + 1)] - y[(v, i)] >= 0)

    #adding equitability constraints
    if equitConst == 'standard':
        for i in range(-1+H):

            floor_sum = 0

            for v in g.nodes:
                floor_sum += x[(v, i)]

            ceil_sum = floor_sum.copy()

            for j in range(i, H):
                floor_sum -= math.floor(n / (j + 1)) * x[(q, j)]
                ceil_sum -= math.ceil(n / (j + 1)) * x[(q, j)]

            M.addConstr(floor_sum >= 0)
            M.addConstr(ceil_sum <= 0)
            print("\r Adding equitability constraints: " + str((i + 1) / H), sep=' ', end='')


    elif equitConst == 'addvars':

        s = []
        for i in range(-1 + H):

            floor_sum = 0
            s.append(M.addVar(vtype=GRB.BINARY, lb=0, ub=1))
            for v in g.nodes:

                floor_sum += x[(v,i)]

            for j in range(i,H):

                floor_sum -= math.floor(n / (j + 1)) * x[(q, j)]



            M.addConstr(floor_sum-s[i] == 0)

            print("\r Adding equitability constraints: " + str((i + 1) / H), sep=' ', end='')

    elif equitConst != 'none':
        print("Wrong Equitability specifier")


    #adding symmetry breaking constraints
    if symm:
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





