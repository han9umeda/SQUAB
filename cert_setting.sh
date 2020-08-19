#!/bin/bash
#
# SQUAB(Scalable QUagga-based Automated configuration on BGP)
# cert_setting.sh
#

ASN=$1

KEY_REPO="/var/lib/bgpsec-keys"

cd $KEY_REPO
qsrx-make-key router_as$ASN
qsrx-make-cert router_as$ASN
qsrx-publish router_as$ASN
cp ski-list.txt priv-ski-list.txt
