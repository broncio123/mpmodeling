import sys
import os
import glob
import json
import re
import subprocess
import concurrent.futures

# Import modules from folder
modules_path = "/home/ba13026/mpmodeling/protocols/"
if modules_path not in sys.path:
    sys.path.append(modules_path)

from setup_db_JobManager import Tags, Jobs
from intercluster_JobManager import get_JobsInfo

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
    tags = json.loads(tags)
    mutant, group, pdb_name = tags
    print(mutant, group, pdb_name)
    
for n in range(len(Data)):
    process_model(n)