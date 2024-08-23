
import pytest
from unittest.mock import patch
from ragmatic.document_sources.source_factory import get_document_source_cls
from ragmatic.document_sources.bases import DocumentSourceBase
from ragmatic.document_sources.filesystem import FilesystemDocumentSource, PycodeFilesystemDocumentSource
from ragmatic.document_sources.storage import TextStoreDocumentSource

def test_get_document_source_cls_known_sources():
    assert get_document_source_cls(FilesystemDocumentSource.name) == FilesystemDocumentSource
    assert get_document_source_cls(PycodeFilesystemDocumentSource.name) == PycodeFilesystemDocumentSource
    assert get_document_source_cls(TextStoreDocumentSource.name) == TextStoreDocumentSource

def test_get_document_source_cls_unknown_source():
    with pytest.raises(ValueError, match="Document source 'unknown_source' not found."):
        get_document_source_cls("unknown_source")

@patch('ragmatic.document_sources.source_factory.import_object')
def test_get_document_source_cls_custom_source(mock_import_object):
    class CustomSource(DocumentSourceBase):
        pass

    mock_import_object.return_value = CustomSource
    
    result = get_document_source_cls("custom.source.CustomSource")
    
    assert result == CustomSource
    mock_import_object.assert_called_once_with("custom.source.CustomSource")

@patch('ragmatic.document_sources.source_factory.import_object')
def test_get_document_source_cls_import_error(mock_import_object):
    mock_import_object.side_effect = ImportError("Module not found")
    
    with pytest.raises(ValueError, match="Document source 'custom.source.NonExistentSource' not found."):
        get_document_source_cls("custom.source.NonExistentSource")

def test_get_document_source_cls_return_type():
    result = get_document_source_cls(FilesystemDocumentSource.name)
    assert issubclass(result, DocumentSourceBase)

@pytest.mark.parametrize("source_name", [
    FilesystemDocumentSource.name,
    PycodeFilesystemDocumentSource.name,
    TextStoreDocumentSource.name
])
def test_get_document_source_cls_all_known_sources(source_name):
    result = get_document_source_cls(source_name)
    assert issubclass(result, DocumentSourceBase)

