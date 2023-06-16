import networkx as nx
import itertools
import math



def k_colorability(G: nx.Graph, k: int):
    n = G.number_of_nodes()
    m = G.number_of_edges()
    with open("SAT.cnf", "w") as f:
        f.write("p cnf " + str(n * k) + " " + str(int(n + k * (k - 1) * 0.5 * n + m * k)))  # k*(k-1)*0.5

        for v in G.nodes():
            clause = " ".join(str(i * n + v + 1) for i in range(k))
            f.write("\n" + clause + " 0")
            for i, j in itertools.combinations(range(k), 2):
                clause = str(-(i * n + v + 1)) + " " + str(-(j * n + v + 1))
                f.write("\n" + clause + " 0")

        for v, w in G.edges():
            for i in range(k):
                clause = str(-(i * n + v + 1)) + " " + str(-(i * n + w + 1))
                f.write("\n" + clause + " 0")


def card_constraint_old(varidx: list, highestIdx):
    n = len(varidx)
    new_vars = (int(math.ceil(math.log(n, 2))))

    formula = ""
    for i, j in itertools.product(range(n), range(1, new_vars + 1)):
        print(i, j)
        print(str(bin(varidx[i]))[2:].zfill(new_vars))
        formula += str(-varidx[i]) + \
            (" " if str(bin(varidx[i]))[2:].zfill(new_vars)[j - 1] == "1" else " -") + \
            str(highestIdx + j * n + i + 1) + " 0\n"


    highestIdx += new_vars

    return highestIdx, formula

def bit_one(i,j):

    if i < (1<<(j-1)):
        return False

    return str(bin(i))[-j] == "1"

def card_constraint(varidx: list, k:int, highestIdx:int,atmost:bool):
    n = len(varidx)
    if not atmost:
        k = n-k
    log_ceil= int(math.ceil(math.log(n, 2)))
    B = {(i,g) :highestIdx + g * n + k + 1 for i, g in itertools.product(range(k), range(1, log_ceil + 1))}
    highestIdx += (log_ceil+1)*k
    T = {(g, i): highestIdx + g * n + i + 1 for i, g in itertools.product(range(n), range(k))}
    highestIdx += n*k
    formula = ""
    for i, g, j in itertools.product(range(n),range(k), range(1, log_ceil + 1)):
        #print(i, j)
        #print(str(bin(varidx[i]))[2:].zfill(new_vars))
        formula += str(-T[g,i]) + " " + str((1 if bit_one(varidx[i],j) else -1)* B[g,j]) + " 0\n"
    for i in range(n):
        formula += str((-1 if atmost else 1)*varidx[i])+" "+" ".join(str(T[g,i]) for g in range(k)) + " 0\n"


    return  formula, highestIdx+1,n*k*log_ceil+n


#print(card_constraint(list(range(11)),2, 10,atmost=True)[1])
# G = nx.wheel_graph(3)
# k_colorability(G,2)
