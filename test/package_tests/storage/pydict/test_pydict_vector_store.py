import pytest
import numpy as np
from ragmatic.storage.pydict.vector_store import PydictVectorStore, PydictVectorStoreConfig, CosineSimilarity

@pytest.fixture
def vector_store(tmp_path):
    config = PydictVectorStoreConfig(filepath=str(tmp_path / "test_vectors.pkl"))
    return PydictVectorStore(config.model_dump())

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
        "vector": np.array([[1, .7, 0]]),
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
    result = vector_store.query_byvector(np.array([[1, .7, 0]]), n=2)
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
