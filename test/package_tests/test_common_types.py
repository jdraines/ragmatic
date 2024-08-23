import pytest

from ragmatic import common_types


def test_imports():
    assert common_types
    assert common_types.TypeAndConfig
    assert common_types.StoreConfig
