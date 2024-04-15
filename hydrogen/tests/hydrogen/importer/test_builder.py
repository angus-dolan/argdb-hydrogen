import pytest
from hydrogen.importer.builder import SadfaceBuilder
from hydrogen.importer.models.sadface import Sadface


def test_initialization_with_empty_document():
    builder = SadfaceBuilder()
    assert builder.sadface.document['metadata']['core']['id'] == '', "Initial ID should be empty"


def test_initialization_with_existing_document():
    existing_document = {
        "metadata": {
            "core": {
                "id": "existing-id",
                "created": "2021-01-01",
                "edited": "2021-01-02",
                "analyst_name": "John Doe",
                "analyst_email": "john@example.com",
                "version": "0.1"
            },
        },
        "nodes": [{"id": "node1"}],
        "edges": [{"source": "node1", "target": "node2"}],
        "resources": [{"url": "http://example.com"}]
    }
    builder = SadfaceBuilder().with_existing_document(existing_document)
    assert builder.sadface.document['metadata']['core'][
               'id'] == 'existing-id', "Builder should initialize with existing document ID"


def test_with_meta_core():
    builder = SadfaceBuilder()
    builder.with_meta_core("id", "new-id")
    assert builder.sadface.document['metadata']['core']['id'] == 'new-id', "Failed to set core metadata"


def test_with_node():
    builder = SadfaceBuilder()
    node = {"id": "node1", "text": "Test node"}
    builder.with_node(node)
    assert node in builder.sadface.document['nodes'], "Node should be added to the document"


def test_with_edge():
    builder = SadfaceBuilder()
    edge = {"source": "node1", "target": "node2"}
    builder.with_edge(edge)
    assert edge in builder.sadface.document['edges'], "Edge should be added to the document"


def test_with_resource():
    builder = SadfaceBuilder()
    resource = {"url": "http://example.com"}
    builder.with_resource(resource)
    assert resource in builder.sadface.document['resources'], "Resource should be added to the document"


def test_build():
    builder = SadfaceBuilder()
    builder.with_meta_core("id", "new-id")
    built_document = builder.build()
    assert isinstance(built_document, Sadface), "Build should return a Sadface instance"
    assert built_document.document['metadata']['core'][
               'id'] == "new-id", "Build should return the document with updated metadata"

