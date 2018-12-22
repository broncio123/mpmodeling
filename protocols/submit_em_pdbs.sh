max_cpus=10
DIR=$(dirname $(readlink -f $0))
COUNTER=0
for group in narrow wide; do
	mylist=${group}_pdbs.txt
	for pdb in `cat $mylist`; do 
		out_path=${group}/output/${pdb%.pdb}/complex
		# Check if system successfully resolvated
		if [ -f ${out_path}/ionise.gro ]; then
			# Create em directory if not existent
			if [ ! -d ${out_path}/em ]; then
	 			mkdir ${out_path}/em	
			fi
			# Generate .tpr file for EM
			cp ~/mpmodeling/protocols/gmx_protocols/templates/em_20000stps.slurm.bg $out_path/jobf/em_20000stps.slurm
			gmx_mpi grompp -f $out_path/mdpf/em_20000stps.mdp -p $out_path/topol.top -c $out_path/ionise.gro -o ${out_path}/em/em_20000stps.tpr &
			# Store Process IDs
			pids[${COUNTER}]=$!
			COUNTER=$[COUNTER + 1]
		fi
		if ! (( $COUNTER % $max_cpus )) ; then
			for pid in ${pids[*]}; do
				wait ${pid} 
			done
			rm \#mdout.mdp.*
		fi
	done
done
