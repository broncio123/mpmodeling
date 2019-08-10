#!/usr/bin/env python 

from pymol import cmd
import sys

in_protein   = sys.argv[1] # PDB file of protein
to_mutate = sys.argv[2] # Residue to mutate in chain
mutate_to = sys.argv[3] # Mutant residue
out_protein = sys.argv[4] # PDB file output

# Load PDB of protein to mutate
cmd.load(in_protein, 'MyProtein')
# Extract list of chain names
Chains = cmd.get_chains('MyProtein')

# Call Mutagenesis function of Wizard
cmd.wizard("mutagenesis")
cmd.refresh_wizard()
# Set name of residue to mutate to
cmd.get_wizard().set_mode(mutate_to)
cmd.get_wizard().set_hyd("none")

for chain in Chains:
	# Select residue to mutate in chain
	cmd.select("to_mutate","/MyProtein//"+chain+"/"+to_mutate)
	# Allow Wizard to identify selected residue
	cmd.get_wizard().do_select('''to_mutate''')
	# Generate mutation 
	cmd.get_wizard().apply()
	# Restart selection for next mutation
	cmd.select("to_mutate", 'none')

# Close Wizard
cmd.set_wizard()
cmd.delete("to_mutate")
	
# res = int(to_mutate.split("`")[1])
# around_res = str(res-1)+":"+str(res+1)
# cmd.select("sidechains", "resi "+around_res+"and ! bb.")
# ## Protect rest of the protein from modifications by sculpting
# cmd.protect('(not sidechains)')

# ## Carry out Sculpting for 5000 cycles
# cmd.sculpt_activate('MyProtein')
# cmd.sculpt_iterate('MyProtein', cycles=5000)
# cmd.sculpt_deactivate('MyProtein')
# cmd.deprotect()

# Save mutated protein
cmd.save(out_protein, "MyProtein")

