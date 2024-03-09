from hydrogen import setup_logging, Config, Database
from hydrogen.importer import ArgsmeBatchImporter

config = Config()
database = Database()

setup_logging('hydrogen.log')


# TODO: Start connection to redis search index

def main():
    config.initialize()
    database.initialize()

    argsme_importer = ArgsmeBatchImporter('./hydrogen/importer/example_data/args-me.json')
    argsme_importer.batch_import()


if __name__ == "__main__":
    main()
