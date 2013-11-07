class Query(object):
def __init__(self, variable, evidence, is_additive) v is a list, e is a list of (variable, value) tuples, is_additive is bool
get_clique_id_from_clique_str=tuple(sorted(clique_str.split(",")))
get_required_factors(c) if len(c)==3 then return self.cpd[(c_O(c), c_R(c), c_P(c))] 
                        else assert len(c)==5 then return (self.cpd[(c_Rtpp(c), c_Rt(c), c_A(c))], self.cpd[(c_Ctpp(c), c_Ct(c), c_A(c))])
choose_appropriate_clique(q) figure out the highest time in all of the times for all the variables in the query. and the corresponding random variable.
                             call that random variables r
                             if it gets a string make that a [string] (a list basically)
                             if r contains "Observation"  only one clique get clique id from observation, position and row
                             else if r contains "action"  only one clique get clique id from action_t, col_t, row_t, col_t+1, row_t+1
                             else assert r contains PositionRow or PositionCol and there is a special case
                                     if t == 0 then get  action_0, row_0, col_0, row_1, col_1
                                     else get action_t-1, row_t-1, col_t-1, row_t, col_t
figure_out_variables_to_marginalize_to_answer_query(apt_clique_id, query) return tuple([e for e in apt_clique_id if e not in query.variables])
Query_Processor
   get_queries(query_filename)
       all queries are made from Query class
   graph
   process_queries
      for q in self.queries:
          if q.is_additive self.graph.process_query(q.variable, q.evidence)
          #All evidence must be strictly differential in case of addition
          else self.graph.reset() ; self.process_query(q)
   process_query(q)
       return self.graph.process_query(q.variable, q.evidence)
class Clique
     self.belief
     self.sepsets=[]
     self.is_ready
     self.is_done
     __init__(self, clique_id, initial_belief)
     add_sepset(sepset_id, other_clique_id) assert one of them is the clique_id itself.
          self.sepsets.append((sepset_id, other_clique_id))
     marginalize
class Sepset __init__(self, endpoints, shared_variables)
     last_message # it must be initialized to None.
div_func(x, y):
     try:
         return x/y
     except:
         return 0.0
get_stride_from_card(card):
     stride=[None]*len(card)
     stride[0]=1
     for i,c in enumerate(card[:-1]):
         stride[i+1]=stride[i]*c
     return stride
class Named_Factor_Matrix
     __init__(self, names, card, stride, values)
     assert names is a tuple.
     names=names
     card
     stride=get_stride_from_card(card)
     val=val
     get_union_of_names_and_card(self, new_names, new_card) # return a tuple
     operate(self, Y, operation_fnc)
         j=0
         k=0
         [united_names, united_card]=get_union_of_names_and_card()
         united_val_len=reduce(lambda x, y: x*y, united_card)
         assignment=[0]*len(united_names)
         united_val=[None]*(united_val_len-1)
         for i=xrange(0:united_val_len)
             united_val[i]=operation_fnc(self.val[j], Y.val[k])
             for l = xrange(0, len(assignment))
                 assignment[l]+=1
                 if assignment[l]==card[l] then
                     assignment[l]=0
                     j = j - (card[l] - 1) * self.stride[l]
                     k = k - (card[l] - 1) * Y.stride[l]
                 else
                     j = j + self.stride[l]
                     k = k + Y.stride[l]
                     break
         return Named_Factor_Matrix(united_names, united_card, get_stride_from_card(united_card), united_val)

     marginalize(variables_to_marginalize_out):
          basic_table=self.val
          basic_names=names
          basic_card=card
          basic_stride=stride
          for name_to_marg in variables_to_marginalize_out:
              index_to_marg = basic_names.index(name_to_marg)
              card_to_marg=basic_card[index_to_marg]
              stride_to_marg=basic_stride[index_to_marg]
              new_stuff=lambda x: [e for i,e in enumerate(x) if i != index_to_marg]
              new_names=new_stuff(basic_names)
              new_card=new_stuff(basic_card)
              new_stride=get_stride_from_card(new_card)
              old_reduced_stride=new_stuff(basic_stride)
              new_table_len=reduce(lambda x, y: x*y, new_card)
              new_table=[None]*new_table_len
              assignment=[0]*len(new_names)
              for i=xrange(0: new_table_len):
                  for l = 0 to len(assignment):
                      assignment[l]+=1
                      if assignment[l]==new_card[l]:
                          assignment[l]=0
                      else:
                          break
                  #_i is location (in basic table) (of assignment)
                  _i=reduce(lambda x, y: x[0]*x[1]+y[0]+y[1], zip(old_reduced_stride, assignment))
                  new_table[i]=sum(basic_table[_i: _i+card_to_marg*stride_to_marg: stride_to_marg])
              basic_table=new_table
              basic_names=new_names
              basic_card=new_card
              basic_stride=new_stride
          return Named_Factor_Matrix(new_names, new_card, new_stride, new_table)
              
     evidentiate(variable, value) #It is inplace unlike other methods
          assert type(value) is int
          idx=self.names.index(variable)
          var_card=self.card[idx]
          increment_arr=[None]*len(self.card)
          increment_arr[0]=self.card[0]
          for i=1:len(self.stride)
              increment_arr[i]=increment_arr[i-1]*self.card[i]
          var_increment=increment_arr[idx]
          var_stride=self.stride[idx]
          valid_indices=[]
          for i=0: len(self.val): var_increment
              iv=i+value*var_card
              valid_indices.extend(io+j for j in 0:var_stride)
          valid_indices=set(valid_indices)
          for i=0:len(self.val)
              if i not in valid_indices:
                  self.val[i]=0
                  
     divide(divider) #I am being divided by the divider
         operate(divider, div_func)
     multiply(self, Y)
        operate(multiply, lambda x, y: x * y)
Graph
   self.clique_set
   self.sepset_set
   self.cpd
   populate_cpd(cpd_file_name) (c_O(c), c_R(c), c_P(c)) (c_Rtpp(c), c_Rt(c), c_A(c)) (c_Ctpp(c), c_Ct(c), c_A(c))
         map =No to 0
         map =Yes to 1
         map MoveNorth to 0
         map MoveEast to 1
         map MoveWest to 2
         map MoveSouth to 3
         for line ObserveLandmark1_E_0=No PositionRow_0=1,PositionCol_0=1 0.803810
         the cpd_id is (ObserveLandmark1_E_0, PositionRow_0, PositionCol_0)
         for line PositionRow_9=6 PositionRow_8=7,Action_8=MoveEast 0.000047
         the cpd_id is (PositionRow_9, PositionRow_8, Action_8)
         for line PositionCol_5=7 PositionCol_4=6,Action_4=MoveNorth 0.000046
         the cpd_id is  (PositionCol_5, PositionCol_4, Action_4)
         the value is the value after the last space in floating point
         the assignment is the value after the = once we replace the comma with a space
         try :
             the cardinality is already in the cpd
             the stride is already in the cpd
             the location is defined by weighted sum of assignment and stride
         except :
             calculate cardinality and stride and fill those in the object
             create a Named_Factor_Matrix object at self.cpd[cpd_id] with the correct cardinality and stride.
             the location is defined by weighted sum of assignment and stride
         self.cpd[cpd_id].val[location]=value

   incrementally_incorporate_evidence(evidence):
       for evid_var, value in evidence:
           apt_clique=choose_appropriate_clique(evid_var)
           apt_clique.factor.evidentiate(evid_var, value)
   initialize(cliquetree_file_name)
       create_cliques_and_sepsets(cliquetree_file_name)
       populate_cpd(cpd_file_name)
       designated_root_id=pick_random_clique()
       self.caliberate(designated_root_id)
       self.backup_clique_set=dict(self.clique_set)
       self.backup_sepset_set=dict(self.sepset_set)
   create_cliques_and_sepsets(cliquetree_file_name, cpd_file_name)
       for every clique_str in file
          clique_id=get_clique_id_from_clique_str(clique_str)
          required_factors=get_required_factors(clique_id)
          initial_belief=reduce(lambda x, y: x.multiply(y), required_factors)
          self.clique_set[clique_id]=Clique(clique_id, initial_belief)
       for every sepset_str in file
          sepset_id=tuple([get_clique_id_from_clique_str(e) for e in sepset_str.split(" -- ")])
          shared_variables=tuple([e for e in sepset_id[0] if e in sepset_id[1]])
          self.sepset_set[sepset_id]=Sepset(sepset_id, shared_variables)
          self.clique_set[sepset_id[0]].add_sepset(sepset_id, sepset_id[1])
          self.clique_set[sepset_id[1]].add_sepset(sepset_id, sepset_id[0])
   caliberate(designated_root_id, do_only_downward_pass=False)
       que=[designated_root_id]
       counter=0
       #make an ordering of nodes
       while len(que) < len(self.clique_set):
           current_clique_id=que[counter]
           for sepset_id, other_clique_id in self.clique_set[current_clique].sepsets:
               que.append(sepset_id, current_clique_id, other_clique_id)
           counter+=1
       #pass message in upward pass(towards root)
       if do_only_downward_pass then skip upward_pass
           for sepset_id, recipient, sender in que[::-1]:
               pass_message(sender, recipient, sepset_id)
       #pass message in downward pass(from root)
       for sepset_id, sender, recipient in que:
           pass_message(sender, recipient, sepset_id)
       return
   pass_message(sender_id, recipient_id, sepset_id) 
       ??? marginalize sender belief
       ??? divide sender belief by sepset_belief (handle the case where sepset_belief is None)
       ??? update sepset_belief
       ??? multiply the message to belief
   process_query(variable, evidence)
     assert variable is tuple and evidence is tuple
     if evidence is not None:
        self.incrementally_incorporate_evidence(evidence)
        do_only_downward_pass=False
        if len(evidence)==1:
            designated_root_id=choose_appropriate_clique(evidence[0][0])
            do_only_downward_pass=True
        else:
            designated_root_id=pick_random_clique()#change this 
        self.caliberate(designated_root_id, do_only_downward_pass)
     apt_clique_id=choose_appropriate_clique(variable)
     v2m_out=figure_out_variables_to_marginalize_to_answer_query(apt_clique_id, variable)
     return self.clique_set[apt_clique_id].belief.marginalize(v2m_out)
   reset() QQQ Must check that this actually works to copy over these objects QQQ
        self.clique_set=copy.deepcopy(self.backup_clique_set)
        self.sepset_set=copy.deepcopy(self.backup_sepset_set)
