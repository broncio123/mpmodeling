#!/bin/bash

# NOTES
# List all ports of running notebooks
# Extract port numbers
# Identify PID of running notebook from port
# Kill process given PID 

for port in  `jupyter notebook list | grep "http://localhost" | awk -F ":" '{print $3}' | awk -F "/" '{print $1}'`; do 
	lsof -n -i4TCP:${port} | awk 'NR>1{system("kill -9 "$2)}'
done

# REF:
# https://github.com/jupyter/notebook/issues/2844
