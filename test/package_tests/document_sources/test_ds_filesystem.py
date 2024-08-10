from unittest.mock import MagicMock, patch
import pytest

from ragmatic.document_sources import filesystem


@pytest.fixture
def filesystem_dc_source_config():
    return filesystem.FilesystemDocumentSourceConfig(root_path="/path/to/root")

@pytest.fixture
def filesystem_dc_source_configdict(filesystem_dc_source_config):
    return filesystem_dc_source_config.model_dump()


@pytest.fixture
def fdc_source(filesystem_dc_source_configdict, monkeypatch):
    monkeypatch.setattr(filesystem.os.path, "exists", MagicMock(return_value=True))
    return filesystem.FilesystemDocumentSource(filesystem_dc_source_configdict)


@pytest.fixture
def pyfdc_source(filesystem_dc_source_configdict, monkeypatch):
    monkeypatch.setattr(filesystem.os.path, "exists", MagicMock(return_value=True))
    return filesystem.PycodeFilesystemDocumentSource(filesystem_dc_source_configdict)


def test_filesystem_dc_config(filesystem_dc_source_config):
    assert filesystem_dc_source_config.root_path == "/path/to/root"


class TestFilesystemDocumentSource:

    def test__init__(self, fdc_source):
        assert fdc_source.root_path == "/path/to/root"

    def test_get_documents(self, fdc_source, monkeypatch):
        monkeypatch.setattr(fdc_source, "_get_all_documents", MagicMock(return_value={"doc1": "content1", "doc2": "content2"}))
        monkeypatch.setattr(fdc_source, "_get_documents_by_names", MagicMock(return_value={"doc1": "content1"}))
        assert fdc_source.get_documents() == {"doc1": "content1", "doc2": "content2"}
        assert fdc_source.get_documents(["doc1"]) == {"doc1": "content1"}

    def test__get_documents_by_names(self, fdc_source):
        fdc_source._document_name_to_file_path = MagicMock(return_value="/path/to/doc1")
        with patch("builtins.open", MagicMock()) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "content1"
            assert fdc_source._get_documents_by_names(["doc1"]) == {"doc1": "content1"}
    
    def test__get_all_documents(self, fdc_source, monkeypatch):
        monkeypatch.setattr(fdc_source, "_file_path_to_doc_name", MagicMock(return_value="doc1.txt"))
        monkeypatch.setattr(filesystem.os, "walk", MagicMock(return_value=[("/path/to/root", [], ["doc1.txt"])]))
        with patch("builtins.open", MagicMock()) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "content1"
            assert fdc_source._get_all_documents() == {"doc1.txt": "content1"}

    def test__document_name_to_file_path(self, fdc_source):
        assert fdc_source._document_name_to_file_path("doc1") == "/path/to/root/doc1"

    def test__file_path_to_doc_name(self, fdc_source):
        assert fdc_source._file_path_to_doc_name("/path/to/root/doc1") == "doc1"
    

class TestPycodeFilesystemDocumentSource:

    def test__document_name_to_file_path(self, pyfdc_source):
        assert pyfdc_source._document_name_to_file_path("dir1.doc1") == "/path/to/root/dir1/doc1.py"

    def test__file_path_to_doc_name(self, pyfdc_source):
        assert pyfdc_source._file_path_to_doc_name("/path/to/root/dir1/doc1.py") == "dir1.doc1"

    def test__rel_path_to_module_name(self, pyfdc_source):
        assert pyfdc_source._rel_path_to_module_name("doc1.py") == "doc1"
        assert pyfdc_source._rel_path_to_module_name("path/to/doc1.py") == "path.to.doc1"
        assert pyfdc_source._rel_path_to_module_name("path/to/doc1") == "path.to.doc1"