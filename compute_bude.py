#!/usr/bin/env python 

import isambard_dev
import warnings, sys

infile = sys.argv[1] # PDB list file
pdblist_file = open(infile, "r")
pdblist = [name.rstrip() for name in pdblist_file.readlines()]

for n in range(len(pdblist)):
	protein = isambard_dev.ampal.convert_pdb_to_ampal(pdblist[n])
	with warnings.catch_warnings():
		warnings.simplefilter("ignore")
		buff_total = protein.buff_interaction_energy.total_energy
		buff_charge = protein.buff_interaction_energy.charge
		buff_steric = protein.buff_interaction_energy.steric
		buff_desolv = protein.buff_interaction_energy.desolvation
	print("{0:s} {1:5.3f} {2:5.3f} {3:5.3f} {4:5.3f}".format(pdblist[n].split("/")[1],buff_total,buff_charge,buff_steric,buff_desolv))


