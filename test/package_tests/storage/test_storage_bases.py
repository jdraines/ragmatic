import pytest
from ragmatic.storage.bases import VectorStore, TextDocumentStore, OmniStore

def test_vector_store_abstract_methods():
    with pytest.raises(TypeError):
        VectorStore()

def test_text_document_store_abstract_methods():
    with pytest.raises(TypeError):
        TextDocumentStore()

def test_omni_store_inheritance():
    assert issubclass(OmniStore, VectorStore)
    assert issubclass(OmniStore, TextDocumentStore)

def test_omni_store_abstract_methods():
    with pytest.raises(NotImplementedError):
        OmniStore({})

def test_omni_store_method_delegation():
    class MockVectorStore(VectorStore):
        def store_vectors(self, vectors): pass
        def get_vectors(self, keys): pass
        def scan_keys(self, match): pass
        def query(self, query): pass
        def query_byvector(self, vector, n): pass

    class MockTextDocStore(TextDocumentStore):
        def store_text_docs(self, text_docs): pass
        def get_document(self, key): return "mock_doc"
        def get_documents(self, keys): pass
        def get_all_documents(self): pass

    class ConcreteOmniStore(OmniStore):
        def __init__(self, config):
            self._vector_store = MockVectorStore()
            self._text_doc_store = MockTextDocStore()

    omni_store = ConcreteOmniStore({})
    assert omni_store.get_document("key") == "mock_doc"

def test_omni_store_attribute_error():
    class ConcreteVectorStore(VectorStore):
        def store_vectors(self, vectors): pass
        def get_vectors(self, keys): pass
        def scan_keys(self, match): pass
        def query(self, query): pass
        def query_byvector(self, vector, n): pass

    class ConcreteTextDocStore(TextDocumentStore):
        def store_text_docs(self, text_docs): pass
        def get_document(self, key): pass
        def get_documents(self, keys): pass
        def get_all_documents(self): pass

    class ConcreteOmniStore(OmniStore):
        def __init__(self, config):
            self._vector_store = ConcreteVectorStore()
            self._text_doc_store = ConcreteTextDocStore()

    omni_store = ConcreteOmniStore({})
    with pytest.raises(AttributeError):
        omni_store.non_existent_method()
    