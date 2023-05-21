#Author: Daniel Faber

import itertools

import networkx as nx
import ModelConstructors as models
import Parser as prs
import os
import Heuristiken as heur
import datetime
import Relabeling as relab
import ModelRunners as modrun

#Dieses Modul beinhaltet Methoden zum Evaluieren der Modelle


def InstanceTester(modelList:list,inst_path:str,parameters = None,m_attributes = None) -> list: #Dies ist eine Methode zum Testen von einer Reihe von Modellen auf einer Instanzen

    print(os.path.abspath(inst_path))
    G = prs.readDimacs(os.path.abspath(inst_path))
    results = modrun.GraphTester(modelList,G,m_attributes = m_attributes,parameters=parameters)
    for result in results:
        result.update({"instance":os.path.basename(inst_path)})
    return results

#Dies ist eine Methode zum Testen von verschiedenen Modellen auf einer Reihe von Instanzen
def ModelComparison(inst_path:str,
                    modelList:list,
                    parameters = None,
                    m_attributes = None,
                    name:str = None)->None:

    os.makedirs("../Experiments",exist_ok=True)
    expName = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") if name is None else name
    ex_path = os.path.join("../Experiments","Ex_"+expName)
    os.makedirs(ex_path, exist_ok=True)
    results = []
    if "LogFile" in m_attributes:
        os.makedirs(os.path.join(ex_path, m_attributes["LogFile"]), exist_ok=True)
        m_attributes["LogFile"] = os.path.join(ex_path,m_attributes["LogFile"],"log_"+os.path.basename(inst_path)+"_")
    for i,f in enumerate(os.listdir(inst_path)):
        if not f.endswith(".col"):
            continue

        results.append(InstanceTester(modelList,os.path.join(os.path.abspath(inst_path),f),parameters=parameters,m_attributes=m_attributes))

    with open(os.path.join(ex_path,"summary.lg"),"w") as f:
        f.write(" ".join(results[0][0].keys())+"\n")
        for instanceTests in results:
            for modelTests in instanceTests:
                f.write(" ".join(map(str,modelTests.values()))+"\n")

def runExperiment(experiment_file:str):
    inst_path = []
    modellist = []
    parameters = []
    m_attributes = {}
    name = None
    with open(experiment_file) as file:
        for line in file:
            if line[0] == "N":
                name = line.split()[1]
            if line[0] == "I":
                inst_path.append(line.split()[1])
            if line[0] == "M":
                _,M,*pars = line.split()
                modellist.append(M)

                if len(pars) > 0:
                    parameters.append({par.split(":")[0]:par.split(":")[1] for par in pars[0].split(",")})
            if line[0] == "A":
                attrs = line.split()[1]
                m_attributes = {attr.split(":")[0]:attr.split(":")[1] for attr in attrs.split(",")}

    for path in inst_path:
        ModelComparison(path,modellist,parameters,m_attributes,name=name)

print("test")
print(runExperiment("test.exp"))

def randomGraphs(n,p,modelList:list,iter=10,parameters = None,m_attributes = None) -> list: #Testet Modelle auf zufällig generierten Graphen
    avDict = {
        "upper_bound": 0.0,
        "lower_bound": 0.0,
        "runtime": 0.0,
        "bbnodes": 0.0,
        "simplex_it": 0.0
    }
    modelDict = {model:avDict.copy() for model in modelList}


    for i in range(iter):

        G = nx.fast_gnp_random_graph(n,p,seed = i)
        result = modrun.GraphTester(modelList=modelList,G=G,parameters=parameters,m_attributes=m_attributes)
        for row in result:
            for k in modelDict[row["model"]]:
                modelDict[row["model"]][k] += row[k]

        if i == 0:
            for row in result:
                for attr in row:
                    if attr not in modelDict[row["model"]]:
                        modelDict[row["model"]][attr] = row[attr]


    results = list(modelDict.values())
    #for M in ["ASS","POP","POPHyb","REP"]:
    #    for key in modelDict[M]:
    #        modelDict[M][key] /= iter
    #    print(modelDict[M])
    #    modelDict[M].update({
    #        "model": M,
    #        "nodes": n,
    #        "density": p,
    #    })

    #    results.append(modelDict[M])

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

