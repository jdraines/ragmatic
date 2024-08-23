import pytest
from ragmatic.storage.pydict.text_doc_store import PydictTextDocumentStore, PydictTextDocumentStoreConfig
from pathlib import Path
import os
import shutil
import pickle

_thisdir = Path(__file__).parent

@pytest.fixture
def tmp_path():
    _path = _thisdir / "tmp"
    os.makedirs(_path, exist_ok=True)
    try:
        yield _path
    finally:
        shutil.rmtree(_path)

@pytest.fixture
def text_doc_store(tmp_path):
    config = PydictTextDocumentStoreConfig(filepath=str(tmp_path / "test_docs.pkl"))
    return PydictTextDocumentStore(config.model_dump())

def test_store_text_docs(text_doc_store):
    docs = {"doc1": "content1", "doc2": "content2"}
    text_doc_store.store_text_docs(docs)
    assert text_doc_store._data == docs

def test_get_document(text_doc_store):
    docs = {"doc1": "content1", "doc2": "content2"}
    text_doc_store.store_text_docs(docs)
    assert text_doc_store.get_document("doc1") == "content1"
    assert text_doc_store.get_document("non_existent") is None

def test_get_documents(text_doc_store):
    docs = {"doc1": "content1", "doc2": "content2"}
    text_doc_store.store_text_docs(docs)
    assert text_doc_store.get_documents(["doc1", "doc2"]) == ["content1", "content2"]

def test_get_documents_missing_key(text_doc_store):
    docs = {"doc1": "content1"}
    text_doc_store.store_text_docs(docs)
    with pytest.raises(KeyError):
        text_doc_store.get_documents(["doc1", "non_existent"])

def test_get_all_documents(text_doc_store):
    docs = {"doc1": "content1", "doc2": "content2"}
    text_doc_store.store_text_docs(docs)
    assert text_doc_store.get_all_documents() == docs

def test_overwrite(tmp_path):
    try:
        with open(tmp_path / "test_docs.pkl", "wb") as f:
            pickle.dump({"doc1": "content1"}, f)
        config = PydictTextDocumentStoreConfig(filepath=str(tmp_path / "test_docs.pkl"), overwrite=True)
        store = PydictTextDocumentStore(config.model_dump())
        store.store_text_docs({"doc1": "content1"})
        store.store_text_docs({"doc2": "content2"})
        assert store.get_all_documents() == {"doc2": "content2"}
    finally:
        os.remove(tmp_path / "test_docs.pkl")

def test_file_not_found(tmp_path):
    config = PydictTextDocumentStoreConfig(filepath=str(tmp_path / "non_existent.pkl"), allow_init=False)
    store = PydictTextDocumentStore(config.model_dump())
    with pytest.raises(FileNotFoundError):
        store.get_document("doc1")
