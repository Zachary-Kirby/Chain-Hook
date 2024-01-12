from json import loads

def load(name):
  with open(name, "rt") as file:
    text = file.read()
    data = loads(text)
  return data
