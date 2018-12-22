#!/usr/bin/python

import re
from operator import itemgetter

class VdW_Radii(object):
    def __init__(self, ampal):
        self.ampal = ampal
        self.simple = VdW_Radii.Simple(self)
        self.amber = VdW_Radii.Amber(self)
            
    def get_atom_res(self):
        """Get list of atom and residue names per chain"""
        chain = self.ampal[0]
        chain_info = [[x.res_label, x.ampal_parent.mol_code] for x in chain.get_atoms()]
        return chain_info
    
    def clean_vdw_data(self, vdwr_raw):
        regex_vdwr = []
        for x in vdwr_raw:
            a,b,c = x
            if '???' in a:
                regex_vdwr.append([a.replace('???','.{0,}'),b.replace('?','.'),c])
            else:
                regex_vdwr.append([a.replace('?','.'),b.replace('?','.'),c])
        return regex_vdwr
        
    def assign_vdwr(self, vdwr_type):
        X = self.get_atom_res()
        vdwr_data = []
        if vdwr_type == 'simple':
            regex_vdwr = self.simple.regex            
            for i in range(len(X)):
                atom_pdb,res_pdb = X[i]
                # Match Hydrogens first, which start with a number
                result = re.match('[0-9]*',atom_pdb)
                span = result.span()[1]
                if span == 0:
                    for k in range(len(regex_vdwr)):
                        atom_pattern, res_pattern, r_vdw = regex_vdwr[k]
                        atom_result =  re.match(atom_pattern, atom_pdb)
                        res_result = re.match(res_pattern, res_pdb)
                        if (atom_result != None) and (res_result != None):
                            vdwr_data.append((i, atom_pdb,res_pdb,r_vdw))
                else:
                    x = atom_pdb[1:]
                    atom_pattern, res_pattern, r_vdw = ['H.{0,}','...','1.00']
                    result = re.match(atom_pattern,x)
                    if result != None:
                        vdwr_data.append((i, atom_pdb,res_pdb,r_vdw))
            
            return vdwr_data

        elif vdwr_type == 'amber':
            regex_vdwr = self.amber.regex
            for i in range(len(X)):
                atom_pdb,res_pdb = X[i]
                matches = []
                # Match Hydrogens first, which start with a number
                result = re.match('[0-9]*',atom_pdb)
                span = result.span()[1]
                if span == 0:
                    for k in range(len(regex_vdwr)):
                        atom_pattern, res_pattern, r_vdw = regex_vdwr[k]
                        atom_result =  re.match(atom_pattern, atom_pdb)
                        res_result = re.match(res_pattern, res_pdb)
                        if (atom_result != None) and (res_result != None):
                            matches.append([i, atom_pdb,atom_pattern,res_pdb,res_pattern,atom_result,r_vdw])
                    if len(matches) == 1:
                        vdwr_data.append(itemgetter(*[0,1,3,-1])(matches[0]))
                    else:
                        for m in range(len(matches)):
                            num,atom_pdb,atom_pattern,res_pdb,res_pattern,atom_result,r_vdw = matches[m]
                            if (atom_pdb == atom_pattern) and (res_pdb == res_pattern):
                                vdwr_data.append(itemgetter(*[0,1,3,-1])(matches[m]))
                                break
                            else:
                                if (atom_pdb == atom_pattern) and (res_pattern == '...'):
                                    vdwr_data.append(itemgetter(*[0,1,3,-1])(matches[m]))
                                    break
                                else:
                                    if len(atom_pdb) == len(atom_pattern):
                                        vdwr_data.append(itemgetter(*[0,1,3,-1])(matches[m]))
                                        break
                                    else:
                                        if matches[m][-2].span()[1] > 1:
                                            vdwr_data.append(itemgetter(*[0,1,3,-1])(matches[m]))
                else:
                    x = atom_pdb[1:]
                    atom_pattern, res_pattern, r_vdw = ['H.{0,}','...','1.00']
                    result = re.match(atom_pattern,x)
                    if result != None:
                        vdwr_data.append((i, atom_pdb,res_pdb,r_vdw))
            
            return vdwr_data
    
    class Simple:
        def __init__(self, a):
            self.a = a
            self.file = '/home/ba13026/hole/hole2/rad/simple.rad'
            self.regex = self.regex()
  
        def regex(self):
            filelines = open(self.file,'r').readlines()
            vdwr_raw = [x.strip().split('VDWR')[-1].split() for x in filelines if re.search(r'VDWR',x)]
            vdwr = self.a.clean_vdw_data(vdwr_raw)
            return vdwr
        
        def get_radii(self):
            return self.a.assign_vdwr('simple')

    class Amber:
        def __init__(self, a):
            self.a = a
            self.file = '/home/ba13026/hole/hole2/rad/amberuni.rad'
            self.regex = self.regex()
        
        def regex(self):
            filelines = open(self.file,'r').readlines()
            vdwr_raw = [x.strip().split('VDWR')[-1].split() for x in filelines if re.search(r'VDWR',x)][2:]
            vdwr_raw = [x[:2]+[float(x[-1])] for x in vdwr_raw]
            vdwr = self.a.clean_vdw_data(vdwr_raw)
            return vdwr
        
        def get_radii(self):
            return self.a.assign_vdwr('amber')