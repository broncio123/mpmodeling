
user='ba13026'
host='bluegem.acrc.bris.ac.uk'

get_port () {  
   echo "$((1000 + RANDOM % 9999))"
}

# Get list of LISTEN ports 
# Linux
#local_ports_used=$(netstat -tulpn | grep LISTEN | awk '{print $4}'| awk -F ":" '{print $NF}')
#local_ARRAY=($local_ports_used)

# MacOS
local_ports_used=$(lsof -nP +c 15 | grep LISTEN | awk '{print $(NF-1)}' | awk -F ":" '{print $NF}')
local_ports_used=($local_ports_used)

# Remote ports
remote_ports_used=$(ssh -i ~/.ssh/mac2bg ${user}@${host} netstat -tulpn | grep LISTEN | awk '{print $4}'| awk -F : '{print $NF}')
remote_ports_used=($remote_ports_used)
######################################
array=()
for port in ${local_ports_used[*]}; do
    array[$port]=1
done

test_local_port=$(get_port)
if [[ ${array[$test_local_port]} ]]; then echo "Exists"; else echo "Doesn't exist" ; fi 
######################################
array=()
for port in ${remote_ports_used[*]}; do
    array[$port]=1
done

test_remote_port=$(get_port)
if [[ ${array[$test_remote_port]} ]]; then echo "Exists"; else echo "Doesn't exist" ; fi
######################################
cmd='nohup jupyter notebook --no-browser --port='${test_remote_port}' > session0.out &'
ssh -i ~/.ssh/mac2bg ${user}@${host} $cmd

######################################
ssh -i ~/.ssh/mac2bg -f -N -L localhost:${test_local_port}:localhost:${test_remote_port} ${user}@${host}

######################################
url="http://localhost:"${test_local_port}"/"
open -a "Google Chrome" $url

