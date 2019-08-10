import numpy
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import permutations
#########################################################
# 
#########################################################
def evaluate_interactions(C, md_stages,P,dP,ddP,delta_0,delta_1,delta_2):
    # Check Probability ABOVE threshold_0, for primary conformation C
    X0 = P[C][md_stages[0]] > delta_0
    # Check Probability difference between conformations, C as primary, ABOVE threshold_1
    # per MD stage
    X1_0 = dP[C][md_stages[0]] > delta_1
    X1_1 = dP[C][md_stages[1]] > delta_1
    X1 = X1_0*X1_1
    # Check Double Probability difference BELOW threshold_2
    X2 = ddP[C] < delta_2
    
    # Check all criteria are fullfilled per interaction, for conformation C
    Y = map(all,numpy.array([X0,X1,X2]).T)
    Z = [all(x) for x in numpy.array([X0,X1,X2]).T]
    # Return assessment per interaction, for conformation C
    return Z
#########################################################
# LOAD DataFrame 
#########################################################
workdir = '/projects/s21/ba13026/Wza_Modeling/L-structures/rosetta/bg_test/md_relax/md_100ns_dbs/dfs/'
df_name = 'df_hbonds_docked_to_urmd_0-10ns.json'
df_path = workdir+df_name

with open(df_path,'r') as fp:
    df_test = pd.DataFrame(json.load(fp))
# Extract interaction data for mutant conformations
dc = 0
df_columns = [str(0+dc),str(7+dc),str(1+dc),str(8+dc)] # Docked and PRMD data, per conformations
df_mutant = df_test[df_columns].fillna(0) # Replace NaN entries with zeros
#########################################################
# INTERACTION ASSESSMENT 
#########################################################
## Threshold values
delta_0 = 0.1; delta_1 = 0.1; delta_2 = 0.4

## Conformations and MD stages to compare
conformations = ['Conformation0', 'Conformation1']
md_stages = ['docked', 'prmd']

## Define Probability differences
P = {
    'Conformation0' : {
        'docked': numpy.array(df_mutant[df_columns[0]]),
        'prmd'  : numpy.array(df_mutant[df_columns[1]])
    },
    'Conformation1' : {
        'docked': numpy.array(df_mutant[df_columns[2]]),
        'prmd'  : numpy.array(df_mutant[df_columns[3]])
    }
}

dP = {}
for C_xy in list(permutations(conformations,2)):
    C_x = C_xy[0]; C_y = C_xy[1];
    dP[C_x] = {}; 
    for stage in md_stages:
        # Porbability difference, identical MD stage
        dP[C_x][stage] = P[C_x][stage] - P[C_y][stage]

ddP = {}
for C_x in conformations:
    # Fluctuations in Probability differences between stages
    ddP[C_x] = abs( dP[C_x][md_stages[-1]] - dP[C_x][md_stages[0]] )
#########################################################
Z = []
for C in conformations:
    output = evaluate_interactions(C, md_stages,P,dP,ddP,delta_0,delta_1,delta_2)
    Z.append(list(map(int,output)))

print(Z)