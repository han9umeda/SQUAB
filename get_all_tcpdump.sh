#!/bin/bash
#
# SQUAB(Scalable QUagga-based Automated configuration on BGP)
# get_all_tcpdump.sh
# input: PROJECT_NAME
#

if [ $# -ne 1 ]
then
	exit 1
fi

PR_NAME=$1

AS_CON_LIST=(`docker ps -a --filter "name=pr_${PR_NAME}_as" --format "{{.Names}}"`)

for con in ${AS_CON_LIST[@]}
do
	echo $con
	docker exec -i $con bash -c "ls /home/* | grep eth | xargs cat"
done
