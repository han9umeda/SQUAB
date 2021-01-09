#!/bin/bash
#
# SQUAB(Scalable QUagga-based Automated configuration on BGP)
# get_all_routing_table.sh
# input: PROJECT_NAME
#

if [ $# -ne 1 ]
then
	exit 1
fi

PR_NAME=$1

AS_CON_LIST=(`docker ps -a --filter "name=${PR_NAME}_router" --format "{{.Names}}"`)

for con in ${AS_CON_LIST[@]}
do
	echo $con
	docker exec -it $con /home/get_rtable.sh
done
