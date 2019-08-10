import os, sys, json
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Enum, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Tags(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True) # SQL id 
    mutant = Column(String(250), nullable=False)
    group = Column(String(250), nullable=False)
    pdb_name = Column(String(250), nullable=False)
    
class Jobs(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    job_name = Column(String(250), nullable=False) # emmd, prmd, md, nemd
    queue = Column(String(250), nullable=False) # local, remote
    queue_id = Column(Integer) # JOB id on queue
    state = Column(String(250), nullable=False) # R (RUNNING), PD(PENDING)
    # Foreign key
    tag_id = Column(Integer, ForeignKey('tag.id'))
    tag = relationship(Tags)
        
if __name__ == "__main__":
        outdb = sys.argv[1] # Output name of database (.db)
        engine = create_engine('sqlite:///'+outdb)
        Base.metadata.create_all(engine)