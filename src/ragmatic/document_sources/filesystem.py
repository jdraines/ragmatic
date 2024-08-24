import os
import typing as t
from ragmatic.utils.refs import RefBaseModel
from .bases import DocumentSourceBase
from ragmatic.utils import ALLOWED_FILE_TYPES


class FilesystemDocumentSourceConfig(RefBaseModel):
    root_path: str


class FilesystemDocumentSource(DocumentSourceBase):
    
    name = "filesystem"
    file_filters: t.List[t.Callable[[str], bool]] = [(lambda x: x.split(".")[-1] in ALLOWED_FILE_TYPES)]

    def __init__(self, config: FilesystemDocumentSourceConfig):
        config = FilesystemDocumentSourceConfig(**config)
        super().__init__(config)
        self.root_path = os.path.abspath(config.root_path)
        if not os.path.exists(self.root_path):
            raise FileNotFoundError(f"Root path {self.root_path} does not exist.")

    def get_documents(self, document_names: t.Optional[list[str]] = None) -> dict[str, str]:
        if document_names is None:
            return self._get_all_documents()
        return self._get_documents_by_names(document_names)
    
    def _get_documents_by_names(self, document_names: list[str]) -> dict[str, str]:
        documents = {}
        for name in document_names:
            path = self._document_name_to_file_path(name)
            with open(path, "r") as f:
                documents[name] = f.read()
        return documents
    
    def _get_all_documents(self) -> dict[str, str]:
        walked = list(os.walk(self.root_path))
        documents = {}
        for root, _, files in walked:
            for file in files:
                if all([f(file) for f in self.file_filters]):
                    file_path = os.path.join(root, file)
                    doc_name = self._file_path_to_doc_name(file_path)
                    with open(file_path, 'r') as file:
                        doc = file.read()
                    documents[doc_name] = doc
        return documents

    def _document_name_to_file_path(self, doc_name: str) -> str:
        return os.path.join(self.root_path, doc_name)

    def _file_path_to_doc_name(self, file_path: str) -> str:
        return os.path.relpath(file_path, self.root_path)


class PycodeFilesystemDocumentSource(FilesystemDocumentSource):

    name = "pycode_filesystem"
    file_filters: t.List = [(lambda x: x.endswith('.py'))]
    
    def _document_name_to_file_path(self, doc_name: str) -> str:
        if not doc_name.endswith('.py'):
            # assume a module name
            doc_name = doc_name.replace('.', os.path.sep) + '.py'
        return super()._document_name_to_file_path(doc_name)

    def _file_path_to_doc_name(self, file_path: str) -> str:
        relpath = super()._file_path_to_doc_name(file_path)
        return self._rel_path_to_module_name(relpath)
        
    def _rel_path_to_module_name(self, rel_path: str) -> str:
        module_name = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
        return module_name
