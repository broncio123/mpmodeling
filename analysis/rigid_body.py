#!/usr/bin/python

import numpy 
import isambard_dev

class RigidBody(object):
    """Something"""
    def __init__(self,ampal):
        self.ampal = ampal
        self.n_chains = len(self.ampal.sequences)
        self.base = self.get_assembly_reference()
    
    def get_primitives(self):
        """Return list of coordinates of all chain primitives"""
        primitives = numpy.array([x.coordinates for x in self.ampal.primitives])
        return primitives

    def get_reference_axis(self):
        """Get Reference Axis coordinates"""
        primitives = self.get_primitives()
        reference_axis = isambard_dev.ampal.pseudo_atoms.Primitive.from_coordinates(
            numpy.mean(primitives, axis=0))
        return reference_axis
    
    def get_chains_com(self):
        prims = self.get_primitives()
        coms = [numpy.mean(prims[n],axis=0) for n in range(self.n_chains)]
        return coms
    
    def get_assembly_com(self):
        coms = self.get_chains_com()
        COM = numpy.mean(coms,axis=0)
        return COM
    
    def get_assembly_reference(self):
        """Obtain set of orthonormal vectors for Assembly frame of reference"""
        ref_axis = self.get_reference_axis().coordinates
        coms = self.get_chains_com()
        COM = self.get_assembly_com()
        Z = ref_axis[-1]-ref_axis[0]
        e_z = Z/numpy.linalg.norm(Z)
        # COM of Chain A
        X = coms[0] - COM
        e_x = X/numpy.linalg.norm(X)
        e_y = numpy.cross(e_x, e_z)
        cartesian_base = [e_x, e_y, e_z]
        return cartesian_base
    
    def get_intrinsic_rbasis(self,A,B,C):
        # Triangle edges
        e_BA = (A-B)/numpy.linalg.norm(A-B)
        e_BC = (C-B)/numpy.linalg.norm(C-B)
        # Define normal vector
        N = numpy.cross(e_BC,e_BA)
        e_yaw = N/numpy.linalg.norm(N)
        # Define ...
        e_pitch = (e_BA+e_BC)/numpy.linalg.norm(e_BA+e_BC)
        e_roll = numpy.cross(e_yaw,e_pitch)    
        return e_yaw, e_pitch, e_roll
    
    def Rotation(self,a,b):
        v = numpy.cross(a,b)
        c = numpy.dot(a,b)
        s = numpy.linalg.norm(v)
        I = numpy.identity(3)
        vXStr = '{} {} {}; {} {} {}; {} {} {}'.format(0, -v[2], v[1], v[2], 0, -v[0], -v[1], v[0], 0)
        k = numpy.matrix(vXStr)
        R = I + k + numpy.matmul(k,k) * ((1 -c)/(s**2))
        return R
    
    def euler_angles(self):
        """Given two arrays of 3D orthonormal axes, obtain Euler angles"""
        # Get base vectors
        e_x, e_y, e_z = self.base
        ########################################
        # Get rotated system base
        prims = self.get_primitives()
        coms = self.get_chains_com()
        COM = self.get_assembly_com()
        ########################################
        rotated_base_chain = []
        for i in range(self.n_chains):
            A,B,C = prims[i][-1],coms[i],prims[i][0]
            e_yaw, e_pitch, e_roll = self.get_intrinsic_rbasis(A,B,C)
            rotated_base_chain.append( [e_yaw, e_pitch, e_roll] )
        ########################################
        theta_per_chain = []
        for i in range(self.n_chains):
            e_roll = rotated_base_chain[i][-1]
            # Find projection of e_roll onto XY plane (assembly reference)
            e_roll_xy = numpy.dot(e_roll,e_x)*e_x + numpy.dot(e_roll, e_y)*e_y
            # Normalize
            e_roll_xy = (e_roll_xy)/numpy.linalg.norm(e_roll_xy)
            # Find angle between e_roll and its projection
            theta = numpy.rad2deg( numpy.arccos( numpy.dot(e_roll, e_roll_xy) ) )
            theta_per_chain.append( theta )            
        ########################################
        psi_per_chain_pair = []
        for i in range(self.n_chains - 1):
            e_roll_0 = rotated_base_chain[i][-1]
            e_roll_1 = rotated_base_chain[i+1][-1]
            psi = numpy.rad2deg( numpy.arccos( numpy.dot(e_roll_0, e_roll_1) ) )
            psi_per_chain_pair.append( psi )
        ########################################
        phi_per_chain = []
        for i in range(self.n_chains):
            e_pitch = rotated_base_chain[i][1]
            e_pitch_xy = numpy.dot(e_pitch,e_x)*e_x + numpy.dot(e_pitch, e_y)*e_y
            e_pitch_xy = (e_pitch_xy)/numpy.linalg.norm(e_pitch_xy)
            # Unit vector pointing towards chain COM
            X = coms[i] - COM
            e_chain = X/numpy.linalg.norm(X)
            phi = numpy.rad2deg( numpy.arccos( numpy.dot(e_pitch_xy, e_chain) ) )
            phi_per_chain.append( phi )
        
        return theta_per_chain, psi_per_chain_pair, phi_per_chain