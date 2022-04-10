#!/bin/bash 
###############################################################################
#Script Name    : hostip.sh                       
#Description    : execute multiple commands on multiple servers                                                                     
#Author         : Satti Siva Ramakrishnareddy       
#Email          : sivaramakrishnareddy.satti@lumen.com
################################################################################

192.168.230.8 -ssh -P 22 -l root
echo
# show system uptime
uptime
echo
# show who is logged on and what they are doing
who
echo
