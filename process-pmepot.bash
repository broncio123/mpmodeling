#!/bin/bash

fname=$1 # Generic file name
group=$2 # Atomic group
t_initial=$3
t_final=$4

Lz=$(tail -1 ${fname}.gro | awk '{print $3}' ) # Box lenght: Z-axis [nm] 

# Generate Index file for atoms in group
if [ $group == "system" ]; then
	printf "keep 0 \n q\n" | gmx make_ndx -f ${fname}.gro -o ${group}.ndx	
elif [ $group == "protein" ]; then
        printf "keep 1 \n q\n" | gmx make_ndx -f ${fname}.gro -o ${group}.ndx
elif [ $group == "popc" ]; then 
	printf "keep 13 \n q\n" | gmx make_ndx -f ${fname}.gro -o ${group}.ndx
elif [ $group == "K" ]; then
	printf "keep 14 \n q\n" | gmx make_ndx -f ${fname}.gro -o ${group}.ndx
elif [ $group == "CL" ]; then
	printf "keep 15 \n q\n" | gmx make_ndx -f ${fname}.gro -o ${group}.ndx
elif [ $group == "water" ]; then
	printf "keep 16 \n q\n" | gmx make_ndx -f ${fname}.gro -o ${group}.ndx
else
	echo "Choose a valid option: protein, popc, K, CL, water"
fi

# Generate PQR file for indicated group 
gmx editconf -f ${fname}.tpr -n ${group}.ndx -mead ${group}.pqr

# Extract trajectory for indicated interval
new_trj=${group}_${t_initial}-${t_final}ps_${fname} 
echo $new_trj
gmx trjconv -f ${fname}.xtc -b ${t_initial} -e ${t_final} -n ${group}.ndx -o ${new_trj}.xtc

# Generate PMEPot electrostatic map (DX file)
python pmepot_emap.py ${group}.pqr ${new_trj}.xtc

# Then, generate Electrostatic Profile for Z-axis
python extract-PME-Zcoord.py ${group}_PMEPot_${new_trj}_emap.dx 0 $Lz > ${group}_PMEPot_${new_trj}_eprofile.dat 

