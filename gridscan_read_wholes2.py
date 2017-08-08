import sys, numpy
import isambard_dev
import analyse_protein_properties
from sqlalchemy import create_engine
from gridscan_setup import Pdb,Crick_Parameters,BUDE_Energies,Interhelix_Interactions,HOLE_Output,SASA_Estimates,Base

# Parameters obtained from analysing cWza PDB, V358-T376
#mean_radius = 15.3063556447
#mean_pitch  = 155.121966666
#mean_phica  = -65.0829383279

#python analyse_protein_properties.py altered_cwza.pdb
#"BUFF charged [kcal/mol]":  -23.183117024334436
#BUFF steric [kcal/mol]:  26.137607661136762
#BUFF desolv [kcal/mol]:  -690.216665510815
#No. H-bonds:  349
#No. KIHs:  26
#SASA hydrophobes [Angstrom^2]:  10069.7685546875
#SASA nonhydrophobes [Angstrom^2]:  3767.831787109375
#SASA positively charged res [Angstrom^2]:  4209.4951171875
#SASA negatively charged res [Angstrom^2]:  430.627685546875
#HOLE VDW_Rmin [Angstroms]:  6.85362
#HOLE Pore_Length [Angstroms]:  60.871
#HOLE Gpred by Rmin [nS]:  1.53613091
#HOLE Gpred by Length [nS]:  1.82517797
#HOLE Gpred by Avg EPot [nS]:  1.87054592

dbfile = sys.argv[1] # DB file
engine = create_engine('sqlite:///'+dbfile)
Base.metadata.bind = engine
from sqlalchemy.orm import sessionmaker
DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

filtered0 = session.query(BUDE_Energies).filter(BUDE_Energies.buff_electrostatic_energy + BUDE_Energies.buff_steric_energy + BUDE_Energies.buff_desolvation_energy < 0).all()
results0 = set([r.pdb_id for r in filtered0])
#print(results0)

#results0 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48]

model = session.query(Crick_Parameters).filter(Crick_Parameters.pdb_id.in_(list(results0))).all()
N = len(model)
parameters = [(model[n].radius,model[n].pitch_length,model[n].iangle_phica,filtered0[n].buff_electrostatic_energy+filtered0[n].buff_steric_energy+filtered0[n].buff_desolvation_energy)  for n in range(N-1)]
#for x in parameters:
#	print(x[0],x[1],x[2],x[3])


