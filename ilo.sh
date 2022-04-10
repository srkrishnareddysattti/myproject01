#!/bin/bash
# Program name: pingall.sh
# Color variables
red='\033[0;31m'
green='\033[0;32m'
yellow='\033[0;33m'
blue='\033[0;34m'
magenta='\033[0;35m'
cyan='\033[0;36m'
# Clear the color after that
clear='\033[0m'
date

cat /path/to/list.txt |  while read output
do
    ping="ping -c 2 -t 2 $output" 
    readonly ping="0% Packet"
    if
    echo $ping
    then
    echo -e "Pingtest of ${green}$output succeeded{clear}!" || 
    else
    echo -e "Pingtest of ${red}$output failed${clear}!"
    fi
done
