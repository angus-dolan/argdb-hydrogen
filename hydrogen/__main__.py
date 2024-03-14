from hydrogen import setup_logging, Config, Database
from hydrogen.importer import ArgsmeBatchImporter

config = Config()
database = Database()
setup_logging('hydrogen.log')


def main():
    config.initialize()
    # database.initialize()
    #
    # argsme_importer = ArgsmeBatchImporter('importer/example_data/args-me.json')
    # argsme_importer.batch_import()


if __name__ == "__main__":
    main()
