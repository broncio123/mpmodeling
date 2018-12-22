max_cpus=10
DIR=$(dirname $(readlink -f $0))
COUNTER=0
for group in narrow wide; do
        mylist=${group}_pdbs.txt
        for pdb in `cat $mylist`; do
		in_path=${group}/input/$pdb
                out_path=${group}/output/${pdb%.pdb}
		mkdir $out_path
		bash  ~/mpmodeling/protocols/gmx_protocols/prepare_protein_com.sh $in_path $out_path > ${out_path}/preparation.log &
                pids[${COUNTER}]=$!
                echo $!
                COUNTER=$[COUNTER + 1]
                if ! (( $COUNTER % $max_cpus )) ; then
                        for pid in ${pids[*]}; do
                                wait ${pid}
                        done
                fi
        done
done

