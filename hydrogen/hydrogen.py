from importer import *
from log_config import setup_logging
from config import Config
from database import Database

config = Config()
database = Database()

setup_logging('hydrogen.log')

if __name__ == "__main__":
    config.initialize()
    database.initialize()

    importer = ArgsmeBatchImporter('./importer/example_data/argsme_grouped.json')
    importer.batch_import()
