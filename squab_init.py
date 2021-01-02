import sys
import yaml

class AS_generator:
  def __init__(self, number):
    self._number = number

args = sys.argv

with open(args[1]) as file:
  config = yaml.safe_load(file)

as_generator_dict = {}
for as_num in config["AS_Setting"].keys():
  as_generator_dict[as_num] = AS_generator(as_num)

print(as_generator_dict)
