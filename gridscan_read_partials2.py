import sys, numpy
import isambard_dev 
from sqlalchemy import create_engine
from gridscan_setup import Pdb,Crick_Parameters,BUDE_Energies,Interhelix_Interactions,HOLE_Output,SASA_Estimates,Base

#python analyse_protein_properties.py cwza_V358-T376.pdb 
#BUFF charged [kcal/mol]:  -91.43627166906927
#BUFF steric [kcal/mol]:  25.69451844451674
#BUFF desolv [kcal/mol]:  -349.9606690575881
#No. H-bonds:  191
#No. KIHs:  16
#SASA hydrophobes [Angstrom^2]:  4707.58984375
#SASA nonhydrophobes [Angstrom^2]:  3035.599853515625
#SASA positively charged res [Angstrom^2]:  2324.489013671875
#SASA negatively charged res [Angstrom^2]:  430.627685546875
#HOLE VDW_Rmin [Angstroms]:  6.85662
#HOLE Pore_Length [Angstroms]:  40.817
#HOLE Gpred by Rmin [nS]:  1.78659111
#HOLE Gpred by Length [nS]:  2.5350265199999997
#HOLE Gpred by Avg EPot [nS]:  1.59354474


dbfile = sys.argv[1] # DB file
engine = create_engine('sqlite:///'+dbfile)
Base.metadata.bind = engine
from sqlalchemy.orm import sessionmaker
DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

filtered6 = session.query(BUDE_Energies).filter(BUDE_Energies.buff_desolvation_energy > -350, BUDE_Energies.buff_desolvation_energy < -349).all()
results6 = set([r.pdb_id for r in filtered6])


#1. Filter by HOLE predicted conductance, correctedt by VDW Minimum Radius [nS]
filtered0 = session.query(HOLE_Output).filter(HOLE_Output.Gpred_Rmin > 1.4, HOLE_Output.Gpred_Rmin < 2).all()
## Find all PDB ids of possible candidates
results0 = set([r.pdb_id for r in filtered0])
#print(results0)

#2. Filter by No. of KIHs
# Assumed that 1 KIH can be missing or additional per helix
filtered1 = session.query(Interhelix_Interactions).filter(Interhelix_Interactions.nkihs > 8,Interhelix_Interactions.nkihs < 24).all()
results1 = set([r.pdb_id for r in filtered1])
#print(results1)

#3. Filter by No. of H-bonds
# Assumed that 1 H-bond can be missing or additional per helix
filtered2 = session.query(Interhelix_Interactions).filter(Interhelix_Interactions.nhbonds > 183,Interhelix_Interactions.nhbonds < 199).all()
results2 = set([r.pdb_id for r in filtered2])
#print(results2)

#4. Filter by No. of S-bridges
filtered3 = session.query(Interhelix_Interactions).filter(Interhelix_Interactions.nsbridges == 0).all()
results3 = set([r.pdb_id for r in filtered3])
#print(results3)

#5. Filter by BUDE electrostatic energy 
filtered4 = session.query(BUDE_Energies).filter(BUDE_Energies.buff_electrostatic_energy > -92 , BUDE_Energies.buff_electrostatic_energy < -90 ).all()
results4 = set([r.pdb_id for r in filtered4])
#print(results4)

#6. Filter by BUDE steric energy 
filtered5 = session.query(BUDE_Energies).filter(BUDE_Energies.buff_steric_energy > 25 , BUDE_Energies.buff_steric_energy < 26 ).all()
results5 = set([r.pdb_id for r in filtered5])
#print(results5)

#7. Filter by BUDE desolvation energy
filtered6 = session.query(BUDE_Energies).filter(BUDE_Energies.buff_desolvation_energy > -350, BUDE_Energies.buff_desolvation_energy < -349).all()
results6 = set([r.pdb_id for r in filtered6])
#print(results6)

intersection = results0 & results3 & results4 
print(intersection)

#{10615, 12167}
#model_id = 10615
model_id = 12167
model = session.query(Crick_Parameters).filter(Crick_Parameters.pdb_id == model_id).one()
print(model.radius, model.pitch_length, model.iangle_phica)

##  Build model with helical packing parameters
npeptides = 8
sequence = 'VPTITGVHDLTETVRYIKT'
nresidues = len(sequence)
model_ampal = isambard_dev.ampal.specifications.CoiledCoil.from_parameters(8,nresidues,model.radius, model.pitch_length, model.iangle_phica)
model_ampal.build()
model_ampal.pack_new_sequences((sequence)*npeptides)

# 1.5 Save model coordinates in PDB
model_pdb = 'mymodels/'+'model'+'_'+str(model_id)+'.pdb'
with open(model_pdb, 'w') as x:
        x.write(model_ampal.pdb)


