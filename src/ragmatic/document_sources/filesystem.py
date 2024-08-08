import os
import typing as t
from pydantic import BaseModel, Field
from .bases import DocumentSourceBase


class FilesystemDocumentSourceConfig(BaseModel):
    root_path: str


class FilesystemDocumentSource(DocumentSourceBase):
    
    name = "filesystem"
    file_filters: t.List[t.Callable[[str], bool]] = [(lambda x: True)]

    def __init__(self, config: FilesystemDocumentSourceConfig):
        config = FilesystemDocumentSourceConfig(**config)
        super().__init__(config)
        self.root_path = config.root_path

    def get_documents(self, document_names: t.Optional[list[str]] = None) -> dict[str, str]:
        if document_names is None:
            return self._get_all_documents()
        return self._get_documents_by_names(document_names)
    
    def _get_documents_by_names(self, document_names: list[str]) -> dict[str, str]:
        documents = {}
        for name in document_names:
            path = os.path.join(self.root_path, name)
            with open(path, "r") as f:
                documents[name] = f.read()
        return documents
    
    def _get_all_documents(self) -> dict[str, str]:
        walked = list(os.walk(self.root_dir))
        documents = {}
        for root, _, files in walked:
            for file in files:
                if all([f(file) for f in self.file_filters]):
                    file_path = os.path.join(root, file)
                    doc_name = self._file_path_to_doc_name(file_path)
                    with open(file_path, 'r') as file:
                        doc = file.read()
                    documents[doc_name] = doc

    def _file_path_to_doc_name(self, file_path: str) -> str:
        return file_path


class PycodeFilesystemDocumentSource(FilesystemDocumentSource):

    name = "pycode_filesystem"
    file_filters: t.List = [(lambda x: x.endswith('.py'))]
    
    def _file_path_to_doc_name(self, file_path: str) -> str:
        return file_path
