#!/bin/sh

path=$1

# 1. Make index file and create Protein_POPC group, and delete any other group
printf "1|13\ndel 0-23\nq\n" | gmx_mpi make_ndx -f ${path}/confout.gro -o ${path}/protein+lipids.ndx

# 2.Pass previous index file to editconf and extract coordinates and save in PDB
gmx_mpi editconf -f ${path}/confout.gro -n ${path}/protein+lipids.ndx -o ${path}/protein+lipids.pdb

# 3. Use SOLVATE to obtain protein-bilayer solvation layers
~/solvate_1.0/solvate -t 3 -n 8 ${path}/protein+lipids ${path}/protein+lipids+sol_layer

# 5. Alter atom/residue names in solvation_layer.pdb; to be compatible with OPLS/AA and SPC water model
pymol -qc alter_solvation_layer.py -- ${path}/protein+lipids+sol_layer.pdb ${path}/protein+lipids+sol_layer_altered.pdb

# 6. Add chain labels for residue lines
pymol -qc label_chains4gro.py -- ${path}/protein+lipids+sol_layer_altered.pdb ${path}/protein_chains+lipids+sol_layer_altered.pdb

# 7. Redefine box dimensions, centering system
read Lx Ly Lz<<<$(tail -1 confout.gro)
Lz=10.0626 

gmx_mpi editconf -f ${path}/protein_chains+lipids+sol_layer_altered.pdb -o ${path}/protein_chains+lipids+sol_layer_altered.pdb -c -box $Lx $Ly $Lz

# 8. Solvate box with ice-water.
## Fix topology before using gmx solvate
sed -i '/SOL/d' ${path}/topol.top
N_waters=$(grep TIP3 ${path}/protein+lipids+sol_layer.pdb | wc -l|awk '{print $1/3}')
printf "SOL\t\t $N_waters\n" >> ${path}/topol.top

gmx_mpi solvate -cp ${path}/protein_chains+lipids+sol_layer_altered.pdb -p ${path}/topol.top -cs spc216.gro -o ${path}/protein+lipids+sol_RAW.pdb

## Fix topology again, adding up solvation layer and ice-waters
N_waters_total=$(grep SOL ${path}/topol.top | awk '{s+=$2} END{printf "SOL\t\t "s}')
sed -i '/SOL/d' ${path}/topol.top
echo $N_waters_total >> ${path}/topol.top

# 9. Water removal: Outisde box, between lipids in bilayer, and from protein-lipids interface 
## Get PDB of protein alone with chain separation 
printf "q\n" | gmx_mpi make_ndx -f ${path}/protein+lipids+sol_RAW.pdb -o ${path}/protein+lipids+sol_RAW.ndx
echo "Protein" | gmx_mpi editconf -f ${path}/protein+lipids+sol_RAW.pdb -n ${path}/protein+lipids+sol_RAW.ndx -o ${path}/protein_RAW.pdb
sed -i '/TER/d' ${path}/protein_RAW.pdb
sed -iw 's/ENDMDL/END/g' protein_RAW.pdb

var=$path python3 <<@@
import os
import numpy, re
import isambard_dev

path = os.environ["var"]

# 1. FIND POSITION OF P8 ATOMS IN POPC
in_file = path+"/"+"protein+lipids+sol_RAW.pdb" 
ifile   = open(in_file, 'r')
lines   = ifile.readlines()
ifile.close()

# Extract Lipid Phosphate (P8) atomic coordinates: Z-axis
P8_z = [float(l.split()[7]) for l in lines if re.search(r"P8", l)]
P8_z_mean  = numpy.mean(P8_z)
# Average Z-axis postions, upper leaflet
P8_z_Upper = [z for z in P8_z if z>P8_z_mean]
P8_z_Upper_mean  = numpy.mean(P8_z_Upper)
# Average Z-axis postions, lower leaflet
P8_z_Lower = [z for z in P8_z if z<P8_z_mean]
P8_z_Lower_mean  = numpy.mean(P8_z_Lower)
del P8_z

# 2. REMOVE WATERS OUTSIDE BOX
box_dim = list(map(float,[l.split()[1:4] for l in lines if re.search(r"CRYST",l)][0]))
Lx,Ly,Lz = box_dim

SOL = [l for l in lines if re.search(r'SOL', l)]
for i in range(0,len(SOL),3):
    atom = SOL[i].split()[-1]
    if atom != 'O':
        SOL[i] = SOL[i][:-1] + "           O\n"
        SOL[i+1] = SOL[i+1][:-1] + "           H\n"
        SOL[i+2] = SOL[i+2][:-1] + "           H\n"

SOL_data = SOL
N = len(SOL_data)
SOL_box = []
for i in range(0,N,3):
        x,y,z = list(map(float,SOL_data[i].split()[-6:-3]))
        if (0 < x < Lx):
            if ( 0 < y < Ly):
                if (0 < z < Lz):
                    SOL_box.append(SOL_data[i])
                    SOL_box.append(SOL_data[i+1])
                    SOL_box.append(SOL_data[i+2])

# SUMMARY OF WATER REMOVAL: FIRST PHASE 
summary_file = open(path+"/"+"water_removal.txt", 'w')
summary_file.write("SUMMARY OF WATER REMOVAL:\nFIRST PHASE: Trim box\n")
summary_file.write("Initial number of waters: "+str(N)+"\n")
summary_file.write("Number of waters within box boundaries: "+str(len(SOL_box))+"\n")
summary_file.write("Percentage surviving: "+str(len(SOL_box)/float(N)*100)+" %"+"\n\n")

# 3. REMOVE WATERS WITHIN BILAYER AND FROM PROTEIN-LIPID INTERFACE 
protein = isambard_dev.ampal.convert_pdb_to_ampal(path+"/"+"protein_RAW.pdb")
protein_com = numpy.array(protein.centre_of_mass)

## Find primitives per chain
ampal = protein
prims = numpy.array([x.coordinates for x in ampal.primitives])
ref_axis = isambard_dev.ampal.pseudo_atoms.Primitive.from_coordinates(numpy.mean(prims, axis=0))

# Determine chain radial profile and define a Z-partition
dist = prims[0] - ref_axis.coordinates
R_profile = numpy.linalg.norm(dist, axis=1)

primitive_z = numpy.array(ref_axis.coordinates).T[2]

protein_z_partition = []
for i in range(len(primitive_z)-1):
    lower_lim = primitive_z[i]
    upper_lim = primitive_z[i+1]
    rad_lim = R_profile[i]
    protein_z_partition.append([lower_lim, upper_lim, rad_lim])

R_low = R_profile[0]
R_upper = R_profile[-1]
total_z_partition = [[P8_z_Lower_mean, primitive_z.min(), R_low]] \
    + protein_z_partition  \
    + [[primitive_z.max(), P8_z_Upper_mean, R_upper]]

## Remove waters inside between bilayer leaflets and from protein-lipid interface,
SOL_data = SOL_box
N = len(SOL_data)
SOL_inside_indices = []
for s in total_z_partition:
    lower_lim = s[0]
    upper_lim = s[1]
    rad_lim = s[2]
    for i in range(0,N,3):
        x,y,z = list(map(float,SOL_data[i].split()[-6:-3]))
        r_xy = numpy.linalg.norm(numpy.array([x,y]) - protein_com[:2])
        if (lower_lim < z <= upper_lim) and (r_xy < rad_lim):
            SOL_inside_indices.append(i)

## Find waters outside bilayer,
SOL_data = SOL_box
N = len(SOL_box)
SOL_outside_indices = []
for i in range(0,N,3):
    x,y,z = list(map(float,SOL_data[i].split()[-6:-3]))
    r_xy = numpy.linalg.norm(numpy.array([x,y]) - protein_com[:2])
    if (z <= P8_z_Lower_mean) or (z > P8_z_Upper_mean):
        SOL_outside_indices.append(i)

## Merge solvent indeces and select water coordinates accordingly,
SOL_filtered_indeces = SOL_inside_indices + SOL_outside_indices
SOL_filtered_indeces.sort()

# SUMMARY OF WATER REMOVAL: SECOND PHASE
summary_file.write("SECOND PHASE: Remove waters within bilayer and protein-lipid interface\n")
summary_file.write("Initial number of waters: "+str(len(SOL_box))+"\n")
summary_file.write("Number of waters within box boundaries: "+str(len(SOL_filtered_indeces))+"\n")
summary_file.write("Water surviving(2): "+str(len(SOL_filtered_indeces)/float(len(SOL_box))*100)+" %"+"\n\n")
summary_file.close()

# 4. GENERATE SYSTEM PDB WITH FILTERED WATERS
SOL_filtered = []
for index in SOL_filtered_indeces:
    SOL_filtered.append(SOL_box[index])
    SOL_filtered.append(SOL_box[index+1])
    SOL_filtered.append(SOL_box[index+2])

pdb_prot_popc = []
for l in lines:
        if re.search(r"SOL", l):
                break
        else:
            pdb_prot_popc.append(l)

out_file = path+'/'+'protein+lipids+sol_clean.pdb'
ofile    = open(out_file, 'w')
for l in pdb_prot_popc:
    ofile.write(l)
for l in SOL_filtered:
    ofile.write(l)
ofile.close()
@@

N_filtered=$(grep "Number of waters within box boundaries" ${path}/water_removal.txt | awk -F":" 'END{print $2}')
sed -i '/SOL/d' ${path}/topol.top
printf "SOL\t\t $N_filtered\n" >> ${path}/topol.top


# 10. Add K-Cl ions to the system, at 1M concentration, neutral
gmx_mpi grompp -f ${path}/mdpf/ionise.mdp -c ${path}/protein+lipids+sol_clean.pdb -o ${path}/ionise.tpr -p ${path}/topol.top
echo "SOL" | gmx_mpi genion -s ${path}/ionise.tpr -p ${path}/topol.top -o ${path}/ionise.gro -conc 1.0 -pname K -nname CL -neutral

# Remove unecessary files
rm \#*
rm mdout.mdp
