import pytest
from ragmatic.summarization.bases import SummarizerBase, SummarizerConfig, TypeAndConfig
from ragmatic.llm_ops.bases import LLMClientBase, LLMState


class MockLLMClient(LLMClientBase):
    def send_message(self, message, system_prompt, role):
        return "Mock response"
    def send_chat(self, state: LLMState) -> str:
        return "Mock response"

class TestSummarizerBase:
    @pytest.fixture
    def config(self):
        return SummarizerConfig(
            llm=TypeAndConfig(type="mock", config={}),
            document_source={"type": "mock", "config": {}}
        )

    @pytest.fixture
    def summarizer(self, config, monkeypatch):
        monkeypatch.setattr("ragmatic.summarization.bases.get_llm_client_class", lambda x: MockLLMClient)
        
        class ConcreteSummarizer(SummarizerBase):
            def summarize_document(self, doc):
                return ["Summary 1", "Summary 2"]

        return ConcreteSummarizer(config)

    def test_initialization(self, summarizer):
        assert isinstance(summarizer._llm_client, MockLLMClient)
        assert summarizer._summaries == {}

    def test_summarize(self, summarizer):
        documents = {"doc1": "content1", "doc2": "content2"}
        result = summarizer.summarize(documents)
        assert result == {"doc1": ["Summary 1", "Summary 2"], "doc2": ["Summary 1", "Summary 2"]}

    def test_build_message(self, summarizer):
        summarizer._document_prompt = "Prompt:"
        result = summarizer._build_message("Code")
        assert result == "Prompt:\n---\nCode"

    def test_file_path_to_doc_name(self, summarizer):
        assert summarizer._file_path_to_doc_name("/path/to/file.py") == "/path/to/file.py"
