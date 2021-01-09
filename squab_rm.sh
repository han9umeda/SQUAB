#!/bin/bash
#
# SQUAB(Scalable QUagga-based Automated configuration on BGP)
# squab_rm.sh
# input: PR_NAME
#

PR_NAME=$1
cd .work_dir

if [ ! -d $PR_NAME ]
then
	echo "project: $PR_NAME is NOT exist." >&2
	exit 1
fi

cd $PR_NAME
docker-compose down
cd ..
rm -r $PR_NAME
