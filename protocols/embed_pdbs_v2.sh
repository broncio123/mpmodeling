max_cpus=10
DIR=$(dirname $(readlink -f $0))
COUNTER=0
for group in narrow wide; do
	mylist=${group}_pdbs.txt
	for pdb in `cat $mylist`; do 
		out_path=${group}/output/${pdb%.pdb}
		if [ -f ${out_path}/complex/confout.gro ]; then 
			continue
		else
			cd $out_path
			paths[${COUNTER}]=$out_path
			bash ~/mpmodeling/protocols/gmx_protocols/embed_protein.sh . > embed.log &
			pids[${COUNTER}]=$!
			echo $!
			COUNTER=$[COUNTER + 1]
			cd -
		fi
		if ! (( $COUNTER % $max_cpus )) ; then
			for pid in ${pids[*]}; do
				wait ${pid} 
			done
			for path in ${paths[*]}; do
				rm ${path}/step*
			done
		fi
	done
done
