import sys
import yaml

class AS_generator:
  def __init__(self, number, flag, address):
    self.number = number
    self.flag = flag
    self.address = address

    self.router_dict = {}

  def make_peer_router_for(self, as_num, address):

    if not as_num in self.router_dict.keys(): # 対応したルータがなければ、生成する
      self.router_dict[as_num] = Router_generator(as_num, address)

    return self.router_dict[as_num]


class Router_generator:
  def __init__(self, number, address):
    self.for_number = number
    self.address = address


class Address_detabase:
  def __init__(self):
    self.AS_NET_ADDRESS_PREFIX = "191.168."
    self.PEER_ADDRESS_PREFIX = "171.17."
    self.RPKI_NET_ADDRESS_PREFIX = "171.16.0."

    self.as_net_i = 2
    self.peer_address_i = 2
    self.rpki_net_i = 2

    self.as_net_dict = {}
    self.peer_address_dict = {}
    self.rpki_net_dict = {}

  def get_as_net_address(self, as_num):

    if not as_num in self.as_net_dict.keys(): # ASに対応したアドレスがなければ、生成する
      self.as_net_dict[as_num] = self.AS_NET_ADDRESS_PREFIX + str(self.as_net_i) + ".0/24"
      self.as_net_i += 1

    return self.as_net_dict[as_num]

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
      return self.peer_address_dict[peer_key][:-5] + ".2/24"
    elif mode == "BIGGER":
      return self.peer_address_dict[peer_key][:-5] + ".3/24"
    else:
      raise ValueError("mode incorrectly!")

  def get_as_net_info(self):

    as_net_info = {}
    for as_num in self.as_net_dict.keys():
      as_net_info["as_net_" + str(as_num)] = {"ipam": {"config": [{"subnet": self.as_net_dict[as_num]}]}}

    return as_net_info


  def get_pnet_info(self):

    pnet_info = {}
    for peer_info in self.peer_address_dict.keys():
      pnet_info["pnet_" + peer_info] = {"ipam": {"config": [{"subnet": self.peer_address_dict[peer_info]}]}}

    return pnet_info


args = sys.argv

with open(args[1]) as file:
  config = yaml.safe_load(file)

address_database = Address_detabase()

as_generator_dict = {}

for as_num in config["AS_Setting"].keys():
  as_generator_dict[as_num] = AS_generator(as_num, config["AS_Setting"][as_num]["flag"], address_database.get_as_net_address(as_num))

for peer in config["Peer_info"]:
  as_generator_dict[peer[0]].make_peer_router_for(peer[1], address_database.get_peer_address(peer[0], peer[1], "SMALLER"))
  as_generator_dict[peer[1]].make_peer_router_for(peer[0], address_database.get_peer_address(peer[0], peer[1], "BIGGER"))

print("Making docker-compose.yml file.")


compose_head = {'version': 3}
compose_services = {'services': {'router': 'as'}}

as_net_info = address_database.get_as_net_info()
pnet_info = address_database.get_pnet_info()
as_net_info.update(pnet_info)
compose_networks = {'networks': as_net_info}

with open('docker-compose.yml', 'w') as f:
  print(yaml.dump(compose_head), file=f)
with open('docker-compose.yml', 'a') as f:
  print(yaml.dump(compose_services), file=f)
  print(yaml.dump(compose_networks), file=f)
