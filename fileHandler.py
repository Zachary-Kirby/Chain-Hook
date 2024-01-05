from json import loads

def load(name):
  with open(name) as file:
    data = loads(file.read())
  return data
