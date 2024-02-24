import pytest
from hydrogen.importer.lexer import Lexer, ArgsmeLexer
from hydrogen.importer.models import ArgsmeToken
from unittest.mock import patch, PropertyMock


@pytest.fixture
def valid_json_data():
    return {
        "premises": [{"text": "Test argument", "stance": "CON"}],
        "context": {
            "sourceId": "test-source-id",
            "previousArgumentInSourceId": "",
            "acquisitionTime": "2020-01-01T00:00:00Z",
            "discussionTitle": "Test Title",
            "sourceTitle": "Test Source Title",
            "sourceUrl": "http://testurl.com",
            "nextArgumentInSourceId": "test-next-id"
        },
        "id": "test-id-000",
        "conclusion": "Test Conclusion"
    }


@pytest.fixture
def invalid_json_data():
    return {
        # Missing the "arguments" key or any other malformed data
    }


@pytest.mark.parametrize("argsme_token,incorrect_value", [
    ('PREMISES', ['premisess']),
    ('PREMISES_TEXT', ['premises', '0', 'text']),
    ('PREMISES_STANCE', ['premises', '0', 'stance']),
    ('PREMISES_TEXT', ['premises', 0, 'textt']),
    ('PREMISES_STANCE', ['premises', 0, 'stancee']),
    ('CTX', ['contex']),
    ('CTX_SRC_ID', ['ctx', 'sourceId']),
    ('CTX_SRC_ID', ['context', 'source']),
    ('ID', ['id']),
    ('CONCLUSION', ['conclusion']),
    ('UNKNOWN_TOKEN', ['unknown']),
    ('UNKNOWN_EMPTY_TOKEN', []),
    ('DICT', {'premises': ['premises']})
])

@pytest.fixture
def argsme_lexer(valid_json_data):
    return ArgsmeLexer(valid_json_data)


@pytest.fixture
def lexer(argsme_lexer):
    return Lexer(argsme_lexer)


def test_lexer_initializes_with_correct_state(argsme_lexer):
    assert argsme_lexer._current_state == 'start', "Lexer should initialize in 'start' state"


def test_lexer_state_transitions(argsme_lexer):
    argsme_lexer.tokenize()
    assert argsme_lexer._current_state == 'end', "Lexer should end in 'end' state after tokenization"


def test_lexer_handles_invalid_argsmetokens(argsme_lexer, argsme_token, incorrect_value):
    with patch(f'path.to.ArgsmeToken.{argsme_token}', new_callable=PropertyMock) as mocked_token_attr:
        mocked_token_attr.return_value = incorrect_value

        # Assuming your lexer has a method to process or validate tokens,
        # you would call it here and assert the expected outcome.
        # For demonstration, let's say we expect the lexer to not raise an exception
        # but instead handle the error gracefully.
        try:
            # Example method call that might be affected by the token values
            result = argsme_lexer.process_tokens()
            # Assert the expected outcome - for example, that result is not None or contains expected data
            assert result is not None, "Lexer failed to process tokens gracefully with incorrect token values."
        except Exception as e:
            pytest.fail(f"Lexer raised an unexpected exception with incorrect token values: {e}")

def test_lexer_retrieves_token_values(argsme_lexer):
    tokens = argsme_lexer.tokenize()
    assert ArgsmeToken.PREMISES_TEXT in tokens, "PREMISES_TEXT token should be present in tokens"
    assert tokens[ArgsmeToken.PREMISES_TEXT] == "Test argument", "PREMISES_TEXT value should match input data"
    # TODO: assert the rest of the tokens ...


def test_lexer_handles_invalid_json(invalid_json_data):
    with pytest.raises(Exception):
        ArgsmeLexer(invalid_json_data).tokenize()


def test_lexer_integration_with_lexer_strategy(lexer):
    tokens = lexer.tokenize()
    assert tokens, "Lexer should return tokens using the provided strategy"
    assert ArgsmeToken.PREMISES_TEXT in tokens, "PREMISES_TEXT token should be present in tokens"
