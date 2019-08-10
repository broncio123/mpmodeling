#!/usr/bin/env python
import sys
import os
import fabric
import subprocess
# Import modules from folder
modules_path = "/home/ba13026/mpmodeling/protocols/"
if modules_path not in sys.path:
    sys.path.append(modules_path)

from cluster_transfer import BG
from cluster_transfer import BC4

# def get_remote_JobIDs(cmd):
#     result = fabric.Connection(
#                 user = BC4.user,
#                 host = BC4.name,
#                 connect_kwargs={"password":BC4.pwd}
#                 ).run(cmd,hide=True)
#     msg = "Ran {0.command!r} on {0.connection.host}, got stdout:\n{0.stdout}"
#     return list(map(int,msg.format(result).split("\n")[1:-1]))


def get_remote_JobIDs(cmd):
    with fabric.Connection(
                user = BC4.user,
                host = BC4.name,
                connect_kwargs={"password":BC4.pwd}
                ) as c: 
        result = c.run(cmd,hide=True)
        msg = "Ran {0.command!r} on {0.connection.host}, got stdout:\n{0.stdout}"
        return list(map(int,msg.format(result).split("\n")[1:-1]))
    c.close()

def get_JobsInfo(cluster_type):
    if cluster_type == 'local':
        cmd1 = ("squeue -u "+BG.user+" -t PD").split()
        proc1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
        PendingJobs = [int(x.split()[0]) for x in list(proc1.stdout)[1:]]

        cmd2 = ("squeue -u "+BG.user+" -t R").split()
        proc2 = subprocess.Popen(cmd2, stdout=subprocess.PIPE)
        RunningJobs = [int(x.split()[0]) for x in list(proc2.stdout)[1:]]

        BG_JobIDs = {
            'PD': PendingJobs,
            'R' : RunningJobs
        }
        return BG_JobIDs
    
    elif cluster_type == 'remote':
        BC4_JobIDs = {}
        cmd1 = "squeue -u "+BC4.user+" -t PD | awk 'NR>1{print $1}' "
        cmd2 = "squeue -u "+BC4.user+" -t R  | awk 'NR>1{print $1}' "

        PendingJobs = get_remote_JobIDs(cmd1)
        RunningJobs = get_remote_JobIDs(cmd2)

        BC4_JobIDs = {
            'PD': PendingJobs,
            'R' : RunningJobs
        }
        return BC4_JobIDs