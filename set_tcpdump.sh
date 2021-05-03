#!/bin/bash
#
# SQUAB(Scalable QUagga-based Automated configuration on BGP)
# set_tcpdump.sh
# input: container_name
#

INTERFACE=($(echo $(ip addr | grep inet | grep eth | cut -f 11 -d' ' | tr '\n' ' ')))

for int in ${INTERFACE[@]}
do
	echo "$1 $int" > /home/bgp_tcpdump_$int
	tcpdump -v -i $int port 179 >> /home/bgp_tcpdump_$int &
done
