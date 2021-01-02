import sys
import yaml

class AS_generator:
  def __init__(self, number, flag, address):
    self._number = number
    self._flag = flag
    self._address = address
  def get_add(self):
    return self._flag

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


args = sys.argv

with open(args[1]) as file:
  config = yaml.safe_load(file)

address_database = Address_detabase()

as_generator_dict = {}

for as_num in config["AS_Setting"].keys():
  as_generator_dict[as_num] = AS_generator(as_num, config["AS_Setting"][as_num]["flag"], address_database.get_as_net_address(as_num))

