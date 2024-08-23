import pytest
from unittest.mock import MagicMock, patch
from ragmatic.actions.rag import RagAction, RagActionConfig
from ragmatic.actions._types import RagAgentComponentConfig
from ragmatic.common_types import TypeAndConfig

@pytest.fixture
def rag_config():
    return RagActionConfig(
        rag_agent=RagAgentComponentConfig(type="test_rag_agent", config={
            "llm": "test_llm",
            "storage": "test_storage",
            "encoder": "test_encoder",
            "n_nearest": 10,
            "prompt": "test prompt",
            "system_prompt": "test system prompt"
        }),
        document_source=TypeAndConfig(type="storage", config={}),
        query="test query"
    )

@patch('ragmatic.actions.rag.get_rag_agent_class')
@patch('ragmatic.actions.rag.get_document_source_cls')
def test_rag_action_initialization(mock_get_document_source_cls, mock_get_rag_agent_class, rag_config):
    mock_source = MagicMock()
    mock_rag_agent = MagicMock()

    mock_get_document_source_cls.return_value = lambda config: mock_source
    mock_get_rag_agent_class.return_value = lambda config, source: mock_rag_agent

    action = RagAction(rag_config)

    assert action.config == rag_config
    assert action._source == mock_source
    assert action._rag_agent == mock_rag_agent

@patch('ragmatic.actions.rag.get_rag_agent_class')
@patch('ragmatic.actions.rag.get_document_source_cls')
def test_rag_action_execute(mock_get_document_source_cls, mock_get_rag_agent_class, rag_config, monkeypatch):
    mock_source = MagicMock()
    mock_rag_agent = MagicMock()

    mock_get_document_source_cls.return_value = lambda config: mock_source
    mock_get_rag_agent_class.return_value = lambda config, source: mock_rag_agent

    mock_rag_agent.query.return_value = {"answer": "test answer"}

    action = RagAction(rag_config)
    action._rag_agent.query = MagicMock(return_value={"answer": "test answer"}) 
    result = action.execute()

    assert result == {"answer": "test answer"}
    mock_rag_agent.query.assert_called_once_with("test query")
