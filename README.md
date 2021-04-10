# SQUAB(Scalable QUagga-based Automated configuration on Bgp) README

## What is SQUAB?

SQUAB is an experiment tool to set up networks by BGP easily on Docker platform.

## How to use.

### initial setting(execute only once)

Setting up Docker and Python3 environment on your computer.

SQUAB uses pyyaml, so you should install pyyaml(for example `$ pip install pyyaml`).

Building container images.
`$ docker build -t quagga -f Quaggafile .`
`$ docker build -t srx -f SRxfile .`

(You must define image names "quagga" and "srx"! If you define other name, it won't execute correctly.)

### Setting up environment

`$ python squab_init.py [config file name]`

SQUAB configuration filename extension must ".yml" or ".yaml".
The place is "don't care".
Sample SQUAB configuration files exist in config directory.
Filename removed extension is used as project name.(filename: example.yml -> project name: example)

### Check the project list of now executing

`$ ./squab_pr_list.sh`

### Take routing infomation of routers.

If you want to get all routers on a project, you can use this script.

`$ ./get_all_routing_table.sh [project name]`

Each router is composed by container, so you can use docker command for each.

### Remove project

`$ ./squab_rm.sh [project name]`

## Sub scripts(except main programs)

### gen\_zebra\_bgp\_conf.sh

Generating zebra.conf and bgpd.conf in quagga container image.

### gen\_zebra\_bgp\_sec\_conf.sh

Generating zebra.conf, bgpd.conf and srx\_server.conf in srx container image.

### cert\_setting.sh

Generating key and the certificate in srx container image.

### srx\_install.sh

When building srx image, it downloads BGP-SRx source and build them.

