#
# SQUAB(Scalable QUagga-based Automated configuration on BGP)
# squab_init.py
# input: squab_config_file.yml
#
import sys
import os
import re
import yaml
import subprocess
from random import randint
import ipaddress

class AS_generator:
  def __init__(self, number, image, rand_gen):
    self.number = number
    self.image = image
    self.as_network_name = "as_net_" + str(self.number)
    self.as_network_address = rand_gen.get_address()

    self.router_dict = {}

  def make_peer_router_for(self, as_num):

    if not as_num in self.router_dict.keys(): # 対応したルータがなければ、生成する
      self.router_dict[as_num] = Router_generator(self.number, as_num, self.image, self.as_network_name)

    return self.router_dict[as_num]

  def get_router_info(self):

    router_info = {}
    for rou_gen in self.router_dict.values():
      rou_info = rou_gen.get_router_info()
      router_info.update(rou_info)

    return router_info

  def get_quagga_router_list(self):

    quagga_list = []
    for router in self.router_dict.values():
      if router.get_image() == "quagga":
        quagga_list.append(router)

    return quagga_list

  def get_srx_router_list(self):

    srx_list = []
    for router in self.router_dict.values():
      if router.get_image() == "srx":
        srx_list.append(router)

    return srx_list

  def get_router_address_list(self):

    address_list = []
    for rou in self.router_dict.values():
      address_list.append(rou.get_intra_as_address())

    return address_list

  def get_as_network_name(self):
    return self.as_network_name

  def get_router_dict(self):
    return self.router_dict

  def get_as_net_info(self):
    return {self.as_network_name: {"ipam": {"config": [{"subnet": self.as_network_address}]}}}


class Router_generator:
  def __init__(self, on_as, for_as, image, as_network_name):
    self.on_as = on_as
    self.for_as = for_as

    self.image = image

    self.peer_network_name = peer_network_name(on_as, for_as)
    self.as_network_name = as_network_name

    self.router_name = "router_" + str(self.on_as) + "_for_" + str(self.for_as)
    self.opposite_router_name = "router_" + str(self.for_as) + "_for_" + str(self.on_as)

  def get_router_info(self):
    if self.image == "quagga":
      return {self.router_name: {"image": self.image, "tty": "true", "networks": {self.peer_network_name: {}, self.as_network_name: {}}}}
    elif self.image == "srx":
      return {self.router_name: {"image": self.image, "tty": "true", "networks": {self.peer_network_name: {}, self.as_network_name: {}, "rnet": {}}}}

  def get_image(self):
    return self.image

  def get_on_as_num(self):
    return self.on_as

  def get_for_as_num(self):
    return self.for_as

  def get_as_network_name(self):
    return self.as_network_name

  def set_as_network_address(self, ip):
    self.as_network_address = ip

  def get_as_network_address(self):
    return self.as_network_address

  def set_peer_address(self, ip):
    self.peer_address = ip

  def get_peer_address(self):
    return self.peer_address

  def set_peer_address_opposite(self, ip):
    self.peer_address_opposite = ip

  def get_peer_address_opposite(self):
    return self.peer_address_opposite

  def set_intra_as_address(self, ip):
    self.intra_as_address = ip

  def get_intra_as_address(self):
    return self.intra_as_address

  def get_router_name(self):
    return self.router_name

  def get_opposite_router_name(self):
    return self.opposite_router_name


class RPKI_generator:
  def get_rpki_info(self):
    return {"rpki": {"image": "srx", "tty": "true", "networks": {"rnet": {}}}}

  def set_rpki_address(self, ip):
    self.address = ip

  def get_rpki_address(self):
    return self.address


def peer_network_name(peer1, peer2):
  peer_ases = [peer1, peer2]
  peer_ases.sort() # 引数として与えられるAS番号の順番に依存しないようにするため

  return "pnet_" + str(peer_ases[0]) + "and" + str(peer_ases[1])

class Random_network_address_generator():
  def __init__(self):
    name = subprocess.run(["docker", "network", "ls", "--filter", "driver=bridge", "--format='{{.Name}}'"], stdout=subprocess.PIPE)
    name = name.stdout.decode('utf-8').replace("'", "").split('\n')[:-1]
    self.used_address_list = []
    for n in name:
      address = subprocess.run(["docker", "network", "inspect", n, "--format='{{.IPAM.Config}}'"], stdout=subprocess.PIPE)
      address = address.stdout.decode('utf-8').split()[0][3:]
      self.used_address_list.append(ipaddress.ip_network(address))

  def get_address(self):
    while True:
      address = ipaddress.ip_network(self.gen_address())
      can_use_flag = True
      for used in self.used_address_list:
        if address.subnet_of(used) or address.supernet_of(used):
          can_use_flag = False
          break
      if can_use_flag == True:
        self.used_address_list.append(address)
        return address.exploded

  def gen_address(self):
    address = ["172"]
    address.append(str(randint(16, 31)))
    address.append(str(randint(0, 255)))
    address.append("0/24")
    return '.'.join(address)

###
### MAIN PROGRAM
###

args = sys.argv

match = re.search("\.yml$|\.yaml$", args[1])
if match == None:
  print("Error: invalid file name. (.yml or .yaml)", file=sys.stderr)
  sys.exit(1)

with open(args[1]) as file:
  config = yaml.safe_load(file)

for im in config["AS_Setting"].values():
  if not (im["image"] == "quagga" or im["image"] == "srx"):
    print("Error: image" + im["image"] + "is NOT supported.", file=sys.stderr)
    sys.exit(1)

peer_as = []
for peer in config["Peer_info"]:
  peer_as.extend(peer)
for written_as in set(peer_as):
  if not written_as in config["AS_Setting"].keys():
    print("Error: AS " + written_as + "is NOT defined.", file=sys.stderr)
    sys.exit(1)

filename = os.path.basename(args[1])
match = re.search("\.yml$|\.yaml$", filename)

project_name = filename[:match.start()]
additional_name = ""
i = 1
while True:
  if os.path.isdir("./.work_dir/" + project_name + additional_name) == False:
    project_name = project_name + additional_name
    break
  additional_name = "_" + str(i)
  i += 1

print("Project name: " + project_name)

random_network_address_generator = Random_network_address_generator()

as_generator_dict = {}
for as_num in config["AS_Setting"].keys():
  as_generator_dict[as_num] = AS_generator(as_num, config["AS_Setting"][as_num]["image"], random_network_address_generator)

peer_network_name_list = []
for peer in config["Peer_info"]:
  as_generator_dict[peer[0]].make_peer_router_for(peer[1])
  as_generator_dict[peer[1]].make_peer_router_for(peer[0])
  peer_network_name_list.append(peer_network_name(peer[0], peer[1]))

rpki_generator = RPKI_generator()

if os.path.isdir("./.work_dir/" + project_name) == False:
  print("Making working directory in ./.work_dir...")
  subprocess.call(["mkdir", "./.work_dir/" + project_name])

compose_file_path = './.work_dir/' + project_name + '/docker-compose.yml'

print("Making docker-compose.yml file...")

compose_head = {'version': '3'}

containers_info = {}
for as_gen in as_generator_dict.values():
  containers_info.update(as_gen.get_router_info())

containers_info.update(rpki_generator.get_rpki_info())

compose_services = {'services': containers_info}

networks_info = {}
for as_gen in as_generator_dict.values():
  networks_info.update(as_gen.get_as_net_info())
for name in peer_network_name_list:
  networks_info.update({name: {"ipam": {"config": [{"subnet": random_network_address_generator.get_address()}]}}})
networks_info.update({"rnet": {}})
compose_networks = {'networks': networks_info}

with open(compose_file_path, 'w') as f:
  print(yaml.dump(compose_head), file=f)
with open(compose_file_path, 'a') as f:
  print(yaml.dump(compose_services), file=f)
  print(yaml.dump(compose_networks), file=f)

print("Running docker-compose...")
subprocess.call(["docker-compose", "-f", compose_file_path, "up", "-d"])

print("Collecting assigned IP address...")

as_network_ip_dict = {}
intra_as_ip_dict = {}
for as_gen in as_generator_dict.values():
  cmd = "docker network inspect " + project_name + "_" + as_gen.get_as_network_name()
  ret_val = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
  net_info = yaml.safe_load(ret_val.stdout)

  # collecting as network address
  as_network_ip_dict.update({net_info[0]["Name"]: net_info[0]["IPAM"]["Config"][0]["Subnet"]})

  # collecting router intra AS IP address
  for con in net_info[0]["Containers"].values():
    intra_as_ip_dict.update({con["Name"]: con["IPv4Address"].split("/")[0]})

print("Assigned AS network address")
print(as_network_ip_dict)

# collecting router peer network IP address
peer_network_ip_dict = {}
for pnet_name in peer_network_name_list:
  cmd = "docker network inspect " + project_name + "_" + pnet_name
  ret_val = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
  net_info = yaml.safe_load(ret_val.stdout)

  for con in net_info[0]["Containers"].values():
    peer_network_ip_dict.update({con["Name"]: con["IPv4Address"].split("/")[0]})
print("Assigned Peer IP address")
print(peer_network_ip_dict)

routers_list = []
for as_gen in as_generator_dict.values():
  routers_list.extend(as_gen.get_router_dict().values())

for rou_gen in routers_list:
  rou_gen.set_peer_address(peer_network_ip_dict[project_name + "_" + rou_gen.get_router_name() + "_1"])
  rou_gen.set_peer_address_opposite(peer_network_ip_dict[project_name + "_" + rou_gen.get_opposite_router_name() + "_1"])

# collecting RPKI IP address
cmd = "docker network inspect " + project_name + "_rnet"
ret_val = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
rnet_info = yaml.safe_load(ret_val.stdout)
for con in rnet_info[0]["Containers"].values():
  if con["Name"] == project_name + "_rpki_1":
    rpki_generator.set_rpki_address(con["IPv4Address"].split("/")[0])
    break
print("Assigned RPKI IP address")
print(rpki_generator.get_rpki_address())

for rou_gen in routers_list:
  rou_gen.set_as_network_address(as_network_ip_dict[project_name + "_" + rou_gen.get_as_network_name()])
  rou_gen.set_intra_as_address(intra_as_ip_dict[project_name + "_" + rou_gen.get_router_name() + "_1"])

print("Making config file in container...")
quagga_list = []
for as_gen in as_generator_dict.values():
  quagga_list.extend(as_gen.get_quagga_router_list())

srx_list = []
for as_gen in as_generator_dict.values():
  srx_list.extend(as_gen.get_srx_router_list())

router_index = 1 # bgp router-id を一意に振るために利用
for quagga in quagga_list:
  rouname = project_name + "_" + quagga.get_router_name() + "_1"
  if len(as_generator_dict[quagga.get_on_as_num()].get_router_address_list()) == 1: # There is one router in the AS.
    neighbor_intra_router_address = ""
  else: # There is some routers in the AS.
    neighbor_intra_router_address = as_generator_dict[quagga.get_on_as_num()].get_router_address_list()
    neighbor_intra_router_address.remove(quagga.get_intra_as_address())
    neighbor_intra_router_address = ' '.join(neighbor_intra_router_address)
  subprocess.call(["docker", "exec", "-d", rouname, "/home/gen_zebra_bgpd_conf.sh", str(router_index), str(quagga.get_on_as_num()), quagga.get_as_network_address(), str(quagga.get_for_as_num()), quagga.get_peer_address_opposite(), neighbor_intra_router_address])
  router_index += 1

subprocess.call(["docker", "exec", "-d", project_name + "_rpki_1", "mkdir", "/home/cert"]) # for srx ruoter certificate
for srx in srx_list:
  rouname = project_name + "_" + srx.get_router_name() + "_1"
  subprocess.call(["docker", "exec", "-d", rouname, "/home/cert_setting.sh", rouname])
  subprocess.call(["docker", "cp", rouname + ":/var/lib/bgpsec-keys/" + rouname + ".cert", "/tmp"])
  subprocess.call(["docker", "cp", "/tmp/" + rouname + ".cert", project_name + "_rpki_1:/home/cert/"])
  subprocess.call(["docker", "exec", "-d", rouname, "/home/gen_zebra_bgpd_sec_conf.sh", str(router_index), str(srx.get_on_as_num()), srx.get_as_network_address(), rpki_generator.get_rpki_address(), str(srx.get_for_as_num()), str(srx.get_peer_address_opposite()), rouname])
  router_index += 1

print("Starting daemons...")
for quagga in quagga_list:
  rouname = project_name + "_" + quagga.get_router_name() + "_1"
  subprocess.call(["docker", "exec", "-d", "--privileged", rouname, "zebra"])
  subprocess.call(["docker", "exec", "-d", "--privileged", rouname, "bgpd"])

for srx in srx_list:
  rouname = project_name + "_" + srx.get_router_name() + "_1"
  subprocess.call(["docker", "exec", "-d", "--privileged", rouname, "srx_server"])
  subprocess.call(["docker", "exec", "-d", "--privileged", rouname, "zebra"])
  subprocess.call(["docker", "exec", "-d", "--privileged", rouname, "bgpd"])

print("Finished!")
