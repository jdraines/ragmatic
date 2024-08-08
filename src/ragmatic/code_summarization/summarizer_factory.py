from .bases import CodeSummarizerBase
from .py_summarizer import PyCodeSummarizer


_summarizers = {
    PyCodeSummarizer.name: PyCodeSummarizer
}


def get_summarizer_class(summarizer_name: str) -> CodeSummarizerBase:
    if summarizer_name not in _summarizers:
        raise ValueError(f"Summarizer {summarizer_name} not found")
    return _summarizers[summarizer_name]
