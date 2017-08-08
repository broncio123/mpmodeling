#!/bin/bash

# Module needed

valid_processes=(embedding solvation equilibration production analysis)

array_contains() { 
    local array="$1[@]"
    local seeking=$2
    local in=1
    for element in "${!array}"; do
        if [[ $element == $seeking ]]; then
            in=0
            break
        fi
    done
    return $in
}


# Identify requested processes
if [[ ($1 == "h") || ($1 == "help") ]]; then
	# Print some text displaying options of interactio with script
	echo "Edit some help here!"
else 

	# Identify how many processes are requested	
	n=$(echo $1 | awk -F':' '{print NF}')
	if   (($n==0)); then
		printf "Please, request a valid process. Check 1st input argument or if in doubt, type 'h' or 'help'\n"
	elif (($n==1)); then
		requested=$1
		valid=$(array_contains valid_processes $requested && echo yes || echo no)
		if [[ ($valid == "no") ]]; then 
			printf "No valid process requested. Check 1st input argument or if in doubt, type 'h' or 'help'\n"
		fi
	else
		read initial final<<<$(echo $1|awk -F':' '{print $1, $2}')
		valid0=$(array_contains valid_processes $initial && echo yes || echo no)
		valid1=$(array_contains valid_processes $final && echo yes || echo no)
		if [[ ($valid0 == "no") || ($valid1 == "no") ]]; then 
			printf "One process requested is not valid. Check 1st input argument or if in doubt, type 'h' or 'help'\n"
		fi
	fi
fi

mode=$2
if [[ ($mode == "standard") ]]; then
	echo "Do something"	
elif [[ ($mode == "file") ]]; then
	# Not ready yet, work on this later! 
	file=$3
	if [ -f "$file" ]; then
		printf "$file found.\n"
	else
		printf "$file not found.\n"
	fi
elif [[ ($mode == "interactive") ]]; then
	# Not ready yet, work on this later!
	echo "Do something interactive! :D"
else
	printf "Define a valid mode execution. Check 2nd input argument or if in doubt, type 'h' or 'help'\n"
fi




