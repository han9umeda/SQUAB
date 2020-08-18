#!/bin/bash
#
# SQUAB(Scalable QUagga-based Automated configuration on BGP)
# gen_zebra_bgpd_conf.sh
# input: AS_INDEX ASN BNET PEER_INFO
#

ZEBRA_CONF_FILE="/etc/quagga/zebra.conf"
BGPD_CONF_FILE="/etc/quagga/bgpd.conf"

INTERFACE=($(echo $(ip addr | grep inet | grep eth | cut -f 11 -d' ' | tr '\n' ' ')))
IP_ADDR=($(echo $(ip addr | grep inet | grep eth | cut -f 6 -d' ' | tr '\n' ' ')))

echo "!" > $ZEBRA_CONF_FILE
echo "! zebra.conf" >> $ZEBRA_CONF_FILE
echo "! generated by gen_zebra_bgpd_conf.sh (SQUAB) `date`" >> $ZEBRA_CONF_FILE
echo "!" >> $ZEBRA_CONF_FILE

echo "hostname Router" >> $ZEBRA_CONF_FILE
echo "password zebra" >> $ZEBRA_CONF_FILE
echo "!" >> $ZEBRA_CONF_FILE
echo "! Interface's description." >> $ZEBRA_CONF_FILE
echo "!" >> $ZEBRA_CONF_FILE

for i in $(seq 0 $(expr ${#INTERFACE[@]} - 1))
do
	echo "interface ${INTERFACE[i]}" >> $ZEBRA_CONF_FILE
	echo " ip address ${IP_ADDR[i]}" >> $ZEBRA_CONF_FILE
	echo " ipv6 nd suppress-ra" >> $ZEBRA_CONF_FILE
	echo "!" >> $ZEBRA_CONF_FILE
done
cat $ZEBRA_CONF_FILE

AS_INDEX=$1
ASN=$2
BNET=$3
PEER=(`echo $@ | cut -f 4- -d' '`)

echo "!" > $BGPD_CONF_FILE
echo "! bgpd.conf" >> $BGPD_CONF_FILE
echo "! generated by gen_zebra_bgpd_conf.sh (SQUAB) `date`" >> $BGPD_CONF_FILE
echo "!" >> $BGPD_CONF_FILE

echo "hostname bgpd" >> $BGPD_CONF_FILE
echo "password  zebra" >> $BGPD_CONF_FILE
echo "log stdout" >> $BGPD_CONF_FILE
echo "!" >> $BGPD_CONF_FILE

echo "router bgp $ASN" >> $BGPD_CONF_FILE
echo " bgp router-id 10.10.10.$AS_INDEX" >> $BGPD_CONF_FILE
echo " network $BNET" >> $BGPD_CONF_FILE
for i in $(seq 0 2 $(expr ${#PEER[@]} - 1))
do
	echo " neighbor ${PEER[$(expr $i + 1)]} remote-as ${PEER[$i]}" >> $BGPD_CONF_FILE
	echo " neighbor ${PEER[$(expr $i + 1)]} next-hop-self" >> $BGPD_CONF_FILE
done
echo "!" >> $BGPD_CONF_FILE

cat $BGPD_CONF_FILE
