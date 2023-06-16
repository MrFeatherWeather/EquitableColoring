import LogicFormula as logic
from BaseColoring import ColoringModel
def preassignVars(zero_vars:list, one_vars:list,formula:logic.LogicFormula):

    for i in range(len(formula.clauses)-1,-1,-1):
        for j in range(len(formula.clauses[i])-1,-1,-1):
            if formula.clauses[i][j] in zero_vars or -formula.clauses[i][j] in one_vars:
                #if 2759 in formula.clauses[i] or -2759 in formula.clauses[i]:
                    #print(formula.clauses[i],"-"*100,formula.clauses[i][j])
                formula.clauses[i].pop(j)
            elif formula.clauses[i][j] in one_vars or -formula.clauses[i][j] in zero_vars:
                #if 2759 in formula.clauses[i] or -2759 in formula.clauses[i]:
                    #print(formula.clauses[i],"-"*100,formula.clauses[i][j])
                formula.clauses.pop(i)
                break
    for zero in zero_vars:
        formula.addClause([-zero])
    for one in one_vars:
        formula.addClause([one])
def precolorClique(model:ColoringModel,formula:logic.LogicFormula,max_clique):
    match model.type:
        case "POP":
            zero_vars = []
            one_vars = []
            for i, v in enumerate(max_clique):

                one_vars+=[model.x[v, j] for j in range(i)]
                zero_vars+=[model.x[v, j] for j in range(i,len(max_clique))]
            preassignVars(zero_vars, one_vars, formula)
        case "ASS":
            zero_vars = []
            one_vars = []
            for i,v in enumerate(max_clique):
                pass
                one_vars.append(model.x[v,i])
                zero_vars += [model.x[v,j] for j in range(len(max_clique)) if j != i]
            #print(one_vars)
            #print(zero_vars)
            preassignVars(zero_vars,one_vars,formula)

        case "POPH":
            zero_vars = []
            one_vars = []
            for i, v in enumerate(max_clique):
                one_vars += [model.y[v, j] for j in range(i)]
                zero_vars += [model.y[v, j] for j in range(i, len(max_clique))]
            preassignVars(zero_vars, one_vars, formula)

