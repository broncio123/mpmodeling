#!/usr/bin/env python
from pymol import cmd
import sys

in_protein = sys.argv[1]
out_protein = sys.argv[2]
to_build = ['trp','ala','asn']
to_build = to_build + ['nhh']

cmd.load(in_protein, "MyProtein")

# Alter exceptional selections in PDB
cmd.select("MSEs", "resn MSE")
cmd.alter("MSEs", "type='ATOM' ")
cmd.alter("MSEs", "resn='MET' ")
cmd.delete("MSEs")

cmd.select("SEs", "name SE")
cmd.alter("SEs", "name='SG' ")
cmd.alter("SEs", "elem='S' ")
cmd.delete("SEs")

# Get original chain names
Chains = cmd.get_chains()

# Fix dihedral angles of residues near C-termini
for chn in Chains:
	# Fix Psi dihedral angle of LYS-375 to alpha-helix
        res0 = 375
        atom2 = "/MyProtein//"+chn+"/"+str(res0)+"/N"
        atom3 = "/MyProtein//"+chn+"/"+str(res0)+"/CA"
        atom4 = "/MyProtein//"+chn+"/"+str(res0)+"/C"
        atom5 = "/MyProtein//"+chn+"/"+str(res0+1)+"/N"

        cmd.set_dihedral(atom2,atom3,atom4,atom5, -45)

	# Set Phi dihedral angle of ARG-376 to alpha-helix
	res0 = 376
        atom1 = "/MyProtein//"+chn+"/"+str(res0-1)+"/C"
        atom2 = "/MyProtein//"+chn+"/"+str(res0)+"/N"
        atom3 = "/MyProtein//"+chn+"/"+str(res0)+"/CA"
        atom4 = "/MyProtein//"+chn+"/"+str(res0)+"/C"
	
	cmd.set_dihedral(atom1,atom2,atom3,atom4, -60)

	# Add missing residues to C-termini on ARG-376
	# NOTE: Amidate C-termini by default. For the last residue, we need a N to set Psi
	# So, this is why we cap peptides from the beginning

	cmd.select("MyAA", "/MyProtein//"+chn+"/ARG`376/C")
        cmd.edit("MyAA")

	for aa in to_build:
                cmd.editor.attach_amino_acid("pk1", aa)
        cmd.unpick()
	
	# Set dihedral angles fo new residues to alpha-helix
	for res0 in range(376,380):
        	atom1 = "/MyProtein//"+chn+"/"+str(res0-1)+"/C"
        	atom2 = "/MyProtein//"+chn+"/"+str(res0)+"/N"
        	atom3 = "/MyProtein//"+chn+"/"+str(res0)+"/CA"
        	atom4 = "/MyProtein//"+chn+"/"+str(res0)+"/C"
        	atom5 = "/MyProtein//"+chn+"/"+str(res0+1)+"/N"

		# Set (Phi,Psi) dihedral angles per residue, respectively 
        	cmd.set_dihedral(atom1,atom2,atom3,atom4, -60)
        	cmd.set_dihedral(atom2,atom3,atom4,atom5, -45)
		
	# Acetylate N-termini on ALA-345 
	cmd.select("MyAA", "/MyProtein//"+chn+"/ALA`345/N")
        cmd.edit("MyAA")
        cmd.editor.attach_amino_acid("pk1",'ace' )
        cmd.unpick()

# Rename NHH to NH2 (GROMACS format)  
cmd.select("NH2s", "resn NHH")
cmd.alter("NH2s", "resn='NH2'")
cmd.delete("NH2s")

# Remove steric clashes between sidechains

## Select only sidechain of ARG-376 to ASN-379 		
cmd.select("sidechains", "resi 376:379 and ! bb.")

## Protect rest of the protein from modifications by sculpting
cmd.protect('(not sidechains)')

## Carry out Sculpting for 7000 cycles
cmd.sculpt_activate('MyProtein')
cmd.sculpt_iterate('MyProtein', cycles=7000)
cmd.sculpt_deactivate('MyProtein')
cmd.deprotect()

# Save sculpted structure into output file
cmd.save(out_protein, "MyProtein")

