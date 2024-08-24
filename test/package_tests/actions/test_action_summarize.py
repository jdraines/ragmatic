import pytest
from unittest.mock import MagicMock, patch
from ragmatic.actions.summarize import SummarizeAction, SummarizeActionConfig
from ragmatic.actions._types import SummarizerComponentConfig, StorageComponentConfig
from ragmatic.common_types import TypeAndConfig

@pytest.fixture
def summarize_config():
    return SummarizeActionConfig(
        summarizer=SummarizerComponentConfig(
            type="python_code",
            config={
                "llm": {
                    "type": "openai",
                    "config": {"api_keyenvvar": "OPENAI_API_KEY"}
                },
                "document_source": {
                    "type": "storage",
                    "config": {}
                }
            }
        ),
        storage=StorageComponentConfig(data_type="metadata", type="pydict", config={}),
        document_source=TypeAndConfig(type="storage", config={})
    )

@patch('ragmatic.actions.summarize.get_summarizer_class')
@patch('ragmatic.actions.summarize.get_document_source_cls')
@patch('ragmatic.actions.summarize.get_store_cls')
def test_summarize_action_initialization(mock_get_store_cls, mock_get_document_source_cls, mock_get_summarizer_class, summarize_config):
    mock_summarizer = MagicMock()
    mock_source = MagicMock()
    mock_store = MagicMock()

    mock_get_summarizer_class.return_value = lambda config: mock_summarizer
    mock_get_document_source_cls.return_value = lambda config: mock_source
    mock_get_store_cls.return_value = lambda config: mock_store

    action = SummarizeAction(summarize_config)

    assert action.config == summarize_config
    assert action._summarizer == mock_summarizer
    assert action._source == mock_source
    assert action._text_doc_store == mock_store

@patch('ragmatic.actions.summarize.get_summarizer_class')
@patch('ragmatic.actions.summarize.get_document_source_cls')
@patch('ragmatic.actions.summarize.get_store_cls')
def test_summarize_action_execute(mock_get_store_cls, mock_get_document_source_cls, mock_get_summarizer_class, summarize_config):
    mock_summarizer = MagicMock()
    mock_source = MagicMock()
    mock_store = MagicMock()

    mock_get_summarizer_class.return_value = lambda config: mock_summarizer
    mock_get_document_source_cls.return_value = lambda config: mock_source
    mock_get_store_cls.return_value = lambda config: mock_store

    mock_source.get_documents.return_value = {"doc1": "content1", "doc2": "content2"}
    mock_summarizer.summarize.return_value = {"doc1": ["summary1"], "doc2": ["summary2"]}

    action = SummarizeAction(summarize_config)
    action.execute()

    mock_source.get_documents.assert_called_once()
    mock_summarizer.summarize.assert_called_once_with({"doc1": "content1", "doc2": "content2"})
    mock_store.store_text_docs.assert_called_once_with({"doc1::0": "summary1", "doc2::0": "summary2"})
