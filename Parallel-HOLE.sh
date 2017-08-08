#!/bin/bash

# NOTE: 28 Nov 2016
# Possible improvements for future versions:
#1. Personalise number of trials
#2. Personalise running option, either serial or parallel
#3. Work out job distribution depending on number of cores available, and jobs requested.
#4. Personalise option of running if folder with PDB frames exists
#5. Personalise whether frames, input files, frames, and HOLE output files not deleted
#6. Change name of output
#7. Enable module loading if script working on Desktop computer or Cluster (gmx_mpi)


create_inp () {
# This function creates ai simple HOLE input file
local fname=$1
local m=$2
number=$RANDOM
echo "!HOLE input file
coord ${fname}.pdb
radius ../hole2/rad/simple.rad
ignore hoh
capsule
raseed $number
endrad 15." > ${fname}_${m}trial.inp
}

avg_std () {
	local X="$@" # Data array
	local a=$(for x in $X ; do echo $x; done | awk '{sum1+=$1} {sum2+=$1^2} END{printf "%.3f\t%.3f\n", sum1/NR, (sum2/NR - sum1^2/NR^2)^0.5}')
	echo $a
}

G_stats () {
	#This function determines the average and std dev. of conductance values and dimensions
	#over all HOLE trials for a particular frame 
	local frame=$1 # PDB file name

	# Extract data
	# Point time [ps]
	local t=$(grep t= $frame | awk '{print $NF}')
	# Channel length [Angstroms]
	local Length=$(grep '"Atomic" length of channel:' ${frame%.pdb}_1trial.txt | awk '{print $5}')
	# Channel Minimum Raiuds [Angstroms] 
	local Rmin=$(grep TAG ${frame%.pdb}_*trial.txt | awk '{print $5}')
	# Non-corrected Integrated Conductance (Bulk) [pS]
	local Gmacro=$(grep TAG ${frame%.pdb}_*trial.txt | awk '{print $7}')
	# Corrected Integrated Conductance by Rmin (8 system)  [pS]
	local Gpred_Rmin=$(grep TAG ${frame%.pdb}_*trial.txt | awk '{print $10 }')
	# Corrected Integrated Conductance by Lenght  [pS] 
	local Gpred_Lenght=$(grep TAG ${frame%.pdb}_*trial.txt | awk '{print $11 }')
	# Corrected Integrated Conductance by Average Electric Potential  [pS]
	local Gpred_AvEPot=$(grep TAG ${frame%.pdb}_*trial.txt | awk '{print $12}')

	# Compute average and standard deviation values
	local x2=$(avg_std $Rmin)
	local x3=$(avg_std $Gmacro)
	local x4=$(avg_std $Gpred_Rmin)
	local x5=$(avg_std $Gpred_Lenght)
	local x6=$(avg_std $Gpred_AvEPot)
	printf "%.0f \t %.3f \t %.3f \t %s \t %s \t %s \t %s \t %s\n" $t $Length 0 "$x2" "$x3" "$x4" "$x5" "$x6"
} 

fname=$1 # Generic file name (without extension)
dt=$2    # Time-space between frames [ps]
mkdir ${fname}_frames
# Split trajectory into seprate frame fles(PDB format)
# Select only Protein coordinates 
echo "Protein" | gmx trjconv -f ${fname}.xtc -s ${fname}.tpr -dt $dt -sep -o ${fname}_frames/frame.pdb 

cd ${fname}_frames
N=$(ls -l *pdb | wc -l) # Total number of frames
N=$(expr $N - 1)

#Print out headers to output file
printf "#Column1: Time [ps]\n" >> ../${fname}_HOLE-Summary.dat

printf "#Column2: Average Length [Å]\n" >> ../${fname}_HOLE-Summary.dat
printf "#Column3: Std Dev Length [Å]\n" >> ../${fname}_HOLE-Summary.dat

printf "#Column4: Average Minimum Radius [Å]\n" >> ../${fname}_HOLE-Summary.dat
printf "#Column5: Std Dev Minimum Radius [Å]\n" >> ../${fname}_HOLE-Summary.dat

printf "#Column6: Average Gmacro [pS]\n" >> ../${fname}_HOLE-Summary.dat
printf "#Column7: Std Dev Gmacro [pS]\n" >> ../${fname}_HOLE-Summary.dat

printf "#Column8: Average Gpred_Rmin [pS]\n" >> ../${fname}_HOLE-Summary.dat
printf "#Column9: Std Dev Gpred_Rmin [pS]\n" >> ../${fname}_HOLE-Summary.dat

printf "#Column10: Average Gpred_Length [pS]\n" >> ../${fname}_HOLE-Summary.dat
printf "#Column11: Std Dev Gpred_Length [pS]\n" >> ../${fname}_HOLE-Summary.dat

printf "#Column12: Average Gpred_AvePot [pS]\n" >> ../${fname}_HOLE-Summary.dat
printf "#Column13: Std Dev Gpred_AvePot [pS]\n" >> ../${fname}_HOLE-Summary.dat

for n in `seq 0 $N`; do 
	for m in `seq 1 5`; do
		# Create a HOLE input file per frame file
	        create_inp frame${n} $m
  
		# Run HOLE for each frame file (5 independent trials)
		../hole2/exe/hole < frame${n}_${m}trial.inp > frame${n}_${m}trial.txt &	
	done
	wait
	G_stats frame${n}.pdb  >> ../${fname}_HOLE-Summary.dat
	rm frame${n}.pdb
	rm frame${n}_*trial*
	
done
cd ../
rm -r ${fname}_frames

