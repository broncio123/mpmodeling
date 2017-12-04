
import sys
from pymol import cmd

finput = sys.argv[1] # PDB 

cmd.load('protein_0ps_md_0mV_5000ps_NVT_After_prmd.pdb', 'MyProtein')
cmd.select('caps','resn ace+nh2')
cmd.alter('caps', "type='HETATM'")
foutput = 'altered_'+finput
cmd.save(foutput, 'MyProtein')


