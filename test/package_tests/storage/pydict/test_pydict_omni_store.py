import pytest
from ragmatic.storage.pydict.omni_store import PydictOmniStore, PydictOmniStoreConfig
from pathlib import Path
import os
import shutil

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
def omni_store(tmp_path):
    config = PydictOmniStoreConfig(dirpath=str(tmp_path))
    yield PydictOmniStore(config.model_dump())

def test_initialization(omni_store):
    assert omni_store._vector_store is not None
    assert omni_store._text_doc_store is not None

def test_store_vectors(omni_store):
    vectors = {"vec1": [1, 2, 3], "vec2": [4, 5, 6]}
    omni_store.store_vectors(vectors)
    assert omni_store._vector_store._data == vectors

def test_store_text_docs(omni_store):
    docs = {"doc1": "content1", "doc2": "content2"}
    omni_store.store_text_docs(docs)
    assert omni_store._text_doc_store._data == docs

def test_get_vectors(omni_store):
    vectors = {"vec1": [1, 2, 3], "vec2": [4, 5, 6]}
    omni_store.store_vectors(vectors)
    result = omni_store.get_vectors(["vec1", "vec2"])
    assert result == [[1, 2, 3], [4, 5, 6]]

def test_get_document(omni_store):
    docs = {"doc1": "content1", "doc2": "content2"}
    omni_store.store_text_docs(docs)
    assert omni_store.get_document("doc1") == "content1"

def test_method_delegation(omni_store):
    vectors = {"vec1": [1, 2, 3]}
    omni_store.store_vectors(vectors)
    assert omni_store.scan_keys("vec.*") == ["vec1"]

    docs = {"doc1": "content1"}
    omni_store.store_text_docs(docs)
    assert omni_store.get_all_documents() == docs

def test_attribute_error(omni_store):
    with pytest.raises(AttributeError):
        omni_store.non_existent_method()
