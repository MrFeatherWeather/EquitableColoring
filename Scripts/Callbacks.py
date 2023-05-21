import gurobipy as gb
from gurobipy import GRB

def countFrac(m,where):
    if where == GRB.Callback.MIPNODE and m.cbGet(GRB.Callback.MIPNODE_STATUS) == GRB.OPTIMAL:
        m._counter += 1
        if m._counter % 1000 == 0:
            g = m._G
            m._counter = 0
            frac_vars = 0
            for var in m.getVars():

                    if 1e-5 < m.cbGetNodeRel(var) < 1-1e-5:
                        frac_vars+=1
            print(frac_vars)