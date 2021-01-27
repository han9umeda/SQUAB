# SQUAB(Scalable QUagga-based Automated configuration on Bgp) README

## SQUABとは

Dockerプラットフォーム上でBGPで通信が行われるネットワークを簡単に構築することができる実験ツールです。

## 実行方法

### 初期設定(初めて利用するときのみ実行)

DockerとPython3系の環境を構築する
pyyamlを入れる
コンテナイメージをビルドする。

`$ docker build -t quagga -f Quaggafile .`
`$ docker build -t srx -f SRxfile .`

(イメージ名をquaggaとsrxにしないとうまく動作しません。)

### 実験環境の立ち上げ

`$ python squab_init.py [config file name]`

configファイルの名前は拡張子が.ymlか.yamlである必要があります。
場所はどこでも構いません。
サンプルファイルがconfigディレクトリに入っています。
ファイル名から拡張子を取り除いたものがプロジェクト名として設定されます。

### 今動いているプロジェクト一覧を表示

`$ ./squab_pr_list.sh`

### ルータから情報を取り出す

環境上に存在する全てのルータから情報を取り出す時

`$ ./get_all_routing_table.sh [project name]`

それぞれのルータはコンテナに入っているため、dockerのコマンドを用いて、内部のルータを直接操作することも可能

### 実験環境の撤去

`$ ./squab_rm.sh [project name]`

## メインプログラム以外の細かなスクリプトについて

### gen\_zebra\_bgp\_conf.sh

quaggaイメージ内でzebra.confとbgpd.confを生成する

### gen\_zebra\_bgp\_sec\_conf.sh

srxイメージ内でzebra.confとbgpd.conf、srx_server.confを生成する

### cert\_setting.sh

srxイメージ内で鍵生成と証明書発行を行う

### srx\_install.sh

srxイメージbuild時にBGP-SRxのダウンロードとbuildを行う
