import sys
from pymol import cmd

protein = sys.argv[1] # PDB file 
outfile = sys.argv[2] # Outfile

cmd.load(protein, 'Protein')
chains = cmd.get_chains('Protein')
N_res = len(cmd.get_fastastr("chain A").split('\n')[1])

for n in range(len(chains)):
	cmd.select('AA', '/Protein//'+chains[n]+'/1/N')
	cmd.edit('AA')
	cmd.editor.attach_amino_acid("pk1",'ace')
	cmd.unpick()
	cmd.select('AA', '/Protein//'+chains[n]+'/'+str(N_res)+'/C')
	cmd.edit('AA')
	cmd.editor.attach_amino_acid("pk1", 'nhh')
	cmd.unpick()

# Rename NHH to NH2 (GROMACS format)  
cmd.select("NH2s", "resn NHH")
cmd.alter("NH2s", "resn='NH2'")
cmd.delete("NH2s")

cmd.save(outfile, 'Protein')

