#Author: Daniel Faber

import itertools

import networkx as nx
import ModelConstructors as models
import Parser as prs
import os
import Heuristiken as heur
import matplotlib.pyplot as plt
import numpy as np
import datetime
import Relabeling as relab
#Dieses Modell beinhaltet Methoden zum Evaluieren der Modelle
def ModelTester(MStr:str,inst_path:str,m_attributes = None) -> list: #Dies ist eine Methode zum Testen von Modellen auf einer Reihe von Instanzen
    modelMap = {
        "ASS":models.createASS,
        "POP":models.createPOP,
        "POPHyb":models.createPOPHyb,
        "REP":models.createRep
    }
    results = []
    for i,f in enumerate(os.listdir(inst_path)):
        if not f.endswith(".col"):
            continue
        print(f, os.path.abspath(inst_path))
        G = prs.readDimacs(os.path.join(os.path.abspath(inst_path),f))
        print("Caclulate heuristic solution")
        H = max(heur.FJK3(G,nx.greedy_color(G,strategy="DSATUR")).keys())+1
        print(H)
        print("Calculate Clique Bound")
        cl,clRep = models.maxCutClique(G,H)
        print("Construct Model")
        if "POP" in MStr:
            #max(G.degree,key=lambda x: x[1])[0]
            G,cl = models.relabelNodes(G,cl)
            M,var,*other = modelMap[MStr](G,H,q=cl[-1],strength = False,symm=True)
            models.precolorClique(M, var, cl)
        elif "ASS" in MStr:
            M,var,*other = modelMap[MStr](G, H,symm = True)
            models.precolorClique(M, var, cl)
        else:
            M, var, *other = modelMap[MStr](G, H,lowBound=len(clRep))
            models.precolorClique(M, var, clRep)

        M.setParam("TimeLimit",3600)
        M.setParam("Seed",0)
        M.setParam("Threads", 1)

        #M.setParam("Heuristics", 0.2)
        if m_attributes is not None:
            for key,value in m_attributes.items():
                if key == "LogFile":
                    M.setParam("LogFile",
                               os.path.join(value, "log_" + MStr + "_" + os.path.basename(f) + ".lg"))
                    continue
                M.setParam(key,value if not value.isnumeric else int(value))

        M.optimize()

        n = G.number_of_nodes()
        m = G.number_of_edges()
        results.append({
            "model":MStr,
            "instance":os.path.basename(f),
            "nodes": n,
            "edges": m,
            "density": m/((n*(n-1))/2),
            "heuristic":H,
            "max_clique":len(cl),
            "max_degree":max(G.degree, key = lambda x:x[1])[1]+1,
            "upper_bound":M.getAttr("ObjVal"),
            "lower_bound":M.getAttr("ObjBound"),
            "runtime":M.getAttr("Runtime"),
            "bbnodes":M.getAttr("NodeCount"),
        })
        #if i >= 2: break
    return results

def InstanceTester(modelList:list,inst_path:str,m_attributes = None) -> list: #Dies ist eine Methode zum Testen von einer Reihe von Modellen auf einer Instanzen
    modelMap = {
        "ASS":models.createASS,
        "POP":models.createPOP,
        "POPHyb":models.createPOPHyb,
        "REP":models.createRep
    }
    results = []


    print(os.path.abspath(inst_path))
    G = prs.readDimacs(os.path.abspath(inst_path))
    print("Caclulate heuristic solution")
    H = max(heur.FJK3(G,nx.greedy_color(G,strategy="DSATUR")).keys())+1
    print(H)
    print("Calculate Clique Bound")
    cl,clRep = models.maxCutClique(G,H)
    print("Construct Model")
    #print(G.degree(cl))
    #G, cl = relab.relabelModel(G, cl, True, H)
    #UPDATE NECESSARY FROM MODELTESTER
    for MStr in modelList:
        if "POP" in MStr:
            # max(G.degree,key=lambda x: x[1])[0]max(cl,key=G.degree)

            M, var,*other = modelMap[MStr](G, H, q=cl[0], strength=False,symm = False,equit=True)
        elif "ASS" in MStr:
            M, var, *other = modelMap[MStr](G, H,symm = False,equit = True)
        else:
            G, clRep = relab.relabelModel(G, clRep)
            M, var, *other = modelMap[MStr](G, H, lowBound=len(clRep),symm = True)

        models.precolorClique(M,var,clRep if "REP" in MStr else cl)
        M.setParam("TimeLimit",3600)
        M.setParam("Seed",0)
        M.setParam("Threads", 1)

        #M.setParam("Heuristics", 0.2)
        if m_attributes is not None:
            for key,value in m_attributes.items():
                if key == "LogFile":
                    M.setParam("LogFile",
                               os.path.join(value, "log_" + MStr + "_" + os.path.basename(inst_path) + ".lg"))
                    continue
                M.setParam(key,value if not value.isnumeric else int(value))

        M.optimize()

        n = G.number_of_nodes()
        m = G.number_of_edges()
        results.append({
            "model":MStr,
            "instance":os.path.basename(inst_path),
            "nodes": n,
            "edges": m,
            "density": m/((n*(n-1))/2),
            "heuristic":H,
            "max_clique":len(cl),
            "max_degree":max(G.degree, key = lambda x:x[1])[1]+1,
            "upper_bound":M.getAttr("ObjVal"),
            "lower_bound":M.getAttr("ObjBound"),
            "runtime":M.getAttr("Runtime"),
            "bbnodes":M.getAttr("NodeCount"),
            "simplex_it:":M.getAttr("IterCount")
        })
        #if i >= 2: break
    return results



def ConfigTester(model:str,inst_path:str,m_attributes = None,plots = None) -> list: #Dies ist eine Methode zum Testen von verschiedenen Modellvarianten eines Modells auf einer Instanzen

    modelMap = {
        "ASS":models.createASS,
        "POP":models.createPOP,
        "POPHyb":models.createPOPHyb,
        "REP":models.createRep
    }
    configMap = {
        0:"Base",
        1:"Asymm",
        2:"IntEquit",
        3:"Strength"
    }


    results = []


    print(os.path.abspath(inst_path))
    G = prs.readDimacs(os.path.abspath(inst_path))
    print("Caclulate heuristic solution")
    H = max(heur.FJK3(G,nx.greedy_color(G,strategy="DSATUR")).keys())+1
    print(H)
    print("Calculate Clique Bound")
    cl,clRep = models.maxCutClique(G,H)
    print("Construct Model")

    if "REP" in model:
        cl = clRep

    G, cl = relab.relabelModel(G, cl, "POP" in model, H)

    configList = []
    if "POP" in model:
        #max(G.degree,key=lambda x: x[1])[0]
        configList.append(modelMap[model](G, H, q=cl[-1],strength = False,symm = False))
        configList.append(modelMap[model](G, H, q=cl[-1], strength=False, symm=True))
        configList.append(modelMap[model](G, H, q=cl[-1], strength=False, symm=False,equitConst=1))
        configList.append(modelMap[model](G, H, q=cl[-1], strength=True, symm=False))
    else:
        configList.append(modelMap[model](G, H,symm = False))
        configList.append(modelMap[model](G, H, symm=True))
        if "ASS" in model:
            configList.append(modelMap[model](G, H, symm=False,equitConst=1))

    for i,model in enumerate(configList):
        M,var,*others = model

        models.precolorClique(M,var, cl)
        M.setParam("TimeLimit",3600)
        M.setParam("Seed",0)
        M.setParam("Threads", 1)

        #M.setParam("Heuristics", 0.2)
        if m_attributes is not None:
            for key,value in m_attributes.items():
                if key == "LogFile":
                    M.setParam("LogFile",
                               os.path.join(value, "log_" + configMap[i] + "_" + os.path.basename(inst_path) + ".lg"))
                    continue
                M.setParam(key,value if not value.isnumeric else int(value))

        M.optimize()

        n = G.number_of_nodes()
        m = G.number_of_edges()
        results.append({
            "model":configMap[i],
            "instance":os.path.basename(inst_path),
            "nodes": n,
            "edges": m,
            "density": m/((n*(n-1))/2),
            "heuristic":H,
            "max_clique":len(cl),
            "max_degree":max(G.degree, key = lambda x:x[1])[1]+1,
            "upper_bound":M.getAttr("ObjVal"),
            "lower_bound":M.getAttr("ObjBound"),
            "runtime":M.getAttr("Runtime"),
            "bbnodes":M.getAttr("NodeCount"),
            "simplex_it:": M.getAttr("IterCount")
        })
    #if i >= 2: break
    return results

def configComparison(inst_path:str,model:str,m_attributes = None,plots=None)->None: ##Dies ist eine Methode zum Testen und Vergleichen von verschiedenen Modellvarianten eines Modells auf einer Reihe von Instanzen
    os.makedirs("../Experiments", exist_ok=True)
    ex_path = os.path.join("../Experiments", "Cf_" +model+"_"+ datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(ex_path, exist_ok=True)
    os.makedirs(os.path.join(ex_path, "Logs"), exist_ok=True)
    results = []
    attributes = {"LogFile": os.path.join(ex_path, "Logs")}

    if m_attributes is not None: attributes.update(m_attributes)
    for i,f in enumerate(os.listdir(inst_path)):
        if not f.endswith(".col"):
            continue

        results.append(ConfigTester(model,os.path.join(os.path.abspath(inst_path),f),attributes))

    with open(os.path.join(ex_path,"summary.lg"),"w") as f:
        f.write(" ".join(results[0][0].keys())+"\n")
        for instanceTests in results:
            for modelTests in instanceTests:
                f.write(" ".join(map(str,modelTests.values()))+"\n")
    def createPlot(attr):
        dim = len(results[0])
        w = 0.75
        dimw = w / dim

        fig, ax = plt.subplots()
        x = np.arange(len(results))

        for i in range(dim):
            y = [d[i][attr] for d in results]
            b = ax.bar(x + i * dimw, y, dimw,bottom = 0.001,label=results[0][i]["model"])
            ax.bar_label(b,labels=map(lambda x:str(round(x,2)),y), padding=3)


        ax.legend()
        #label = ["\n".join((resultsInstances[i][0]["instance"],str(resultsInstances[i][0]["nodes"]),str(round(resultsInstances[i][0]["density"],2)))) for i in range(len(resultsInstances))]
        label = [results[i][0]["instance"] for i in range(len(results))]
        ax.set_xticks(x + dimw / 2, labels=label)#map(str, x))
        ax.set_yscale('log')

        ax.set_xlabel("Instances")
        ax.set_ylabel(attr)



        plt.savefig(os.path.join(ex_path,"plot_"+attr+".pdf"),format="pdf")

    if plots is not None:
        for plot in plots:
            createPlot(plot)

def ModelComparison(inst_path:str,modelList:list,m_attributes = None,plots=None)->None: #Dies ist eine Methode zum Testen von verschiedenen Modellen auf einer Reihe von Instanzen
    os.makedirs("../Experiments",exist_ok=True)
    ex_path = os.path.join("../Experiments","Ex_"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(ex_path, exist_ok=True)
    os.makedirs(os.path.join(ex_path,"Logs"), exist_ok=True)
    results = []
    for M in modelList:
        attributes = {"LogFile":os.path.join(ex_path,"Logs")}
        if m_attributes is not None: attributes.update(m_attributes)
        results.append(ModelTester(M,inst_path,attributes))

    resultsInstances = []
    for i in range(len(results[0])):
        resultsInstances.append([results[j][i] for j in range(len(results))])
    print(resultsInstances)
    with open(os.path.join(ex_path,"summary.lg"),"w") as f:
        f.write(" ".join(resultsInstances[0][0].keys())+"\n")
        for instanceTests in resultsInstances:
            for modelTests in instanceTests:
                f.write(" ".join(map(str,modelTests.values()))+"\n")

    def createPlot(attr):
        dim = len(resultsInstances[0])
        w = 0.75
        dimw = w / dim

        fig, ax = plt.subplots()
        x = np.arange(len(resultsInstances))

        for i in range(dim):
            y = [d[i][attr] for d in resultsInstances]
            b = ax.bar(x + i * dimw, y, dimw,bottom = 0.001,label=resultsInstances[0][i]["model"])
            ax.bar_label(b,labels=map(lambda x:str(round(x,2)),y), padding=3)


        ax.legend()
        #label = ["\n".join((resultsInstances[i][0]["instance"],str(resultsInstances[i][0]["nodes"]),str(round(resultsInstances[i][0]["density"],2)))) for i in range(len(resultsInstances))]
        label = [resultsInstances[i][0]["instance"] for i in range(len(resultsInstances))]
        ax.set_xticks(x + dimw / 2, labels=label)#map(str, x))
        ax.set_yscale('log')

        ax.set_xlabel("Instances")
        ax.set_ylabel(attr)



        plt.savefig(os.path.join(ex_path,"plot_"+attr+".pdf"),format="pdf")

    if plots is not None:
        for plot in plots:
            createPlot(plot)

def ModelComparison2(inst_path:str,modelList:list,m_attributes = None,plots=None)->None: #Dies ist eine Methode zum Testen von verschiedenen Modellen auf einer Reihe von Instanzen, ist aber effizienter als die obere da die obere Cliquen und Schranken unnötig mehrfach berechnet
    os.makedirs("../Experiments",exist_ok=True)
    ex_path = os.path.join("../Experiments","Ex_"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(ex_path, exist_ok=True)
    os.makedirs(os.path.join(ex_path,"Logs"), exist_ok=True)
    results = []
    for i,f in enumerate(os.listdir(inst_path)):
        if not f.endswith(".col"):
            continue
        attributes = {"LogFile": os.path.join(ex_path, "Logs")}
        if m_attributes is not None: attributes.update(m_attributes)
        results.append(InstanceTester(modelList,os.path.join(os.path.abspath(inst_path),f),attributes))

    #for i in range(len(results[0])):
    #    results.append([results[j][i] for j in range(len(results))])

    with open(os.path.join(ex_path,"summary.lg"),"w") as f:
        f.write(" ".join(results[0][0].keys())+"\n")
        for instanceTests in results:
            for modelTests in instanceTests:
                f.write(" ".join(map(str,modelTests.values()))+"\n")

    def createPlot(attr):
        dim = len(results[0])
        w = 0.75
        dimw = w / dim

        fig, ax = plt.subplots()
        x = np.arange(len(results))

        for i in range(dim):
            y = [d[i][attr] for d in results]
            b = ax.bar(x + i * dimw, y, dimw,bottom = 0.001,label=results[0][i]["model"])
            ax.bar_label(b,labels=map(lambda x:str(round(x,2)),y), padding=3)


        ax.legend()
        #label = ["\n".join((resultsInstances[i][0]["instance"],str(resultsInstances[i][0]["nodes"]),str(round(resultsInstances[i][0]["density"],2)))) for i in range(len(resultsInstances))]
        label = [results[i][0]["instance"] for i in range(len(results))]
        ax.set_xticks(x + dimw / 2, labels=label)#map(str, x))
        ax.set_yscale('log')

        ax.set_xlabel("Instances")
        ax.set_ylabel(attr)



        plt.savefig(os.path.join(ex_path,"plot_"+attr+".pdf"),format="pdf")

    if plots is not None:
        for plot in plots:
            createPlot(plot)


def GraphTester(modelList:list,G:nx.graph,m_attributes = None,clq = None) -> list:#Dies ist eine Methode zum Testen von verschiedenen Modellvarianten eines Modells auf einer Reihe von Graphen
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
    if clq is None:
        cl,clRep = models.maxCutClique(G,H)
    else:
        cl = clq
        clRep = clq
    print("Construct Model")
    #print(G.degree(cl))
    #G, cl = relab.relabelModel(G, cl, True, H)
    #UPDATE NECESSARY FROM MODELTESTER
    for MStr in modelList:
        if "POP" in MStr:
            # max(G.degree,key=lambda x: x[1])[0]max(cl,key=G.degree)

            M, var,*other = modelMap[MStr](G, H, q=cl[0], strength=False,symm = False,equit=True)
        elif "ASS" in MStr:
            M, var, *other = modelMap[MStr](G, H,symm = False,equit = True)
        else:
            G, clRep = relab.relabelModel(G, clRep)
            M, var, *other = modelMap[MStr](G, H, lowBound=len(clRep),symm = True)

        models.precolorClique(M,var,clRep if "REP" in MStr else cl)
        M.setParam("TimeLimit",3600)
        M.setParam("Seed",0)
        M.setParam("Threads", 1)

        #M.setParam("Heuristics", 0.2)
        if m_attributes is not None:
            for key,value in m_attributes.items():
                M.setParam(key,value if not value.isnumeric else int(value))

        M.optimize()

        n = G.number_of_nodes()
        m = G.number_of_edges()
        results.append({
            "model":MStr,
            "nodes": n,
            "edges": m,
            "density": m/((n*(n-1))/2),
            "heuristic":H,
            "max_clique":len(cl),
            "max_degree":max(G.degree, key = lambda x:x[1])[1]+1,
            "upper_bound":M.getAttr("ObjVal"),
            "lower_bound":M.getAttr("ObjBound"),
            "runtime":M.getAttr("Runtime"),
            "bbnodes":M.getAttr("NodeCount"),
            "simplex_it":M.getAttr("IterCount")
        })
        #if i >= 2: break
    return results

def randomGraphs(n,p,iter=10): #Testet Modelle auf zufällig generierten Graphen
    avDict = {
        "upper_bound": 0.0,
        "lower_bound": 0.0,
        "runtime": 0.0,
        "bbnodes": 0.0,
        "simplex_it": 0.0
    }
    modelDict = {
        "ASS":avDict.copy(),
        "POP": avDict.copy(),
        "POPHyb": avDict.copy(),
        "REP": avDict.copy()
    }

    for i in range(iter):

        G = nx.fast_gnp_random_graph(n,p,seed = i)
        result = GraphTester(["ASS","POP","POPHyb","REP"],G)
        for row in result:
            for k in modelDict[row["model"]]:
                modelDict[row["model"]][k] += row[k]

    results = []
    for M in ["ASS","POP","POPHyb","REP"]:
        for key in modelDict[M]:
            modelDict[M][key] /= iter
        print(modelDict[M])
        modelDict[M].update({
            "model": M,
            "nodes": n,
            "density": p,
        })

        results.append(modelDict[M])

    return results

def clqGraphs(n,p,clqSize,iter=10):#Wurde benutzt um Graphen mit fester Cliquegröße zu erstellen, diese Versuche haben aber nichts ergeben
    avDict = {
        "upper_bound": 0.0,
        "lower_bound": 0.0,
        "runtime": 0.0,
        "bbnodes": 0.0,
        "simplex_it": 0.0
    }
    modelDict = {
        "ASS":avDict.copy(),
        "POP": avDict.copy(),
        "POPHyb": avDict.copy(),
        "REP": avDict.copy()
    }

    for i in range(iter):

        G = nx.fast_gnp_random_graph(n,p,seed = i)
        G.add_edges_from((u,v) for u,v in itertools.combinations(range(clqSize),2))

        result = GraphTester(["ASS","POP","POPHyb","REP"],G,clq=list(range(clqSize)))
        for row in result:
            for k in modelDict[row["model"]]:
                modelDict[row["model"]][k] += row[k]

    results = []
    for M in ["ASS","POP","POPHyb","REP"]:
        for key in modelDict[M]:
            modelDict[M][key] /= iter
        print(modelDict[M])
        modelDict[M].update({
            "model": M,
            "nodes": n,
            "density": p,
        })

        results.append(modelDict[M])

    return results

def testLog(nList:list,pList:list,iter = 10,m_attributes = None)->None: #Testet Modelle auf einer Reihe von zufällig generierten Graphen mit fester Knotenzahl und Kantendichte
    os.makedirs("../Experiments",exist_ok=True)
    ex_path = os.path.join("../Experiments","Rnd_"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(ex_path, exist_ok=True)

    results = []
    if pList is not None:
        combs = itertools.product(nList,pList)
    else:
        combs = nList
    for n,p in combs:
        print("Test:",n,p,"-"*100)
        attributes = {"LogFile": os.path.join(ex_path, "Logs")}
        if m_attributes is not None: attributes.update(m_attributes)
        results.append(randomGraphs(n,p,iter))

    #for i in range(len(results[0])):
    #    results.append([results[j][i] for j in range(len(results))])

    with open(os.path.join(ex_path,"summary.lg"),"w") as f:
        f.write(" ".join(results[0][0].keys())+"\n")
        for instanceTests in results:
            for modelTests in instanceTests:
                f.write(" ".join(map(str,modelTests.values()))+"\n")

def testLogClq(nList:list,pList:list,cList:list,iter = 10,m_attributes = None)->None: #Testet Modelle auf einer Reihe von Graphen mit fester Cliquegröße(wurde nicht in der Arbeit verwendet)
    os.makedirs("../Experiments",exist_ok=True)
    ex_path = os.path.join("../Experiments","Clq_"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(ex_path, exist_ok=True)

    results = []
    if pList is not None:
        combs = itertools.product(nList,pList,cList)
    else:
        combs = nList
    for n,p,c in combs:
        print("Test:",n,p,c,"-"*100)
        attributes = {"LogFile": os.path.join(ex_path, "Logs")}
        if m_attributes is not None: attributes.update(m_attributes)
        results.append(clqGraphs(n,p,c,iter))

    #for i in range(len(results[0])):
    #    results.append([results[j][i] for j in range(len(results))])

    with open(os.path.join(ex_path,"summary.lg"),"w") as f:
        f.write(" ".join(results[0][0].keys())+"\n")
        for instanceTests in results:
            for modelTests in instanceTests:
                f.write(" ".join(map(str,modelTests.values()))+"\n")

#testLog([60],[0.1,0.3,0.5,0.7,0.9])


#for p in [0.1,0.3,0.5,0.7,0.9]:
#    clSize = 0
#    Heur = 0
#    for i in range(10):
#        G = nx.fast_gnp_random_graph(100,p,seed = i)
#        H = heur.FJK3(G,nx.greedy_color(G,strategy="DSATUR"))
#        bla,cl = models.maxCutClique(G,10)
#        clSize+=len(cl)
#        Heur += max(H.keys())+1
#    print(Heur/clSize)

