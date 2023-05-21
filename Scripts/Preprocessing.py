import networkx as nx


def maxCutClique(G:nx.Graph, H): #Finden einer Clique für REP und ASS/POP/POPH-Modell
    max_clique = None
    max_clique_rep = None
    clique_val = 0
    clique_val_rep = 0

    #if the graph is small enough: iterate over all possible cliques
    if (2*G.number_of_edges()/(G.number_of_nodes()**2-G.number_of_nodes())) <= 0.5 and G.number_of_nodes() < 300:

        max_clique = max(nx.find_cliques(G),key=lambda x:len(x)*H+nx.cut_size(G,x))

        max_clique_rep = max(nx.find_cliques(G),key=lambda x:len(x))
    else:
        #else find maximal independent sets in the antigraph

        antiG = nx.complement(G)
        for i in range(300*int(G.number_of_edges()/G.number_of_nodes())):

            clique = nx.maximal_independent_set(antiG,seed=i)

            new_val = H * len(clique) + nx.cut_size(G, clique)

            if new_val > clique_val:
                max_clique = clique
                clique_val = new_val

            if len(clique) > clique_val_rep:
                max_clique_rep = clique
                clique_val_rep = len(clique)



    return max_clique,max_clique_rep


def precolorClique(M, var,max_clique): #Vorfärbung der Clique


    match M._type:
        case "POP":
            y = var
            q = M._q

            #precoloring q will not work
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


