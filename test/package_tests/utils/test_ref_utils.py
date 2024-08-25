import pytest
import json

from ragmatic.utils import refs


@pytest.fixture
def ref():
    return refs.Ref("test")

@pytest.fixture
def ref_dict(ref):
    return {
        "a": ref,
        "b": {"c": ref}
    }

@pytest.fixture
def ref_json_str():
    return r'{"a": "!ref test", "b": {"c": "!ref test"}}'

def test_json_dump_ref(ref_dict):
    dumped = json.dumps(ref_dict, default=refs.ref_dumper_default)
    assert dumped == r'{"a": "!ref test", "b": {"c": "!ref test"}}'

def test_json_load(ref_json_str):
    loaded = json.loads(ref_json_str, cls=refs.RefDecoder)
    assert loaded == {"a": refs.Ref("test"), "b": {"c": refs.Ref("test")}}
