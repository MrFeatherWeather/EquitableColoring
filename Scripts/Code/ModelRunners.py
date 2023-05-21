import networkx
import

def runModel(model:callable,G:networkx.Graph, H:int,clq:list):

    M, var, *other = model(G, H, q=clq[0], strength=False, symm=False, equit=True)
    models.precolorClique(M, var, clRep if "REP" in MStr else cl)