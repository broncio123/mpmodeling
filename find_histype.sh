#!/bin/sh

pdbfile=$1 # PDB name
# Extract identity of HIS atoms from docked PDB
HIS_atoms=$(grep "HIS B" $pdbfile | awk '{print $3}')

# @@ arbitrary character
var=$HIS_atoms python3 <<@@
import os
HIS_atoms = os.environ["var"].split()

# Make library of HIS protonation states (OPLS/AA f.f)
HISD_atoms="N H CA HA CB 1HB 2HB CG ND1 HD1 CD2 HD2 CE1 HE1 NE2 C O".split()
HISH_atoms="N H CA HA CB 1HB 2HB CG ND1 HD1 CD2 HD2 CE1 HE1 NE2 HE2 C O".split()
HISE_atoms="N H CA HA CB 1HB 2HB CG ND1 CD2 HD2 CE1 HE1 NE2 HE2 C O".split()
Option_HIS = {'HISD':0, 'HISE':1, 'HISH':2}

HIS_states = {'HISD':HISD_atoms, 'HISH':HISH_atoms, 'HISE':HISE_atoms}
# Print identified HIS protonation state
for HIS_type in HIS_states.keys():
	if set(HIS_atoms) == set(HIS_states[HIS_type]):
		#print("HIS is of type: ", HIS_type)
		print(Option_HIS[HIS_type])
@@

# GROMACS HIS-protonation options
#0. H on ND1 only (HISD)
#1. H on NE2 only (HISE)
#2. H on ND1 and NE2 (HISH)
#3. Coupled to Heme (HIS1)
