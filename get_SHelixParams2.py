
import os, numpy, sys
from numpy.linalg import norm
import isambard_dev

def get_SHparams(protein): 
	sequence = protein[0].sequence
	residue_ids = [protein[0][i].id for i in range(len(protein[0].sequence))]
	reference_axis = isambard_dev.analyse_protein.reference_axis_from_chains(protein)
	residue_code =  [sequence[n]+str(n+1)  for n in range(len(sequence))]

	N_chains = len(protein.sequences)
	# Calculate mean radius just for residues in range
	data = []
	for n in range(N_chains):
		chain = protein[n]
		radius_list = isambard_dev.analyse_protein.polymer_to_reference_axis_distances(chain, reference_axis)
		data.append(radius_list)

	data = numpy.array(data).T
	mean_radii      = list(numpy.mean(data, axis=1))
	std_radii       = list(numpy.std(data, axis=1))
	ca_radii = [[residue_code[n], mean_radii[n], std_radii[n]] for n in range(len(residue_code))]

	# Get cylindrical azimuthal phi-angle (radians)
	data = []
	ra_xyz     = reference_axis.coordinates
	for n in range(N_chains):
		chain = protein[n]
		protein_xyz     = chain.primitive.coordinates
		r0 = protein_xyz[0] - ra_xyz[0]
		data_per_chain = []
		data_per_chain.append(0)
		for j in range(1,len(protein_xyz)):
			distance2axis   = protein_xyz[j] - ra_xyz[j]
			cos_angle       = numpy.dot(r0, distance2axis)/(norm(r0)*norm(distance2axis))
			phi_angle       = numpy.rad2deg(numpy.arccos(cos_angle))
			data_per_chain.append(phi_angle)
		data.append(data_per_chain)

	data = numpy.array(data).T
	mean_phis       = list(numpy.mean(data, axis=1))
	std_phis        = list(numpy.std(data, axis=1))
	azimuthal_angles = [[residue_code[n], mean_phis[n], std_phis[n]] for n in range(len(residue_code))]	

	# Get CA positions relative to reference axis
	ra_xyz = reference_axis.coordinates
	L = [norm(r - ra_xyz[0]) for r in ra_xyz]
	
	# Get interface angles 
	data = []
	for n in range(N_chains):
		chain = protein[n]
		protein_xyz = chain.primitive.coordinates
		crangles = isambard_dev.analyse_protein.crick_angles(chain, reference_axis)
		crangles = [x for x in crangles if x is not None]
		data.append(crangles)

	data = numpy.array(data).T
	mean_crangles   = list(numpy.mean(data, axis=1))
	mean_crangles.append('None')
	std_crangles    = list(numpy.std(data, axis=1))
	std_crangles.append('None')
	interface_angles = [[residue_code[n], mean_crangles[n], std_crangles[n]] for n in range(len(residue_code))]

	return ca_radii, azimuthal_angles, L, interface_angles

if __name__ == "__main__":
	infile = sys.argv[1] # input file
	protein = isambard_dev.ampal.ampal.convert_pdb_to_ampal(infile)
	ca_radii, azimuthal_angles, axial_positions, interface_angles = get_SHparams(protein)
	print("Z-axis positions: ", axial_positions, "\n")
	print("Mean and Std values of CA radius wrt reference axis per aa, per chain:\n", ca_radii, "\n")
	print("Mean and Std values of Azimuthal Angle per aa, per chain; wrt reference axis:\n" , azimuthal_angles, "\n")
	print("Mean and Std values of Inerface Angle wrt reference axis per aa, per chain:\n", interface_angles, "\n")
