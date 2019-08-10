import sys
import os
import json
import subprocess
import concurrent.futures

ncores = int(sys.argv[1])
json_input = sys.argv[2]

with open(json_input,'r') as fp:
    param_list = json.load(fp)

modules_path = "/home/ba13026/mpmodeling/tools/"
if modules_path not in sys.path:
    sys.path.append(modules_path)

from protein_frame_extractor_API import execute_extractor

def main():
    with concurrent.futures.ProcessPoolExecutor(max_workers = ncores) as executor:
        executor.map(execute_extractor, param_list)

if __name__ == '__main__':
        main()