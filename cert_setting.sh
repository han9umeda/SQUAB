#!/bin/bash
#
# SQUAB(Scalable QUagga-based Automated configuration on BGP)
# cert_setting.sh
# input: ROUTER_NAME
#

ROUTER_NAME=$1

KEY_REPO="/var/lib/bgpsec-keys"

cd $KEY_REPO
qsrx-make-key $ROUTER_NAME
qsrx-make-cert $ROUTER_NAME
qsrx-publish $ROUTER_NAME
cp ski-list.txt priv-ski-list.txt
