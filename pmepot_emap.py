#!/usr/bin/env python

import os, sys

pqr_file	= sys.argv[1] # PRQ file name
trj_file	= sys.argv[2] # Trajectory file (.xtc)

c1	= "mol load pqr %s\n" % pqr_file # VMD: Load PQR file
c2	= "mol addfile  %s waitfor all\n" % trj_file # VMD: Load trajectory into molecule (PQR)
c3	= "package require pmepot\n" # VMD: Load package PMEPot
# VMD: Execute PMEPot for all frames in trajectory with default PMEPot parameters
c4	= "pmepot -frames all -dxfile %s\n" % (pqr_file[:-4]+"_PMEPot_"+trj_file[:-4]+"_emap.dx")

# Call VMD without launching GUI
vmdin = os.popen("vmd -dispdev none","w")
# Execute all the above-defined commands
vmdin.write("%s"%c1)
vmdin.write("%s"%c2)
vmdin.write("%s"%c3)
vmdin.write("%s"%c4)
#vmdin.flush()

