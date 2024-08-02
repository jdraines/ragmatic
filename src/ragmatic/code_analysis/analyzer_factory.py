from .bases import CodebaseAnalyzerBase
from .py_analyzer import PyCodebaseAnalyzer


_analyzers = {
    PyCodebaseAnalyzer.analyzer_type: PyCodebaseAnalyzer,
}


def get_analyzer_cls(analyzer_type: str) -> CodebaseAnalyzerBase:
    if analyzer_type not in _analyzers:
        raise ValueError(f"Analyzer type {analyzer_type} not found")
    return _analyzers[analyzer_type]
