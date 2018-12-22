#!/bin/bash

#path='.'
path=$1
######################################################################
for X in A B C D E F G H; do
# Modify chain topology files
head -n -5 ${path}/topol_Protein_chain_${X}.itp > ${path}/topol_Protein_chain_${X}.temp.itp;

printf -- "
; Position restraint SC and BB
#ifdef POSRES_SC_BB
#include \"posre_Protein_SC+BB_chain_%s.itp\"
#endif

; Position restraint BB only
#ifdef POSRES_BB
#include \"posre_Protein_BB_chain_%s.itp\"
#endif\n" $X $X >> ${path}/topol_Protein_chain_${X}.temp.itp;

mv ${path}/topol_Protein_chain_${X}.itp  ${path}/topol_Protein_chain_${X}.itp.bak;
mv ${path}/topol_Protein_chain_${X}.temp.itp  ${path}/topol_Protein_chain_${X}.itp;
done
######################################################################
# Protein-SC+BB restraints
for X in  A B C D E F G H; do
# Print header
printf -- "
; position restraints for Protein of Protein in POPC in water

[ position_restraints ]
;  i funct       fcx        fcy        fcz\n" > ${path}/posre_Protein_SC+BB_chain_${X}.itp;

# Print atom numbers from topology file and force vectors
awk '/\[ atoms \]/,/\[ bonds \]/ {print $1}' ${path}/topol_Protein_chain_${X}.itp | 
grep -o '[0-9]\+' |
awk '{printf "%4.i    1       3000       3000       3000\n",$1}' >> ${path}/posre_Protein_SC+BB_chain_${X}.itp;
done
######################################################################
# Protein-BB restraints
for X in  A B C D E F G H; do
# Rename default posres files
cp ${path}/posre_Protein_chain_${X}.itp ${path}/posre_Protein_chain_${X}.itp.bak
mv ${path}/posre_Protein_chain_${X}.itp  ${path}/posre_Protein_BB_chain_${X}.itp;
# Increase restraining force
sed -i 's/1000/3000/g' ${path}/posre_Protein_BB_chain_${X}.itp;
done
######################################################################
# Lipid POPC restraints
printf -- "
; position restraints for POPC of Protein in POPC in water

[ position_restraints ]
;  i funct       fcx        fcy        fcz\n" > ${path}/posre_POPC.itp;

# Print atom numbers from topology file and force vectors
awk '/\[ atoms \]/,/\[ bonds \]/ {print $1}' ${path}/topol_POPC.itp |
grep -o '[0-9]\+' |
awk '{printf "%4.i    1       3000       3000       3000\n",$1}' >> ${path}/posre_POPC.itp
######################################################################
