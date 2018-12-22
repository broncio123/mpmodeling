import sys
import isambard_dev as isambard
from sqlalchemy import create_engine
from setup_db import Json, Pdb, SuperHelix_Parameters, Conformation, BUDE_Energies, RosettaMP_Energies, Interhelix_Interactions, HOLE_Output, SASA_Estimates, Base

dbfile = 'test.db' # DB file
engine = create_engine('sqlite:///'+dbfile)
Base.metadata.bind = engine
from sqlalchemy.orm import sessionmaker
DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()


models = session.query(Pdb).all()
print([m.pdb_name for m in models])

model_hole = session.query(HOLE_Output).all()
print([m.Gpred_Rmin for m in model_hole])

model_shp = session.query(SuperHelix_Parameters).all()
print([m.ca_radii for m in model_shp])
data = [m.ca_radii for m in model_shp] # This already returns a list
print(data[0]*2) # Awesome! :D

data = [m.interface_angles for m in model_shp]
print(data[0])

model_rosettamp = session.query(RosettaMP_Energies).all()
data = [m.I_sc for m in model_rosettamp]
print(data)
