import pytest
from ragmatic.summarization.summarizer_factory import get_summarizer_class, PyCodeSummarizer

def test_get_existing_summarizer():
    summarizer_class = get_summarizer_class("python_code")
    assert summarizer_class == PyCodeSummarizer

def test_get_non_existing_summarizer():
    with pytest.raises(ValueError, match="Summarizer non_existing not found"):
        get_summarizer_class("non_existing")

def test_get_summarizer_from_import(monkeypatch):
    def mock_import_object(name):
        class MockSummarizer:
            pass
        return MockSummarizer

    monkeypatch.setattr("ragmatic.summarization.summarizer_factory.import_object", mock_import_object)
    
    summarizer_class = get_summarizer_class("mock.summarizer.MockSummarizer")
    assert summarizer_class.__name__ == "MockSummarizer"
