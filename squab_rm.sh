#!/bin/bash

PROJECT_NAME=$1
cd .work_dir

if [ ! -d $PROJECT_NAME ]
then
	echo "project: $PROJECT_NAME is NOT exist." >&2
	exit 1
fi

cd $PROJECT_NAME
docker-compose down
cd ..
rm -r $PROJECT_NAME
