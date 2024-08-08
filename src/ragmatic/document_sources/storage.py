import os
from pydantic import BaseModel, Field
from .bases import DocumentSourceBase
from ..storage.store_factory import get_store_cls
from ..storage.bases import TextDocumentStore, VectorStore
from ..common_types import StoreConfig



class TextStoreDocumentSource(DocumentSourceBase):
    
    name = "text_store"

    def __init__(self, config: StoreConfig):
        config = StoreConfig(**config)
        super().__init__(config)
        self.config = config
        self._text_doc_store: TextDocumentStore = self._initialize_text_doc_store()
    
    def _initialize_text_doc_store(self):
        store_cls = get_store_cls(self.config.data_type, self.config.type)
        store_config = self.config.config
        return store_cls(store_config)

    def get_documents(self, document_names: list[str] = None) -> dict[str, str]:
        if document_names:
            return {
                document_name: self._text_doc_store.get_document(document_name)
                for document_name in document_names
            }
        return self._text_doc_store.get_all_documents()
