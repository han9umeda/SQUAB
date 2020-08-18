#!/bin/bash +
#
#
#

PR_NAME=$1

CON_LIST=(`docker ps --filter "name=pr_$PR_NAME" --format "{{.Names}}"`)
for con in ${CON_LIST[@]}
do
	docker kill $con
	docker rm $con
done

NET_LIST=(`docker network ls --filter="name=pr_$PR_NAME" --format {{.Name}}`)
for net in ${NET_LIST[@]}
do
	docker network rm $net
done
