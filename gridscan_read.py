import sys
import isambard_dev as isambard
from sqlalchemy import create_engine
from gridscan_setup import Pdb,Crick_Parameters,BUDE_Energies,Interhelix_Interactions,HOLE_Output,SASA_Estimates,Base

dbfile = sys.argv[1] # DB file
engine = create_engine('sqlite:///'+dbfile)
Base.metadata.bind = engine
from sqlalchemy.orm import sessionmaker
DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

#session.query(Pdb).all()

#model = session.query(Pdb).all()
#results = [r.pdb_code for r in model]
#print(results)

#model_nhbonds = session.query(HOLE_Output).all()
#results0 = [r.Gpred_Rmin for r in model_nhbonds]
#print(results0)

mymodel = session.query(Pdb).filter(Pdb.id == 7643).first()
print(mymodel.pdb_code)

ckp = session.query(Crick_Parameters).filter(Crick_Parameters.pdb_id == 7643).one()
print(ckp.radius)

modele = session.query(BUDE_Energies).filter(BUDE_Energies.pdb_id == 7643).one()
print(modele.buff_desolvation_energy)

#hole = session.query(HOLE_Output).filter(HOLE_Output.pdb_id == 7643).first()
#print(hole.Gpred_Rmin)


#model_energy = session.query(Bude_energies).all()
#results = [r.buff_steric_energy for r in model_energy]
#print(results)



