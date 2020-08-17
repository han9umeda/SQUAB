#!/bin/bash
#
# net_init.sh
#
PR_NAME=tmp
QUAGGA_CONTAINER_IMAGE=quagga_124
SRX_CONTAINER_IMAGE=srx_511

BNET_ADDRESS_PREFIX=192.168
PNET_ADDRESS_PREFIX=172.17
RNET_ADDRESS_PREFIX=172.16.0

# 設定ファイルの読み込み

while read -r line
do
	INPUT+=($line)
done < ${1}

if [ ${INPUT[0]} != AS_Setting ]
then
	echo "Syntax error: Keyword \"AS_Setting\" is NOT exist." 1>&2
	exit 1
fi
INPUT=("${INPUT[@]:1}")

while [ ${INPUT[0]} != Peer_info ]
do
	AS_NUMBER+=(${INPUT[0]})
	SECF=${INPUT[1]}
	if [ $SECF -eq 0 -o $SECF -eq 1 ]
	then
		eval SEC_FLAG_AS${INPUT[0]}=$SECF
	else
		echo "Syntax error: SEC Flag is 1 or 0." 1>&2
		exit 1
	fi
	INPUT=("${INPUT[@]:2}")
done

#TODO: Peer_info以下の読み取り
#TODO: 存在するASであるか確認、一意のPeerであるか確認(重複は削除？)、同じAS同士でないか確認

echo "Including Config file: succeeded"

# ASを作っていく
i=0
for asn in ${AS_NUMBER[@]}
do
	eval SECF=\$SEC_FLAG_AS$asn
	if [ $SECF -eq 1 ]	# BGPsec
	then
		echo "docker run -d --name pr_${PR_NAME}_as$asn ${SRX_CONTAINER_IMAGE}"
	else			# BGP
		echo "docker run -d --name pr_${PR_NAME}_as$asn ${QUAGGA_CONTAINER_IMAGE}"
	fi
	echo "docker network create --subnet ${BNET_ADDRESS_PREFIX}.$(expr $i + 1).0/24 pr_${PR_NAME}_bnet_as$asn"
	echo "docker network connect --ip ${BNET_ADDRESS_PREFIX}.$(expr $i + 1).2/24 pr_${PR_NAME}_bnet_as$asn pr_${PR_NAME}_as$asn"
	eval BNET_ADDRESS_AS$asn=${BNET_ADDRESS_PREFIX}.$(expr $i + 1).2/24
	i=`expr $i + 1`
done

for as in ${AS_NUMBER[@]}
do
	eval "echo \$BNET_ADDRESS_AS$as"
done

# AS間接続を構成していく

PEER_ARR1=(72 345 72)
PEER_ARR2=(6591 17 345)

for i in $(seq 0 $(expr ${#PEER_ARR1[@]} - 1))
do
	PEER1=${PEER_ARR1[i]}
	PEER2=${PEER_ARR2[i]}
	echo "docker network create --subnet ${PNET_ADDRESS_PREFIX}.$(expr $i + 1).0/24 pr_${PR_NAME}_pnet_$(expr $i + 1)"
	echo "docker network connect --ip ${PNET_ADDRESS_PREFIX}.$(expr $i + 1).2/24 pr_${PR_NAME}_pnet_$(expr $i + 1) pr_${PR_NAME}_as${PEER1}"
	echo "docker network connect --ip ${PNET_ADDRESS_PREFIX}.$(expr $i + 1).3/24 pr_${PR_NAME}_pnet_$(expr $i + 1) pr_${PR_NAME}_as${PEER2}"
	TMP=($PEER2 "${PNET_ADDRESS_PREFIX}.$(expr $i + 1).2/24")
	eval PEER_INFO_AS$PEER1+=\(${TMP[@]}\)
	TMP=($PEER1 "${PNET_ADDRESS_PREFIX}.$(expr $i + 1).3/24")
	eval PEER_INFO_AS$PEER2+=\(${TMP[@]}\)
	# eval "echo \${PEER_INFO_AS$PEER1[@]}"
	# eval "echo \${PEER_INFO_AS$PEER2[@]}"
done

# RPKIを作って、全ASと接続
echo "docker run -d --name pr_${PR_NAME}_rpki ${SRX_CONTAINER_IMAGE}"
echo "docker network create --subnet ${RNET_ADDRESS_PREFIX}.0/24 pr_${PR_NAME}_rnet"
RPKI_ADDRESS=${RNET_ADDRESS_PREFIX}.254
echo "docker network connect --ip ${RPKI_ADDRESS}/24 pr_${PR_NAME}_rnet pr_${PR_NAME}_rpki"
i=0
for asn in ${AS_NUMBER[@]}
do
	eval SECF=\$SEC_FLAG_AS$asn
	if [ $SECF -eq 1 ]	# BGPsec
	then
		echo "docker network connect --ip ${RNET_ADDRESS_PREFIX}.$(expr $i + 2)/24 pr_${PR_NAME}_rnet pr_${PR_NAME}_as$asn"
		i=`expr $i + 1`
	fi
done

# コンテナ内のconfigファイル生成
as_index=1
for asn in ${AS_NUMBER[@]}
do
	eval SECF=\$SEC_FLAG_AS$asn
	if [ $SECF -eq 0 ]	# BGP
	then
		eval BNET=\$BNET_ADDRESS_AS$asn
		eval PEER=\${PEER_INFO_AS$asn[@]}
		PARAM="$as_index $asn $BNET $PEER"
		echo "docker exec -d pr_${PR_NAME}_as$asn /home/gen_zebra_bgpd_conf.sh $PARAM"
	fi
	as_index=`expr $as_index + 1`
done
# ファイル生成過程で鍵の生成も行う

# 証明書をrpkiへ移動

# コンテナ内でプロセスの立ち上げ

