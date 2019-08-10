import os
import glob
import subprocess

# Sorted by Priority for Submission
MD_STAGES = [
    ('urmd','md_100ns'),
    ('prmd','prmd'),
    ('emmd','em_20000stps')
]

def check_for_md_files(model_dir, sname_main):
    """Check if range of file types with common name found in folder """
    out = {}
    # GROMACS file extensions
    FILETYPES = ['.gro', '.xtc']
    path_suffix = 'complex/mdf'
    for extension in FILETYPES:
        file_path = os.path.join(model_dir, path_suffix, sname_main + extension)
        out[extension] = os.path.isfile(file_path)
    
    return out

def check_for_submission_files(model_dir, sname_main):
    FILETYPES = ['.tpr' ,'.slurm']
    SUFFICES = ['complex/mdf', 'complex/jobf']
    out = {}
    for i in range(len(FILETYPES)):
        path_suffix = SUFFICES[i]
        extension = FILETYPES[i]
        file_path = os.path.join(model_dir, path_suffix, sname_main + extension)
        out[extension] = os.path.isfile(file_path)
    
    return out

def determine_last_md_stage(model_dir):
    for i in range(len(MD_STAGES)):
        stage, filename = MD_STAGES[i]
        if all(check_for_md_files(model_dir, filename).values()):
            break
        elif stage == 'emmd' and check_for_md_files(model_dir, filename)['.gro']:
            pass
    return stage

def generate_slurm(model_dir, sname_main, stage):
    #######################################
    # Default params per MD stage: BlueGem SLURM format
    #######################################
    path_prefix_slurm = "complex/jobf"
    path_prefix_md = "complex/mdf"

    if stage == 'urmd':
        n_nodes = 2
        sim_time = "5-12:30"

    elif stage == 'prmd':
        n_nodes = 1
        sim_time = "1-12:30"

    elif stage == 'emmd':
        n_nodes = 1
        sim_time = "12:30"        
    #######################################
    # Script content
    #######################################
    slurm_template = (
        "#!/bin/bash -login \n"
        "#SBATCH -p cpu \n"
        "#SBATCH --ntasks-per-node=16 \n"
        "#SBATCH -N "+str(n_nodes)+" \n"
        "#SBATCH -t "+sim_time+" \n"
        "#SBATCH -A S2.1 \n"
        "#SBATCH -o "+path_prefix_slurm+"/"+sname_main+"_slurm.log \n"
        "#SBATCH -e "+path_prefix_slurm+"/"+sname_main+"_slurm.error \n"
        "\n"
        "# Load GROMACS module \n"
        "module load apps/gromacs-5.0.6 \n"
        "\n"
        "mpiexec.hydra -psm -bootstrap slurm gmx_mpi mdrun "
        "-s "+path_prefix_md+"/"+sname_main+".tpr "
        "-deffnm "+path_prefix_md+"/"+sname_main+" \n"
    )
    #######################################
    # Write submission file for BG
    #######################################
    path_output = os.path.join(model_dir, path_prefix_slurm, sname_main+'.bg.slurm')
    with open(path_output, 'w') as fp:
        fp.write(slurm_template)
    fp.close()

def generate_tpr(model_dir, sname_main, sname_prev):
    """Generate GROMACS run input file"""
    #######################################
    # GROMACS command with input parameters
    #######################################
    if check_for_md_files(model_dir, sname_prev)['.gro']:
        cmd = [
            'gmx_mpi','grompp',
            '-f','/home/ba13026/mpmodeling/protocols/gmx_protocols/templates/'+sname_main+'.mdp',
            '-c',model_dir+'/complex/mdf/'+sname_prev+'.gro',
            '-p',model_dir+'/complex/'+'topol.top',
            '-o',model_dir+'/complex/mdf/'+sname_main+'.tpr',
            '-maxwarn','3',
        ]
        #######################################
        # Run GROMACS command 
        #######################################
        p = subprocess.Popen(cmd)
        p.wait()
        #######################################
        # Clean backup files to reduce storage
        #######################################
        files2remove = glob.glob('./'+'#mdout.mdp.*')
        for f in files2remove:
            os.remove(f)
    else:
        mssg = "ERROR: Coordinates from previous MD stage missing!"
        print(mssg)
        
def prepare_submission_files(model_dir, sname_main, stage_last, stage_next):
    out_check = check_for_submission_files(model_dir, sname_main)
    if out_check['.tpr']:
        generate_tpr(model_dir, sname_main, stage_last)
    elif out_check['.slurm']:
        generate_slurm(model_dir, sname_main, stage_next)