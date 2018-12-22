import sys
import string
from pymol import cmd

pdb_in = sys.argv[1]   # input pdb
pdb_out = sys.argv[2]  # output pdb 

# Number of chains 
nchains = 8
# Load input pdb
cmd.load(pdb_in, "MyProtein")
# Number of atoms per chain
N = float(cmd.count_atoms("MyProtein"))/float(nchains)
# List of chain labels
chains = list(string.ascii_uppercase[:nchains])

for i in range(nchains):
        # Select all atoms in chain range and relabel
        chn_sele = 'id '+str(1+i*N)+'-'+str((i+1)*N)
        cmd.select("sele", chn_sele)
        cmd.alter("sele", "chain="+"'"+chains[i]+"'")

####### test lines
cmd.select("myres","res 32 and name O1")
cmd.alter("myres",'name="O"')
######

# Retain order of atoms in PDB and save
cmd.set("retain_order",1)
cmd.save(pdb_out, "MyProtein")
#cmd.save(pdb_out[:-4]+"_bb.pdb", "bb.")
