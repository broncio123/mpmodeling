import sys
import os
import json
import subprocess
import concurrent.futures


# Import modules from folder
modules_path = "/home/ba13026/mpmodeling/protocols/"
if modules_path not in sys.path:
    sys.path.append(modules_path)

from cluster_transfer import BG

ncores = int(sys.argv[1])
json_input = sys.argv[2]

with open(json_input,'r') as fp:
    param_list = json.load(fp)

name = 'md_100ns'
atomic_group = 'Backbone'

refined_param_list = []
for model_dir in param_list:
    filename1 = name+".gro"
    filename2 = name+".xtc"
    file2check1 = BG.workdir+model_dir+'/complex/mdf/'+filename1
    file2check2 = BG.workdir+model_dir+'/complex/mdf/'+filename2
    if os.path.isfile(file2check1) and os.path.isfile(file2check2):
        refined_param_list.append(model_dir)

param_list = refined_param_list

def get_rmsd(r_model_dir):
    script_path = '/home/ba13026/mpmodeling/tools/rmsd_from_traj.py'
    cmd = ['python', script_path, name, atomic_group, r_model_dir]
    proc = subprocess.Popen(cmd)
    proc.wait()

def main():
    with concurrent.futures.ProcessPoolExecutor(max_workers = ncores) as executor:
        executor.map(get_rmsd, param_list)

if __name__ == '__main__':
        main()