import pytest
from hydrogen.importer.lexer import Lexer, ArgsmeLexer
from hydrogen.importer.models import ArgsmeToken

valid_json = {
    "premises": [{
        "stance": "support",
        "text": "It is beneficial."
    }],
    "context": {
        "acquisitionTime": "2021-01-01T00:00:00Z",
        "sourceId": "source123",
        "previousArgumentInSourceId": "prev123",
        "nextArgumentInSourceId": "next123",
        "discussionTitle": "Context Title"
    },
    "id": "argument123",
    "conclusion": "Therefore, it is accepted."
}


def test_ArgsmeLexer_initialization():
    lexer = ArgsmeLexer()
    assert lexer.get_lexed_tokens() == {}, "Initial lexed tokens should be empty"


def test_state_transitions_and_token_processing():
    lexer = ArgsmeLexer(valid_json)
    lexer.tokenize()
    expected_tokens = {
        ArgsmeToken.PREMISES_STANCE: "support",
        ArgsmeToken.PREMISES_TEXT: "It is beneficial.",
        ArgsmeToken.CTX_ACQ_TIME: "2021-01-01T00:00:00Z",
        ArgsmeToken.CTX_SRC_ID: "source123",
        ArgsmeToken.CTX_PREV_ID: "prev123",
        ArgsmeToken.CTX_NEXT_ID: "next123",
        ArgsmeToken.CTX_TITLE: "Context Title",
        ArgsmeToken.ID: "argument123",
        ArgsmeToken.CONCLUSION: "Therefore, it is accepted."
    }
    assert lexer.get_lexed_tokens() == expected_tokens, "Tokenized output did not match expected"


def test_incorrect_json_structure():
    with pytest.raises(Exception):
        lexer = ArgsmeLexer({"incorrect": "data"})
        lexer.tokenize()


def test_lexer_integration():
    base_lexer = ArgsmeLexer(valid_json)
    lexer = Lexer(base_lexer)
    lexer.tokenize()
    assert lexer.get_lexed_tokens() == base_lexer.get_lexed_tokens(), "Lexer integration failed to properly use the strategy pattern"
