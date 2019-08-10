import sys
import numpy
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import permutations

def is_significant(X, delta):
    X = numpy.array(X)
    assessment = X > delta
    return assessment

def is_relevant_to_conformation(X_a, X_b, delta):
    """Assess relevance of interactions relative to a conformation in contrast to another above some threshold"""
    X_a = numpy.array(X_a)
    X_b = numpy.array(X_b)
    try:
        dX = X_a - X_b
        assessment = dX > delta
        return assessment
    except:
        print("Check input vectors")

def is_robust_after_md(X_init, X_final, delta_2):
    """Assess probability change between different simulation stages up to some threshold"""
    X_init  = numpy.array(X_init)
    X_final = numpy.array(X_final)
    
    dX = X_final - X_init
    bol_assessment = abs(dX) < delta_2

    return bol_assessment

def is_relevant_and_robust(P, conformations, md_stages, Deltas):
    """Assess whethere relevance of iteractions per conformations is robust under MD stages"""
    delta_0 = Deltas[0]
    delta_1 = Deltas[1]
    delta_2 = Deltas[2]
    stage_init = md_stages[0]; stage_final = md_stages[-1]
    Z = []
    for C_ab in list(permutations(conformations,2)):
        C_a = C_ab[0]; C_b = C_ab[1];
        X_a_init = P[C_a][stage_init] ; X_a_final = P[C_a][stage_final]
        X_b_init = P[C_b][stage_init] ; X_b_final = P[C_b][stage_final]
        ############################################
        test0_a_init = is_significant(X_a_init, delta_0)

        test1_a_init = is_relevant_to_conformation(X_a_init, X_b_init, delta_1)
        test1_a_final = is_relevant_to_conformation(X_a_final, X_b_final, delta_1)

        test2_a = is_robust_after_md(X_a_final - X_a_init, X_b_final - X_b_init, delta_2)
        ############################################
        overall = numpy.array([
                                test0_a_init,
                                test1_a_init*test1_a_final,
                                test2_a
                            ]).T

        bol_assessment = [all(x) for x in overall]
        Z.append(list(map(int,bol_assessment)))
    return Z
########################################################
if __name__ ==  "__main__" :
    df_name = sys.argv[1] # JSON DF input
    outfile = sys.argv[2] # JSON output
    #########################################################
    # LOAD DataFrame 
    #########################################################
    workdir = '/projects/s21/ba13026/Wza_Modeling/L-structures/rosetta/bg_test/md_relax/md_100ns_dbs/'
    df_path = workdir+df_name

    with open(df_path,'r') as fp:
        df_test = pd.DataFrame(json.load(fp))
    #########################################################
    # INTERACTION ASSESSMENT 
    #########################################################
    ## Set up values
    md_stages = ['docked', 'prmd'] 
    mutant_names = ['cWza','cWza-K375C','cWza-S355C','cWza-Y373C']

    CONFORMATIONS = {
        'cWza' : ['Conformation0', 'Conformation1'],
        'cWza-K375C' : ['Conformation0', 'Conformation1'],
        'cWza-S355C' : ['Conformation0', 'Conformation1'],
        'cWza-Y373C' : ['Conformation1']
    }
    
    ## Threshold values
    Deltas = [0.1, 0.1, 0.4]
    dc = 0
    ASSESSMENT = {}
    for i in range(len(mutant_names)):
        mutant = mutant_names[i]
        conformations = CONFORMATIONS[mutant]
        if mutant != 'cWza-Y373C':
            #########################################################
            # Extract interaction data for mutant conformations and MD stages
            #########################################################
            if mutant != 'cWza-K375C':
                df_columns = [str(0+dc),str(14+dc),str(1+dc),str(15+dc)] # Docked and PRMD data, per conformations
            else:
                df_columns = [str(0+dc),str(15+dc),str(1+dc),str(14+dc)] # Docked and PRMD data, per conformations
            df_mutant = df_test[df_columns].fillna(0) # Replace NaN entries with zeros
            ## Conformations and MD stages to compare
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
            #########################################################
            # Interaction assessment
            #########################################################
            assessment =  is_relevant_and_robust(P, conformations, md_stages, Deltas)
            ASSESSMENT[mutant] = assessment
            
        else: 
            #########################################################
            # Extract interaction data for mutant single conformation and MD stages
            #########################################################
            df_columns = [str(0+dc),str(14+dc)] # Docked and PRMD data, per conformations
            df_mutant = df_test[df_columns].fillna(0) # Replace NaN entries with zeros
            ## Conformations and MD stages to compare
            P = {
                'Conformation1' : {
                    'docked': numpy.array(df_mutant[df_columns[0]]),
                    'prmd'  : numpy.array(df_mutant[df_columns[1]])
                                }
                }
            #########################################################
            # Interaction assessment
            #########################################################
            delta_0 = Deltas[0]; delta_2 = Deltas[2]
            C = 'Conformation1'
            X_init = P[C]['docked']; X_final = P[C]['prmd'];
            test_0 = is_significant(X_init, delta_0)
            test_1 = is_robust_after_md(X_init, X_final, delta_2)
            overall = numpy.array([
                    test_0,
                    test_1
                ]).T
            assessment = list(map(int,[all(x) for x in overall]))
            #########################################################
            ASSESSMENT[mutant] = assessment
        dc += 2
    #########################################################
    # Save data in DF as JSON file
    #########################################################
    # DF Columns
    Columns = [
    'cWza:C0',
    'cWza:C1',
    'cWza-K375C:C0',
    'cWza-K375C:C1',
    'cWza-S355C:C0',
    'cWza-S355C:C1',
    'cWza-Y373C:C'
    ]
    # Get data for heatmap
    inter_dict = ASSESSMENT
    Data = numpy.array([
        inter_dict['cWza'][0],
        inter_dict['cWza'][1],
        inter_dict['cWza-K375C'][0],
        inter_dict['cWza-K375C'][1],
        inter_dict['cWza-S355C'][0],
        inter_dict['cWza-S355C'][1],
        inter_dict['cWza-Y373C']
        ]).T
    # Define DF and filter out
    df_out = pd.DataFrame(Data, columns=Columns)
    df_out.set_axis(list(df_test.index),axis=0)
    df_out.to_json(outfile)