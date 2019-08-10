import re
import os
import subprocess
from operator import itemgetter

def CheckHeavyAtom(atom_name):
    # Search according to regex list
    HeavyAtoms = ['^N','^C','^O']
    HeavyAtoms_regex = "(" + ")|(".join(HeavyAtoms) + ")"
    if re.search(HeavyAtoms_regex, atom_name) != None:
        return True

def get_Indices4restrain(top_file, residue_list, group):
    # Get all lines from Chain Topology file
    atom_lines = [x.strip() for x in open(top_file,'r').readlines() if 'qtot' in x]
    # Extract indices for atoms per group and residue in list
    output_indices = []
    if group == 'Backbone':
        Backbone = ['N','C','CA','O']
        for resn in residue_list:
            for line in atom_lines:
                if int(line.split()[2]) == resn:
                    atom_name = line.split()[4]
                    if atom_name in Backbone:
                        index = int(line.split()[0])
                        output_indices.append(index)

    elif group == 'HeavyAtoms':
        for resn in residue_list:
            for line in atom_lines:
                if int(line.split()[2]) == resn:
                    atom_name = line.split()[4]
                    if CheckHeavyAtom(atom_name):
                        index = int(line.split()[0])
                        output_indices.append(index)

    return output_indices

def posres_format(index, force):
    line = ' '*2+str(index).rjust(4)+' '*5+str(1)+(' '*2+str(force))*3+"\n"
    return line

def generate_posres(outfile, indices, force):
    heading = (
    "; Customised position restrains for residue list\n"
    "[ position_restraints ]\n"
    "; atom  type      fx      fy      fz\n"
    )
    # Write posres lines into file
    with open(outfile, 'w') as fp:
        fp.write(heading)
        for idx in indices:
            line = posres_format(idx, force)
            fp.write(line)
    fp.close()

def modify_chain_topology(top_file, posres_file, posres_tag):
    # Append to chain topology
    posres_lines = (
    "\n"
    "; Position restrain "+posres_tag+"\n"
    "#ifdef POSRES_"+posres_tag.upper()+"\n"
    '#include '+'"'+os.path.basename(posres_file)+'"'+"\n"
    "#endif"+"\n"
    )
    
    # Backup original chain topology files
    cmd = ['cp', top_file, top_file+'.bak']
    proc = subprocess.Popen(cmd)
    proc.wait()
    
    # Modify chain topology to include reference to posres       
    with open(top_file, 'a') as fp:
        fp.write(posres_lines)
    fp.close()