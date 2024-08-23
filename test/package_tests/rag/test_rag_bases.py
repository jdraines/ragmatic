import pytest
from unittest.mock import Mock, patch
from ragmatic.rag.bases import RagAgentBase, RagAgentConfig
from ragmatic.document_sources.bases import DocumentSourceBase

@pytest.fixture
def mock_document_source():
    return Mock(spec=DocumentSourceBase)

@pytest.fixture
def rag_agent_config():
    return RagAgentConfig(
        llm={"type": "mock_llm", "config": {}},
        storage={"data_type": "mock_data", "type": "mock_store", "config": {}},
        encoder={"type": "mock_encoder", "config": {}},
        n_nearest=5,
        prompt="Test prompt",
        system_prompt="Test system prompt"
    )

class TestRagAgentBase:
    @patch('ragmatic.rag.bases.get_llm_client_class')
    @patch('ragmatic.rag.bases.get_store_cls')
    @patch('ragmatic.rag.bases.get_embedder_cls')
    def test_initialization(self, mock_get_embedder_cls, mock_get_store_cls, mock_get_llm_client_class, rag_agent_config, mock_document_source):
        mock_get_llm_client_class.return_value = Mock()
        mock_get_store_cls.return_value = Mock()
        mock_get_embedder_cls.return_value = Mock()

        class ConcreteRagAgent(RagAgentBase):
            def build_user_message(self, query, context_docs):
                pass

        agent = ConcreteRagAgent(rag_agent_config, mock_document_source)

        assert agent.config == rag_agent_config
        assert agent.prompt == "Test prompt"
        assert agent._document_source == mock_document_source
        assert agent._n == 5
        assert isinstance(agent._llm_client, Mock)
        assert isinstance(agent._vector_store, Mock)
        assert isinstance(agent._embedder, Mock)

    @patch('ragmatic.rag.bases.get_llm_client_class')
    @patch('ragmatic.rag.bases.get_store_cls')
    @patch('ragmatic.rag.bases.get_embedder_cls')
    def test_query(self, mock_get_embedder_cls, mock_get_store_cls, mock_get_llm_client_class, rag_agent_config, mock_document_source):
        mock_get_llm_client_class.return_value = Mock()
        mock_get_store_cls.return_value = Mock()
        mock_get_embedder_cls.return_value = Mock()

        class ConcreteRagAgent(RagAgentBase):
            def build_user_message(self, query, context_docs):
                return f"Query: {query}, Docs: {context_docs}"

        agent = ConcreteRagAgent(rag_agent_config, mock_document_source)
        agent._embedder.encode.return_value = [Mock()]
        agent._vector_store.query_byvector.return_value = ["doc1", "doc2"]
        agent._document_source.get_documents.return_value = {"doc1": "content1", "doc2": "content2"}

        result = agent.query("test query")

        agent._embedder.encode.assert_called_once_with(["test query"])
        agent._vector_store.query_byvector.assert_called_once()
        agent._document_source.get_documents.assert_called_once_with(["doc1", "doc2"])
        agent._llm_client.send_message.assert_called_once_with(
            "Query: test query, Docs: {'doc1': 'content1', 'doc2': 'content2'}",
            system_prompt="Test system prompt"
        )
        assert result == agent._llm_client.send_message.return_value

    @patch('ragmatic.rag.bases.get_llm_client_class')
    @patch('ragmatic.rag.bases.get_store_cls')
    @patch('ragmatic.rag.bases.get_embedder_cls')
    def test_build_user_message_not_implemented(self, _, __, ___, rag_agent_config, mock_document_source):
        agent = RagAgentBase(rag_agent_config, mock_document_source)
        with pytest.raises(NotImplementedError):
            agent.build_user_message("query", {})