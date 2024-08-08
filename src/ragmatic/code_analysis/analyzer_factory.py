from .bases import CodebaseAnalyzerBase
from .py_analyzer import PyCodebaseAnalyzer
from ragmatic.utils import import_object

_analyzers = {
    PyCodebaseAnalyzer.analyzer_type: PyCodebaseAnalyzer,
}


def get_analyzer_cls(analyzer_type: str) -> CodebaseAnalyzerBase:
    if analyzer_type not in _analyzers:
        try:
            return import_object(analyzer_type)
        except Exception:
            raise ValueError(f"Analyzer type {analyzer_type} not found")
    return _analyzers[analyzer_type]
