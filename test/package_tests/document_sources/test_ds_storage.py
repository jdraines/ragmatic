from unittest.mock import MagicMock, patch
import pytest

from ragmatic.document_sources import storage


@pytest.fixture
def store_config():
    return storage.StoreConfig(
        data_type="text",
        type="file",
        config={"root_path": "/path/to/root"}
    )

@pytest.fixture
def documents() -> dict[str, str]:
    return {
        "doc1": "content of doc1",
        "doc2": "content of doc2"
    }

@pytest.fixture
def mock_text_doc_store(documents):
    class MockTextDocStore(storage.TextDocumentStore):
        def __init__(self, config):
            self.__documents = documents

        def get_all_documents(self):
            return self.__documents

        def get_document(self, document_name: str):
            return self.__documents.get(document_name)
        
        def get_documents(self, document_names: list[str]):
            return [
                self.__documents.get(doc_name) for doc_name in document_names
            ]

        def store_text_docs(self, docs: dict[str, str]):
            self.__documents.update(docs)

    return MockTextDocStore

@pytest.fixture
def storage_dc_source(store_config, mock_text_doc_store):
    with patch("ragmatic.document_sources.storage.get_store_cls", MagicMock(return_value=mock_text_doc_store)):
        return storage.TextStoreDocumentSource(store_config)


class TestTextStoreDocumentSource:

    def test__init__(self, storage_dc_source, store_config, mock_text_doc_store):
        assert hasattr(storage_dc_source, "name")
        assert storage_dc_source.config == store_config
        assert isinstance(storage_dc_source._text_doc_store, mock_text_doc_store)
    

    def test__initialize_text_doc_store(self, storage_dc_source, mock_text_doc_store):
        with patch("ragmatic.document_sources.storage.get_store_cls", MagicMock(return_value=mock_text_doc_store)):
            assert isinstance(storage_dc_source._initialize_text_doc_store(), mock_text_doc_store)
    
    def test_get_documents(self, storage_dc_source, documents):
        assert storage_dc_source.get_documents() == documents
        assert storage_dc_source.get_documents(["doc1"]) == {"doc1": "content of doc1"}
        assert storage_dc_source.get_documents(["doc1", "doc2"]) == documents
        assert storage_dc_source.get_documents(["doc3"]) == {"doc3": None}
        assert storage_dc_source.get_documents([]) == documents
        assert storage_dc_source.get_documents(None) == documents