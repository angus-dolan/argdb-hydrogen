import pytest
from hydrogen.importer.parser import ArgsmeParser
from hydrogen.importer.models import ArgsmeToken

sample_lexed_tokens = {
    ArgsmeToken.ID: "12345",
    ArgsmeToken.PREMISES_STANCE: "support",
    ArgsmeToken.PREMISES_TEXT: "Argument text here",
    ArgsmeToken.CTX_PREV_ID: "previous123",
    ArgsmeToken.CTX_SRC_ID: "source123",
    ArgsmeToken.CTX_ACQ_TIME: "2021-01-01T00:00:00Z",
    ArgsmeToken.CTX_TITLE: "Sample Argument Title"
}


@pytest.fixture
def argsme_parser():
    return ArgsmeParser(lexed_tokens=sample_lexed_tokens)


class MockSadfaceBuilder:
    def __init__(self):
        self.document = {}

    def with_node(self, node):
        self.document['node'] = node

    def with_edge(self, edge):
        self.document['edge'] = edge

    def with_meta_core(self, key, value):
        self.document[key] = value

    def build(self):
        return self.document


@pytest.fixture
def mock_builder():
    return MockSadfaceBuilder()


def test_initialization(argsme_parser):
    assert argsme_parser is not None


def test_build_node(argsme_parser, mock_builder):
    argsme_parser._builder = mock_builder
    argsme_parser.build_node()
    expected_node = {
        "id": "12345",
        "metadata": {
            "stance": "support",
        },
        "text": "Argument text here",
        "type": "atom",
    }
    assert mock_builder.document['node'] == expected_node


def test_build_edge(argsme_parser, mock_builder):
    argsme_parser._builder = mock_builder
    argsme_parser.build_edge()
    expected_edge = {
        "source_id": "previous123",
        "target_id": "12345"
    }
    assert mock_builder.document['edge'] == expected_edge


def test_meta_core(argsme_parser, mock_builder):
    argsme_parser._builder = mock_builder
    argsme_parser.meta_core()
    expected_meta = {
        "id": "source123",
        "created": "2021-01-01T00:00:00Z",
        "edited": "2021-01-01T00:00:00Z",
        "title": "Sample Argument Title"
    }
    for key, value in expected_meta.items():
        assert mock_builder.document[key] == value
