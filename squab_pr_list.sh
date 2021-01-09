#!/bin/bash
#
# SQUAB(Scalable QUagga-based Automated configuration on BGP)
# squab_pr_list.sh
#

cd .work_dir
ls | sed 's/ /\n/g'
