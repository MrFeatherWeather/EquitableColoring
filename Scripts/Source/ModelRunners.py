import networkx as nx
import Preprocessing
import Utility
import ModelConstructors as models
import Heuristiken as heur
import Relabeling as relabel

def runModel(model:callable,G:nx.Graph, H:int,clq:list,parameters:dict, m_attributes:dict = None) -> dict:

    M, var, *other = model(G, H, **parameters)
    Preprocessing.precolorClique(M, var, clq)
    M.setParam("TimeLimit", 3600)
    M.setParam("Seed", 0)
    M.setParam("Threads", 1)

    if m_attributes is not None:
        for key, value in m_attributes.items():
            M.setParam(key, value if not value.isnumeric else int(value))
    M.optimize()
    n = G.number_of_nodes()
    m = G.number_of_edges()

    coloring = Utility.getColoringFromModel(M,var)
    if not Utility.checkColoringEq(G,coloring,eqCheck=M._eq):
        raise Exception("Not an", "equitable" if M._eq else "","Coloring")
    return{
        "model": M.getAttr("ModelName"),
        "parameters": ",".join(":".join((name,str(val))) for name,val in parameters.items() if name != "q"),
        "nodes": n,
        "edges": m,
        "density": m / ((n * (n - 1)) / 2),
        "heuristic": H,
        "max_clique": len(clq),
        "max_degree": max(G.degree, key=lambda x: x[1])[1] + 1,
        "upper_bound": M.getAttr("ObjVal"),
        "lower_bound": M.getAttr("ObjBound"),
        "runtime": M.getAttr("Runtime"),
        "bbnodes": M.getAttr("NodeCount"),
        "simplex_it": M.getAttr("IterCount")
    }

#Dies ist eine Methode zum Testen von verschiedenen Modellvarianten eines Modells auf einen Graphen
def GraphTester(modelList:list,G:nx.graph,m_attributes = None,parameters:list = None,clq = None) -> list:
    modelMap = {
        "ASS":models.createASS,
        "POP":models.createPOP,
        "POPHyb":models.createPOPHyb,
        "REP":models.createREP
    }
    results = []

    print("Caclulate heuristic solution")
    H = max(heur.FJK2(G,nx.greedy_color(G,strategy="DSATUR")).keys())+1
    print(H)
    print("Calculate Clique Bound")
    if clq is None:
        cl,clRep = Preprocessing.maxCutClique(G,H)
    else:
        cl = clq
        clRep = clq

    GRep, clRep = relabel.relabelModel(G, clRep, H, POP=False)
    G, cl = relabel.relabelModel(G, cl, H, POP=True)
    print("Construct Model")

    for i,MStr in enumerate(modelList):
        if "LogFile" in m_attributes:
            m_attributes["LogFile"] += MStr + ".lg"
        model_params = {}
        if "POP" in MStr:
            model_params = dict(q=cl[-1],strength = True,symm = True, equitConst = 'standard')
        if MStr == "REP":
            model_params = dict(symm = True,lowBound = len(clRep))
            cl = clRep
            G = GRep
        if MStr == "ASS":
            model_params = dict(symm=False,equitConst='standard')
        if parameters is not None and len(parameters) > i:
            model_params.update(parameters[i])

        result = runModel(modelMap[MStr],G,H,cl,model_params,m_attributes)

        results.append(result)

    return results

