Certainly! I'll create separate test modules for each of the modules you provided. Here are the unit tests using pytest:

1. Test module for `ragmatic.storage.bases`:

```python
# test_bases.py
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
    class ConcreteOmniStore(OmniStore):
        def __init__(self, config):
            self._vector_store = VectorStore()
            self._text_doc_store = TextDocumentStore()

    omni_store = ConcreteOmniStore({})
    with pytest.raises(AttributeError):
        omni_store.non_existent_method()
```

2. Test module for `ragmatic.storage.pydict.obj_store`:

```python
# test_obj_store.py
import pytest
from ragmatic.storage.pydict.obj_store import PydictObjStore, PydictObjStoreConfig, NoMap, JoblibParallelMap

@pytest.fixture
def obj_store():
    config = PydictObjStoreConfig(filepath="test_data.pkl")
    return PydictObjStore(config.dict())

def test_store_data(obj_store, tmp_path):
    obj_store.filepath = str(tmp_path / "test_data.pkl")
    test_data = {"key1": "value1", "key2": "value2"}
    obj_store.store_data(test_data)
    assert obj_store._data == test_data

def test_query_data(obj_store):
    test_data = {
        "module1": {"name": "module1", "imports": ["os", "sys"]},
        "module2": {"name": "module2", "imports": ["pytest"]}
    }
    obj_store.store_data(test_data)
    obj_store._allowed_query_keys = ["name", "imports"]
    
    result = obj_store.query_data([("name", "eq", "module1")])
    assert result == {"module1"}

    result = obj_store.query_data([("imports", "in", "os")])
    assert result == {"module1"}

def test_invalid_query_key(obj_store):
    obj_store._allowed_query_keys = ["name", "imports"]
    with pytest.raises(ValueError, match="Query key invalid_key not allowed"):
        obj_store.query_data([("invalid_key", "eq", "value")])

def test_invalid_operator(obj_store):
    obj_store._allowed_query_keys = ["name"]
    with pytest.raises(ValueError, match="Query operator invalid_op not allowed"):
        obj_store.query_data([("name", "invalid_op", "value")])

def test_no_map():
    no_map = NoMap({})
    result = no_map.map(lambda x: x * 2, [(1,), (2,), (3,)])
    assert result == [2, 4, 6]

@pytest.mark.parametrize("map_op", [NoMap({}), JoblibParallelMap({"n_jobs": 2})])
def test_map_ops(map_op):
    with map_op as mapper:
        result = mapper.map(lambda x: x * 2, [(1,), (2,), (3,)])
    assert result == [2, 4, 6]
```

3. Test module for `ragmatic.storage.pydict.text_doc_store`:

```python
# test_text_doc_store.py
import pytest
from ragmatic.storage.pydict.text_doc_store import PydictTextDocumentStore, PydictTextDocumentStoreConfig

@pytest.fixture
def text_doc_store(tmp_path):
    config = PydictTextDocumentStoreConfig(filepath=str(tmp_path / "test_docs.pkl"))
    return PydictTextDocumentStore(config.dict())

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
    config = PydictTextDocumentStoreConfig(filepath=str(tmp_path / "test_docs.pkl"), overwrite=False)
    store = PydictTextDocumentStore(config.dict())
    store.store_text_docs({"doc1": "content1"})
    store.store_text_docs({"doc2": "content2"})
    assert store.get_all_documents() == {"doc1": "content1", "doc2": "content2"}

def test_file_not_found(tmp_path):
    config = PydictTextDocumentStoreConfig(filepath=str(tmp_path / "non_existent.pkl"))
    store = PydictTextDocumentStore(config.dict())
    with pytest.raises(FileNotFoundError):
        store.get_document("doc1")
```

4. Test module for `ragmatic.storage.pydict.vector_store`:

```python
# test_vector_store.py
import pytest
import numpy as np
from ragmatic.storage.pydict.vector_store import PydictVectorStore, PydictVectorStoreConfig, CosineSimilarity

@pytest.fixture
def vector_store(tmp_path):
    config = PydictVectorStoreConfig(filepath=str(tmp_path / "test_vectors.pkl"))
    return PydictVectorStore(config.dict())

def test_store_vectors(vector_store):
    vectors = {"vec1": np.array([1, 2, 3]), "vec2": np.array([4, 5, 6])}
    vector_store.store_vectors(vectors)
    assert np.array_equal(vector_store._data["vec1"], vectors["vec1"])
    assert np.array_equal(vector_store._data["vec2"], vectors["vec2"])

def test_get_vectors(vector_store):
    vectors = {"vec1": np.array([1, 2, 3]), "vec2": np.array([4, 5, 6])}
    vector_store.store_vectors(vectors)
    result = vector_store.get_vectors(["vec1", "vec2"])
    assert np.array_equal(result[0], vectors["vec1"])
    assert np.array_equal(result[1], vectors["vec2"])

def test_scan_keys(vector_store):
    vectors = {"vec1": np.array([1, 2, 3]), "vec2": np.array([4, 5, 6]), "other": np.array([7, 8, 9])}
    vector_store.store_vectors(vectors)
    result = vector_store.scan_keys("vec.*")
    assert set(result) == {"vec1", "vec2"}

def test_query(vector_store):
    vectors = {
        "vec1": np.array([[1, 0, 0]]),
        "vec2": np.array([[0, 1, 0]]),
        "vec3": np.array([[0, 0, 1]])
    }
    vector_store.store_vectors(vectors)
    query = {
        "method": "cosine_similarity",
        "vector": np.array([[1, 1, 0]]),
        "limit": 2
    }
    result = vector_store.query(query)
    assert result == ["vec1", "vec2"]

def test_query_byvector(vector_store):
    vectors = {
        "vec1": np.array([[1, 0, 0]]),
        "vec2": np.array([[0, 1, 0]]),
        "vec3": np.array([[0, 0, 1]])
    }
    vector_store.store_vectors(vectors)
    result = vector_store.query_byvector(np.array([1, 1, 0]), n=2)
    assert result == ["vec1", "vec2"]

def test_cosine_similarity():
    v1 = np.array([[1, 1]])
    v2 = np.array([[1, 0], [0, 1], [-1, 0]])
    result = CosineSimilarity._cosine_similarity(v1, v2)
    expected = np.array([[0.70710678, 0.70710678, -0.70710678]])
    assert np.allclose(result, expected)

def test_invalid_query_method(vector_store):
    with pytest.raises(ValueError, match="Invalid query method: invalid_method"):
        vector_store.query({"method": "invalid_method"})
```

5. Test module for `ragmatic.storage.pydict.omni_store`:

```python
# test_omni_store.py
import pytest
from ragmatic.storage.pydict.omni_store import PydictOmniStore, PydictOmniStoreConfig

@pytest.fixture
def omni_store(tmp_path):
    config = PydictOmniStoreConfig(dirpath=str(tmp_path))
    return PydictOmniStore(config.dict())

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
```

These test modules cover the main functionality of each module you provided. They test various aspects such as initialization, data storage and retrieval, querying, and error handling. You can run these tests using pytest by placing them in the appropriate test directory and running `pytest` command.
