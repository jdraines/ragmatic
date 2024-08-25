import pytest
import numpy as np
from ragmatic.storage.pydict.vector_store import PydictVectorStore, PydictVectorStoreConfig, CosineSimilarity

@pytest.fixture
def vector_store(tmp_path):
    config = PydictVectorStoreConfig(filepath=str(tmp_path / "test_vectors.pkl"))
    return PydictVectorStore(config.model_dump())

@pytest.fixture
def mock_stored_vectors():
    return {
        "vec1": np.array([[1, 1, 0, 0]]),
        "vec2": np.array([[1, 1, 0, 1]]),
        "vec3": np.array([[0, 0, 1, 0]]),
        "vec4": np.array([[0, 0, 0, 1]])
    }

@pytest.fixture
def mock_query_vector():
    return np.array([[1, 1, 0, 0]])


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

def test_query(vector_store, mock_stored_vectors, mock_query_vector):
    vectors = mock_stored_vectors
    vector_store.store_vectors(vectors)
    query = {
        "method": "cosine_similarity",
        "vector": mock_query_vector,
        "limit": 2
    }
    result = vector_store.query(query)
    assert result == ["vec1", "vec2"]

def test_query_byvector(vector_store, mock_stored_vectors, mock_query_vector):
    vectors = mock_stored_vectors
    vector_store.store_vectors(vectors)
    result = vector_store.query_byvector(mock_query_vector, n=2)
    assert result == ["vec1", "vec2"]


def test_cosine_similarity_execute():
    query = {
        "method": "cosine_similarity",
        "vector": np.array([[1, 2, 3]]),
        "limit": 5
    }

    data = {
        "doc1": np.array([[1, 2, 3]]),
        "doc2": np.array([[4, 5, 6]]),
        "doc3": np.array([[7, 8, 9]]),
        "doc4": np.array([[10, 11, 12]]),
        "doc5": np.array([[13, 14, 15]]),
        "doc6": np.array([[16, 17, 18]]),
        "doc7": np.array([[19, 20, 21]]),
        "doc8": np.array([[22, 23, 24]]),
        "doc9": np.array([[25, 26, 27]]),
        "doc10": np.array([[28, 29, 30]]),
    }
    output = CosineSimilarity.execute(query, data)
    assert output == ["doc1", "doc2", "doc3", "doc4", "doc5"]

def test_cosine_similarity(mock_stored_vectors, mock_query_vector):
    v2_multi = np.stack(list(mock_stored_vectors.values()), axis=0).reshape(4, 4)
    vq = mock_query_vector

    result = CosineSimilarity._cosine_similarity(vq, v2_multi)
    expected = np.array([[1., 0.81649658, 0., 0.]])
    # assert np.mean(expected) == 0
    assert np.all(result) == np.all(expected)


def test_invalid_query_method(vector_store):
    with pytest.raises(ValueError, match="Invalid query method: invalid_method"):
        vector_store.query({"method": "invalid_method"})
