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

#1. Filter by HOLE predicted conductance, correctedt by VDW Minimum Radius [nS]
filtered0 = session.query(HOLE_Output).filter(HOLE_Output.Gpred_Rmin > 1.4, HOLE_Output.Gpred_Rmin < 1.65).all()
## Find all PDB ids of possible candidates
results0 = set([r.pdb_id for r in filtered0])
#print(results0)

#2. Filter by No. of KIHs
# Assumed that 1 KIH can be missing or additional per helix
filtered1 = session.query(Interhelix_Interactions).filter(Interhelix_Interactions.nkihs > 18,Interhelix_Interactions.nkihs < 34).all()
results1 = set([r.pdb_id for r in filtered1])
#print(results1)

#3. Filter by No. of H-bonds
# Assumed that 1 H-bond can be missing or additional per helix
filtered2 = session.query(Interhelix_Interactions).filter(Interhelix_Interactions.nhbonds > 357,Interhelix_Interactions.nhbonds < 341).all()
results2 = set([r.pdb_id for r in filtered2])
#print(results2)

#4. Filter by No. of S-bridges
filtered3 = session.query(Interhelix_Interactions).filter(Interhelix_Interactions.nsbridges == 0).all()
results3 = set([r.pdb_id for r in filtered3])
#print(results3)

#5. Filter by BUDE electrostatic energy 
#"BUFF charged [kcal/mol]":  -23.183117024334436
#BUFF steric [kcal/mol]:  26.137607661136762
#BUFF desolv [kcal/mol]:  -690.216665510815

filtered4 = session.query(BUDE_Energies).filter(BUDE_Energies.buff_electrostatic_energy > -24 , BUDE_Energies.buff_electrostatic_energy < -22 ).all()
results4 = set([r.pdb_id for r in filtered4])
#print(results4)

#6. Filter by BUDE steric energy 
filtered5 = session.query(BUDE_Energies).filter(BUDE_Energies.buff_steric_energy > 25 , BUDE_Energies.buff_steric_energy < 27 ).all()
results5 = set([r.pdb_id for r in filtered5])
#print(results5)

#7. Filter by BUDE desolvation energy
filtered6 = session.query(BUDE_Energies).filter(BUDE_Energies.buff_desolvation_energy > -691, BUDE_Energies.buff_desolvation_energy < -689).all()
results6 = set([r.pdb_id for r in filtered6])
#print(results6)

intersection = results0 & results3 & results4 
print(intersection)

# Candidate model:
#model_id = 12320
model_id = 12380
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

whole_model_pdb = 'mymodels/'+'whole_model'+'_'+str(model_id)+'.pdb'
crystal_structure_pdb = 'altered_cwza.pdb'
model_ampal = analyse_protein_properties.pymol_align_protein2model(crystal_structure_pdb,model_pdb,whole_model_pdb)

model_pdb = whole_model_pdb 
with open(model_pdb, 'w') as x:
        x.write(model_ampal.pdb)


#{12320, 12380}

