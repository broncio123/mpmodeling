#!/usr/bin/env python

import sys, numpy
from gridData import Grid

fname	= sys.argv[1] # Main DX format file [.dx file]
V 	= float(sys.argv[2]) # Voltage correction [Volts]
Lz 	= float(sys.argv[3]) # Z-axis lenght - Sim. Box [nm]
g	= Grid(fname) # Load grid data
xy_grid = g.grid.T    # Extract all XY grids
N	= len(xy_grid) # Number of grids
C	= 0.02588716    # Conversion factor [Volts/PMEPot unit]
dn	= 1/160.
dz      =  float(Lz)/float(N)
for n in range(N):
	grid_n	=  xy_grid[n]
	Nx, Ny	=  grid_n.shape
	z	=  n*dz
	average_potential = C*numpy.sum(grid_n)/float(Nx*Ny)
	corrected_potential = V*n*dn + average_potential
		
	print  z, corrected_potential





