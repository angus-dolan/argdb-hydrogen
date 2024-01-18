import sadface as sf

class SadfaceBuilder:
  def __init__(self):
    self.sadface = {
      "metadata": {
        "core": {}
      },
      "nodes": [],
      "edges": [],
      "resources": []
    }

  def default_metadata_core(self):
    self.sadface["metadata"]["core"]["analyst_name"] = ""
    self.sadface["metadata"]["core"]["analyst_email"] = ""
    self.sadface["metadata"]["core"]["version"] = "0.1"
    return self

  def with_metadata_core(self, key, value):
    self.sadface["metadata"]["core"][key] = value
    return self

  def with_metadata_other(self, option, key, value):
    if option not in self.sadface["metadata"]:
      self.sadface["metadata"][option] = {}
      
    self.sadface["metadata"][option][key] = value
    return self

  def with_node(self, node):
    self.sadface["nodes"].append(node)
    return self
  
  def with_edge(self, edge):
    self.sadface["edges"].append(edge)
    return self
  
  def with_resource(self, resource):
    self.sadface["resources"].append(resource)
    return self

  def set_option(self, option, value):
    self.sadface[option] = value
    return self

  def set_flag(self, flag):
    self.sadface[flag] = True
    return self

  def validate(self):
    return sf.validation.verify(self.sadface)

  def build(self):
    return self.sadface
