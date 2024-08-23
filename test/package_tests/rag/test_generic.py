import pytest
from ragmatic.rag.generic import GenericRagAgent
from ragmatic.llm_ops import client_factory as cf
from ragmatic.rag.bases import RagAgentConfig
from unittest.mock import Mock, MagicMock, patch

@pytest.fixture
def rag_agent_config():
    return RagAgentConfig(
        llm={"type": "unittest.mock.MagicMock", "config": {}},
        storage={"data_type": "omni", "type": "pydict", "config": {}},
        encoder={"type": "mock_encoder", "config": {}},
        n_nearest=5,
    )

@pytest.fixture(autouse=True)
def register_mock_llm_client():
    cf._clients["mock_llm"] = MagicMock()


@pytest.fixture
def mock_document_source():
    return Mock()

class TestGenericRagAgent:
    @patch('ragmatic.rag.bases.get_llm_client_class')
    @patch('ragmatic.rag.bases.get_store_cls')
    @patch('ragmatic.rag.bases.get_embedder_cls')
    def test_initialization(self, _, __, ___, rag_agent_config, mock_document_source):
        agent = GenericRagAgent(rag_agent_config, mock_document_source)
        assert agent.name == "generic"
        assert "You are an assistant with attention to detail" in agent.system_prompt
        assert "I have a question about some documents in a collection" in agent.prompt

    def test_file_filters(self):
        assert len(GenericRagAgent.file_filters) == 1
        assert GenericRagAgent.file_filters[0]("test.txt")
        assert GenericRagAgent.file_filters[0]("test.md")
        assert not GenericRagAgent.file_filters[0]("test.exe")

    @patch('ragmatic.rag.bases.get_llm_client_class')
    @patch('ragmatic.rag.bases.get_store_cls')
    @patch('ragmatic.rag.bases.get_embedder_cls')
    def test_build_user_message(self, _, __, ___, rag_agent_config, mock_document_source):
        agent = GenericRagAgent(rag_agent_config, mock_document_source)
        query = "What is the main topic?"
        context_docs = {
            "doc1.txt": "This is the content of doc1.",
            "doc2.txt": "This is the content of doc2."
        }
        message = agent.build_user_message(query, context_docs)
        
        assert agent.prompt in message
        assert query in message
        assert agent.q_context_delimiter in message
        assert "```txt file=doc1.txt" in message
        assert "```txt file=doc2.txt" in message
        assert "This is the content of doc1." in message
        assert "This is the content of doc2." in message
