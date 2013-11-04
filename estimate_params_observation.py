from collections import defaultdict
def get_observation_prob_from_insane_input_file(file_name):
    f=open(file_name)
    d=defaultdict(lambda: defaultdict(int))
    for l in f:
        l=l.split(" ")[2:]
        l[0]=l[0].split("=")[1]
        l[1]=l[1].split("=")[1]
        l[2]=None
        position=l[0]+"_"+l[1]
        for i in range(3, len(l)):
            observation=l[i].split("=")[0][:-2]
            d[position][observation]+=1
        d[position]["total"]+=1
    for position in d:
        for observation in d[position]:
            if observation != "total":
                d[position][observation] /= float(d[position]["total"])
    return d        
    
