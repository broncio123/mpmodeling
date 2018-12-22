import os, sys
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Pdb(Base):
	__tablename__ = 'pdb'
	id = Column(Integer, primary_key=True) # SQL id 
	pdb_code = Column(String(250), nullable=False) # Model grid-id

class Crick_Parameters(Base):
	__tablename__ = 'crick'
	id = Column(Integer, primary_key=True)
	npeptides = Column(Integer)	# Number of peptide chains 
	radius = Column(Float)		# Helical packing radius [Angstroms]
	pitch_length = Column(Float) 	# Helical packing pitch length [Angstroms]
	iangle_phica = Column(Float)	# Sidechain interface angle - Phi_C_alpha [deg]
	# Foreign key
	pdb_id = Column(Integer, ForeignKey('pdb.id'))
	pdb = relationship(Pdb)

class BUDE_Energies(Base):
	# BUDE force field energetic contributions [kcal/mol]
	__tablename__ = 'interaction_energy'
	id = Column(Integer, primary_key=True)
	buff_steric_energy = Column(Float) 
	buff_desolvation_energy = Column(Float) 
	buff_electrostatic_energy = Column(Float)
	# Foreign key 
	pdb_id = Column(Integer, ForeignKey('pdb.id'))
	pdb = relationship(Pdb)

class Interhelix_Interactions(Base):
	__tablename__ = 'interhelix_interactions'
	id = Column(Integer, primary_key=True)
	nsbridges = Column(Integer) # Number of Salt Bridges
	nhbonds = Column(Integer) # Number of Hydrogen bonds
	nkihs = Column(Integer)	  # Number of found Knobs-Into-Holes 
	# Foreign key 
	pdb_id = Column(Integer, ForeignKey('pdb.id'))
	pdb = relationship(Pdb)

class HOLE_Output(Base):
	# HOLE pore conductance estimates (Gpred), different correction factors 
	__tablename__ = 'hole'
	id = Column(Integer, primary_key=True)
	Gmacro = Column(Float)		# Non-corrected conductance
	Gpred_Rmin = Column(Float)	# Corrected by Minimum Radius
	HOLE_Rmin = Column(Float)	# [Angstroms]
	Gpred_Length = Column(Float)	# Corrected by Length
	HOLE_Length = Column(Float)	# [Angstroms]
	Gpred_AvgEPot = Column(Float)	# Corrected by Average electric potential
	# Foreign key 
	pdb_id = Column(Integer, ForeignKey('pdb.id'))
	pdb = relationship(Pdb)

class SASA_Estimates(Base):
	# Solvent Accessible Surface Area(SASA) estimate, different residue-type groups [Angstroms^2]
	__tablename__ = 'sasa'
	id = Column(Integer, primary_key=True)
	sasa_hydrophobes = Column(Float)
	sasa_nonhydrophobes = Column(Float)
	sasa_pcharged = Column(Float)
	sasa_ncharged = Column(Float)	
	# Foreign key 
	pdb_id = Column(Integer, ForeignKey('pdb.id'))
	pdb = relationship(Pdb)

if __name__ == "__main__":
	outdb = sys.argv[1] # Output name of database (.db)
	engine = create_engine('sqlite:///'+outdb)
	Base.metadata.create_all(engine)

