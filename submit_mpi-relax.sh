#!/bin/bash

make_slurmf () {
file=$1
printf -- "#!/bin/bash -login
#SBATCH -p cpu
#SBATCH --ntasks-per-node=16
#SBATCH -N 1
#SBATCH -t 1-12:30
#SBATCH -A S2.1
#SBATCH -o jobf2/%s.log
#SBATCH -e jobf2/error_%s.log

module add apps/rosetta/mpi/3.8

mpiexec \$ROSETTA38_MPI/rosetta_scripts.mpi.linuxgccrelease -database \$ROSETTA38_DB @jobf2/%s_relax_flags -mpi_tracer_to_file ./logs2/run\n" $file $file $file > jobf2/${file}.slurm
}

make_rflagf () {
file=$1
printf -- "-parser:protocol membrane_relax.xml
-in:file:s ./input/%s.pdb 
-ignore_unrecognized_res true
-mp:scoring:hbond 
-mp:setup:spanfiles ./input/cwza_NoWPN_ignorechain_0001_tweaked.span
-mp:thickness 20
-mp:visualize:thickness 20
-nstruct 1000
-relax:fast
-relax:jump_move true
-out:path:pdb ./output2
-out:file:scorefile %s.sc
-out:path:score ./output2
-packing:pack_missing_sidechains 0\n" $file $file  > jobf2/${file}_relax_flags
}

#pdblist_file=$1

for pdbname in `cat pdblist_test.txt` ; do
	name=$(basename ${pdbname%.pdb})  
	make_rflagf $name
	make_slurmf $name
	sbatch jobf2/${name}.slurm
done
