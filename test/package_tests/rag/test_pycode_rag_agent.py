import pytest
from ragmatic.rag.pycode_rag_agent import PyCodeRagAgent
from ragmatic.rag.bases import RagAgentConfig
from unittest.mock import Mock, patch

@pytest.fixture
def rag_agent_config():
    return RagAgentConfig(
        llm={"type": "mock_llm", "config": {}},
        storage={"data_type": "mock_data", "type": "mock_store", "config": {}},
        encoder={"type": "mock_encoder", "config": {}},
        n_nearest=5,
    )

@pytest.fixture
def mock_document_source():
    return Mock()


class TestPyCodeRagAgent:
    
    @patch('ragmatic.rag.bases.get_llm_client_class')
    @patch('ragmatic.rag.bases.get_store_cls')
    @patch('ragmatic.rag.bases.get_embedder_cls')
    def test_initialization(self, _, __, ___, rag_agent_config, mock_document_source):
        agent = PyCodeRagAgent(rag_agent_config, mock_document_source)
        assert agent.name == "python_code"
        assert "You are an assistant with expertise in programming" in agent.system_prompt
        assert "I'm a python developer, and I have a question about some code" in agent.prompt

    def test_file_filters(self):
        assert len(PyCodeRagAgent.file_filters) == 1
        assert PyCodeRagAgent.file_filters[0]("test.py")
        assert not PyCodeRagAgent.file_filters[0]("test.txt")
        assert not PyCodeRagAgent.file_filters[0]("test.js")

    @patch('ragmatic.rag.bases.get_llm_client_class')
    @patch('ragmatic.rag.bases.get_store_cls')
    @patch('ragmatic.rag.bases.get_embedder_cls')
    def test_build_user_message(self, _, __, ___, rag_agent_config, mock_document_source):
        agent = PyCodeRagAgent(rag_agent_config, mock_document_source)
        query = "How does this code work?"
        context_docs = {
            "file1.py": "def hello():\n    print('Hello, World!')",
            "file2.py": "class MyClass:\n    pass"
        }
        message = agent.build_user_message(query, context_docs)
        
        assert agent.prompt in message
        assert query in message
        assert agent.q_context_delimiter in message
        assert "```python file=file1.py" in message
        assert "```python file=file2.py" in message
        assert "def hello():" in message
        assert "class MyClass:" in message