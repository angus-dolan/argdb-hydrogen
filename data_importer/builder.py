class ArgumentBuilder:
  def __init__(self):
    self.argument = {}

  def set_option(self, option, value):
    self.argument[option] = value
    return self

  def set_flag(self, flag):
    self.argument[flag] = True
    return self

  def build(self):
    return self.argument

# Usage example
builder = ArgumentBuilder()
argument = (
  builder
  .set_option("nodes", "")
  .set_option("edges", "")
  .set_option("metadata", "")
  .set_option("resources", "")
  .build()
)
print(argument)
