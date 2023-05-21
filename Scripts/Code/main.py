#Author: Daniel Faber

from Evaluation import*


#Dieses Skript ist der Ausgangspunkt für die Evaluationen. Man wählt zuerst den Modus "0" oder "1", wobei im Modus "0" die Modelle
#miteinander verglichen werden und im Modus "1" für ein bestimmtes Modell die verschiedenen Varianten miteinander verglichen werden
#Danach gibt man den Pfad mit den zu testenden Instanzen an, die Liste von den zu testenden Modellen und gegebenfalls Modellparameter
#und Modellattribute, die man als Plot visualisiert haben möchte

mode = input("Enter testing mode\n")
if mode == "compare" or mode == "0" :
    input = input("Enter experiment parameters:Instance_Path Models Model_Attributes(Optional) Plots(Optional) Example:\n"+
          "../Instances/ ASS,POP Timelimit:100,LogFile:../Logs/ runtime,bbnodes\n")
    inpath,inmodels,*opts = input.split()
    inattr = None
    inplots = None
    if len(opts) == 2:
        inattr,inplots = opts
    elif len(opts) == 1:
        if ':' in opts[0]:
            inattr = opts[0]
        else:
            inplots = opts[0]
    modelList = inmodels.split(",")
    if inplots is not None:
        plotlist = inplots.split(",")
    else:
        plotlist = None
    if inattr is not None:
        attrlist = inattr.split(",")
        attrdict = {attr.split(":")[0]: attr.split(":")[1] for attr in attrlist}
    else:
        attrdict = None

    ModelComparison2(inpath,modelList,m_attributes=attrdict,plots=plotlist)

else:
    input = input(
        "Enter experiment parameters:Instance_Path Model Model_Attributes(Optional) Plots(Optional) \n" +
        "../Instances/ ASS Timelimit:100,LogFile:../Logs/ runtime,bbnodes\n")
    inpath, inmodels, *opts = input.split()
    inattr = None
    inplots = None
    if len(opts) == 2:
        inattr, inplots = opts
    elif len(opts) == 1:
        if ':' in opts[0]:
            inattr = opts[0]
        else:
            inplots = opts[0]

    if inplots is not None:
        plotlist = inplots.split(",")
    else:
        plotlist = None
    if inattr is not None:
        attrlist = inattr.split(",")
        attrdict = {attr.split(":")[0]: attr.split(":")[1] for attr in attrlist}
    else:
        attrdict = None
    configComparison(inpath, inmodels, m_attributes=attrdict, plots=plotlist)



