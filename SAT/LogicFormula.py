import math
import itertools
class LogicFormula:
    def __init__(self):
        self.variables = []
        self.clauses = []

    def addVar(self)->int:
        self.variables.append(len(self.variables)+1)
        return self.variables[-1]

    def addVars(self, n)->list:
        self.variables += list(range(len(self.variables)+1,len(self.variables)+n))
        return self.variables[-n:]

    def addClause(self, literals:list):
        self.clauses.append(literals)

    def addClauses(self, clauses:list):
        self.clauses += (clauses)

    def parseAsString(self):
        return f"p cnf {len(self.variables)}  {len(self.clauses)}\n" \
               + "\n".join(" ".join(str(lit) for lit in clause)+" 0" for clause in self.clauses)
def bit_one(i,j):

    if i < (1<<(j-1)):
        return False

    return str(bin(i))[-j] == "1"

def at_least_1_const(vars:list, formula:LogicFormula):
    formula.addClause(vars.copy())

def at_most_1_const(vars: list, formula: LogicFormula):
        formula.addClause([-x for x in vars])

def k_card_const(vars:list, formula:LogicFormula,k:int,atmost:bool):
    n = len(vars)
    if not atmost:
        k = n-k
    log_ceil = int(math.ceil(math.log(n, 2)))
    B = {(i, g): formula.addVar() for i, g in itertools.product(range(k), range(1, log_ceil + 1))}
    T = {(g, i): formula.addVar() for i, g in itertools.product(range(n), range(k))}
    for i, g, j in itertools.product(range(n), range(k), range(1, log_ceil + 1)):
        formula.addClause([-T[(g,i),(1 if bit_one(vars[i],j) else -1)* B[g,j]]])
