import pytest
from ragmatic.storage.pydict.obj_store import PydictObjStore, PydictObjStoreConfig, NoMap, JoblibParallelMap

@pytest.fixture
def obj_store():
    config = PydictObjStoreConfig(filepath="test_data.pkl")
    return PydictObjStore(config.model_dump())

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
