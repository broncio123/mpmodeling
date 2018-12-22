#!/usr/bin/env python

import sys
import isambard_dev
import numpy as np

def get_alldihedrals(protein):
	"""Get all dihedral angle sequences (Omega, Phi, and Psi; as well as Chi1, Chi2 when applicable) for all chains in protein (AMPAL object)"""
	sequence = protein.sequences[0]
	N = len(protein.sequences[0])
	N_chains = len(protein.sequences)
	omega_prc = []
	phi_prc = []
	psi_prc = []
	chi1_prc = []
	chi2_prc = []

	for atomn in range(N):
		res = sequence[atomn]
		Omega_allchains = []
		Phi_allchains = []
		Psi_allchains = []
		Chi1_allchains = []
		Chi2_allchains = []
		for chainn in range(N_chains):
			# Define reference atoms per chain
			ra1 = protein[chainn][atomn]
			try:
				ra2 = protein[chainn][atomn+1]
			except:
				ra2 = 'None'
			try:
				ra3 = protein[chainn][atomn+2]
			except:
				ra3 = 'None'
			# Work out all dihedral angles per chain
			if ra2 == 'None':
				omega = 'None'
				phi = 'None'
			else:
				omega = isambard_dev.geometry.dihedral(ra1['CA'], ra1['C'], ra2['N'], ra2['CA'])
				phi = isambard_dev.geometry.dihedral(ra1['C'], ra2['N'], ra2['CA'], ra2['C'])
				if "CG" not in list(ra2.atoms.keys()):
					chi1 = 'None'
				else:
					chi1 = isambard_dev.geometry.dihedral(ra2['N'], ra2['CA'], ra2['CB'], ra2['CG'])
					if "CD1" not in list(ra2.atoms.keys()):
						chi2 = 'None'
					else:
						chi2 = isambard_dev.geometry.dihedral(ra2['CA'], ra2['CB'], ra2['CG'], ra2['CD1'])
			if (ra2 == 'None') or (ra3 == 'None'):
				psi = 'None'
			else:
				psi = isambard_dev.geometry.dihedral(ra2['N'], ra2['CA'], ra2['C'], ra3['N'])
			#print(omega, phi, psi, chi1, chi2) # enable this line for testing
			Omega_allchains.append(omega)
			Phi_allchains.append(phi)
			Psi_allchains.append(psi)
			Chi1_allchains.append(chi1)
			Chi2_allchains.append(chi2)

		#print(Omega_allchains, Phi_allchains, Psi_allchains, Chi1_allchains, Chi2_allchains)
		if 'None' in Omega_allchains:
			omega_prc.append([res+str(atomn+1), 'None', 'None'])
		else:
			omega_prc.append([res+str(atomn+1), np.mean(Omega_allchains), np.std(Omega_allchains)])
		if 'None' in Phi_allchains:
			phi_prc.append([res+str(atomn+1), 'None', 'None'])
		else:
			phi_prc.append([res+str(atomn+1), np.mean(Phi_allchains), np.std(Phi_allchains)])
		if 'None' in Psi_allchains:
			psi_prc.append([res+str(atomn+1), 'None', 'None'])
		else:
			psi_prc.append([res+str(atomn+1), np.mean(Psi_allchains), np.std(Psi_allchains)])
		if 'None' in Chi1_allchains:
			chi1_prc.append([res+str(atomn+1), 'None', 'None'])
		else:
			chi1_prc.append([res+str(atomn+1), np.mean(Chi1_allchains), np.std(Chi1_allchains)])
		if 'None' in Chi2_allchains:
			chi2_prc.append([res+str(atomn+1), 'None', 'None'])
		else:
			chi2_prc.append([res+str(atomn+1), np.mean(Chi2_allchains), np.std(Chi2_allchains)])
	#def turn2csv(var):
        #	return ",".join(map(str,var))

	#return turn2csv(omega_prc), turn2csv(phi_prc), turn2csv(psi_prc), turn2csv(chi1_prc), turn2csv(chi2_prc)
	return omega_prc, phi_prc, psi_prc, chi1_prc, chi2_prc


if __name__ == '__main__':
	pdb = sys.argv[1]
	protein = isambard_dev.ampal.convert_pdb_to_ampal(pdb)
	omega_prc, phi_prc, psi_prc, chi1_prc, chi2_prc = get_alldihedrals(protein)
	print("Omega", omega_prc)
	print("Phi", phi_prc)
	print("Psi", psi_prc)
	print("Chi1", chi1_prc)
	print("Chi2", chi2_prc)

