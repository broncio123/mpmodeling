import sys
import os
import glob
import json
import re
import subprocess

import concurrent.futures
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import modules from folder
modules_path = "/home/ba13026/mpmodeling/protocols/"
if modules_path not in sys.path:
    sys.path.append(modules_path)

from setup_db_JobManager import Tags, Jobs, Base
from intercluster_JobManager import get_JobsInfo

dbfile  = sys.argv[1] # Database filename
n_threads = int(sys.argv[2]) # Number of threads

# Create engine and bind it to current session
engine = create_engine('sqlite:///'+dbfile)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def get_models_JobsData():
    data = []
    for queue in ['local','remote']:
        X = get_JobsInfo(queue)
        for state in ['R','PD']:
            for job_id in X[state]:
                cmd = ('scontrol show jobid -dd '+ str(job_id)).split()
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                job_info = [x.decode('utf-8') for x in list(proc.stdout)]
                job_name = [x.split("=")[-1].strip() for x in job_info if re.search(r"Name", x)][0].split(".")[0]
                job_workdir = [x.split("=")[-1].strip().split() for x in job_info if re.search("WorkDir", x)]
                tags = json.dumps(job_workdir[0][0].split("/")[-3:])
                job_data = [job_name, queue, job_id, state]
                data.append([tags, job_data])
    return data

Data = get_models_JobsData()

def process_model(n):
    tags, job_data = Data[n]
    #####################################
    # Model identifiers
    tags = json.loads(tags)
    mutant, group, pdb_name = tags
    model_tags  = Tags(
        mutant = mutant, 
        group = group, 
        pdb_name = pdb_name
    )
    session.add(model_tags)
    #####################################
    job_name, queue, queue_id, state = job_data
    model_jobs = Jobs(
        job_name = job_name,
        queue = queue,
        queue_id = queue_id,
        state = state,
        tag = model_tags
    )
    session.add(model_jobs)
    # COMMIT CHANGES TO DATABASE  
    session.commit()

def main():
        model_n = list(range(len(Data)))
        with concurrent.futures.ProcessPoolExecutor(max_workers = n_threads) as executor:
                executor.map(process_model, model_n)

if __name__ == '__main__':
    main()