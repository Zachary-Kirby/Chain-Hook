from json import loads

def load(name):
  with open(name, "r") as file:
    data = loads(file.read())
  return data
