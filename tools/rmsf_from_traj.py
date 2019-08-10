import sys
import os
import subprocess
import concurrent.futures

# Import modules from folder
modules_path = "/home/ba13026/mpmodeling/protocols/"
if modules_path not in sys.path:
    sys.path.append(modules_path)

from cluster_transfer import BG

# Get path to filename
name = sys.argv[1]
atomic_group = sys.argv[2]
model_path = sys.argv[3]

if os.path.isdir(model_path):
    pass
else:
    try:
        model_path = BG.workdir + model_path
        if os.path.isdir(model_path):
            pass
    except:
        print("Not a valid dir path for model")

extension = '.xtc'
filename = model_path+'/complex/mdf/' + name

# Generate index file
cmd = [
        'gmx_mpi','rmsf',
        '-f',filename+'.xtc',
        '-s',filename+'.tpr',
        #'-n',filename+'.ndx',
        '-res',
        '-o',filename+'_rmsf_'+atomic_group+'.xvg'
        ]
proc = subprocess.Popen(cmd, stdin = subprocess.PIPE)

proc.communicate(bytes(atomic_group+"\n",'utf-8'))
proc.wait()
