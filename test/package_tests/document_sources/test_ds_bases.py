import pytest

from ragmatic.document_sources import bases


def test_document_source_base():
    ds = bases.DocumentSourceBase({})
    assert ds.config == {}
    with pytest.raises(NotImplementedError):
        ds.get_documents()
    