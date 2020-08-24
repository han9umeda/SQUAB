# SQUAB README

## 実行方法

 - 実行の準備(初回のみ)

`$ docker load < quagga_099224.tar`
`$ docker load < srx_511.tar`

 - ネットワークの自動構築

`$ ./net_init.sh <configファイル>`

(configファイルのサンプルはconfigディレクトリ内にあります)

 - 構築したネットワークの削除
`$ ./rm_project.sh <プロジェクト名>`

(現在、プロジェクト名はnet_init.shにおいて、testでハードコーディングされています)

## 各ファイルの説明

 - init_net.sh

走らせることで、コンテナを立てて、ネットワークも構成する。入力としてconfigファイルを与えて実行。RPKIの設定は自動化できていないので、コンテナに入って手作業での処理が必要。

 - gen_zebra_bgpd_conf.sh

quagga_099224において、zebra.confファイルとbgpd.confファイルを生成するスクリプト。

 - gen_zebra_bgpd_sec_conf.sh

srx_511において、zebra.confファイルとbgpd.confファイル、srx_server.confを生成するスクリプト。

 - cert_setting.sh

鍵を生成して、証明書を発行し、publishを行うスクリプト。

 - quagga_099224

quagga, expectコマンドをインストールして、gen_zebra_bgpd_conf.sh, get_rtable.shを/homeに設置したコンテナイメージ。

 - srx_511

NIST-BGP-SRxをgit cloneして、各種buildツールをインストールしてbuild、そのPATHを通す。qsrx-make-certが求める/etc/qsrx-router-key.cnfのファイルをコピーして設置。cert_setting.shとgen_zebra_bgpd_sec_conf.shを/homeに設置したコンテナイメージ。
cp srxcryptoapi.conf.sample srxcryptoapi.confも行う。
expectコマンドもインストール。get_rtable.shを/homeに設置。

 - configフォルダ

net_init.shを実行する時に入力として与えるファイルのサンプル集
