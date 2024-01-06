import json
from src.sadface_translator.lexer import Lexer

def load_json_as_string(file_path):
    with open(file_path, 'r') as file:
        data_string = file.read()
    return data_string

file_path = 'src/data_importer/example_data/argsme-example.json'
json_string = load_json_as_string(file_path)
# print(json_string)

# Lexer 
mylexer = Lexer(json_string)
mylexer.tokenize()