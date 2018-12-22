
init_file="ionise.gro"
for group in narrow wide; do
        for pdb in `cat ${group}_remaining_pdbs.txt`; do
                path=${group}/output/${pdb%.pdb}/complex
                if [ -e ${path}/$init_file ]; then
			mkdir ${path}/em
			gmx_mpi grompp -f ${path}/mdpf/em_20000stps.mdp -c ${path}/$init_file -p ${path}/topol.top -o ${path}/em/em_20000stps.tpr &
		fi
	rm \#mdout* 
	done
done
