import subprocess
import SatParser
import Scripts.Source.Heuristiken as heur
import networkx as nx
import DecideColorable as decis2
import Scripts.Source.Parser as prs
import DecideColorable2 as decis
import Scripts.Source.Utility as util
import Scripts.Source.Preprocessing as pre
import time
import os
def coloring(G:nx.Graph,H:int = None,clq = None):
    n = G.number_of_nodes()
    if H is None:
        H = max(heur.FJK2(G,nx.greedy_color(G,strategy="DSATUR")).keys())+1
    lowerLimit = len(pre.maxCutClique(G,H)[1])
    upperLimit = H
    print(H)
    while upperLimit-lowerLimit > 1:
        print(lowerLimit, upperLimit)
        middle = lowerLimit+int((upperLimit-lowerLimit)/2)
        decis.k_colorability(G,middle,clq)
        run = subprocess.run(['kissat.exe', 'SAT.cnf'], stdout=subprocess.PIPE)
        result = SatParser.parseSatResult(run.stdout.decode('utf-8'))
        if result is None:
            lowerLimit = middle
        else:
            upperLimit = middle
    print(lowerLimit,upperLimit)
    x = decis.k_colorability(G, upperLimit,clq)

    run = subprocess.run(['kissat.exe', 'SAT.cnf'], stdout=subprocess.PIPE)

    result = SatParser.parseSatResult(run.stdout.decode('utf-8'))
    if result is not None:

        return SatParser.varsToColor(result,x)
    else:
        x = decis.k_colorability(G, lowerLimit,clq)
        run = subprocess.run(['kissat.exe', 'SAT.cnf'], stdout=subprocess.PIPE)

        result = SatParser.parseSatResult(run.stdout.decode('utf-8'))

        return SatParser.varsToColor(result,x)

def coloring_pop(G:nx.Graph,H:int = None):
    n = G.number_of_nodes()
    if H is None:
        H = max(heur.FJK2(G,nx.greedy_color(G,strategy="DSATUR")).keys())+1
    lowerLimit = len(pre.maxCutClique(G,H)[1])
    upperLimit = H
    print(H)
    while upperLimit-lowerLimit > 1:
        print(lowerLimit, upperLimit)
        middle = lowerLimit+int((upperLimit-lowerLimit)/2)
        decis.k_colorability_pop(G,middle)
        run = subprocess.run(['kissat.exe', 'SAT.cnf'], stdout=subprocess.PIPE)
        result = SatParser.parseSatResult(run.stdout.decode('utf-8'))
        if result is None:
            lowerLimit = middle
        else:
            upperLimit = middle
    print(lowerLimit,upperLimit)
    x = decis.k_colorability_pop(G, upperLimit)

    run = subprocess.run(['kissat.exe', 'SAT.cnf'], stdout=subprocess.PIPE)

    result = SatParser.parseSatResult(run.stdout.decode('utf-8'))
    if result is not None:

        return SatParser.varsToColor_POP(result,x)
    else:
        x = decis.k_colorability_pop(G, lowerLimit)
        run = subprocess.run(['kissat.exe', 'SAT.cnf'], stdout=subprocess.PIPE)

        result = SatParser.parseSatResult(run.stdout.decode('utf-8'))

        return SatParser.varsToColor_POP(result,x)

def coloring_general(model:decis.ColoringModel, G:nx.Graph,H:int = None,timeout:int=None):

    runtime = 0

    def solveSatFile():
        nonlocal runtime
        nonlocal timeout
        remaining = None
        if timeout is not None:
            remaining = timeout-runtime
        checkpoint = time.time()
        try:
            run = subprocess.run(['kissat.exe', 'SAT.cnf'], stdout=subprocess.PIPE,timeout=remaining)
        except subprocess.TimeoutExpired:
            raise
        runtime += time.time() - checkpoint
        return run
    n = G.number_of_nodes()
    if H is None:
        H = max(heur.FJK2(G,nx.greedy_color(G,strategy="DSATUR")).keys())+1
    lowerLimit = len(pre.maxCutClique(G,H)[1])
    upperLimit = H
    print(H)
    while upperLimit-lowerLimit > 1:
        print(lowerLimit, upperLimit)
        middle = lowerLimit+int((upperLimit-lowerLimit)/2)
        model.k_coloring_formula(G,middle)
        try:
            run = solveSatFile()
        except subprocess.TimeoutExpired:
            print(f"Timeout: Runtime exceeded {timeout} seconds")
            return lowerLimit, upperLimit
        result = SatParser.parseSatResult(run.stdout.decode('utf-8'))
        if result is None:
            lowerLimit = middle
        else:
            upperLimit = middle
    print(lowerLimit,upperLimit)
    model.k_coloring_formula(G, upperLimit)
    try:
        run = solveSatFile()
    except subprocess.TimeoutExpired:
        print(f"Timeout: Runtime exceeded {timeout} seconds")
        return lowerLimit, upperLimit
    result = SatParser.parseSatResult(run.stdout.decode('utf-8'))
    if result is not None:
        print("Runtime:", runtime)
        return model.coloring_from_vars(result)
    else:
        model.k_coloring_formula(G, lowerLimit)
        try:
            run = solveSatFile()
        except subprocess.TimeoutExpired:
            print(f"Timeout: Runtime exceeded {timeout} seconds")
            return lowerLimit, upperLimit
        result = SatParser.parseSatResult(run.stdout.decode('utf-8'))
        print("Runtime:", runtime)
        return model.coloring_from_vars(result)

def coloring_equit(G:nx.Graph,H:int = None):
    n = G.number_of_nodes()
    if H is None:
        H = max(heur.FJK2(G,nx.greedy_color(G,strategy="DSATUR")).keys())+1
    lowerLimit = len(pre.maxCutClique(G,H)[1])
    upperLimit = H
    print(H)
    k = lowerLimit
    result = None
    x = {}
    while result is None:
        x = decis.exact_k_coloring_equit(G, k)

        run = subprocess.run(['kissat.exe', 'SAT.cnf'], stdout=subprocess.PIPE)

        result = SatParser.parseSatResult(run.stdout.decode('utf-8'))
        k+=1

    return SatParser.varsToColor_POP(result, x)


def SATcoloring(model:decis.ColoringModel,G:nx.Graph, H:int,lb:int,parameters:dict = None, timeout:int = None,clq = None):
    runtime = 0

    def solveSatFile():
        nonlocal runtime
        nonlocal timeout
        remaining = None
        if timeout is not None:
            remaining = timeout - runtime
        checkpoint = time.time()
        try:
            run = subprocess.run(['kissat.exe', 'SAT.cnf'], stdout=subprocess.PIPE, timeout=remaining)
        except subprocess.TimeoutExpired:
            raise
        runtime += time.time() - checkpoint
        return run

    lowerLimit = lb
    upperLimit = H
    print(H)
    while upperLimit - lowerLimit > 1:
        print(lowerLimit, upperLimit)
        middle = lowerLimit + int((upperLimit - lowerLimit) / 2)
        model.k_coloring_formula(G, middle)
        try:
            run = solveSatFile()
        except subprocess.TimeoutExpired:
            print(f"Timeout: Runtime exceeded {timeout} seconds")
            model.lb,model.ub,model.runtime = lowerLimit,upperLimit,timeout
            return lowerLimit, upperLimit
        result = SatParser.parseSatResult(run.stdout.decode('utf-8'))
        if result is None:
            lowerLimit = middle
        else:
            upperLimit = middle
    print(lowerLimit, upperLimit)
    model.k_coloring_formula(G, lowerLimit)
    try:
        run = solveSatFile()
    except subprocess.TimeoutExpired:
        print(f"Timeout: Runtime exceeded {timeout} seconds")
        model.lb, model.ub, model.runtime = lowerLimit, upperLimit, timeout
        return lowerLimit, upperLimit
    result = SatParser.parseSatResult(run.stdout.decode('utf-8'))
    if result is not None:
        print("Runtime:", runtime)
        model.lb, model.ub, model.runtime = lowerLimit, lowerLimit, runtime
        return model.coloring_from_vars(result)
    else:
        model.k_coloring_formula(G, upperLimit)
        try:
            run = solveSatFile()
        except subprocess.TimeoutExpired:
            print(f"Timeout: Runtime exceeded {timeout} seconds")
            model.lb, model.ub, model.runtime = upperLimit, upperLimit, timeout
            return upperLimit, upperLimit
        result = SatParser.parseSatResult(run.stdout.decode('utf-8'))
        print("Runtime:", runtime)
        model.lb, model.ub, model.runtime = upperLimit, upperLimit, runtime
        return model.coloring_from_vars(result)

def runSATModel(model:decis.ColoringModel,G:nx.Graph, H:int,clq:list,parameters:dict = None, timeout:int = None,lb = 0):
    if lb == 0: lb = len(clq)
    model.setClique(clq)
    col = SATcoloring(model, G,H,lb,parameters=parameters, timeout=timeout)

    if model.lb != model.ub:
        lower, upper = model.lb,model.ub

    else:
        if not util.checkColoringEq(G,col,eqCheck=False):
            print(col)
            raise Exception("Not a Coloring")
        lower = upper = max(col.keys())+1

    n = G.number_of_nodes()
    m = G.number_of_edges()
    if parameters is None:
        parameters = {}
    return {
        "model": model.type+"-SAT",
        "parameters": ",".join(":".join((name, str(val))) for name, val in parameters.items() if name != "q"),
        "nodes": n,
        "edges": m,
        "density": m / ((n * (n - 1)) / 2),
        "heuristic": H,
        "max_clique": len(clq),
        "max_degree": max(G.degree, key=lambda x: x[1])[1] + 1,
        "upper_bound":  upper,
        "lower_bound": lower,
        "runtime": model.runtime,
    }

def solveFormula(formula:str,n_vars:int,n_clauses:int):
    with open("SAT.cnf", "w") as f:
        f.write("p cnf " + str(n_vars) + " " + str(n_clauses)+"\n")
        f.write(formula)
    run = subprocess.run(['kissat.exe', 'SAT.cnf'], stdout=subprocess.PIPE)
    result = SatParser.parseSatResult(run.stdout.decode('utf-8'))

    print(result)

#solveFormula(*decis.card_constraint(list(range(1,7)),2, 6,atmost=False))
result = []
for file in os.listdir("../Instances/mycielski"):

    if file.endswith(".col"):
        print(file)
        G = prs.readDimacs(os.path.join("../Instances/mycielski", file))
        H = heur.UpperBoundDsatur(G)
        clq = pre.maxCutClique(G,H)[1]
        col_mods =[decis.ASS_SAT(), decis.POP_SAT(),decis.POPHyb_SAT()]
        for col_mod in col_mods:
            col = runSATModel(col_mod,G,H,clq,timeout=300)
            res_dict = {"instance":file}
            res_dict.update(col)
            result.append(res_dict)

print("\n".join(str(row) for row in result))
#print(len(col))
#print(col)
#if type(col) == dict:
#    print(util.checkColoringEq(G,col,False))
#result = subprocess.run(['kissat.exe', 'SAT.cnf'], stdout=subprocess.PIPE)
#print(SatParser.parseSatResult(result.stdout.decode('utf-8')))