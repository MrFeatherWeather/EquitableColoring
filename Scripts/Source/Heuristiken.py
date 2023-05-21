#Author: Daniel Faber

import networkx as nx
import colorsys
import itertools
#Bemerkung: dieses Paket enthält die benutzten Heuristiken
def Naive(G:nx.Graph,coloring):

    MAX_COLOR = max(coloring.values())
    color_freq = [0]*(MAX_COLOR+1)
    color_ind_inv = range(MAX_COLOR+1)
    color_groups = {k:[] for k in range(MAX_COLOR+1)}
    for v,c in coloring.items():
        color_freq[c] +=1
        color_groups[c].append(v)




    color_ind_inv,color_freq = zip(*sorted(zip(color_ind_inv,color_freq),key=lambda x:x[1],reverse = True))
    color_freq = list(color_freq)
    color_ind_inv = list(color_ind_inv)
    color_ind = [i[1] for i in sorted(zip(color_ind_inv,range(len(color_ind_inv))),key=lambda x:x[0])]

    def recolor(v,large, small):
        coloring[v] = small
        color_groups[large].remove(v)
        color_groups[small].append(v)

        color_freq[0] -= 1

        if color_freq[0] < color_freq[1]:
            pivot = 1

            while color_freq[pivot] > color_freq[0]:
                pivot+=1
            pivot-=1
            color_freq[0],color_freq[pivot] = color_freq[pivot],color_freq[0]
            color_ind[color_ind_inv[0]],color_ind[color_ind_inv[pivot]] = color_ind[color_ind_inv[pivot]], color_ind[color_ind_inv[0]]
            color_ind_inv[0],color_ind_inv[pivot] = color_ind_inv[pivot],color_ind_inv[0]

        color_freq[-1] += 1

        if color_freq[-1] > color_freq[-2]:
            pivot = len(color_freq)-2

            while color_freq[pivot] < color_freq[-1]:
                pivot -= 1
            pivot += 1
            color_freq[-1], color_freq[pivot] = color_freq[pivot], color_freq[-1]
            color_ind[color_ind_inv[-1]], color_ind[color_ind_inv[pivot]] = color_ind[color_ind_inv[pivot]], color_ind[
                color_ind_inv[-1]]
            color_ind_inv[-1], color_ind_inv[pivot] = color_ind_inv[pivot], color_ind_inv[-1]

    def addColor(v,large):
        COLOR_IND = len(color_freq)
        color_freq.append(1)
        color_ind_inv.append(COLOR_IND)
        color_ind.append(COLOR_IND)
        color_groups[COLOR_IND] = [v]
        coloring[v] = COLOR_IND

        color_groups[large].remove(v)
        color_freq[0] -= 1
        if color_freq[0] < color_freq[1]:
            pivot = 1

            while color_freq[pivot] > color_freq[0]:
                pivot+=1
            pivot-=1
            color_freq[0],color_freq[pivot] = color_freq[pivot],color_freq[0]
            color_ind[color_ind_inv[0]],color_ind[color_ind_inv[pivot]] = color_ind[color_ind_inv[pivot]], color_ind[color_ind_inv[0]]
            color_ind_inv[0],color_ind_inv[pivot] = color_ind_inv[pivot],color_ind_inv[0]


    while(color_freq[0] > color_freq[-1]+1):
        recolor_success = False
        for v in color_groups[color_ind_inv[0]]:
            if all([coloring[w] != color_ind_inv[-1] for w in G.neighbors(v)]):
                #print("v:",v,"CG 0:",color_groups[color_ind_inv[0]])
                recolor(v,color_ind_inv[0],color_ind_inv[-1])
                recolor_success = True
                break
        if not recolor_success:
            addColor(color_groups[color_ind_inv[0]][0],color_ind_inv[0])

    return color_groups





def FJK(G:nx.Graph,coloring):
    MAX_COLOR = max(coloring.values())
    color_freq = [0]*(MAX_COLOR+1)
    color_groups = {k: [] for k in range(MAX_COLOR + 1)}
    for v,c in coloring.items():
        color_freq[c] +=1
        color_groups[c].append(v)
    maxim = max(color_freq)
    minim = min(color_freq)
    while maxim > minim+1:

        min_colors = [i for i in range(len(color_freq)) if color_freq[i] == minim]
        max_colors = [i for i in range(len(color_freq)) if color_freq[i] == maxim]

        recolor_success = False
        for cmax in max_colors:
            if recolor_success:
                break
            for v in color_groups[cmax]:
                if recolor_success:
                    break
                for cmin in min_colors:
                    if all([cmin != coloring[w] for w in G.neighbors(v)]):
                        coloring[v] = cmin
                        color_groups[cmax].remove(v)
                        color_groups[cmin].append(v)
                        color_freq[cmin] +=1
                        color_freq[cmax] -=1
                        recolor_success = True
                        break
        if not recolor_success:

            color_freq.append(1)
            color_freq[max_colors[0]] -=1
            newCol = len(color_freq)-1
            v = color_groups[max_colors[0]][0]
            color_groups[newCol] = [v]
            color_groups[max_colors[0]].remove(v)
            coloring[v] = newCol

        maxim = max(color_freq)
        minim = min(color_freq)

    return color_groups

def FJK2(G:nx.Graph,coloring):
    MAX_COLOR = max(coloring.values())
    color_freq = [0]*(MAX_COLOR+1)
    color_groups = {k: [] for k in range(MAX_COLOR + 1)}
    for v,c in coloring.items():
        color_freq[c] +=1
        color_groups[c].append(v)
    maxim = max(color_freq)
    minim = min(color_freq)
    while maxim > minim+1:
        #print(maxim,minim)
        min_colors = [i for i in range(len(color_freq)) if color_freq[i] == minim]
        max_colors = [i for i in range(len(color_freq)) if color_freq[i] == maxim]

        recolor_success = False
        candidate = None
        maxNeighbours = G.number_of_nodes()
        for cmax in max_colors:
            if recolor_success:
                break
            for v in color_groups[cmax]:
                if recolor_success:
                    break
                for cmin in min_colors:
                    if all([cmin != coloring[w] for w in G.neighbors(v)]):

                        #coloring[v] = cmin
                        #color_groups[cmax].remove(v)
                        #color_groups[cmin].append(v)
                        #color_freq[cmin] +=1
                        #color_freq[cmax] -=1
                        recolor_success = True
                        numbermaxNeigbours = len(list(filter(lambda v: coloring[v] in max_colors,G.neighbors(v))))

                        if numbermaxNeigbours < maxNeighbours:
                            candidate = v,cmin
                            maxNeighbours = numbermaxNeigbours


        if recolor_success:
            v,cmin = candidate
            cmax = coloring[v]
            coloring[v] = cmin
            color_groups[cmax].remove(v)
            #print(color_freq)
            #print(color_groups)

            color_groups[cmin].append(v)
            color_freq[cmin] +=1
            color_freq[cmax] -=1
        else:
            candidate = None
            maxNeighbours = G.number_of_nodes()

            newCol = len(color_freq)-1
            for cmax in max_colors:
                for v in color_groups[cmax]:
                    numbermaxNeigbours = len(list(filter(lambda v: coloring[v] in max_colors, G.neighbors(v))))
                    if numbermaxNeigbours < maxNeighbours:
                        candidate = v
                        maxNeighbours = numbermaxNeigbours
            color_freq.append(1)
            color_freq[coloring[candidate]] -= 1
            newCol = len(color_freq) - 1

            color_groups[newCol] = [candidate]
            color_groups[coloring[candidate]].remove(candidate)
            coloring[candidate] = newCol
        maxim = max(color_freq)
        minim = min(color_freq)


    return color_groups


def colorGraph(color_groups,colored,path): #Visualisiert die Färbung

    col = max(color_groups.keys())+1
    for i in range(col):

        rgbcolor = '#%02x%02x%02x' % tuple([round(c*255) for c in colorsys.hsv_to_rgb(i/col,1,1)])

        for v in color_groups[i]:
            colored.nodes[v]["graphics"] = {"hasFill":True,"fill":rgbcolor}

    nx.write_gml(colored, path)

def checkColoringEq(G:nx.Graph,c_groups:dict)->bool:#Überprüft ob die Färbung eine gültige equitable Färbung ist
    frequencies = [len(c) for c in c_groups.values()]
    frequencies.sort()
    if frequencies[0]+1 < frequencies[-1]:
        print("Not balanced:", frequencies)
        return False
    coloring = [0]*G.number_of_nodes()
    for c in c_groups.values():
        for v in c:
            coloring[v] = c

    for u,v in G.edges:
        if coloring[u] == coloring[v]:
            print("Conflict:",u,",",v)
            return False
    return True


