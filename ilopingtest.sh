# check the ping to the servers 
#! /bin/bash

for s in `cat hosts_list` 
do 
echo "----ping test for $s---"
 
echo "##* HOST: $s - "`host $s | cut -d " " -f5`" *##" 

echo "" 

ping -c2 -t 1 $s 
 
echo "-----completed---------" 
echo ""
done
