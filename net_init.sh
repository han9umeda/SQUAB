#!/bin/bash -x
#
# SQUAB(Scalable QUagga-based Automated configuration on BGP)
# net_init.sh
#
PR_NAME=testone
QUAGGA_CONTAINER_IMAGE=quagga_099224
SRX_CONTAINER_IMAGE=srx_511

BNET_ADDRESS_PREFIX=191.168
PNET_ADDRESS_PREFIX=171.17
RNET_ADDRESS_PREFIX=171.16.0

# 設定ファイルの読み込み
echo "Import Config file..."
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

INPUT=("${INPUT[@]:1}") # "Peer_info"行の削除

while [ ${#INPUT[@]} -ne 0 ]
do
	PEER_ARR1+=(${INPUT[0]})
	PEER_ARR2+=(${INPUT[1]})
	INPUT=("${INPUT[@]:2}")
done

# ASを作っていく
echo "Making AS Container..."
i=0
for asn in ${AS_NUMBER[@]}
do
	eval SECF=\$SEC_FLAG_AS$asn
	if [ $SECF -eq 1 ]	# BGPsec(PATHを通しているのでオプションが長い)
	then
		docker run -td --privileged --name pr_${PR_NAME}_as$asn -e PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/NIST-BGP-SRx/local-5.1.1/bin:/home/NIST-BGP-SRx/local-5.1.1/sbin" ${SRX_CONTAINER_IMAGE}
	else			# BGP
		docker run -td --privileged --name pr_${PR_NAME}_as$asn ${QUAGGA_CONTAINER_IMAGE}
	fi
	docker network create --subnet ${BNET_ADDRESS_PREFIX}.$(expr $i + 1).0/24 pr_${PR_NAME}_bnet_as$asn
	docker network connect --ip ${BNET_ADDRESS_PREFIX}.$(expr $i + 1).2 pr_${PR_NAME}_bnet_as$asn pr_${PR_NAME}_as$asn
	eval BNET_ADDRESS_AS$asn=${BNET_ADDRESS_PREFIX}.$(expr $i + 1).2/24
	i=`expr $i + 1`
done

# AS間接続を構成していく
echo "Making Peer connection..."
for i in $(seq 0 $(expr ${#PEER_ARR1[@]} - 1))
do
	PEER1=${PEER_ARR1[i]}
	PEER2=${PEER_ARR2[i]}
	docker network create --subnet ${PNET_ADDRESS_PREFIX}.$(expr $i + 1).0/24 pr_${PR_NAME}_pnet_$(expr $i + 1)
	docker network connect --ip ${PNET_ADDRESS_PREFIX}.$(expr $i + 1).2 pr_${PR_NAME}_pnet_$(expr $i + 1) pr_${PR_NAME}_as${PEER1}
	docker network connect --ip ${PNET_ADDRESS_PREFIX}.$(expr $i + 1).3 pr_${PR_NAME}_pnet_$(expr $i + 1) pr_${PR_NAME}_as${PEER2}
	TMP=($PEER2 "${PNET_ADDRESS_PREFIX}.$(expr $i + 1).3")
	eval PEER_INFO_AS$PEER1+=\(${TMP[@]}\)
	TMP=($PEER1 "${PNET_ADDRESS_PREFIX}.$(expr $i + 1).2")
	eval PEER_INFO_AS$PEER2+=\(${TMP[@]}\)
done

# RPKIを作って、全ASと接続
echo "Setting security system..."
docker run -td --privileged --name pr_${PR_NAME}_rpki -e PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/NIST-BGP-SRx/local-5.1.1/bin:/home/NIST-BGP-SRx/local-5.1.1/sbin" ${SRX_CONTAINER_IMAGE}
docker exec -d pr_${PR_NAME}_rpki mkdir /home/cert
docker network create --subnet ${RNET_ADDRESS_PREFIX}.0/24 pr_${PR_NAME}_rnet
RPKI_ADDRESS=${RNET_ADDRESS_PREFIX}.254
docker network connect --ip ${RPKI_ADDRESS} pr_${PR_NAME}_rnet pr_${PR_NAME}_rpki
i=0
for asn in ${AS_NUMBER[@]}
do
	eval SECF=\$SEC_FLAG_AS$asn
	if [ $SECF -eq 1 ]	# BGPsec
	then
		docker network connect --ip ${RNET_ADDRESS_PREFIX}.$(expr $i + 2) pr_${PR_NAME}_rnet pr_${PR_NAME}_as$asn
		i=`expr $i + 1`
	fi
done

# コンテナ内のconfigファイル生成
echo "Making config file in container..."
as_index=1
for asn in ${AS_NUMBER[@]}
do
	eval SECF=\$SEC_FLAG_AS$asn
	eval BNET=\$BNET_ADDRESS_AS$asn
	eval PEER=\${PEER_INFO_AS$asn[@]}
	if [ $SECF -eq 0 ]	# BGP
	then
		PARAM="$as_index $asn $BNET $PEER"
		docker exec -d pr_${PR_NAME}_as$asn /home/gen_zebra_bgpd_conf.sh $PARAM
	else			# BGPsec
		docker exec -d --privileged pr_${PR_NAME}_as$asn /bin/bash -c "/home/cert_setting.sh $asn"	# 鍵生成と証明書作成
		PARAM="$as_index $asn $BNET $RPKI_ADDRESS $PEER"
		docker exec -d pr_${PR_NAME}_as$asn /home/gen_zebra_bgpd_sec_conf.sh $PARAM
		# 証明書をRPKIへ移動
		docker cp pr_${PR_NAME}_as$asn:/var/lib/bgpsec-keys/router_as$asn.cert /tmp
		docker cp /tmp/router_as$asn.cert pr_${PR_NAME}_rpki:/home/cert
	fi
	as_index=`expr $as_index + 1`
done


# コンテナ内でプロセスの立ち上げ
echo "Starting daemons..."
for asn in ${AS_NUMBER[@]}
do
	docker exec -d --privileged pr_${PR_NAME}_as$asn zebra
	docker exec -d --privileged pr_${PR_NAME}_as$asn bgpd

	eval SECF=\$SEC_FLAG_AS$asn
	if [ $SECF -eq 1 ]	# BGPsec
	then
		docker exec -d --privileged pr_${PR_NAME}_as$asn srx_server
	fi
done
echo "Finished!"
