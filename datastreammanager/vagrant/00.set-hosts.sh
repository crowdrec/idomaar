#!/bin/bash
## THIS IS TO SET HOSTNAME FOR VIRTUALBOX MACHINES
## ASSUMPTION IS THAT A VB MACHINE HAS MORE THAN ONE ETH INTERFACES

ifconfig eth1
if [ $? -eq 0 ]; then
   echo "$1 vagrant-ubuntu-trusty-64" >> /etc/hosts
fi

exit 0