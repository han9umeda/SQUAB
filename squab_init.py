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

class AS_generator:
  def __init__(self, number, flag, address_database):
    self.number = number
    self.flag = flag
    self.address_database = address_database
    self.address = address_database.get_as_net_address(self)
    self.as_network_name = "as_net_" + str(self.number)

    self.router_dict = {}

  def make_peer_router_for(self, as_num, address_database, peer_address_flag):

    if not as_num in self.router_dict.keys(): # 対応したルータがなければ、生成する
      self.router_dict[as_num] = Router_generator(self.number, as_num, address_database, peer_address_flag, self.flag, self.as_network_name)

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
    return {self.as_network_name: {}}


class Router_generator:
  def __init__(self, on_as, for_as, address_database, peer_address_flag, flag, as_network_name):
    self.on_as = on_as
    self.for_as = for_as
    self.address_database = address_database
    self.peer_address = address_database.get_peer_address(on_as, for_as, peer_address_flag)
    if peer_address_flag == "SMALLER":
      self.peer_address_opposite = address_database.get_peer_address(on_as, for_as, "BIGGER")
    elif peer_address_flag == "BIGGER":
      self.peer_address_opposite = address_database.get_peer_address(on_as, for_as, "SMALLER")

    peer_ases = [on_as, for_as]
    peer_ases.sort() # 引数として与えられるAS番号の順番に依存しないようにするため
    self.network_name = "pnet_" + str(peer_ases[0]) + "and" + str(peer_ases[1])
    self.as_network_name = as_network_name

    self.router_name = "router_" + str(self.on_as) + "_for_" + str(self.for_as)

    if flag == 0:
      self.image = "quagga"
    elif flag == 1:
      self.image = "srx"
      self.rnet_address = address_database.get_rnet_address_for_router(self)
    else:
      raise ValueError("flag incorrectly")

  def get_router_info(self):
    if self.image == "quagga":
      return {self.router_name: {"image": self.image, "tty": "true", "networks": {self.network_name: {"ipv4_address": self.peer_address}, self.as_network_name: {}}}}
    elif self.image == "srx":
      return {self.router_name: {"image": self.image, "tty": "true", "networks": {self.network_name: {"ipv4_address": self.peer_address}, self.as_network_name: {"ipv4_address": self.intra_as_address}, "rnet": {"ipv4_address": self.rnet_address}}}}

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

  def get_peer_address(self):
    return self.peer_address

  def get_peer_address_opposite(self):
    return self.peer_address_opposite

  def set_intra_as_address(self, ip):
    self.intra_as_address = ip

  def get_intra_as_address(self):
    return self.intra_as_address

  def get_router_name(self):
    return self.router_name


class RPKI_generator:
  def __init__(self, rpki_net_address):
    self.address = rpki_net_address[:-5] + ".254"

  def get_rpki_info(self):
    return {"rpki": {"image": "srx", "tty": "true", "networks": {"rnet": {"ipv4_address": self.address}}}}

  def get_rpki_address(self):
    return self.address

class Address_detabase:
  def __init__(self):
    self.AS_NET_ADDRESS_PREFIX = "191.168."
    self.PEER_ADDRESS_PREFIX = "171.17."
    self.RPKI_NET_ADDRESS_PREFIX = "171.16.0."

    self.as_net_i = 2
    self.peer_address_i = 2
    self.rnet_address_i = 2

    self.as_net_dict = {}
    self.peer_address_dict = {}
    self.rnet_address_dict = {}

  def get_as_net_address(self, as_gen):

    if not as_gen in self.as_net_dict.keys(): # ASに対応したアドレスがなければ、生成する
      self.as_net_dict[as_gen] = self.AS_NET_ADDRESS_PREFIX + str(self.as_net_i) + ".0/24"
      self.as_net_i += 1

    return self.as_net_dict[as_gen]

  def get_peer_address(self, peer1, peer2, mode):

    peer_ases = [peer1, peer2]
    peer_ases.sort() # 引数として与えられるAS番号の順番に依存しないようにするため

    peer_key = str(peer_ases[0]) + "and" + str(peer_ases[1])

    if not peer_key in self.peer_address_dict.keys():
      self.peer_address_dict[peer_key] = self.PEER_ADDRESS_PREFIX + str(self.peer_address_i) + ".0/24"
      self.peer_address_i += 1

    if mode == "NET":
      return self.peer_address_dict[peer_key]
    elif mode == "SMALLER":
      return self.peer_address_dict[peer_key][:-5] + ".2"
    elif mode == "BIGGER":
      return self.peer_address_dict[peer_key][:-5] + ".3"
    else:
      raise ValueError("mode incorrectly!")

  def get_pnet_info(self):

    pnet_info = {}
    for peer_info in self.peer_address_dict.keys():
      pnet_info["pnet_" + peer_info] = {"ipam": {"config": [{"subnet": self.peer_address_dict[peer_info]}]}}

    return pnet_info

  def get_rnet_address(self):

    return self.RPKI_NET_ADDRESS_PREFIX + "0/24"

  def get_rnet_address_for_router(self, router_gen):

    if not router_gen in self.rnet_address_dict.keys(): # ルータに対応したアドレスがなければ、生成する
      self.rnet_address_dict[router_gen] = self.RPKI_NET_ADDRESS_PREFIX + str(self.rnet_address_i)
      self.rnet_address_i += 1

    return self.rnet_address_dict[router_gen]

  def get_rnet_info(self):
    return {"rnet": {"ipam": {"config": [{"subnet": self.get_rnet_address()}]}}}


def peer_network_name(peer1, peer2):
  peer_ases = [peer1, peer2]
  peer_ases.sort() # 引数として与えられるAS番号の順番に依存しないようにするため

  return "pnet_" + str(peer_ases[0]) + "and" + str(peer_ases[1])

###
### MAIN PROGRAM
###

args = sys.argv

match = re.search("\.yml$|\.yaml$", args[1])
if match == None:
  print("invalid file name. (.yml or .yaml)")
  sys.exit(1)
filename = os.path.basename(args[1])

match = re.search("\.yml$|\.yaml$", filename)

project_name = filename[:match.start()]
print("Project name: " + project_name)

with open(args[1]) as file:
  config = yaml.safe_load(file)

address_database = Address_detabase()

as_generator_dict = {}

for as_num in config["AS_Setting"].keys():
  as_generator_dict[as_num] = AS_generator(as_num, config["AS_Setting"][as_num]["flag"], address_database)

for peer in config["Peer_info"]:
  as_generator_dict[peer[0]].make_peer_router_for(peer[1], address_database, "SMALLER")
  as_generator_dict[peer[1]].make_peer_router_for(peer[0], address_database, "BIGGER")

rpki_generator = RPKI_generator(address_database.get_rnet_address())

if os.path.isdir("./work_dir/" + project_name) == False:
  print("Making working directory in ./work_dir...")
  subprocess.call(["mkdir", "./work_dir/" + project_name])

compose_file_path = './work_dir/' + project_name + '/docker-compose.yml'

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
networks_info.update(address_database.get_pnet_info())
networks_info.update(address_database.get_rnet_info())
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

print("Assigned AS network IP address")
print(as_network_ip_dict)

routers_list = []
for as_gen in as_generator_dict.values():
  routers_list.extend(as_gen.get_router_dict().values())

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
  rouname = project_name + "_router_" + str(quagga.get_on_as_num()) + "_for_" + str(quagga.get_for_as_num()) + "_1"
  if len(as_generator_dict[quagga.get_on_as_num()].get_router_address_list()) == 1: # There is one router in the AS.
    neighbor_intra_router_address = ""
  else: # There is some routers in the AS.
    neighbor_intra_router_address = as_generator_dict[quagga.get_on_as_num()].get_router_address_list()
    neighbor_intra_router_address.remove(quagga.get_intra_as_address())
    neighbor_intra_router_address = ' '.join(neighbor_intra_router_address)
  subprocess.call(["docker", "exec", "-d", rouname, "/home/gen_zebra_bgpd_conf.sh", str(router_index), str(quagga.get_on_as_num()), quagga.get_as_network_address(), str(quagga.get_for_as_num()), quagga.get_peer_address_opposite(), neighbor_intra_router_address])
  router_index += 1

for srx in srx_list:
  rouname = project_name + "_router_" + str(srx.get_on_as_num()) + "_for_" + str(srx.get_for_as_num()) + "_1"
  subprocess.call(["docker", "exec", "-d", rouname, "/home/gen_zebra_bgpd_sec_conf.sh", str(router_index), str(srx.get_on_as_num()), srx.get_as_network_address(), rpki_generator.get_rpki_address(), str(srx.get_for_as_num()), str(srx.get_peer_address_opposite())])
  router_index += 1

print("Starting daemons...")
for quagga in quagga_list:
  rouname = project_name + "_router_" + str(quagga.get_on_as_num()) + "_for_" + str(quagga.get_for_as_num()) + "_1"
  subprocess.call(["docker", "exec", "-d", "--privileged", rouname, "zebra"])
  subprocess.call(["docker", "exec", "-d", "--privileged", rouname, "bgpd"])

for srx in srx_list:
  rouname = project_name + "_router_" + str(srx.get_on_as_num()) + "_for_" + str(srx.get_for_as_num()) + "_1"
  subprocess.call(["docker", "exec", "-d", "--privileged", rouname, "srx_server"])
  subprocess.call(["docker", "exec", "-d", "--privileged", rouname, "zebra"])
  subprocess.call(["docker", "exec", "-d", "--privileged", rouname, "bgpd"])

print("Finished!")
