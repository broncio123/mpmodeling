
import sys
from pymol import cmd

inputf = sys.argv[1]

def pymol_sasa(inputf, visualise=False, test=False):
	# Load PDB input file
	cmd.load(inputf, "MyProtein")
	""" Set molecular surface area 
	# Note: This will determine the whole area of the residues
	# without considering overlapping between residue surfaces, as SASA does
	#cmd.set('dot_solvent', value="off")
	"""
	# Set solvent accessible surface area (SASA)
	cmd.set('dot_solvent', value="on")
	
	# Set dot density for area calculation
	# Higest density. Dot density ranges:1-4
	cmd.set('dot_density', value="4")
	
	# Select residues by type
	cmd.select("hydrophobes","resn ala+gly+val+ile+leu+phe+met+trp+pro")
	cmd.select("nonhydrophobes", "resn ser+thr+cys+tyr+asn+gln")
	cmd.select("pcharged", "resn lys+arg+his")
	cmd.select("ncharged", "resn glu+asp")

	if visualise == True:
	# Veirfy correct selection by visualisation
		cmd.color("grey", "hydrophobes")
		cmd.color("green", "nonhydrophobes")
		cmd.color("red", "ncharged")
		cmd.color("blue", "pcharged")
		mysel = "hydrophobes or nonhydrophobes or ncharged or pcharged"
		cmd.hide("lines", "all")
		cmd.show("dots", mysel)

	# Work out SASA for each aminoacid-type group
	sasa_all = cmd.get_area("all")	
	sasa_hydrophobes = cmd.get_area("hydrophobes")
	sasa_nonhydrophobes = cmd.get_area("nonhydrophobes")
	sasa_ncharged = cmd.get_area("ncharged")
	sasa_pcharged = cmd.get_area("pcharged")
	print(sasa_hydrophobes, sasa_nonhydrophobes, sasa_ncharged, sasa_pcharged)
	
	if test == True:
		# Test: Compare total surface area of protein to area of added selections
		# to determine the difference due to exclusion of ACE and NH2 caps
		sasa_mysel = sasa_hydrophobes +sasa_nonhydrophobes+sasa_ncharged+sasa_pcharged
		print(sasa_all, sasa_mysel)
		# Output [Angstroms^2]: Not too bad (!?)
		# 30928.1113281 30106.6063232

pymol_sasa(inputf, False, False)
