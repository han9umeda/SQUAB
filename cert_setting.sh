#!/bin/bash
#
# SQUAB(Scalable QUagga-based Automated configuration on BGP)
# cert_setting.sh
# input: ROUTER_NAME ASN
#

ROUTER_NAME=$1
ASN=$2

KEY_REPO="/var/lib/bgpsec-keys"

cd $KEY_REPO
qsrx-make-key $ROUTER_NAME
sed -e "s/{QSRX_ASN}/$ASN/g" /NIST-BGP-SRx-master/srx-crypto-api/tools/qsrx-router-key.conf > qsrx-router-key.conf
qsrx-make-cert --conf . $ROUTER_NAME
qsrx-publish $ROUTER_NAME
cp ski-list.txt priv-ski-list.txt
