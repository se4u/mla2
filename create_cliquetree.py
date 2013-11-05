#python create_cliquetree.py  f/network-grid10x10-t10.txt cliquetree-grid10x10-t10.txt 
#python create_cliquetree.py  f/network-grid10x10-t100.txt cliquetree-grid10x10-t100.txt
#python create_cliquetree.py  f/network-grid10x10-t1000.txt cliquetree-grid10x10-t1000.txt
#python create_cliquetree.py  f/network-grid15x15-t100.txt   cliquetree-grid15x15-t100.txt   
#python create_cliquetree.py  f/network-grid25x25-t100.txt cliquetree-grid25x25-t100.txt
#python create_cliquetree.py  f/network-grid30x30-t100.txt cliquetree-grid30x30-t100.txt
#python create_cliquetree.py  f/network-grid40x40-t100.txt cliquetree-grid40x40-t100.txt
#Running these commands would create the clique tree file.
import sys
input_file_name=sys.argv[1]
output_file_name=sys.argv[2]

f=open(input_file_name)
number_of_variables=int(f.next())
variables=[e.split(" ")[0] for e in list(f)[:number_of_variables]]
def find_out_number_of_landmarks(variables):
    return max(int(v[15:].split("_")[0]) for v in variables if v.startswith("ObserveLandmark"))

def find_out_number_of_time_steps(variables):
    return 1+max(int(v[7:]) for v in variables if v.startswith("Action_"))

T=find_out_number_of_time_steps(variables)
L=find_out_number_of_landmarks(variables)
#print L, T

number_of_cliques=(4*L+4+1)*T-1
cliques=[]
edges=[]
previous_clique=None
for t in range(0, T):
    row_string="PositionRow_%d"
    col_string="PositionCol_%d"
    action_string="Action_%d"
    if t < T-1:
        mega_clique=",".join([row_string%t, col_string%t, action_string%t, col_string%(t+1), row_string%(t+1)])
        cliques.append(mega_clique)
    else:
        mega_clique=0
    for direction in ["N", "E", "W", "S"]:
        ob_clique=",".join(["ObserveWall_%s_%d"%(direction, t), row_string%t, col_string%t])
        cliques.append(ob_clique)
        if t < T-1:
            edges.append(" ".join([mega_clique, "--", ob_clique]))
        else:
            edges.append(" ".join([previous_clique, "--", ob_clique]))
        for landmark in range(1, L+1):
            ob_clique=",".join(["ObserveLandmark%d_%s_%d"%(landmark, direction, t), row_string%t, col_string%t])
            cliques.append(ob_clique)
            if t < T-1:
                edges.append(" ".join([mega_clique, "--", ob_clique]))
            else:
                edges.append(" ".join([previous_clique, "--", ob_clique]))
    if t > 0 and t < T-1: #Add edge
        edges.append(" ".join([previous_clique, "--", mega_clique]))
    else:
        pass
    previous_clique=mega_clique

f.close()
assert number_of_cliques==len(cliques), len(cliques)
assert number_of_cliques-1 == len(edges)
with open(output_file_name, "wb") as f:
    for e in [number_of_cliques] + cliques + edges:
        f.write(str(e)); f.write("\n")
