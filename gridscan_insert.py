#!/usr/bin/env python
import concurrent.futures
import sys,itertools, subprocess, isambard_dev
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from gridscan_setup import Pdb,Crick_Parameters,BUDE_Energies,Interhelix_Interactions,HOLE_Output,SASA_Estimates,Base
import analyse_protein_properties

# SQLAlchemy stuff
dbfile = sys.argv[1] # Database filename
ncores = int(sys.argv[2])
protein_set = sys.argv[3]
if protein_set == 'whole':
	crystal_structure_pdb = sys.argv[4]

engine = create_engine('sqlite:///'+dbfile)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

npeptides = 8
sequence = 'VPTITGVHDLTETVRYIKT'
nresidues = len(sequence)

mean_radius = 15.3063556447
mean_pitch  = 155.121966666
mean_phica  = -65.0829383279

radius_length = 6 
pitch_length = 200
phica_length = 5 

radius_step = 0.5 #6#0.5
pitch_step = 10  #100#10 
phica_step = 0.5 #4#0.5

radius_axis = np.arange(mean_radius - radius_length, mean_radius + radius_length, radius_step)
pitch_axis = np.arange(100,200,1)
phica_axis = np.arange(mean_phica - phica_length, mean_phica + phica_length, phica_step)
param_triple = list(itertools.product(radius_axis,pitch_axis,phica_axis))

Nrad = range(len(radius_axis))
Npitch = range(len(pitch_axis))
Nphica = range(len(phica_axis))
ident_triple = list(itertools.product(Nrad,Npitch,Nphica))

def process_model(n):
	# MODEL GENERATION
	## 1.1 Set identity tag of model in grid and save in database
	nrad,npitch,nphica = ident_triple[n]
	model_tag = str(nrad)+'-'+str(npitch)+'-'+str(nphica)
	model = Pdb(pdb_code = model_tag)
	session.add(model)
		
	## 1.2 Set Crick parameters of model in grid
	model_radius,model_pitch,model_phica = param_triple[n]
	model_parameters = Crick_Parameters(npeptides=8,radius=model_radius,pitch_length=model_pitch,iangle_phica=model_phica,pdb=model)
	session.add(model_parameters)
		
	## 1.4 Build model with helical packing parameters
	model_ampal = isambard_dev.ampal.specifications.CoiledCoil.from_parameters(npeptides,nresidues,model_radius,model_pitch,model_phica)
	model_ampal.build()
	model_ampal.pack_new_sequences((sequence)*npeptides)
		
	# 1.5 Save model coordinates in PDB
	model_pdb = 'mymodels/'+'model'+'_'+model_tag+'.pdb'
	with open(model_pdb, 'w') as x:
		x.write(model_ampal.pdb)
	
	if protein_set == 'whole':
		whole_model_pdb = 'mymodels/'+'whole_model'+'_'+model_tag+'.pdb'
		model_ampal = analyse_protein_properties.pymol_align_protein2model(crystal_structure_pdb,model_pdb,whole_model_pdb)	
		old_model_pdb = model_pdb
		model_pdb = whole_model_pdb	
	
	# ANALYSE MODEL IN GRID
	## 2.1 All BUDE energetic components for helix-helix interactions [kcal/mol]
	charge_buff,steric_buff,desolv_buff = analyse_protein_properties.buff_energies(model_ampal)
	model_energies = BUDE_Energies(buff_electrostatic_energy=charge_buff,buff_steric_energy=steric_buff,buff_desolvation_energy=desolv_buff,pdb=model)
	session.add(model_energies)
		
	## 2.2 Number Salt bridges, Hydrogen bonds, and Knobs-Into-Holes interactions between helices
	model_nsbridges = analyse_protein_properties.salt_bridges(model_ampal)
	model_nhbonds = analyse_protein_properties.hydrogen_bonds(model_ampal)
	model_nkihs =  analyse_protein_properties.knobs_into_holes(model_ampal)
	model_interhelix_interactions = Interhelix_Interactions(nsbridges=model_nsbridges,nhbonds=model_nhbonds,nkihs=model_nkihs,pdb=model)
	session.add(model_interhelix_interactions) 
	
	## 2.3 Solvent Accessible Surface Area (SASA) estimates per residue-type group [Angstrom^2]
	sasa_hydrophobes,sasa_nonhydrophobes,sasa_ncharged,sasa_pcharged = analyse_protein_properties.sasas(model_pdb)
	model_sasas = SASA_Estimates(sasa_hydrophobes=sasa_hydrophobes,sasa_nonhydrophobes=sasa_nonhydrophobes,sasa_ncharged=sasa_ncharged,sasa_pcharged=sasa_pcharged,pdb=model)	
	session.add(model_sasas)
	
	## 2.4 HOLE dimensions [Angstroms] and conductance estimates [nS]
	HOLE_dimensions,HOLE_conductance_estimates = analyse_protein_properties.hole(model_pdb) 
	VDW_Rmin,pore_length = HOLE_dimensions
	Gmacro,Gpred_Rmin,Gpred_Length,Gpred_AvgEPot = HOLE_conductance_estimates
	model_HOLE = HOLE_Output(HOLE_Rmin=VDW_Rmin,HOLE_Length=pore_length,Gmacro=Gmacro,Gpred_Rmin=Gpred_Rmin,Gpred_Length=Gpred_Length,Gpred_AvgEPot=Gpred_AvgEPot,pdb=model)	
	session.add(model_HOLE)

	session.commit()
	# Remove output files, all relevant data saved in database
	subprocess.call(['rm',old_model_pdb])
	subprocess.call(['rm',model_pdb])
	subprocess.call(['rm',model_pdb[:-4]+'.hole_inp'])
	subprocess.call(['rm',model_pdb[:-4]+'.hole_dat'])

model_n = list(range(len(ident_triple)))
def main():
	with concurrent.futures.ProcessPoolExecutor(max_workers=ncores) as executor:
		executor.map(process_model, model_n)

if __name__ == '__main__':
    main()

