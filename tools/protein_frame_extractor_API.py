import sys
import os
import subprocess
import concurrent.futures

# Import modules from folder
modules_path = "/home/ba13026/mpmodeling/protocols/"
if modules_path not in sys.path:
    sys.path.append(modules_path)

def execute_extractor(input_dict):
    #############################################
    # Extract relevant values from input dict
    workdir = input_dict['workdir']
    name = input_dict['name']
    model_path = input_dict['model_path']
    t_init = input_dict['t_init']
    t_final = input_dict['t_final']
    dt = input_dict['dt']
    #############################################
    if os.path.isdir(model_path):
        pass
    else:
        try:
            model_path = workdir + model_path
            if os.path.isdir(model_path):
                pass
        except:
            print("Not a valid dir path for model")

    extension = '.xtc'
    filename = model_path+'/complex/mdf/' + name

    # Generate index file
    cmd = [
            'gmx_mpi','make_ndx',
            '-f',filename+'.tpr',
            '-o',filename+'.ndx'
            ]
    proc = subprocess.Popen(cmd, stdin = subprocess.PIPE)
    proc.communicate(b"q\n")
    proc.wait()

    # Make directory to store frames
    cmd = ['mkdir', filename]
    proc = subprocess.Popen(cmd)
    proc.wait()

    # Extract frames
    outdir = filename
    cmd = [
            'gmx_mpi','trjconv',
            '-f',filename+'.xtc',
            '-s',filename+'.tpr',
            '-n',filename+'.ndx',
            '-b',str(t_init),
            '-e',str(t_final),
            '-dt',str(dt),
            '-sep',
            '-o',outdir+'/'+'Protein_.pdb'
        ]
    proc = subprocess.Popen(cmd, stdin = subprocess.PIPE)
    proc.communicate(b"Protein\n")
    proc.wait()

    # Alter frames fro Isambard
    def fix_pdb(pdb_path):
        script_path = '/home/ba13026/mpmodeling/tools/fix_pdb.py'
        cmd = [
            'pymol','-qc',
            script_path,'--',
            pdb_path
            ]
        try:
            proc = subprocess.Popen(cmd)
            proc.wait()
        except:
            print("There was an error. Perhaps the PDB has already been altered!")

    Protein_frames = os.listdir(outdir)
    param_list = [outdir+'/'+pdb_frame for pdb_frame in Protein_frames]
    n_threads = 4
    with concurrent.futures.ThreadPoolExecutor(max_workers = n_threads) as executor:
        executor.map(fix_pdb, param_list)
