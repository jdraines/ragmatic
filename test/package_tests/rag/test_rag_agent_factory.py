import pytest
from ragmatic.rag.rag_agent_factory import get_rag_agent_class
from ragmatic.rag.pycode_rag_agent import PyCodeRagAgent
from ragmatic.rag.generic import GenericRagAgent

class TestRagAgentFactory:
    def test_get_rag_agent_class_python_code(self):
        agent_class = get_rag_agent_class("python_code")
        assert agent_class == PyCodeRagAgent

    def test_get_rag_agent_class_generic(self):
        agent_class = get_rag_agent_class("generic")
        assert agent_class == GenericRagAgent

    def test_get_rag_agent_class_custom(self):
        with pytest.raises(ValueError):
            get_rag_agent_class("custom_agent")

    def test_get_rag_agent_class_invalid(self):
        with pytest.raises(ValueError):
            get_rag_agent_class("invalid_agent")

    def test_get_rag_agent_class_full_path(self):
        agent_class = get_rag_agent_class("ragmatic.rag.pycode_rag_agent.PyCodeRagAgent")
        assert agent_class == PyCodeRagAgent