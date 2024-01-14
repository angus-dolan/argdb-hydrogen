from configparser import ConfigParser
import os

class Config:
  def __init__(self, pathname='argdb.cfg'):
    self.pathname = pathname
    self.active = None
    self.initialize()

  def initialize(self):
    if not os.path.exists(self.pathname):
      self.generate_default()

    self.load_config()

  def generate_default(self):
    cp = ConfigParser()
    cp['datastore'] = {'name': 'argdb', 'path': '.'}
    cp['gui'] = {'port': '8080'}
    cp['api'] = {'port': '5000'}

    with open(self.pathname, 'w') as config_file:
      cp.write(config_file)

  def load_config(self):
    try:
      self.active = ConfigParser()
      self.active.read(self.pathname)
    except Exception as e:
      raise Exception(f"Error loading configuration from {self.pathname}: {e}")

  def get_active(self):
    return self.active
