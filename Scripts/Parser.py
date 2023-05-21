#Author: Daniel Faber

import colorsys

import networkx as nx

#Paket zum Einlesen von Graphen
def readDimacs(path): #Liest Instanzen im DIMACS-Standardformat ein und speichert sie als networkx-Graphen

    G = None
    with open(path,"r") as f:
        for line in f:
            if line[0] == "p":
                form = line.split()

                G = nx.empty_graph(int(form[2]))

            if line[0] == "e":
                edge = line.split()
                u, v = int(edge[1]), int(edge[2])
                if u != v:
                    G.add_edge(u-1,v-1)

    return G

def readDimacsBin(path):  #Liest Instanzen im binären DIMACS-Standardformat ein und speichert sie als networkx-Graphen(wurde tatsächlich in der Arbeit nicht gebraucht)

    G = None
    n = 0


    with open(path,"rb") as f:
        line = f.readline().decode("utf-8")

        while line[0] != "p":
            line = f.readline().decode("utf-8")

        form = line.split(" ")
        G = nx.empty_graph(int(form[2]))
        n = int(form[2])

        for i in range(n):
            mat_line = f.read((int((i + 8)/8)))
            byte_pos = 0
            for byte in mat_line:
                for j in range(8):
                    adj = (byte >> j) & 1
                    byte_pos += 1

                    if adj:
                        G.add_edge(i,j)

            if len(mat_line) < (int((i + 8)/8))-1:
                break

    return G

def writeDimacs(path,solution):  #Schreibt Färbungen ins Standard-DIMACS Format(wurde tatsächlich in der Arbeit nicht gebraucht)


    with open(path, "a") as f:
        f.write(f"s col {solution}")

def colorGraph(M,v_vars,colored,path): #Visualisiert eine berechnete Färbung

    col = int(M.getObjective().getValue())
    for i in range(col):

        rgbcolor = '#%02x%02x%02x' % tuple([round(c*255) for c in colorsys.hsv_to_rgb(i/col,1,1)])
        print(rgbcolor)
        for v in range(len(v_vars)):
            if v_vars[v][i].X == 1:

                colored.nodes[v]["graphics"] = {"hasFill":True,"fill":rgbcolor}

    nx.write_gml(colored, path)

