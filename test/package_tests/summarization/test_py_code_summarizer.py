import pytest
from ragmatic.summarization.py_code_summarizer import PyCodeSummarizer
from ragmatic.summarization.bases import SummarizerConfig, TypeAndConfig
from ragmatic.llm_ops.bases import LLMClientBase, LLMState


class MockLLMClient(LLMClientBase):
    def send_message(self, message, system_prompt, role):
        return "<summary>Summary 1</summary><summary>Summary 2</summary>"
    def send_chat(self, state: LLMState) -> str:
        return "Mock response"


class TestPyCodeSummarizer:
    @pytest.fixture
    def config(self):
        return SummarizerConfig(
            llm=TypeAndConfig(type="mock", config={}),
            document_source={"type": "mock", "config": {}}
        )

    @pytest.fixture
    def summarizer(self, config, monkeypatch):
        monkeypatch.setattr("ragmatic.summarization.bases.get_llm_client_class", lambda x: MockLLMClient)
        return PyCodeSummarizer(config)

    def test_initialization(self, summarizer):
        assert summarizer.name == "python_code"
        assert len(summarizer.file_filters) == 1
        assert summarizer.file_filters[0]("test.py") == True
        assert summarizer.file_filters[0]("test.txt") == False

    def test_summarize_document(self, summarizer):
        result = summarizer.summarize_document("def test():\n    pass")
        assert result == ["Summary 1", "Summary 2"]

    def test_file_path_to_doc_name(self, summarizer):
        assert summarizer._file_path_to_doc_name("./path/to/file.py") == "path.to.file"

    def test_file_path_to_module_name(self, summarizer):
        assert summarizer._file_path_to_module_name("path/to/file.py") == "path.to.file"
