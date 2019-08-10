# Essential data for logging-in
user='ba13026'
host='bluegem.acrc.bris.ac.uk'
key=~/.ssh/Desktop2BG
workdir=/projects/s21/ba13026/Notebooks

# Generate random port numbers
get_port () {  
   echo "$((1000 + RANDOM % 9999))"
}

# Local ports (Linux) 
local_ports_used=$(netstat -tulpn | grep LISTEN | awk '{print $4}'| awk -F ":" '{print $NF}')
local_ARRAY=($local_ports_used)

# Remote ports 
remote_ports_used=$(ssh -i $key ${user}@${host} netstat -tulpn | grep LISTEN | awk '{print $4}'| awk -F : '{print $NF}')
remote_ports_used=($remote_ports_used)
######################################
# Test if random local port already in use
array=()
for port in ${local_ports_used[*]}; do
    array[$port]=1
done

test_local_port=$(get_port)
if [[ ${array[$test_local_port]} ]]; then echo "Exists"; else echo "Doesn't exist" ; fi 
######################################
# Test if random remote port already in use
array=()
for port in ${remote_ports_used[*]}; do
    array[$port]=1
done

test_remote_port=$(get_port)
if [[ ${array[$test_remote_port]} ]]; then echo "Exists"; else echo "Doesn't exist" ; fi
######################################
# Execute command (cmd) on remote host
# Go to Working directory and then launch Jupyter
cmd='cd '${workdir}'; nohup jupyter notebook --no-browser --port='${test_remote_port}' > session0.out &'
ssh -i $key ${user}@${host} $cmd
######################################
# Connect to remote host via established local/remote ports
ssh -i $key -f -N -L localhost:${test_local_port}:localhost:${test_remote_port} ${user}@${host}
######################################
url="http://localhost:"${test_local_port}"/tree"
# Launch Chrome: For Linux
google-chrome --new-window $url
