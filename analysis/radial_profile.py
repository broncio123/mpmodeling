#!/usr/bin/python

import sys
import numpy
import isambard_dev
from shapely.geometry import Point
from shapely.ops import cascaded_union
from itertools import combinations
from concurrent import futures
from operator import itemgetter

modules_path = "/home/ba13026/mpmodeling/analysis/"
if modules_path not in sys.path:
    sys.path.append(modules_path)

from rigid_body import RigidBody
from vdw_radii import VdW_Radii

class RadialProfile():
    """Hello"""
    def __init__(self, ampal):
        self.ampal = ampal
        ######### Inhereted classes ###############
        self.rigid_body = RigidBody(self.ampal)
        self.vdw_analysis = VdW_Radii(self.ampal)
        #########################################
        self.n_threads = 4
        self.Atoms_XYZ = [numpy.array([atom.x,atom.y,atom.z]) for atom in self.ampal.get_atoms()]
        self.cartesian_base = self.rigid_body.get_assembly_reference()
        self.e_x = self.cartesian_base[0]
        self.e_y = self.cartesian_base[1]
        self.e_z = self.cartesian_base[2]
        self.COM = self.rigid_body.get_assembly_com()
    ############################################
    # Types of profiles
    ############################################
    def primitive(self):
        prims = self.rigid_body.get_primitives()
        xyz = prims[0]
        return self.get_profile(xyz)

    def punctual(self):
        xyz = self.Atoms_XYZ
        return self.get_profile(xyz)

    def vdw(self, vdw_type):
        if vdw_type == 'simple':
            vdw_data = self.vdw_analysis.simple.get_radii()
        elif vdw_type == 'amber':
            vdw_data = self.vdw_analysis.amber.get_radii()
        else:
            print("Not valid VdW Radius type")
        ################################################
        vdw_circle_union = self.get_union_vdw_circles(vdw_data)
        profile = numpy.array(vdw_circle_union.exterior.coords).T
        return profile
    
    def vdw_per_residue(self, vdw_type):
        if vdw_type == 'simple':
            vdw_data = self.vdw_analysis.simple.get_radii()
        elif vdw_type == 'amber':
            vdw_data = self.vdw_analysis.amber.get_radii()
        else:
            print("Not valid VdW Radius type")
        ################################################
        vdw_unions_per_residue =  self.get_union_vdw_circles_per_residue(vdw_data)
        profiles_per_residue = []
        sequence = self.ampal[0].sequence
        for i in range(len(sequence)):
            vdw_union = vdw_unions_per_residue[i]
            profile = numpy.array(vdw_union.exterior.coords).T
            profiles_per_residue.append( [sequence[i],i+1,profile] )
        return profiles_per_residue
    
    def get_profile(self, xyz):
        N = len(xyz)
        r = xyz - self.COM # Coordinates relative to COM
        # Projection onto Assembly frame of reference
        A_x = numpy.dot(r, self.e_x).reshape((N,1))
        A_y = numpy.dot(r, self.e_y).reshape((N,1))
        e_x = self.e_x.reshape((1,3))
        e_y = self.e_y.reshape((1,3))
        ################################################
        r_xy = numpy.matmul(A_x,e_x) + numpy.matmul(A_y,e_y)
        d_xy = numpy.linalg.norm(r_xy,axis = 1)
        ################################################
        r_z = numpy.dot(r, self.e_z)
        ################################################
        profile = [r_z, d_xy]
        return profile
    
    def get_vdw_circles(self, vdw_data):
        Z, R = self.punctual()
        VdW_Radii = [float(x[-1]) for x in vdw_data]
        data = list( zip(Z, R, VdW_Radii) )
        circles = [Point(r_z, d_xy).buffer(vdwr) for r_z,d_xy,vdwr in data]
        return circles
        
    def get_union_vdw_circles(self, vdw_data):
        circles = self.get_vdw_circles(vdw_data)
        return cascaded_union(circles)

    def get_union_vdw_circles_per_residue(self, vdw_data):
        circles = self.get_vdw_circles(vdw_data)
        ################################################
        chain = self.ampal[0]
        tags = [x.unique_id for x in list(chain.get_atoms())]
        ################################################
        # Get sorted list of residue numbers
        resnum = sorted( list(map(int, set(map(lambda x:x[1], tags)))) )
        ################################################
        # Get atom indices corresponding to each residue
        indices_per_residue = [[x[-1]-1 for x in tags if x[1] == str(n)] for n in resnum]
        ################################################
        union_per_residue = []
        for indices in indices_per_residue:
            union_residue = cascaded_union( itemgetter(*indices)(circles) )
            union_per_residue.append( union_residue )
        ################################################
        return union_per_residue