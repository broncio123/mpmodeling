import os
import sys
import numpy
import pandas as pd
import json
import subprocess
import isambard_dev
import operator
import matplotlib.pyplot as plt
plt.switch_backend('agg')
from operator import itemgetter
import seaborn as sns

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
##########################################################
modules_paths = [
    "/home/ba13026/mpmodeling/analysis",
    "/home/ba13026/mpmodeling/protocols"
]

for path in modules_paths:
    if path not in sys.path:
        sys.path.append(path)
##########################################################
from cluster_transfer import BG
        
import setup_geometry_interactions_db
from setup_geometry_interactions_db import \
    Json,Tags,RigidBody,RadialProfiles,Miscellaneous,Interhelix_Interactions, Base

from insert2db_geometry_interactions import interaction_direction

import geometry_interactions
from geometry_interactions import Models, Analyse_Interactions, start_session, sort_superbase
##########################################################
inter_type = sys.argv[1] # Define either 'kihs' or 'hbonds'
start_frame_no = int(sys.argv[2])
WD = BG.workdir+'md_100ns_dbs/'
##########################################################
class MyDB:
    def __init__(self):
        self.db_path = ''
        self.name = ''
        self.tags = []
        self.id_extractor = ''
##########################################################
# DOCKED MODELS
docked = MyDB()
db_path = WD+'mutants_docked_geometry-interactions.db'
docked.db_path = db_path 
docked.name = 'docked'
docked.tags = [
            json.dumps(['cWza','conformation0']),
            json.dumps(['cWza','conformation1']),
            json.dumps(['cWza-K375C','conformation0']),
            json.dumps(['cWza-K375C','conformation1']),
            json.dumps(['cWza-S355C','conformation0']),
            json.dumps(['cWza-S355C','conformation1']),
            json.dumps(['cWza-Y373C','conformation0'])
            ]

# STUFF FOR DATABASE ID EXTRACTION
with open(WD+'filtered_ids_new.json','r') as fp:
    Filtered_IDs = json.load(fp)

def extractor_docked(session, tags):
    mutant, group = json.loads(tags)
    return list(Filtered_IDs[mutant][group])

docked.id_extractor = extractor_docked
##########################################################
# EMMD MODELS
emmd = MyDB()
db_path = WD+'mutants_em-conformations_geometry-interactions.db'
emmd.db_path = db_path
emmd.name = 'emmd'
emmd.tags = [
            json.dumps(['cWza','em-conformation0']),
            json.dumps(['cWza','em-conformation1']),
            json.dumps(['cWza-K375C','em-conformation0']),
            json.dumps(['cWza-K375C','em-conformation1']),
            json.dumps(['cWza-S355C','em-conformation0']),
            json.dumps(['cWza-S355C','em-conformation1']),
            json.dumps(['cWza-Y373C','em-conformation1'])
            ]

def extractor_emmd(mysession, tags):
    mutant, group = json.loads(tags)
    return [x[0] for x in mysession.query(Tags.id).filter_by(mutant=mutant,group=group).all()]

emmd.id_extractor = extractor_emmd
##########################################################
# PRMD MODELS
prmd = MyDB()
db_path = WD+'mutants_prmd-conformations_geometry-interactions.db'
prmd.db_path = db_path
prmd.name = 'prmd'
prmd.tags = [
            json.dumps(['cWza','conformation0']),
            json.dumps(['cWza','conformation1']),
            json.dumps(['cWza-K375C','conformation0']),
            json.dumps(['cWza-K375C','conformation1']),
            json.dumps(['cWza-S355C','conformation0']),
            json.dumps(['cWza-S355C','conformation1']),
            json.dumps(['cWza-Y373C','conformation1'])
            ]

def get_ModelsIDs_prmd(session):
    inter_tags = {
            'hbonds': Interhelix_Interactions.hbonds,
            'kihs': Interhelix_Interactions.kihs
    }
    with open(WD+'mutants_prmd_conformations_pdb_paths.json','r') as fp:
        DBTags = json.load(fp)
    
    FrameRange = range(40,51) 
    ModelsIDs_per_tag = {}
    
    for tag in prmd.tags:
        ModelsIDs_per_tag[tag] = []
        for info in DBTags:
            mutant, group, pdb_name = info[0]
            conformation, stage_name, frame_no = group.split(':')
            db_tag = json.dumps([mutant, conformation])
            if (db_tag == tag) and (int(frame_no) in FrameRange):
                try:
                    db_id = session.query(Tags.id).filter_by(mutant=mutant,group=group,pdb_name=pdb_name).first()[0]
                    ModelsIDs_per_tag[tag].append(db_id)
                except:
                    print("No ID for model: ", mutant, group, pdb_name)
    # Find IDs with no interaction data
    IDs_to_remove = []
    for i in range(len(prmd.tags)):
        for id in list(ModelsIDs_per_tag[prmd.tags[i]]):
            for inter_type in inter_tags.keys():
                try:
                    data = session.query(inter_tags[inter_type]).filter_by(id=id).first()[0]
                except:
                    IDs_to_remove.append([prmd.tags[i], id])
    # Remove IDs with no interaction data
    for x in IDs_to_remove:
        tag, id = x
        try:
            ModelsIDs_per_tag[tag].remove(id)
        except:
            pass
    return ModelsIDs_per_tag

def extractor_prmd(session, db_tag):
    ModelsIDs_per_tag = get_ModelsIDs_prmd(session)
    return ModelsIDs_per_tag[db_tag]    

prmd.id_extractor = extractor_prmd
##########################################################
# URMD MODELS
urmd = MyDB()
n = start_frame_no
db_path = WD+'mutants_urmd_'+str(n)+'-'+str(n+10)+'ns-conformations_geometry-interactions.db'
urmd.db_path = db_path
urmd.name = 'urmd_'+str(n)+'-'+str(n+10)+'ns'
urmd.tags = [
            json.dumps(['cWza','conformation0']),
            json.dumps(['cWza','conformation1']),
            json.dumps(['cWza-K375C','conformation0']),
            json.dumps(['cWza-K375C','conformation1']),
            json.dumps(['cWza-S355C','conformation0']),
            json.dumps(['cWza-S355C','conformation1']),
            json.dumps(['cWza-Y373C','conformation1'])
            ]

##########################################################
# STUFF FOR DATABASE ID EXTRACTION
##########################################################
def get_ModelsIDs_urmd(session):
    inter_tags = {
            'hbonds': Interhelix_Interactions.hbonds,
            'kihs': Interhelix_Interactions.kihs
    }
    n = start_frame_no
    with open(WD+'mutants_urmd_'+str(n)+'-'+str(n+10)+'ns-conformations_pdb_paths.json','r') as fp:
        DBTags = json.load(fp)
    
    FrameRange = range(start_frame_no,start_frame_no+11) 
    ModelsIDs_per_tag = {}
    
    for tag in urmd.tags:
        ModelsIDs_per_tag[tag] = []
        for info in DBTags:
            mutant, group, pdb_name = info[0]
            conformation, stage_name, frame_no = group.split(':')
            db_tag = json.dumps([mutant, conformation])
            if (db_tag == tag) and (int(frame_no) in FrameRange):
                try:
                    db_id = session.query(Tags.id).filter_by(mutant=mutant,group=group,pdb_name=pdb_name).first()[0]
                    ModelsIDs_per_tag[tag].append(db_id)
                except:
                    print("No ID available for model: ", mutant, group, pdb_name)

    # Find IDs with no interaction data
    IDs_to_remove = []
    for i in range(len(urmd.tags)):
        for id in list(ModelsIDs_per_tag[urmd.tags[i]]):
            for inter_type in inter_tags.keys():
                try:
                    data = session.query(inter_tags[inter_type]).filter_by(id=id).first()[0]
                except:
                    IDs_to_remove.append([urmd.tags[i], id])
    # Remove IDs with no interaction data
    for x in IDs_to_remove:
        tag, id = x
        try:
            ModelsIDs_per_tag[tag].remove(id)
        except:
            pass
    return ModelsIDs_per_tag

def extractor_urmd(session, db_tag):
    ModelsIDs_per_tag = get_ModelsIDs_urmd(session)
    return ModelsIDs_per_tag[db_tag]    

urmd.id_extractor = extractor_urmd
##########################################################
def visualise_data0(df, Labels, stage, dc, inter_type):
    Inter_Labels = {
    'hbonds': 'HO-atoms',
    'kihs': 'KIH-atoms'
        }

    fig,ax = plt.subplots(2,2,figsize=(14,16))

    mutant_names = ['cWza','cWza-K375C','cWza-S355C','cWza-Y373C']

    axes = {
        'cWza':ax[0,0],
        'cWza-K375C':ax[0,1],
        'cWza-S355C':ax[1,0],
        'cWza-Y373C':ax[1,1]
    }

    DFColumns = {
        'cWza':[0+dc,1+dc],
        'cWza-K375C':[2+dc,3+dc],
        'cWza-S355C':[4+dc,5+dc],
        'cWza-Y373C':[6+dc]    
    }

    Colors = {
        'cWza':['blue','green'],
        'cWza-K375C':['blue','green'],
        'cWza-S355C':['blue','green'],
        'cWza-Y373C':['green']
    }

    Conformation = {
        'cWza':['Narrow', 'Wide'],
        'cWza-K375C':['Narrow', 'Wide'],
        'cWza-S355C':['Narrow', 'Wide'],
        'cWza-Y373C':['Single'],
    }


    for mutant in mutant_names:
        df.plot(kind='barh', y=DFColumns[mutant],color=Colors[mutant],ax=axes[mutant])
        axes[mutant].legend(Conformation[mutant],loc='best',fontsize=15)
        axes[mutant].set_xlim(0,1)
        axes[mutant].tick_params(axis='both',direction='in')
        axes[mutant].set_title(mutant+" : "+stage.name, fontsize=28)


    ax[1,0].set_xlabel("probability", fontsize=22)
    ax[1,1].set_xlabel("probability", fontsize=22)

    ax[0,0].set_ylabel("")
    ax[1,0].set_ylabel("")
    ax[0,1].set_ylabel(Inter_Labels[inter_type], fontsize=25)
    ax[1,1].set_ylabel(Inter_Labels[inter_type], fontsize=25)

    axes['cWza'].set_yticklabels(itemgetter(*list(df.index))(Labels), fontsize=15)
    axes['cWza-S355C'].set_yticklabels(itemgetter(*list(df.index))(Labels), fontsize=15)
    axes['cWza-K375C'].set_yticklabels("")
    axes['cWza-Y373C'].set_yticklabels("")

    fig.tight_layout()

    plt.show()
    filename = WD+inter_type+'_'+stage.name+'_'+urmd.name+'.png'
    plt.savefig(filename)
##########################################################
# PERFORM CALCULATION
STAGES = [docked, emmd, prmd, urmd]
##########################################################
Superbases = {}
Interaction_data = {}
Analyses = {}

for stage in STAGES:
    stage_session = start_session(stage.db_path)
    models = Models(stage_session)
    MyTags = stage.tags 
    Interaction_data[stage.name] = {}
    Superbases[stage.name] = {}
    Analyses[stage.name] = {}
    for tags in MyTags:
        mutant, group = json.loads(tags)
        models.ids = stage.id_extractor(models.session, tags)
        analysis = Analyse_Interactions(models)
        Analyses[stage.name][tags] = analysis
        Interaction_data[stage.name][tags] = analysis.get_interaction_data(inter_type)
        sbase = analysis.get_superbase(inter_type)
        Superbases[stage.name][tags] = sbase

def NestedDictValues(d):
    for v in d.values():
        if isinstance(v, dict):
            yield from NestedDictValues(v)
        else:
            yield v

unified_sbase = set()
for sb in list(NestedDictValues(Superbases)):
    unified_sbase = unified_sbase.union(set(sb))
    
sbase = list(unified_sbase)
sbase0 = sort_superbase(list(sbase), N_residues=32)


with open(WD+"superbase_"+inter_type+"_docked2urmd.json",'w') as fp:
	json.dump(fp,sbase0,indent=4)

###########################################################
# Probabilities are determined relative to the superbase
Probs = {}
for stage in STAGES:
    MyTags = stage.tags
    Probs[stage.name] = {}
    for tags in MyTags:
        analysis = Analyses[stage.name][tags]
        atoms = Interaction_data[stage.name][tags]
        stats = analysis.get_interaction_stats(sbase0, atoms)
        prob = analysis.get_interaction_probability(sbase0, stats)
        Probs[stage.name][tags] = prob

tools = geometry_interactions.Tools()
Labels = tools.labels_df(sbase0,inter_type)
###########################################################
# FRAME AND FILTER PROBABILITY DATA
SortedData = []
for stage in STAGES:
    MyTags = stage.tags
    for tag in MyTags:
        SortedData.append(Probs[stage.name][tag])
SortedData = numpy.array(SortedData).T

import pandas as pd
df = pd.DataFrame( SortedData )
tolerance = 0.05
df = df[df > tolerance]
df = df[df.notnull().any(axis=1)]
# Save DataFrame
df.to_json(WD+'df_'+inter_type+'_docked_to_'+urmd.name+'.json')
##########################################################
# PLOT ALL DATA AND SAVE FIGURES
dc = 0
for stage in STAGES:
    visualise_data0(df, Labels, stage, dc, inter_type)
    dc = dc + 7
