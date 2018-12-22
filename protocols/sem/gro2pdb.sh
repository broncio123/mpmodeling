protein=$1 # Path to .gro file

# Make index file for protein/bb-protein alone
printf "q\n" | gmx_mpi make_ndx -f $protein -o ${protein%.gro}.ndx

# Convert system coordinate file to PDB, only for protein atoms in index file. Also, label chains as 'A' 
printf "Protein" | gmx_mpi editconf -f $protein -n ${protein%.gro}.ndx -o ${protein%.gro}.pdb  -label A

# Relabel chains
pymol -qc ~/mpmodeling/protocols/sem/label_chains4gro2.py -- ${protein%.gro}.pdb ${protein%.gro}_Protein.pdb
