import pytest
from unittest.mock import MagicMock, patch
from ragmatic.actions.encode import EncodeAction, EncodeActionConfig
from ragmatic.actions._types import EncoderComponentConfig, StorageComponentConfig
from ragmatic.common_types import TypeAndConfig

@pytest.fixture
def encode_config():
    return EncodeActionConfig(
        encoder=EncoderComponentConfig(type="hugging_face", config={}),
        document_source=TypeAndConfig(type="storage", config={}),
        storage=StorageComponentConfig(data_type="vector", type="pydict", config={})
    )

@patch('ragmatic.actions.encode.get_embedder_cls')
@patch('ragmatic.actions.encode.get_document_source_cls')
@patch('ragmatic.actions.encode.get_store_cls')
def test_encode_action_initialization(mock_get_store_cls, mock_get_document_source_cls, mock_get_embedder_cls, encode_config):
    mock_embedder = MagicMock()
    mock_source = MagicMock()
    mock_store = MagicMock()

    mock_get_embedder_cls.return_value = lambda config: mock_embedder
    mock_get_document_source_cls.return_value = lambda config: mock_source
    mock_get_store_cls.return_value = lambda config: mock_store

    action = EncodeAction(encode_config)

    assert action.config == encode_config
    assert action._embedder == mock_embedder
    assert action._source == mock_source
    assert action._vector_store == mock_store

@patch('ragmatic.actions.encode.get_embedder_cls')
@patch('ragmatic.actions.encode.get_document_source_cls')
@patch('ragmatic.actions.encode.get_store_cls')
def test_encode_action_execute(mock_get_store_cls, mock_get_document_source_cls, mock_get_embedder_cls, encode_config):
    mock_embedder = MagicMock()
    mock_source = MagicMock()
    mock_store = MagicMock()

    mock_get_embedder_cls.return_value = lambda config: mock_embedder
    mock_get_document_source_cls.return_value = lambda config: mock_source
    mock_get_store_cls.return_value = lambda config: mock_store

    mock_source.get_documents.return_value = {"doc1": "content1", "doc2": "content2"}
    mock_embedder.encode.return_value = [[0.1, 0.2], [0.3, 0.4]]

    action = EncodeAction(encode_config)
    action.execute()

    mock_source.get_documents.assert_called_once()
    mock_embedder.encode.assert_called_once_with(["content1", "content2"])
    mock_store.store_vectors.assert_called_once_with({"doc1": [0.1, 0.2], "doc2": [0.3, 0.4]})
