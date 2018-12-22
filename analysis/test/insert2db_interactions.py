import sys
import numpy
import operator
import subprocess
import json
import concurrent.futures
import isambard_dev
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setup_db_interactions import  Json, Tags, Interhelix_Interactions, Base

def interaction_direction(chain_combination):
    chainc_ccwise = ['AB','BC','CD','DE','EF','FG','GH','HA']
    chainc_cwise  = ['AH','HG','GF','FE','ED','DC','CB','BA']
    chainc_intrachn = ['AA','BB','CC','DD','EE','FF','GG','HH']
    if chain_combination in chainc_cwise:
        return 1
    elif chain_combination in chainc_ccwise:
        return -1
    elif chain_combination in chainc_intrachn:
        return 0

def get_OH_atoms(file):
	"""Get all OH-atoms per H-bond in PDB, in residue-number/OH-atom format plus chain direction"""
	try:
		p = isambard_dev.ampal.convert_pdb_to_ampal(file)
		hbonds = isambard_dev.interactions.find_hydrogen_bonds(p)
		# Find all H-bonds and select those between sidechain atoms
		sc_hbonds_raw = [hb for hb in hbonds if hb.is_sidechain_sidechain == True]
		sc_hbonds_reduced = []
		for hb in sc_hbonds_raw:
			donor_H = [hb.donor.ampal_parent.id , hb.donor.res_label]
			acceptor_O = [hb.acceptor.ampal_parent.id , hb.acceptor.res_label]
			direction_HO = hb.donor.unique_id[0]+hb.acceptor.unique_id[0]
			hb_reduced = donor_H+acceptor_O+[direction_HO]
			data = json.dumps(hb_reduced)
			sc_hbonds_reduced.append( data )
	except:
		sc_hbonds_reduced = 'NoFile'
	return sc_hbonds_reduced

def get_KIHs(file):
    """Get all KIHs in PDB, in residue number format plus chain direction"""
    try:
        p = isambard_dev.ampal.convert_pdb_to_ampal(file)
        kihs_raw = isambard_dev.add_ons.knobs_into_holes.find_kihs(p)
        kihs_reduced = []
        for kih in kihs_raw:
            knob_data = ''.join(kih.knob.unique_id).rstrip()
            hole_data = [''.join(kih.hole[x].unique_id).rstrip() for x in range(len(kih.hole))]
            kih_direction = knob_data[0]+hole_data[0][0]
            kih_reduced = [knob_data[1:]]+[s[1:] for s in hole_data]+[kih_direction]
            data = json.dumps(kih_reduced)
            kihs_reduced.append(data)
    except:
        kihs_reduced = 'NoFile'
    return kihs_reduced

def process_model(n):
	#####################################
	# Model identifiers
	tags, pdb_path = PDBs_Info[n]
	mutant, group, pdb_name = tags
	model_tags  = Tags(mutant = mutant, group = group, pdb_name = pdb_name)
	session.add(model_tags)
	#####################################
	##  Inter-helix interactions: H-bonds and KIHs
	hbonds = get_OH_atoms(pdb_path)
	kihs = get_KIHs(pdb_path)
	# 
	model_interactions = Interhelix_Interactions(
		hbonds=hbonds,
		kihs=kihs,
		tag=model_tags
	)
	session.add(model_interactions)

	# COMMIT CHANGES TO DATABASE  
	session.commit()

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
