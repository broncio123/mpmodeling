max_cpus=20
DIR=$(dirname $(readlink -f $0))
COUNTER=0
for group in narrow wide; do
	mylist=${group}_remaining_pdbs.txt
	for pdb in `cat $mylist`; do 
		out_path=${group}/output/${pdb%.pdb}/complex
		bash ~/mpmodeling/protocols/gmx_protocols/resolvate2.sh ${out_path} > ${out_path}/resolvate.log &
		pids[${COUNTER}]=$!
		rm \#mdout.mdp.*		
		COUNTER=$[COUNTER + 1]
		if ! (( $COUNTER % $max_cpus )) ; then
			for pid in ${pids[*]}; do
				wait ${pid} 
			done
		fi
	done
done
