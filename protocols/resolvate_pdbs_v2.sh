max_cpus=10
DIR=$(dirname $(readlink -f $0))
COUNTER=0
for group in narrow wide; do
	mylist=${group}_pdbs.txt
	for pdb in `cat $mylist`; do 
		out_path=${group}/output/${pdb%.pdb}/complex
		if [ ! -f ${out_path}/confout.gro -o -f ${out_path}/ionise.gro ]; then
			continue
		else
			bash ~/mpmodeling/protocols/gmx_protocols/resolvate2.sh ${out_path} > ${out_path}/resolvate.log &
			pids[${COUNTER}]=$!
			rm \#mdout.mdp.*		
			COUNTER=$[COUNTER + 1]
		fi
		if ! (( $COUNTER % $max_cpus )) ; then
			for pid in ${pids[*]}; do
				wait ${pid} 
			done
		fi
	done
done

