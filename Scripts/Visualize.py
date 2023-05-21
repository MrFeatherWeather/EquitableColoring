import os
import matplotlib.pyplot as plt
import numpy as np
def readLog(path:str):
    dictKeys = []
    instanceList = []
    with open(path,"r") as f:
        for i,line in enumerate(f):
            if i == 0:
                dictKeys = line.split()
                continue
            results = line.split()
            instanceList.append({dictKeys[i]:results[i] for i in range(len(dictKeys))})
    return(instanceList)


def groupDict(results:list,size = range(0,100000)):
    groupedDict = {}
    for r in results:

        if int(r["nodes"]) in size:

            if r["instance"] not in groupedDict:
                groupedDict[r["instance"]] = []
            groupedDict[r["instance"]].append(r)
    if False:
        for key in list(groupedDict.keys()):
            if all(m["lower_bound"] == m["upper_bound"] for m in groupedDict[key]):
                groupedDict.pop(key)
    return groupedDict

def latexTable(results:dict,ex_path:str = "../table.tex"):
    def prsNum(n: str,tl = False):
        if n == "inf":
            return "$\infty$"
        num = float(n)
        if num > 3600 and tl:
            return "tl"
        return str(round(num, 2))
    modelDict={
        "ASS":0,
        "POP": 0,
        "POPHyb": 0,
        "REP":0
    }
    modelDict = {
        "ASS":0,
        "POP": 0,
        "POPHyb": 0,
        "REP":0
    }
    firstRow = next(iter(results.values()))
    models = [el["model"] for el in firstRow]
    #solvedInst = [sum([float(inst[i]["runtime"])<=3600 for inst in results.values()]) for i in range(len(models))]
    #print(solvedInst)
    rowCount = 0
    with open(ex_path,"w") as f:
        f.write("\\begin{tabular}{|c|c c"+"|c c c"*len(models)+"|}\n")
        f.write("\\hline\n")
        f.write("&"+"".join("&&&"+m for m in models)+"\\\\\n")
        f.write("Instance & |V| & |E|"+"&lb&ub&time"*len(models)+"\\\\\n")
        f.write("\\hline\n")
        for inst,row in sorted(results.items(),key=lambda x:x[0]):
            inststr = inst.replace("_","\\_")
            inststr = inststr[:-4]
            nodes = row[0]["nodes"]
            edges = row[0]["edges"]
            #if int(edges) > 40000:continue
            f.write(inststr+"&"+nodes+"&"+edges+"&"+
                    "&".join([prsNum(m["lower_bound"]) + "&" +prsNum(m["upper_bound"])+"&"+prsNum(m["runtime"],True) for m in row])+
                    "\\\\\n")
            for m in row:
                modelDict[m["model"]]+=float(m["runtime"])
            rowCount+=1
        print(modelDict)

        for m in modelDict:
            modelDict[m] /= rowCount

        print(modelDict)
        print(len(results.values()))
        f.write("\\end{tabular}\n")
        f.write(str(modelDict))
        f.write(str(len(results.values())))

def fillNaN(results:dict):

    for key in results:
        if len(results[key])<4:
            clone = results[key][0].copy()
            clone["model"] = "REP"
            for k in ["runtime","bbnodes","upper_bound","lower_bound","simplex_it:"]:
                clone[k] = np.nan
            results[key].append(clone)
    print(results)

def fillInst(results:list):

    for entry in results:

        entry["instance"] = "n = "+entry["nodes"]+"\n p="+str(round(float(entry["density"])*100,2))

def visualize(results:dict,attr:str,ex_path = "../plots/plot.svg"):
    dim = len(next(iter(results.values())))
    print(next(iter(results.values())))

    sortedVals = sorted(results.values(), key = lambda x:(float(x[0]["density"])))
    sortedKeys = sorted(results.items(), key = lambda x:(float(x[1][0]["density"])))

    sortedKeys = [el[0] for el in sortedKeys]

    models = [el["model"] for el in next(iter(results.values()))]
    w = 0.75
    dimw = w / dim

    fig, ax = plt.subplots()
    x = np.arange(len(results))
    ylimit = 0
    for i in range(dim):
        y = list(map(lambda x: 1E5 if x == "inf" else float(x),[d[i][attr] for d in sortedVals]))
        ylimit = max(ylimit,max(filter(lambda x:x<1E5,y),default=0))

        print(y)
        b = ax.bar(x + i * dimw, y, dimw, bottom=0.001, label=models[i])
        #ax.bar_label(b, labels=map(lambda x: str(round(float(x), 2)), y), padding=3)

    ax.legend()
    # label = ["\n".join((resultsInstances[i][0]["instance"],str(resultsInstances[i][0]["nodes"]),str(round(resultsInstances[i][0]["density"],2)))) for i in range(len(resultsInstances))]
    label = map(lambda x:x[:-4]+"\n p="+str(round(float(results[x][0]["density"])*100,2)),sortedKeys)
    ax.set_xticks(x + dimw / 2, labels=label)  # map(str, x))

    ax.set_yscale('linear')
    ax.set_xlabel("Instances")
    ax.set_ylabel(attr)
    ax.set_ylim([0., ylimit+5])



    plt.xticks(rotation=45, ha="right",fontsize=6,weight="bold")

    plt.legend(loc='lower right')
    plt.savefig(os.path.join(ex_path), format="svg",bbox_inches = "tight")


rdLog = readLog("../Results/ResultsFinal.txt")


groupedDict = groupDict(rdLog)
#print(groupedDict)
#print(groupDict(readLog("../Experiments/summary.lg")))
#latexTable(groupedDict,ex_path="../Results/Table/bla"+".tex")
#latexTable(groupDict(readLog("../Results/FinaleA1A2.lg")))
for i,rng in enumerate([range(1,300),range(300,600),range(600,10000)]):
    groupedDict = groupDict(readLog("../Results/ResultsFinal.txt"),size=rng)
    fillNaN(groupedDict)
    visualize(groupedDict,"upper_bound",ex_path="../plots/final/plot_upper_bound"+str(i+1)+".svg")