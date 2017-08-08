#!/usr/bin/env python
import isambard_dev,sys,subprocess,re, os
from ast import literal_eval

def pymol_align_protein2model(mobile,target,out_pdb,ampal_out=True):
	pymol_command = ['pymol','-qc','align_protein2model.py','--',mobile,target,out_pdb]
	if ampal_out == True:
		subprocess.check_output(pymol_command)
		protein_output = isambard_dev.ampal.convert_pdb_to_ampal(out_pdb)
		return(protein_output)

def buff_energies(protein):
	# Determine BUFF energetics [Units?]
	## NOTE: BUFF score is insensitive to added hydrogens in structure
	charge_buff = protein.buff_interaction_energy.charge
	steric_buff = protein.buff_interaction_energy.steric
	desolv_buff = protein.buff_interaction_energy.desolvation
	return(charge_buff,steric_buff,desolv_buff)

def hydrogen_bonds(protein):
	# Find Hydrogen bonds and count them
	## Add hydrogens to protein, if missing
	protein_with_hydrogens = isambard_dev.external_programs.assembly_plus_protons(protein.pdb, path=False)
	hbonds = isambard_dev.interactions.find_hydrogen_bonds(protein_with_hydrogens)
	nhbonds = len(hbonds)
	return(nhbonds)

def salt_bridges(protein):
	# Find Salt brdiges
	## NOTE: Had to modify function 'salt_bridges' in code file
	##  ~/code/isambard_dev/isambard_dev/ampal/interactions.py
	## Added element 'HIS' : ['ND1', 'NE2'] in dictionary 'salt_bridge_pos'
	sbridges = isambard_dev.interactions.find_salt_bridges(protein)
	nsbridges = len(sbridges)
	return(nsbridges)

def knobs_into_holes(protein):
	# Find Knobs-Into-Holes in structure
	kihs = isambard_dev.add_ons.knobs_into_holes.find_kihs(protein)
	nkihs = len(kihs)
	return(nkihs)

def sasas(inputfile):
	# Compute Solvent-Accessible-Surface-Area (SASA), PyMOL
	pymol_command = ['pymol','-qc','workout_sasa_aagroup.py','--',inputfile]
	proc = subprocess.Popen(pymol_command, stdout = subprocess.PIPE)
	output = proc.stdout.read()
	output = literal_eval(output.decode("utf-8"))
	sasa_hydrophobes,sasa_nonhydrophobes,sasa_ncharged,sasa_pcharged = output
	return(sasa_hydrophobes,sasa_nonhydrophobes,sasa_ncharged,sasa_pcharged)

def hole(inputfile):
	# Compute HOLE conductance estimates and pore lumen dimensions/features
	# NOTE: Had to wrap HOLE code in bash code 'run_hole' to automatically generate HOLE input file
	fname = os.path.splitext(inputfile)[0]
	subprocess.check_output(["run_hole", inputfile])
	hole_lines = open(fname+'.hole_dat','r').readlines()		
	# Filter HOLE output file
	for l in hole_lines:
		if re.search(r'"Atomic" length of channel',l):
			pore_length = float(l.split()[4]) # [Angstroms]
		elif re.search(r'TAG',l):
			# All conductance estimates are in [nano-Siemens]
			x = l.split()
			VDW_Rmin = float(x[3]) # [Angstroms]
			Gmacro = 0.001*float(x[5])
			Gpred_Rmin = 0.001*float(x[8])
			Gpred_Lenght = 0.001*float(x[9])
			Gpred_AvgEPot = 0.001*float(x[10])
	HOLE_dimensions = (VDW_Rmin,pore_length)
	HOLE_conductance_estimates = (Gmacro,Gpred_Rmin,Gpred_Lenght,Gpred_AvgEPot)
	return(HOLE_dimensions,HOLE_conductance_estimates)	

if __name__ == "__main__":
	inputfile = sys.argv[1] # Input PDB file
	# Load protein PDB and convert into AMPAL 
	protein = isambard_dev.ampal.convert_pdb_to_ampal(inputfile)
	# Determine all analysed properties	
	charge_buff,steric_buff,desolv_buff = buff_energies(protein)
	print('BUFF charged [~kJ/mol]: ', charge_buff)
	print('BUFF steric [~kJ/mol]: ', steric_buff)
	print('BUFF desolv [~kJ/mol]: ', desolv_buff)
	nhbonds = hydrogen_bonds(protein)
	print('No. H-bonds: ', nhbonds)
	nkihs =  knobs_into_holes(protein)
	print('No. KIHs: ', nkihs)
	sasa_hydrophobes,sasa_nonhydrophobes,sasa_ncharged,sasa_pcharged = sasas(inputfile)
	print('SASA hydrophobes [Angstrom^2]: ', sasa_hydrophobes)
	print('SASA nonhydrophobes [Angstrom^2]: ', sasa_nonhydrophobes)
	print('SASA positively charged res [Angstrom^2]: ', sasa_pcharged)
	print('SASA negatively charged res [Angstrom^2]: ', sasa_ncharged)
	HOLE_dimensions,HOLE_conductance_estimates = hole(inputfile)
	VDW_Rmin,pore_length = HOLE_dimensions
	print('HOLE VDW_Rmin [Angstroms]: ', VDW_Rmin)
	print('HOLE Pore_Length [Angstroms]: ', pore_length)
	Gmacro,Gpred_Rmin,Gpred_Length,Gpred_AvgEPot = HOLE_conductance_estimates
	print('HOLE Gpred by Rmin [nS]: ', Gpred_Rmin)
	print('HOLE Gpred by Length [nS]: ', Gpred_Length)
	print('HOLE Gpred by Avg EPot [nS]: ', Gpred_AvgEPot)
