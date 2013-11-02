import os, sys, re
network_file_name=sys.argv[1]
training_file_name=sys.argv[2]
output_cpd_file_name=sys.argv[3]
#print network_file_name, training_file_name

nf=[e.strip() for e in open(network_file_name).readlines()]
number_of_rv=int(nf[0])
names_and_values_of_rv=[dict(name=e.split(" ")[0], values=e.split(" ")[1].split(",")) for e in nf[1:number_of_rv+1]]
random_variables={}
for e in names_and_values_of_rv:
    random_variables[e["name"]]=dict(values=e["values"], context=[])

assert "ObserveLandmark2_W_9" in random_variables
assert "PositionRow_1" in random_variables

for e in nf[number_of_rv+1:]:
    [context, rv]=e.split(" -> ")
    random_variables[rv]["context"].append(context)

assert random_variables["PositionRow_1"]==dict(values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], context=["Action_0", "PositionRow_0"]), random_variables["PositionRow_1"]

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

#How many variables do I have to estimate?
cpd_to_estimate={}
for rv,v in random_variables.items():
    context_variables=v["context"]
    possible_values_of_contexts=[random_variables[e]["values"] for e in context_variables]
    if possible_values_of_contexts != []:
        combinations_of_contexts=reduce(combine_two_lists, possible_values_of_contexts)
    else:
        combinations_of_contexts=[""]
    for context in combinations_of_contexts:
        for value in v["values"]:
            #print "%(rv)s=%(value)s %(context)s"%dict(rv=rv, value=value, context=",".join(["=".join(e) for e in zip(context_variables, context)]))
            cpd_to_estimate[rv+value+str(context)]=dict(rv=rv, value=value, context=dict(zip(context_variables, context)), context_string=str(context), estimated_value=None)

landmarks=set([e["rv"][15] for e in cpd_to_estimate.values() if e["rv"].startswith("ObserveLandmark")])
time_points=set(e["rv"][-1] for e in cpd_to_estimate.values())
rows=set([e["value"] for e in cpd_to_estimate.values() if e["rv"].startswith("PositionRow")])
cols=set([e["value"] for e in cpd_to_estimate.values() if e["rv"].startswith("PositionCol")])
actions=set([e["value"] for e in cpd_to_estimate.values() if e["rv"].startswith("Action")])
#Start counting
#Count the observations Model
training_data=open(training_file_name).readlines()
for cpd in cpd_to_estimate.values():
    if cpd["estimated_value"] is None:
        if cpd["rv"].startswith("Observe"):
            cpdrvm1=cpd["rv"][-1]
            cpdrvupto1=cpd["rv"][:-1]
            row=cpd["context"]["PositionRow_"+cpdrvm1]
            col=cpd["context"]["PositionCol_"+cpdrvm1]
            values_that_this_rv_can_take=random_variables[cpd["rv"]]["values"]
            restr=".*PositionRow_.=%(row)s PositionCol_.=%(col)s .*%(cpdrvupto1)s.=(%(options)s)"%dict(row=row, col=col, cpdrvupto1=cpdrvupto1, options="|".join(values_that_this_rv_can_take))
            regex_to_search=re.compile(restr)
            eligible_observations=[e for e in training_data if re.match(regex_to_search, e)]
            denominator=len(eligible_observations)+len(values_that_this_rv_can_take)

            
            print "regex", restr
            print "total_observations ", len(eligible_observations)
            print "denominator ", denominator, " it should be total_observation+2"

            
            for value in values_that_this_rv_can_take:
                restr=".*PositionRow_.=%(row)s PositionCol_.=%(col)s .*%(cpdrvupto1)s.=%(value)s"%dict(row=row, col=col, cpdrvupto1=cpdrvupto1, value=value)
                
                regex_to_search=re.compile(restr)
                e2=[e for e in eligible_observations if re.match(regex_to_search, e)]
                numerator = len(e2)+1

                print "value we are filtering on ", value
                print "numerator regex ", restr
                print "numerator ", numerator
                
                for time in time_points:
                    key=cpdrvupto1+time+value+cpd["context_string"]
                    print key, numerator/float(denominator)
                    assert key in cpd_to_estimate
                    cpd_to_estimate[key]["estimated_value"]=numerator/float(denominator)
                reg_gold_output="%(cpdrvupto1)s.=%(value)s PositionRow_.=%(row)s,PositionCol_.=%(col)s"%dict(row=row, col=col, value=value, cpdrvupto1=cpdrvupto1)
                command = 'grep "'+reg_gold_output + '" test_est_params_cpd.txt.gold'
                print command 
                os.system(command)
                import pdb; pdb.set_trace()

        
        
# count_observations=defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
# for row in rows:
#     for col in cols:
#         for landmark in landmarks:
#             for direction in directions:
#                 #find all occurences of row col landmark_direction regardless of value.
#                 for value_of_landmark_direction in ["yes", "no"]:
#                     count_observations[row][col][landmark_direction] += specific_count+1/total_count+2 #the number of times this particular row occurs in the training data.

#We need to match every CPD of form 'ObserveLandmark2_S_8=Yes PositionRow_8=10,PositionCol_8=10'
#to strings of form 'ObserveLandmark2_S_[123456789]=Yes PositionRow_[123456789]=10,PositionCol_[123456789]=10'
contexts_to_count=[]
    

    
