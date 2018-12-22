#!/usr/bin/python

import sys
import os
import numpy
import operator
import subprocess
import json
import concurrent.futures
import isambard_dev
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import modules from folder
modules_path = "/home/ba13026/mpmodeling/analysis/"
if modules_path not in sys.path:
    sys.path.append(modules_path)

from setup_db_geometry import Json, Tags, RigidBody, RadialProfiles, Miscellaneous, Base
from split_vdw_profile import split_vdw_profile
from channel_bottleneck import find_vdw_minima
import rigid_body
import radial_profile


def get_rigid_body_data(ampal):
    try:
        com_bb = [unit.backbone.centre_of_mass for unit in ampal]
        com_aa = [unit.centre_of_mass for unit in ampal]
        #####################################
        ampal_rb = rigid_body.RigidBody(ampal)
        com_primitives = ampal_rb.get_chains_com()
        com_assembly = ampal_rb.get_assembly_com()
        #####################################
        euler_angles = ampal_rb.euler_angles() # Based on chain primitives
        #####################################
        # Convert to list format for JSON serialisation
        com_bb = list(map(list, com_bb))
        com_aa = list(map(list, com_aa))
        com_primitives = list(map(list, com_primitives))
        com_assembly = list(com_assembly)
        euler_angles = list(map(list, euler_angles))
        #####################################
        return com_bb, com_aa, com_primitives, com_assembly, euler_angles
    except:
        return 'Fail'

def get_radial_profiles(ampal):
    try:
        ampal_rp_bb = radial_profile.RadialProfile(ampal.backbone)
        ampal_rp_aa = radial_profile.RadialProfile(ampal)
        ####################################
        primitive = ampal_rp_aa.primitive()
        ####################################
        punctual_bb = ampal_rp_bb.punctual()
        punctual_aa = ampal_rp_aa.punctual()
        #####################################
        vdw_bb = ampal_rp_bb.vdw('simple')
        vdw_aa = ampal_rp_aa.vdw('simple')
        #####################################
        # Turn into lists to make JSON seriable
        primitive = list(map(list, primitive))
        punctual_bb = list(map(list, punctual_bb))
        punctual_aa = list(map(list, punctual_aa))
        vdw_bb = list(map(list, vdw_bb))
        vdw_aa = list(map(list, vdw_aa))
        ####################################
        # Split VdW profiles and make JSON seriable
        vdw_bb_lower, vdw_bb_upper = split_vdw_profile(primitive, vdw_bb)
        vdw_aa_lower, vdw_aa_upper = split_vdw_profile(primitive, vdw_aa)
        # Make JSON seriable
        vdw_bb_lower = list(map(list, vdw_bb_lower))
        vdw_bb_upper = list(map(list, vdw_bb_upper))
        vdw_aa_lower = list(map(list, vdw_aa_lower))
        vdw_aa_upper = list(map(list, vdw_aa_upper))
        ####################################
        return primitive, punctual_bb, punctual_aa, vdw_bb_lower, vdw_bb_upper, vdw_aa_lower, vdw_aa_upper
    except:
        return 'Fail'    

def get_vdw_minima(ampal):
    try:
        ampal_rp_aa = radial_profile.RadialProfile(ampal)
        chain_profile = ampal_rp_aa.vdw('simple')
        residue_profiles_data = ampal_rp_aa.vdw_per_residue('simple')
        vdw_minima = find_vdw_minima(chain_profile, residue_profiles_data, Rmin_tol=1)
        return vdw_minima
    except:
        return 'Fail'
    
def process_model(n):
    """Insert description here"""
    #####################################
    # Model identifiers
    tags, pdb_path = PDBs_Info[n]
    mutant, group, pdb_name = tags
    model_tags  = Tags(mutant = mutant, group = group, pdb_name = pdb_name)
    session.add(model_tags)
    #####################################
    ampal = isambard_dev.ampal.convert_pdb_to_ampal(pdb_path)
    #####################################
    ##  Rigid body data
    dataRB = get_rigid_body_data(ampal)
    modelRB = RigidBody(
                        com_bb = dataRB[0],
                        com_aa = dataRB[1],
                        com_primitives = dataRB[2],
                        com_assembly = dataRB[3],
                        euler_angles = dataRB[4],
                        tag = model_tags
                        )
    session.add(modelRB)
    #####################################
    ## Radial profiles
    dataRP = get_radial_profiles(ampal)
    modelRP = RadialProfiles(
                            primitive = dataRP[0],
                            punctual_bb = dataRP[1],
                            punctual_aa = dataRP[2],
                            vdw_bb_lower = dataRP[3],
                            vdw_bb_upper = dataRP[4],    
                            vdw_aa_lower = dataRP[5],
                            vdw_aa_upper = dataRP[6],
                            tag = model_tags
                            )
    session.add(modelRP)
    #####################################
    # Minima from VdW chain profile and residue identity
    dataM = get_vdw_minima(ampal)
    modelM = Miscellaneous(vdw_minima = dataM)
    session.add(modelM)
    #####################################
    ## COMMIT CHANGES TO DATABASE  
    session.commit()
#####################################
# Parallel Process Execution
def main():
        model_n = list(range(len(PDBs_Info)))
        with concurrent.futures.ProcessPoolExecutor(max_workers = ncores) as executor:
                executor.map(process_model, model_n)

if __name__ == '__main__':
    dbfile  = sys.argv[1] # Database filename
    mutants_info = sys.argv[2] # Dictionary with mutant structures info
    ncores = int(sys.argv[3]) # Number of cores

    # Extract info from dictionary
    with open(mutants_info, 'r') as fp:
            PDBs_Info = json.load(fp)

    # Create engine and bind it to current session
    engine = create_engine('sqlite:///'+dbfile)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
 
    main()        