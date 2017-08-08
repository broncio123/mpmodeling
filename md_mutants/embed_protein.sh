#!/bin/sh

module load apps/gromacs-5.0.6

# Run embedding
gmx_mpi grompp -f mdpf/embed.mdp -c  for_embedding.gro -p for_embedding.top -o for_embedding.tpr -n for_embedding.ndx

printf "1\n24\n"| mdrun_mpi -s for_embedding.tpr -membed mdpf/membed.dat -mn for_embedding.ndx -mp for_embedding.top
# Remove extra generated files
rm step*



