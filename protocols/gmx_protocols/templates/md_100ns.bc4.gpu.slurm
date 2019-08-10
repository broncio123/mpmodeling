#!/bin/bash -login
#SBATCH --nodes=1
#SBATCH --gres=gpu:2
#SBATCH --partition gpu
#SBATCH --mem=3GB
#SBATCH -o md_100ns_slurm.log
#SBATCH -e error_md_100ns_slurm.log
#SBATCH --time=2-12:00:00
#SBATCH --job-name=gmxGPU

# Load GROMACS module
module add apps/gromacs/2018-mpi-gpu-intel
module add CUDA
cd $SLURM_SUBMIT_DIR

srun gmx_mpi mdrun -s  md_100ns.tpr -deffnm md_100ns -nb gpu -tunepme 

