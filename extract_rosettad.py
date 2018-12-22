import sys, re

def extract_rosettad(scfile, pdbname):
	"""Extracts relevant metrics from RosettaMP symdock scorefile"""
	infile = open(scfile, 'r')
	lines = infile.readlines()
	matches = []
	for i in range(2, len(lines)):
		if re.search(pdbname, lines[i]):
			matches.append(lines[i])
	lline = matches[-1] # last line
	data = lline.split()
	total_score = float(data[1])
	#rmsd = float(data[2])
	I_sc = float(data[2])
	#return total_score, rmsd, I_sc
	return total_score, I_sc


if __name__ == '__main__':
	scfile = sys.argv[1]  # RosettaMP SymDock scorefile
	# scfile = 'symdock1.sc' # enable for test
	pdbnamef =  sys.argv[2]  # List of plain pdbnames, also in scofile 
	# pdbnamef = 'pdbnames.txt' # enable for test
	infile = open(pdbnamef,'r')
	pdbnames = [l.rstrip() for l in infile.readlines()]
	for name in pdbnames:
		#total_score, rmsd, I_sc = extract_rosettad(scfile,name)
		total_score, I_sc = extract_rosettad(scfile,name)
		print("PDB analysed:",name)
		print("TOTAL ROSETTA SCORES [REU ~ kJ/mol]:",total_score)
		#print("RMSD TO NAITVE [Angstroms]:",rmsd)
		print("INTERFACIAL SCORE [REU ~ kJ/mol]:",I_sc,"\n")
