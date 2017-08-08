#!/bin/bash

module add apps/gromacs-5.0.6
module add apps/python-2.7.10

# Resize simulation box, containing Protein and bilayer atmos only
	## Create index file of protein and lipid atomic indexes
printf "1|13\nq\n"| gmx_mpi make_ndx -f confout.gro -o protein+lipids.ndx
	## Extract box dimensions
read Lx Ly Lz <<<$(tail -1 confout.gro)
	## Redifine box dimension, Z-axis
Lz_new=16.000
	## Centre bilayer and protein in larger box
printf "24\n24\n"| gmx_mpi editconf -f confout.gro -n protein+lipids.ndx -o protein+lipids.gro -c -box $Lx $Ly $Lz_new

# Resolvate new box, SPC water model
gmx_mpi solvate -cp protein+lipids.gro -cs spc216.gro -o protein+lipids+water.gro
	## Remove water molecules within bilayer
python bilayer_drier.py protein+lipids+water.gro > summary_dry.txt
	## Extract new number fo waters after drying bilayer
N_water=$(tail -1 summary_dry.txt | awk -F":" '{print $2}')
	## New topology file, preserve correct number of lipids and protein chains
head -n -3 for_embedding.top > topol.top
printf "SOL\t%s\n" "$N_water" >> topol.top

# Ionise system at fixed concentration
gmx_mpi grompp -f mdpf/ionise.mdp -c protein+lipids+water_dry.gro -o ionise.tpr -p topol.top
	## Set KCl electrolyte, at 1 M concentration (neutral)
echo "15\n"| gmx_mpi genion -s ionise.tpr -p topol.top -o ionise.gro -conc 1.0 -pname K -nname CL -neutral

# Energy minimise whole configuration, prior to NPT equilibration
gmx_mpi  grompp -f mdpf/em_20000stps.mdp -c ionise.gro -p topol.top -o em/em_20000stps.tpr
	## EM: 20,000 steps to allow 'Steepest descent' to converge
mpirun -np 16 mdrun_mpi -s em/em_20000stps.tpr -deffnm em/em_20000stps
