Certainly! I'll provide unit tests for the `ragmatic.actions.bases`, `ragmatic.actions.summarize`, and `ragmatic.actions.rag` modules using pytest. I'll create mock configurations that adhere to the Pydantic models defined in `ragmatic.actions._types`.

First, let's create a `conftest.py` file to define some fixtures that can be used across multiple test files:

```python
# tests/conftest.py
import pytest
from ragmatic.actions._types import (
    DocumentSourceComponentConfig,
    LLMComponentConfig,
    SummarizerComponentConfig,
    StorageComponentConfig,
    RagAgentComponentConfig,
)
from ragmatic.rag.bases import RagAgentConfig
from ragmatic.summarization.bases import SummarizerConfig
from ragmatic.common_types import TypeAndConfig

@pytest.fixture
def mock_document_source_config():
    return DocumentSourceComponentConfig(
        type="storage",
        config={"path": "/mock/path"}
    )

@pytest.fixture
def mock_llm_config():
    return LLMComponentConfig(
        type="openai",
        config={"model": "gpt-3.5-turbo"}
    )

@pytest.fixture
def mock_summarizer_config():
    return SummarizerComponentConfig(
        type="python_code",
        config=SummarizerConfig(
            llm="mock_llm",
            chunk_size=1000,
            chunk_overlap=100
        )
    )

@pytest.fixture
def mock_storage_config():
    return StorageComponentConfig(
        data_type="summary",
        type="pydict",
        config={}
    )

@pytest.fixture
def mock_rag_agent_config():
    return RagAgentComponentConfig(
        type="basic",
        config=RagAgentConfig(
            retriever="mock_retriever",
            llm="mock_llm"
        )
    )
```

Now, let's create test files for each module:

```python
# tests/test_actions_bases.py
import pytest
from ragmatic.actions.bases import Action, ActionConfig

def test_action_base():
    class TestActionConfig(ActionConfig):
        test_field: str

    class TestAction(Action):
        config_cls = TestActionConfig
        name = "test_action"

    config = TestActionConfig(test_field="test_value")
    action = TestAction(config)

    assert action.config == config
    assert action.name == "test_action"

    with pytest.raises(NotImplementedError):
        action.execute()
```

```python
# tests/test_actions_summarize.py
import pytest
from unittest.mock import MagicMock, patch
from ragmatic.actions.summarize import SummarizeAction, SummarizeActionConfig
from ragmatic.common_types import TypeAndConfig

@pytest.fixture
def mock_summarize_config(mock_document_source_config, mock_summarizer_config, mock_storage_config):
    return SummarizeActionConfig(
        document_source=TypeAndConfig(type="mock", config=mock_document_source_config.config),
        summarizer=mock_summarizer_config,
        storage=mock_storage_config
    )

@pytest.fixture
def mock_summarize_action(mock_summarize_config):
    with patch('ragmatic.actions.summarize.get_store_cls') as mock_get_store_cls, \
         patch('ragmatic.actions.summarize.get_summarizer_class') as mock_get_summarizer_class, \
         patch('ragmatic.actions.summarize.get_document_source_cls') as mock_get_document_source_cls:
        
        mock_store = MagicMock()
        mock_summarizer = MagicMock()
        mock_source = MagicMock()

        mock_get_store_cls.return_value = lambda config: mock_store
        mock_get_summarizer_class.return_value = lambda config: mock_summarizer
        mock_get_document_source_cls.return_value = lambda config: mock_source

        action = SummarizeAction(mock_summarize_config)
        action._text_doc_store = mock_store
        action._summarizer = mock_summarizer
        action._source = mock_source

        return action

def test_summarize_action_init(mock_summarize_action, mock_summarize_config):
    assert mock_summarize_action.config == mock_summarize_config
    assert mock_summarize_action.name == "summarize"

def test_summarize_action_execute(mock_summarize_action):
    mock_documents = {"doc1": "content1", "doc2": "content2"}
    mock_summaries = {"doc1": ["summary1"], "doc2": ["summary2"]}
    mock_kv_summaries = {"doc1_0": "summary1", "doc2_0": "summary2"}

    mock_summarize_action._source.get_documents.return_value = mock_documents
    mock_summarize_action._summarizer.summarize.return_value = mock_summaries
    
    with patch.object(mock_summarize_action, 'summaries_to_key_value_pairs', return_value=mock_kv_summaries):
        mock_summarize_action.execute()

    mock_summarize_action._source.get_documents.assert_called_once()
    mock_summarize_action._summarizer.summarize.assert_called_once_with(mock_documents)
    mock_summarize_action._text_doc_store.store_text_docs.assert_called_once_with(mock_kv_summaries)

def test_summaries_to_key_value_pairs():
    action = SummarizeAction(SummarizeActionConfig(
        document_source=TypeAndConfig(type="mock", config={}),
        summarizer=MagicMock(),
        storage=MagicMock()
    ))
    summaries = {
        "doc1": ["summary1", "summary2"],
        "doc2": ["summary3"]
    }
    expected = {
        "doc1_0": "summary1",
        "doc1_1": "summary2",
        "doc2_0": "summary3"
    }
    assert action.summaries_to_key_value_pairs(summaries) == expected
```

```python
# tests/test_actions_rag.py
import pytest
from unittest.mock import MagicMock, patch
from ragmatic.actions.rag import RagAction, RagActionConfig
from ragmatic.common_types import TypeAndConfig

@pytest.fixture
def mock_rag_config(mock_document_source_config, mock_rag_agent_config):
    return RagActionConfig(
        document_source=TypeAndConfig(type="mock", config=mock_document_source_config.config),
        rag_agent=mock_rag_agent_config,
        query="What is the capital of France?"
    )

@pytest.fixture
def mock_rag_action(mock_rag_config):
    with patch('ragmatic.actions.rag.get_document_source_cls') as mock_get_document_source_cls, \
         patch('ragmatic.actions.rag.get_rag_agent_class') as mock_get_rag_agent_class:
        
        mock_source = MagicMock()
        mock_rag_agent = MagicMock()

        mock_get_document_source_cls.return_value = lambda config: mock_source
        mock_get_rag_agent_class.return_value = lambda config, source: mock_rag_agent

        action = RagAction(mock_rag_config)
        action._source = mock_source
        action._rag_agent = mock_rag_agent

        return action

def test_rag_action_init(mock_rag_action, mock_rag_config):
    assert mock_rag_action.config == mock_rag_config
    assert mock_rag_action.name == "rag"

def test_rag_action_execute(mock_rag_action):
    expected_response = {"answer": "The capital of France is Paris."}
    mock_rag_action._rag_agent.query.return_value = expected_response

    result = mock_rag_action.execute()

    mock_rag_action._rag_agent.query.assert_called_once_with(mock_rag_action.config.query)
    assert result == expected_response
```

These test files cover the basic functionality of the Action classes, including initialization and execution. They use mock objects to simulate the behavior of external dependencies like document sources, summarizers, and RAG agents.

To run these tests, you'll need to have pytest installed and run the following command in the root directory of your project:

```
pytest tests/
```

Note that these tests assume the existence of certain factory functions (`get_store_cls`, `get_summarizer_class`, `get_document_source_cls`, `get_rag_agent_class`) which are mocked in the tests. If these functions are defined differently in your actual code, you may need to adjust the mocking accordingly.

Also, make sure to create an empty `__init__.py` file in the `tests/` directory to make it a proper Python package.
