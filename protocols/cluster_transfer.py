#!/usr/bin/env python
import pysftp

class Cluster(object):
    def __init__(self):
        self.type = ''
        self.name = ''
        self.user = ''
        self.pwd = ''
        self.workdir = ''
        self.slurm_template = ''
        
# BlueGem
BG = Cluster()
BG.type = 'local'
BG.name = 'bluegem.acrc.bris.ac.uk'
BG.user = 'ba13026'
BG.pwd = '@Aguilar.s.87'
BG.workdir = '/projects/s21/ba13026/Wza_Modeling/L-structures/rosetta/bg_test/md_relax/'

name = 'prmd'
BG.slurm_template = (
    "#!/bin/bash -login \n"
    "#SBATCH -p cpu \n"
    "#SBATCH --ntasks-per-node=16 \n"
    "#SBATCH -N 1 \n"
    "#SBATCH --exclusive \n"
    "#SBATCH -t 1-12:30 \n"
    "#SBATCH -A S2.1 \n"
    "#SBATCH -o complex/jobf/"+name+"_slurm.log \n"
    "#SBATCH -e complex/jobf/"+name+"_slurm.error \n"
    "\n"
    "# Load GROMACS module \n"
    "module load apps/gromacs-5.0.6 \n"
    "\n"
    "mpiexec.hydra -psm -bootstrap slurm gmx_mpi mdrun -s complex/mdf/"+name+".tpr -deffnm complex/mdf/"+name+" \n"
)

# BlueCrystal Phase 4
BC4 = Cluster()
BC4.type = 'remote'
BC4.name = 'bc4login.acrc.bris.ac.uk'
BC4.user = 'ba13026'
BC4.pwd = 'AHuevo.123'
BC4.workdir = '/mnt/storage/scratch/ba13026/md_relax/'

name = 'prmd'
BC4.slurm_template = (
    "#!/bin/bash -login \n"
    "#SBATCH --job-name="+name+" \n"
    "#SBATCH --partition=cpu \n"
    "#SBATCH --nodes=1 \n"
    "#SBATCH --ntasks-per-node=28 \n"
    "#SBATCH --cpus-per-task=1 \n"
    "#SBATCH --time=4-00:00:0 \n"
    "#SBATCH -o "+name+"_slurm.log \n"
    "#SBATCH -e "+name+"_slurm.error \n\n"
    "module add apps/gromacs/5.1.4-mpi-intel \n"
    "module load languages/intel/2017.01 \n"  
    "export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so \n\n"
    "srun gmx_mpi mdrun -s "+name+".tpr -deffnm "+name+" \n"
)

def transfer(filename_origin, Cluster_origin, filename_destiny, Cluster_destiny):
    """Inter-cluster file-transfer engine. Clusters should be defined as objects"""
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(
                            host = BC4.name,
                            username = BC4.user,
                            password = BC4.pwd,
                            cnopts = cnopts
                            ) as sftp:
        if Cluster_origin.type == 'local':
            action = sftp.put
        elif Cluster_origin.type == 'remote':
            action = sftp.get 
        else:
            print("Not a valid cluster")
        try: 
            path_origin = Cluster_origin.workdir + filename_origin
            path_destiny = Cluster_destiny.workdir + filename_destiny
            action(path_origin, path_destiny)
        except:
            print("Error")
    sftp.close()