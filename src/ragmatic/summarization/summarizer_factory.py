from .bases import SummarizerBase
from .py_code_summarizer import PyCodeSummarizer
from ragmatic.utils import import_object

_summarizers = {
    PyCodeSummarizer.name: PyCodeSummarizer
}


def get_summarizer_class(summarizer_name: str) -> SummarizerBase:
    if summarizer_name not in _summarizers:
        try:
            return import_object(summarizer_name)
        except Exception:
            raise ValueError(f"Summarizer {summarizer_name} not found")
    return _summarizers[summarizer_name]
