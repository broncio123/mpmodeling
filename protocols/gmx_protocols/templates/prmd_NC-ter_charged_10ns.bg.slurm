#!/bin/bash -login 
#SBATCH -p cpu 
#SBATCH --ntasks-per-node=16 
#SBATCH -N 6 
#SBATCH -t 0-10:30 
#SBATCH -A S2.1 
#SBATCH -o complex/jobf/prmd_NC-ter_charged_10ns.log 
#SBATCH -e complex/jobf/prmd_NC-ter_charged_10ns.error 

# Load GROMACS module 
module load apps/gromacs-5.0.6 

mpiexec.hydra -psm -bootstrap slurm gmx_mpi mdrun -s complex/mdf/prmd_NC-ter_charged_10ns.tpr -deffnm complex/mdf/prmd_NC-ter_charged_10ns

