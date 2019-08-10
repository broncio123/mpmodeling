pdb=$1
pymol -qc ~/mpmodeling/tools/add_WAN_C-ter.py -- $pdb ${pdb%.pdb}_WAN.pdb
wait
pymol -qc ~/mpmodeling/tools/mutate_pdb.py -- ${pdb%.pdb}_WAN.pdb 'ALA`34' 'PRO' ${pdb%.pdb}_WPN.pdb 
wait
rm ${pdb%.pdb}_WAN.pdb
