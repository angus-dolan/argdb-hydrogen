import sadface as sf

class Sadface:
  def __init__(self):
    self.document = {
      "metadata": {
       "core": {
          "id": "",
          "created": "",
          "edited": "",
          "analyst_name": "",
          "analyst_email": "",
          "version": "0.1"
        },
      },
      "nodes": [],
      "edges": [],
      "resources": []
    }
  
  def __set_metadata(self, option, key, value):
    if option not in self.document["metadata"]:
      self.document["metadata"][option] = {}
    self.document["metadata"][option][key] = value
  
  def set_core_metadata(self, key, value):
    self.__set_metadata("core", key, value)

  def set_other_metadata(self, option, key, value):
    self.__set_metadata(option, key, value)

  def add_node(self, node):
    self.document["nodes"].append(node)

  def add_edge(self, edge):
    self.document["edges"].append(edge)

  def add_resource(self, resource):
    self.document["resources"].append(resource)

  def validate(self):
    return sf.validation.verify(self.document)