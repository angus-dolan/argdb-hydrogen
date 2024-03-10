from setuptools import setup, find_packages


def load_requirements(filename='requirements.txt'):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines() if not line.startswith('#')]


setup(
    name='hydrogen',
    version='0.1',
    packages=find_packages(),
    install_requires=load_requirements()
)

