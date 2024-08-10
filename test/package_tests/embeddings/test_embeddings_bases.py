import pytest

from ragmatic.embeddings import bases


@pytest.fixture
def embeddings_base():
    return bases.Embedder


def test_embeddings_bases(embeddings_base):
    assert True