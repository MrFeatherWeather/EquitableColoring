def parseSatResult(result:str)-> list:
    variables = []
    reachedVars = False
    for line in result.splitlines():

        if line[0] == "s" and line.split()[1] == "UNSATISFIABLE":
            return None
        if line[0] == "v":
            variables += [0 if lit[0] == "-" else 1 for lit in line.split() if lit != "v" and lit != "0"]
            reachedVars = True
        else:
            if reachedVars: return variables



def varsToColor2(vars, n):
    coloring = {}

    for idx,val in enumerate(vars):
        v = idx % n
        i = int(idx/n)
        if val == 1:
            if i not in coloring:
                coloring[i] = []
            coloring[i].append(v)
    return coloring

def varsToColor(vars,x):
    coloring = {}
    colored = set()

    for v,i in x:
        if v in colored:
            continue
        if vars[x[v,i]-1] == 1:
            if i not in coloring:
                coloring[i] = []
            coloring[i].append(v)
            colored.add(v)
    return coloring