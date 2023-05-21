import subprocess
import SatParser
import Scripts.Source.Heuristiken as heur
import networkx as nx
import DecideColorable as decis2
import Scripts.Source.Parser as prs
import DecideColorable2 as decis
def coloring(G:nx.Graph,H:int = None):
    n = G.number_of_nodes()
    if H is None:
        H = max(heur.FJK2(G,nx.greedy_color(G,strategy="DSATUR")).keys())+1
    lowerLimit = 3
    upperLimit = H
    print(H)
    while upperLimit-lowerLimit > 1:
        print(lowerLimit, upperLimit)
        middle = lowerLimit+int((upperLimit-lowerLimit)/2)
        decis.k_colorability(G,middle)
        run = subprocess.run(['kissat.exe', 'SAT.cnf'], stdout=subprocess.PIPE)
        result = SatParser.parseSatResult(run.stdout.decode('utf-8'))
        if result is None:
            lowerLimit = middle
        else:
            upperLimit = middle
    print(lowerLimit,upperLimit)
    x = decis.k_colorability(G, upperLimit)

    run = subprocess.run(['kissat.exe', 'SAT.cnf'], stdout=subprocess.PIPE)

    result = SatParser.parseSatResult(run.stdout.decode('utf-8'))
    if result is not None:

        return SatParser.varsToColor(result,x)
    else:
        x = decis.k_colorability(G, lowerLimit)
        run = subprocess.run(['kissat.exe', 'SAT.cnf'], stdout=subprocess.PIPE)

        result = SatParser.parseSatResult(run.stdout.decode('utf-8'))

        return SatParser.varsToColor(result,x)



def solveFormula(formula:str,n_vars:int,n_clauses:int):
    with open("SAT.cnf", "w") as f:
        f.write("p cnf " + str(n_vars) + " " + str(n_clauses)+"\n")
        f.write(formula)
    run = subprocess.run(['kissat.exe', 'SAT.cnf'], stdout=subprocess.PIPE)
    result = SatParser.parseSatResult(run.stdout.decode('utf-8'))

    print(result)

#solveFormula(*decis.card_constraint(list(range(1,7)),2, 6,atmost=False))
G = prs.readDimacs("../Instances/InstancesA/5-FullIns_3.col")
col = coloring(G)
#print(len(col))
print(col)
#result = subprocess.run(['kissat.exe', 'SAT.cnf'], stdout=subprocess.PIPE)
#print(SatParser.parseSatResult(result.stdout.decode('utf-8')))