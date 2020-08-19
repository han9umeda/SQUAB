#!/bin/bash
#
#
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
	docker exec -it $con /home/get_rtable.sh
done
