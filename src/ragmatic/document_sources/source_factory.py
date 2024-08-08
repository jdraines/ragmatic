from .bases import DocumentSourceBase
from .filesystem import FilesystemDocumentSource, PycodeFilesystemDocumentSource
from .storage import TextStoreDocumentSource
from ragmatic.utils import import_object


_sources = {
    FilesystemDocumentSource.name: FilesystemDocumentSource,
    PycodeFilesystemDocumentSource.name: PycodeFilesystemDocumentSource,
    TextStoreDocumentSource.name: TextStoreDocumentSource,
}


def get_document_source_cls(name: str) -> DocumentSourceBase:
    if name not in _sources:
        try:
            return import_object(name)
        except Exception:
            raise ValueError(f"Document source '{name}' not found.")
    return _sources[name]
