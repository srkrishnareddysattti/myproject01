#!/bin/bash

echo " HTTPD is going to download"

yum install -y httpd*

echo "Httpd downloaded successfully"

date=$(date)

uptime=$(uptime)

echo " current date is $date"
echo "server uptime is $ uptime"

which httpd

systemctl status httpd
    or
service httpd status

systemctl start httpd

echo " Httpd curren status is"
systemctl status httpd
use -l




	
	
	
