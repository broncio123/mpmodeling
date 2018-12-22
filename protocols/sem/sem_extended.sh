#!/bin/bash

path=$1
#path="."
n_cpus=30
sem_stages=(
	"PR-POPC_SC+BB_Protein_Cbonds" 
	"PR-SC+BB_Protein_Cbonds" 
	"PR-BB_Protein_Cbonds" 
	"No-PR_Cbonds" 
	"No-PR_Ubonds"
	)
#####################################################################################################
# Perform Smooth Energy Minimization
init_file="ionise.gro"
for stage in "${sem_stages[@]}"; do
    gmx_mpi grompp -f ${path}/mdpf/sem_${stage}.mdp -c ${path}/$init_file -p ${path}/topol.top -o ${path}/em/sem_${stage}.tpr
    mpirun -np $n_cpus mdrun_mpi -s ${path}/em/sem_${stage}.tpr -deffnm ${path}/em/sem_${stage} 
    wait
    echo "Potential" | gmx_mpi energy -f ${path}/em/sem_${stage}.edr -o ${path}/em/energy_sem_${stage}.xvg
    init_file=em/sem_${stage}.gro
done
wait
#####################################################################################################
# Perform Rough Energy Minimization (No-PR groups, Unconstrained bonds)
init_file="ionise.gro"
gmx_mpi grompp -f ${path}/mdpf/sem_No-PR_Ubonds.mdp -c ${path}/$init_file -p ${path}/topol.top -o ${path}/em/em_No-PR_Ubonds.tpr
mpirun -np $n_cpus mdrun_mpi -s ${path}/em/em_No-PR_Ubonds.tpr -deffnm ${path}/em/em_No-PR_Ubonds
wait
echo "Potential" | gmx_mpi energy -f ${path}/em/em_No-PR_Ubonds.edr -o ${path}/em/energy_em_No-PR_Ubonds.xvg
#####################################################################################################
# Perform Semi-rough Energy Minimization 
## First: No-PR groups, Constrained bonds
init_file="ionise.gro"
gmx_mpi grompp -f ${path}/mdpf/sem_No-PR_Cbonds.mdp -c ${path}/$init_file -p ${path}/topol.top -o ${path}/em/em_No-PR_Cbonds.tpr
mpirun -np $n_cpus mdrun_mpi -s ${path}/em/em_No-PR_Cbonds.tpr -deffnm ${path}/em/em_No-PR_Cbonds
wait
echo "Potential" | gmx_mpi energy -f ${path}/em/em_No-PR_Cbonds.edr -o ${path}/em/energy_em_No-PR_Cbonds.xvg

## Second: No-PR groups, Unconstrained bonds
init_file="em/em_No-PR_Cbonds.gro"
gmx_mpi grompp -f ${path}/mdpf/sem_No-PR_Ubonds.mdp -c ${path}/$init_file -p ${path}/topol.top -o ${path}/em/em_No-PR_Ubonds_After_Cbonds.tpr
mpirun -np $n_cpus mdrun_mpi -s ${path}/em/em_No-PR_Ubonds_After_Cbonds.tpr -deffnm ${path}/em/em_No-PR_Ubonds_After_Cbonds
wait
echo "Potential" | gmx_mpi energy -f ${path}/em/em_No-PR_Ubonds_After_Cbonds.edr -o ${path}/em/energy_em_No-PR_Ubonds_After_Cbonds.xvg
#####################################################################################################
