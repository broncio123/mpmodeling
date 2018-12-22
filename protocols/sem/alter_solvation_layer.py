import sys
from pymol import cmd

solvated_output = sys.argv[1] # PDB file 
altered_pdb = sys.argv[2]

cmd.load(solvated_output, 'System')

cmd.select("sele", "resn tip3")
cmd.alter("sele", "resn='SOL'")
cmd.select("sele_Os", "name OH2 and resn SOL")
cmd.alter("sele_Os", "name='OW'")
cmd.select("sele_H1s", "name H1 and resn SOL")
cmd.alter("sele_H1s", "name='HW1'")
cmd.select("sele_H2s", "name H2 and resn SOL")
cmd.alter("sele_H2s", "name='HW2'")
cmd.set("retain_order",1)
cmd.save(altered_pdb, 'System')

