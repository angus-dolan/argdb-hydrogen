from configparser import ConfigParser
import os


class Config:
    def __init__(self, config_path='argdb.cfg'):
        self.config_path = config_path
        self._config = None
        self.initialize()

    def initialize(self):
        if not os.path.exists(self.config_path):
            self._generate_default_file()

        self._load_config_file()

    def _generate_default_file(self):
        cp = ConfigParser()
        cp['datastore'] = {'name': 'argdb', 'path': '.'}
        cp['search_index'] = {'port': '6379', 'index_name': 'search_index'}
        cp['frontend'] = {'port': '3000'}
        cp['api'] = {'port': '5000'}

        with open(self.config_path, 'w') as config_file:
            cp.write(config_file)

    def _load_config_file(self):
        try:
            self._config = ConfigParser()
            self._config.read(self.config_path)
        except Exception as e:
            raise Exception(f"Error loading configuration from {self.config_path}: {e}")

    def get(self, section, option):
        return self._config.get(section, option)
