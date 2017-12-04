#!/usr/bin/env python
import concurrent.futures
import sys,itertools, subprocess, isambard_dev, time, os
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setup_db import Json, Pdb, SuperHelix_Parameters, Conformation, BUDE_Energies, RosettaMP_Energies, Interhelix_Interactions, HOLE_Output, SASA_Estimates, Base
import analyse_protein_properties
from extract_rosettad import extract_rosettad
from get_SHelixParams import get_SHparams
from get_alldihedrals import get_alldihedrals

dbfile	= sys.argv[1] # Database filename
pdblist	= sys.argv[2] # List of PDB files
scfile	= sys.argv[3] # Rosetta score file
pdbnamef = sys.argv[4]
ncores	= int(sys.argv[5]) # Number of cores to use

# Extract names of all pdb files in list
infile = open(pdblist, 'r')
lines = infile.readlines()
pdbfiles = [l.rstrip() for l in lines]

# pdbnamef = 'pdbnames.txt' # enable for test
infile2 = open(pdbnamef,'r')
pdbnames = [l.rstrip() for l in infile2.readlines()]


# Create engine and bind it to current session
engine = create_engine('sqlite:///'+dbfile)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Useful output messages
print("Test date: "+str(time.strftime("%d/%m/%Y"))+'; time:'+str(time.strftime("%H:%M:%S")))
print("%d models will be sampled"%len(pdbfiles))

def process_model(n):
	# MODEL ANALYSIS AND ADD DATA TO DATABASE
	# Load protein PDB in list and extract basic info
	protein = isambard_dev.ampal.convert_pdb_to_ampal(pdbfiles[n])	
	npeptides = len(protein.sequences)
	sequence = protein.sequences[0]

	model  = Pdb(sequence = sequence, npeptides = npeptides, pdb_name = pdbfiles[n])
	session.add(model)      

	# Super helix parameters, including interface angle per residue, per chain
	ca_radii, azimuthal_angles, axial_positions, interface_angles = get_SHparams(protein)	

	model_shparams = SuperHelix_Parameters(ca_radii = ca_radii, azimuthal_angles = azimuthal_angles, axial_positions = axial_positions, interface_angles = interface_angles, pdb = model)
	session.add(model_shparams)

	# Dihedral angles per residue, per chain
	omega_prc, phi_prc, psi_prc, chi1_prc, chi2_prc = get_alldihedrals(protein)

	model_dihedrals = Conformation(omega_angles = omega_prc, phi_angles = phi_prc, psi_angles = psi_prc, chi1_angles = chi1_prc, chi2_angles = chi2_prc, pdb = model)
	session.add(model_dihedrals)
	
	# BUDE energetic components for helix-helix interactions [BEU ~ kcal/mol] 
	electrostatic, steric, desolvation = analyse_protein_properties.buff_energies(protein)
	
	bude_energies = BUDE_Energies(electrostatic = electrostatic, steric = steric, desolvation = desolvation, pdb = model)
	session.add(bude_energies)

	# RosettaMP energetic components for helix-helix interactions [REU ~ kcal/mol]
	total_score, rmsd, I_sc = extract_rosettad(scfile, pdbnames[n])
	
	rosetta_energies = RosettaMP_Energies(total_score = total_score, I_sc = I_sc, rmsd = rmsd, pdb = model)
	session.add(rosetta_energies)

	## Number Salt bridges, Hydrogen bonds, and Knobs-Into-Holes interactions between helices 
	nsbridges = analyse_protein_properties.salt_bridges(protein)
	nhbonds = analyse_protein_properties.hydrogen_bonds(protein)
	nkihs =  analyse_protein_properties.knobs_into_holes(protein)

	interhelix_interactions = Interhelix_Interactions(nsbridges = nsbridges, nhbonds = nhbonds, nkihs = nkihs, pdb = model)
	session.add(interhelix_interactions)
	
	## Solvent Accessible Surface Area (SASA) estimates per residue-type group [Angstrom^2] 
	sasa_hydrophobes,sasa_nonhydrophobes,sasa_ncharged,sasa_pcharged = analyse_protein_properties.sasas(pdbfiles[n])

	sasas = SASA_Estimates(sasa_hydrophobes = sasa_hydrophobes, sasa_nonhydrophobes = sasa_nonhydrophobes, sasa_ncharged = sasa_ncharged, sasa_pcharged = sasa_pcharged, pdb = model)
	session.add(sasas)
	
	## HOLE dimensions [Angstroms] and conductance estimates [nS]
	HOLE_dimensions,HOLE_conductance_estimates = analyse_protein_properties.hole(pdbfiles[n]) 
	VDW_Rmin,pore_length = HOLE_dimensions
	Gmacro,Gpred_Rmin,Gpred_Length,Gpred_AvgEPot = HOLE_conductance_estimates

	model_HOLE = HOLE_Output(HOLE_Rmin=VDW_Rmin,HOLE_Length=pore_length,Gmacro=Gmacro,Gpred_Rmin=Gpred_Rmin,Gpred_Length=Gpred_Length,Gpred_AvgEPot=Gpred_AvgEPot, pdb = model)	
	session.add(model_HOLE)

	# COMMIT CHANGES TO DATABASE  
	session.commit()

model_n = list(range(len(pdbfiles)))
def main():
	with concurrent.futures.ProcessPoolExecutor(max_workers=ncores) as executor:
		executor.map(process_model, model_n)

if __name__ == '__main__':
    main()

