#vimdiff test_est_params_cpd.txt <(sort test_est_params_cpd.txt.gold)
#to test after running
#estimate-params test_est_params_network.txt test_est_params_training.txt test_est_params_cpd.txt
import sys, os
from collections import defaultdict

def combine_two_lists(l1, l2):
    if l1 ==[] or l2 ==[]:
        raise AssertionError
    else:
        l=list()
        for e1 in l1:
            for e2 in l2:
                if type(e1) is list:
                    l.append(e1 + [e2])
                else:
                    l.append([e1, e2])
        return l

def get_transition_probs_from_the_insane_input_file(file_name):
    f=open(file_name)
    o=[]
    number_of_time_steps_per_training_run=max(int(e.split(" ")[1]) for e in f)
    f.seek(0)
    for i, l in enumerate(f):
        i=i%(number_of_time_steps_per_training_run+1)
        important_stuff=[e.split("=")[1] for e in l.split(" ")[2:5]]
        if i==0:
            previous_pos=important_stuff
        else:
            row_delta=int(important_stuff[0])-int(previous_pos[0])
            col_delta=int(important_stuff[1])-int(previous_pos[1])
            if row_delta < -1:
                row_delta=1
            if row_delta > 1:
                row_delta = -1
            if col_delta < -1:
                col_delta=1
            if col_delta > 1:
                col_delta = -1
            o.append([previous_pos[-1], row_delta, col_delta])
            previous_pos=important_stuff
    d={}.fromkeys(["MoveEast", "MoveWest", "MoveSouth", "MoveNorth"])
    for action in d:
        t=filter(lambda x: x[0]==action, o)
        d[action]={}
        d[action]["row_increase"]=float(sum(1 for e in t if e[1]==1)+1)
        d[action]["row_decrease"]=float(sum(1 for e in t if e[1]==-1)+1)
        d[action]["row_same"]=float(sum(1 for e in t if e[1]==0)+1)
        s=d[action]["row_increase"]+d[action]["row_decrease"]+d[action]["row_same"]
        d[action]["row_increase"] /= s
        d[action]["row_decrease"] /= s
        d[action]["row_same"] /= s
        d[action]["col_increase"]=float(sum(1 for e in t if e[2]==1)+1)
        d[action]["col_decrease"]=float(sum(1 for e in t if e[2]==-1)+1)
        d[action]["col_same"]=float(sum(1 for e in t if e[2]==0)+1)
        s=d[action]["col_increase"]+d[action]["col_decrease"]+d[action]["col_same"]
        d[action]["col_increase"] /= s
        d[action]["col_decrease"] /= s
        d[action]["col_same"] /= s
    return d


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

def find_out_number_of_landmarks(variables):
    return max(int(v[15:].split("_")[0]) for v in variables if v.startswith("ObserveLandmark"))

def find_out_number_of_time_steps(variables):
    return 1+max(int(v[15:].split("_")[-1]) for v in variables if v.startswith("ObserveLandmark"))

def find_out_number_of_row(variables):
    return 1+max(int(v[12:]) for v in variables if v.startswith("PositionRow_"))

def find_out_number_of_col(variables):
    return 1+max(int(v[12:]) for v in variables if v.startswith("PositionCol_"))

####
## Command line input parsing 
####
network_file_name=sys.argv[1]
training_file_name=sys.argv[2]
output_cpd_file_name=sys.argv[3]

nf=[e.strip() for e in open(network_file_name).readlines()]
number_of_rv=int(nf[0])
random_variables={}
for e in nf[1:number_of_rv+1]:
    name=e.split(" ")[0]
    values=e.split(" ")[1].split(",")
    
    random_variables[name]=dict(values=values, context=[])

#print random_variables.keys()

T=find_out_number_of_time_steps(random_variables.keys())
L=find_out_number_of_landmarks(random_variables.keys())

rows=find_out_number_of_row(random_variables.keys())
cols=find_out_number_of_col(random_variables.keys())

print L, T, rows, cols
assert "PositionRow_1" in random_variables

for e in nf[number_of_rv+1:]:
    [context, rv]=e.split(" -> ")
    random_variables[rv]["context"].append(context)

transition_probs=get_transition_probs_from_the_insane_input_file(training_file_name)
observation_prob=get_observation_prob_from_insane_input_file(training_file_name)

######
##Calculate how many variables do I have to estimate?
#####
def yield_variable_combinations():
    for rv,v in random_variables.items():
        if not (rv.startswith("Action") or rv == "PositionRow_0" or rv == "PositionCol_0" ):
            context_variables=v["context"]
            possible_values_of_contexts=[random_variables[e]["values"] for e in context_variables]
            if possible_values_of_contexts != []:
                combinations_of_contexts=reduce(combine_two_lists, possible_values_of_contexts)
                #print rv, context_variables, combinations_of_contexts
                for context in combinations_of_contexts:
                    for value in v["values"]:
                        yield dict(rv=rv, value=value, context=dict(zip(context_variables, context)))
            else:
                #combinations_of_contexts=[""]
                raise Exception("not good " + str(rv))


output_file=open(output_cpd_file_name, "wb")
####
##Write the output file
####
for cpd in yield_variable_combinations():
    split_rv=cpd["rv"].split("_")
    time_value=split_rv[-1]
    rv_of_interest="_".join(split_rv[:-1])
    if cpd["rv"].startswith("Observe"):
        
        try:
            row=cpd["context"]["PositionRow_"+time_value]
        except :
            import pdb; pdb.set_trace()
        col=cpd["context"]["PositionCol_"+time_value]
        assert random_variables[cpd["rv"]]["values"] == ["Yes", "No"] or random_variables[cpd["rv"]]["values"] == ["No", "Yes"]
        
        probability={}
        probability["Yes"] = observation_prob[row+"_"+col][rv_of_interest]
        probability["No"] = 1-probability["Yes"]
        
        
        pval=probability[cpd["value"]]
        output_string="%(rv_of_interest)s_%(time_value)s=%(val_type)s PositionRow_%(time_value)s=%(row)s,PositionCol_%(time_value)s=%(col)s %(pval).6f\n"%dict(row=row, col=col, rv_of_interest=rv_of_interest, val_type=cpd["value"], pval=pval, time_value=time_value)
        output_file.write(output_string)
                #print o,
            #command = 'grep "'+ c1 + '" test_est_params_cpd.txt.gold '
            #print key, pval
            #print command 
            #os.system(command)
    elif cpd["rv"].startswith("Position"):
        rv=cpd["rv"]            
        positional_context_key=filter(lambda x: x.startswith("Position"), cpd["context"].keys())[0]
        action_context_key=filter(lambda x: x.startswith("Action"), cpd["context"].keys())[0]
        pcv=int(cpd["context"][positional_context_key])
        rvv=int(cpd["value"])
        acv=cpd["context"][action_context_key]
        if "Col" in positional_context_key:
            limit=cols
            key_prefix="col"
        else:
            limit=rows
            key_prefix="row"

        estimated_prob_value=None
        if rvv - pcv in [1, 1-limit]:
            estimated_prob_value=transition_probs[acv][key_prefix+"_increase"]
        elif rvv == pcv:
            estimated_prob_value=transition_probs[acv][key_prefix+"_same"]
        elif rvv -pcv in [-1, limit-1]:
            estimated_prob_value=transition_probs[acv][key_prefix+"_decrease"]
        else:
            pass
        if estimated_prob_value is not None:
            output_string="%(rv)s=%(rvv)d %(positional_context_key)s=%(pcv)d,%(action_context_key)s=%(acv)s %(estimated_prob_value).6f\n"%dict(
                rv=rv,
                rvv=rvv,
                positional_context_key=positional_context_key,
                pcv=pcv,
                action_context_key=action_context_key,
                acv=acv,
                estimated_prob_value=estimated_prob_value,
                )
            #print output_string,
            output_file.write(output_string)
    else:
        raise Exception("cant handle " + cpd["rv"])


output_file.close()
os.system("sort %s > tmp && uniq tmp > %s"%(output_cpd_file_name, output_cpd_file_name))
