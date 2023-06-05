import LogicFormula as logic
import DecideColorable2 as decis
def preassignVars(zero_vars:list, one_vars:list,formula:logic.LogicFormula):

    for i in range(len(formula.clauses)-1,-1,-1):
        for j in range(len(formula.clauses[i])-1,-1,-1):
            if formula.clauses[i][j] in zero_vars or -formula.clauses[i][j] in one_vars:
                formula.clauses[i].pop(j)
            if formula.clauses[i][j] in one_vars or -formula.clauses[i][j] in zero_vars:
                formula.clauses.pop(i)
                break

def precolorClique(model:decis.ColoringModel,formula:logic.LogicFormula,max_clique):
    match model.type:
        case "POP":
            zero_vars = []
            one_vars = []
            for i, v in enumerate(max_clique):
                if i > 0:
                    one_vars.append(model.y[i-1, v])
                zero_vars.append(model.y[i, v])
            preassignVars(zero_vars, one_vars, formula)
        case "ASS":
            zero_vars = []
            one_vars = []
            for i,v in enumerate(max_clique):
                one_vars.append(model.x[i,v])
                zero_vars += [model.x[j,v] for j in range(len(max_clique)) if j != i]
            preassignVars(zero_vars,one_vars,formula)

        case "POPH":
            zero_vars = []
            one_vars = []
            for i, v in enumerate(max_clique):
                if i > 0:
                    one_vars.append(model.y[i - 1, v])
                zero_vars.append(model.y[i, v])
            preassignVars(zero_vars, one_vars, formula)

