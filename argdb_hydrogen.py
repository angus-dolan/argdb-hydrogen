import json
from src.sadface_translator.lexer import LexerContext, ArgsmeLexer

file_path = 'src/data_importer/example_data/argsme-example.json'

def load_json_as_string(file_path):
  with open(file_path, 'r') as file:
    data_string = file.read()
    return data_string

# Using ArgsmeLexer
json_string = load_json_as_string(file_path)
lexer = LexerContext(ArgsmeLexer())
tokens = lexer.tokenize_data(json_string)
print(tokens)