from .bases import DocumentSourceBase
from .filesystem import FilesystemDocumentSource, PycodeFilesystemDocumentSource
from .storage import TextStoreDocumentSource


_sources = {
    FilesystemDocumentSource.name: FilesystemDocumentSource,
    PycodeFilesystemDocumentSource.name: PycodeFilesystemDocumentSource,
    TextStoreDocumentSource.name: TextStoreDocumentSource,
}

def get_document_source_cls(name: str) -> DocumentSourceBase:
    if name not in _sources:
        raise ValueError(f"Document source '{name}' not found.")
    return _sources[name]
