import networkx as nx
import matplotlib.pyplot as plt
a,b,*c = 1,2,3,4
d,e = c
print(d)
if False:
    for i in range(100):
        for j in range(1000000):
            r = 5**5
        print("\r test"+str(i),end="",flush=False)
    x = [j/50 for j in range(51)]

    y = []
    for i in x:
        G = nx.fast_gnp_random_graph(50,i,456)
        cliques = nx.find_cliques(G)
        y.append(len(list(cliques)))
        print("Density: ",i,"Cliques: ",y[-1])

print()


