import sys

protein = sys.argv[1]
output_pdb = sys.argv[2]

cmd.load(protein,"MyProtein")
chn_sele = 'chain A+B'
cmd.create("ChainAB",chn_sele)
cmd.delete("MyProtein")
cmd.alter("chain B","resi=str(int(resi)-32)")
cmd.save(output_pdb,"ChainAB")


