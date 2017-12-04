import os, sys, json
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Enum, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Json(TypeDecorator):
	"""Useful to turn seriable objects like lists into JSON objects"""
	impl = String
	def process_bind_param(self, value, dialect):
		return json.dumps(value)
	def process_result_value(self, value, dialect):
		return json.loads(value)

class Pdb(Base):
	__tablename__ = 'pdb'
	id = Column(Integer, primary_key=True) # SQL id 
	sequence        = Column(String)        # protein sequence
	npeptides       = Column(Integer)       # Number of peptide chains 
	pdb_name = Column(String(250), nullable=False) 

class SuperHelix_Parameters(Base):
	__tablename__ = 'super_helix'
	id = Column(Integer, primary_key=True)
	ca_radii       = Column(Json)          # Mean/Std Helical packing radius per aa, per chain [Angstroms]
	azimuthal_angles = Column(Json)          # Mean/Std Azimuthal angle per aa, per chain [deg]
	axial_positions    = Column(Json)          # Reference axis position per monomer [Angstroms]
	interface_angles = Column(Json)          # Mean/Std Sidechain interface angle [deg]
	# Foreign key
	pdb_id = Column(Integer, ForeignKey('pdb.id'))
	pdb = relationship(Pdb)

class Conformation(Base):
	__tablename__ = 'conformation'
	id = Column(Integer, primary_key=True)
	omega_angles = Column(Json) # Mean/Std Omega dihedral angles per aa, per chain [deg]
	phi_angles = Column(Json) # Mean/Std Phi dihedral angles per aa, per chain [deg]
	psi_angles = Column(Json) # Mean/Std Psi dihedral angles per aa, per chain [deg]
	chi1_angles = Column(Json) # Mean/Std Psi dihedral angles per aa, per chain [deg]
	chi2_angles = Column(Json) # Mean/Std Psi dihedral angles per aa, per chain [deg]
	# Foreign key
	pdb_id = Column(Integer, ForeignKey('pdb.id'))
	pdb = relationship(Pdb)

class BUDE_Energies(Base):
	# BUDE force field energetic contributions [iBEU ~ kcal/mol]
	__tablename__ = 'bude_energies'
	id = Column(Integer, primary_key=True)
	steric = Column(Float) 
	desolvation = Column(Float) 
	electrostatic = Column(Float)
	# Foreign key 
	pdb_id = Column(Integer, ForeignKey('pdb.id'))
	pdb = relationship(Pdb)

class RosettaMP_Energies(Base):
	# Rosetta energetic contributions [REU ~ kcal/mol]
	__tablename__ = 'rosettamp_energies'
	id = Column(Integer, primary_key=True)
	total_score = Column(Float)
	rmsd = Column(Float)
	I_sc = Column(Float) 
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

