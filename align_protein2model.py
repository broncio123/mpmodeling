#!/usr/bin/env python
from pymol import cmd

import sys

mobile	= sys.argv[1]
target	= sys.argv[2]
out_pdb = sys.argv[3]

#mobile = 'altered_cwza.pdb'
#target = 'final_opt_cwza_L.pdb'
#target = 'with_seq_final_opt_cwza_L.pdb'
#target = 'bb_cwza_opt.pdb'

cmd.load(mobile, 'MyProtein')
cmd.load(target, 'MyModelBB')

Chains = cmd.get_chains('MyProtein')
for chain in Chains:
	cmd.create('MyChain'+chain, '/MyProtein//'+chain)
	mobile_bb = 'MyChain'+chain
	target_bb = '/MyModelBB//'+chain
	cmd.align(mobile_bb, target_bb)
	
cmd.delete('MyProtein')
cmd.delete('MyModelBB')
cmd.orient()

cmd.create('MyModel', 'all')

cmd.select('sidechains', 'MyModel')
## Protect rest of the protein from modifications by sculpting
cmd.protect('(not sidechains)')

## Carry out Sculpting for 5000 cycles
cmd.sculpt_activate('MyModel')
cmd.sculpt_iterate('MyModel', cycles=500)
cmd.sculpt_deactivate('MyModel')
cmd.deprotect()

cmd.save(out_pdb, "MyModel")

