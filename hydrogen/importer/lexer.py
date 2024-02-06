from abc import ABC, abstractmethod
from models import *

class BaseLexer(ABC):
    @abstractmethod
    def tokenize(self):
        pass


class Lexer:
    def __init__(self, lexer_strategy: BaseLexer):
        self._lexer_strategy = lexer_strategy

    def set_lexer_strategy(self, lexer_strategy):
        self._lexer_strategy = lexer_strategy

    def tokenize_argument(self):
        return self._lexer_strategy.tokenize()


class ArgsmeLexer(BaseLexer):
    def __init__(self, json_data):
        self.json_data = json_data
        self.current_state = 'start'
        self.STATE_TRANSITIONS = {
            'start': 'premises',
            'premises': 'context',
            'context': 'id',
            'id': 'conclusion',
            'conclusion': 'end',
        }
        self.STATE_TOKENS = {
            'premises': [
                ArgsmeToken.PREMISES_STANCE,
                ArgsmeToken.PREMISES_TEXT
            ],
            'context': [
                ArgsmeToken.CTX_ACQ_TIME,
                ArgsmeToken.CTX_SRC_ID,
                ArgsmeToken.CTX_PREV_ID,
                ArgsmeToken.CTX_TITLE
            ],
            'id': [ArgsmeToken.ID],
            'conclusion': [ArgsmeToken.CONCLUSION]
        }
        self.lexed_tokens = []

    def access_nested_json(self, nested_keys):
        value = self.json_data
        final_values = []  # Use a list to collect values from lists in JSON
        try:
            for key in nested_keys:
                if isinstance(value, dict):
                    value = value[key]
                elif isinstance(value, list) and key.isdigit():  # Check if key is an index
                    value = value[int(key)]  # Access list element by index
            else:
                # Handle lists where we want to collect data from all elements
                if key == nested_keys[-1]:  # Only proceed if it's the final key in the path
                    for item in value:
                        if key in item:
                            final_values.append(item[key])
                    return final_values
        except KeyError as e:
            self.error(f"Key '{e.args[0]}' not found in JSON data.")
            return None
        except IndexError as e:
            self.error(f"Index {e.args[0]} out of range.")
            return None
        return value if not final_values else final_values

    def process(self):
        next_state = self.STATE_TRANSITIONS.get(self.current_state)
        if next_state == 'end':
            return

        self.current_state = next_state

        for token_enum in self.STATE_TOKENS[self.current_state]:
            nested_keys = token_enum.value
            token_val = self.access_nested_json(nested_keys)

            if token_val is not None:
                # Check if token_val is a list and handle accordingly
                if isinstance(token_val, list):
                    for val in token_val:
                        self.lexed_tokens.append(Token(val, token_enum))
                else:
                    self.lexed_tokens.append(Token(token_val, token_enum))

        self.process()

    def error(self, error_message):
        print("Error:", error_message)
        self.current_state = 'end'

    def tokenize(self):
        self.process()

        print(self.json_data['premises'][0]['stance'])
        print(self.json_data['context']['sourceTitle'])
        print(self.json_data['id'])
        # print(len(self.lexed_tokens))
        # for token in self.lexed_tokens:
        #    print(token.type, token.value)
