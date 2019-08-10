import os
import sys
import numpy
import json
import subprocess
import isambard_dev
import operator
import pandas as pd
from operator import itemgetter
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('darkgrid')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

modules_path = "/home/ba13026/mpmodeling/analysis/"
if modules_path not in sys.path:
    sys.path.append(modules_path)

import setup_geometry_interactions_db
from setup_geometry_interactions_db import \
    Json,Tags,RigidBody,RadialProfiles,Miscellaneous,Interhelix_Interactions, Base
from insert2db_geometry_interactions import interaction_direction

def sort_superbase(S_inter, N_residues=32):
    Y = list(S_inter)
#     Y = [json.dumps(x[:-1]+[interaction_direction(x[-1])]) for x in [json.loads(x) for x in X]]
    S_inter_sorted = []
    for resn in range(1,N_residues+1):
        for y in Y:
            x = json.loads(y)
            if int(x[0]) == resn:
                S_inter_sorted.append(json.dumps(x))
    return S_inter_sorted

def start_session(db_path):
    engine = create_engine('sqlite:///'+db_path)
    Base.metadata.bind = engine
    DBSession = sessionmaker()
    DBSession.bind = engine
    session = DBSession()
    return session

class Models:
    def __init__(self, session):
        self.session = session
        self.ids = []

class Analyse_Interactions(object):
    def __init__(self, models):
        self.dbtag = {
            'hbonds': Interhelix_Interactions.hbonds,
            'kihs': Interhelix_Interactions.kihs
        }
        self.session = models.session
        self.models_ids = models.ids
        self.interaction_probability = self.Interaction_Probability
        self.superbase = self.get_superbase
        self.tools = Tools()


    def get_superbase(self, inter_type):
        N_residues = 32
        S_inter = set()    
        for j in range(len(self.models_ids)):
            id = self.models_ids[j]
            data = self.session.query(self.dbtag[inter_type]).filter_by(id=id).first()[0]
            S_inter = S_inter.union(set(data))
        # Sort base by residue number    
        X = list(S_inter)
        Y = [json.dumps(x[:-1]+[interaction_direction(x[-1])]) for x in [json.loads(x) for x in X]]
        S_inter_sorted = []
        for resn in range(1,N_residues+1):
            for y in set(Y):
                x = json.loads(y)
                if int(x[0]) == resn:
                    S_inter_sorted.append(json.dumps(x))
        return S_inter_sorted
    
    def get_interaction_data(self, inter_type):
        mutant_interaction_data = {}
        for j in range(len(self.models_ids)):
            id = self.models_ids[j]
            try:
                data = self.session.query(self.dbtag[inter_type]).filter_by(id=id).first()[0]
                mutant_interaction_data[id] = data
            except:
                print("No Interaction data for id: ", id)
        return mutant_interaction_data

    def get_interaction_stats(self, S_inter, mutant_interaction_data):
        S = S_inter
        X = mutant_interaction_data
        mutant_interaction_stats = {}
        for id in list(X.keys()):
            decomposition_vector = []
            for s in S:
                counter = 0
                for x in X[id]:
                    x_raw = json.loads(x)
                    y = json.dumps(x_raw[:-1]+[interaction_direction(x_raw[-1])])
                    if y == s:
                        counter +=1
                decomposition_vector.append(counter)
            mutant_interaction_stats[id] = decomposition_vector
        return mutant_interaction_stats

    def get_interaction_probability(self, S_inter, mutant_interaction_stats, N_chains = 8):
        probability_data_raw = {}        
        Sx = S_inter        
        data = mutant_interaction_stats
        N_models = len(list(mutant_interaction_stats.keys()))
        X = numpy.zeros(len(Sx))
        for id in list(data.keys()):
            x = data[id]
            X = X + numpy.asarray(x)
        probability_inter = X/float(N_chains*N_models)
        return probability_inter
    
    def Interaction_Probability(self, superbase, inter_type):
#         superbase = self.get_superbase(inter_type)
        atoms = self.get_interaction_data(inter_type)
        stats =  self.get_interaction_stats(superbase, atoms)
        probability = self.get_interaction_probability(superbase, stats)
        return probability
    
class Tools:
    def __init__(self):
        pass

    def relabel_interaction_json(self, atoms_json, inter_type):
        try: 
            if inter_type == 'hbonds':
                ho_atoms = json.loads(atoms_json)
                label = ho_atoms[0]+'-'+ho_atoms[1]+' ||| '+ ho_atoms[2]+'-'+ho_atoms[3]+', '+str(ho_atoms[-1])
            elif inter_type == 'kihs':
                kih_atoms = json.loads(atoms_json)
                knob = kih_atoms[0]
                hole = "-".join(kih_atoms[1:-1])
                direct = kih_atoms[-1]
                label = knob+' >> '+hole+', '+str(direct)
            return label
        except:
            print("Provide a valid interaction type")

    def labels_df(self, S_inter, inter_type):
        return [self.relabel_interaction_json(s, inter_type) for s in S_inter]
