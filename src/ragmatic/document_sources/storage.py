from .bases import DocumentSourceBase
from ..storage.store_factory import get_store_cls
from ..storage.bases import TextDocumentStore
from ..common_types import StoreConfig



class TextStoreDocumentSource(DocumentSourceBase):
    
    name = "storage"

    def __init__(self, config: StoreConfig):
        if isinstance(config, dict):
            config = StoreConfig(**config)
        super().__init__(config)
        self._text_doc_store: TextDocumentStore = self._initialize_text_doc_store()
    
    def _initialize_text_doc_store(self):
        store_cls = get_store_cls(self.config.data_type, self.config.type)
        store_config = self.config.config
        return store_cls(store_config)

    def get_documents(self, document_names: list[str] = None) -> dict[str, str]:
        if document_names:
            return dict(
                zip(
                    document_names,
                    self._text_doc_store.get_documents(document_names)
                )
            )
        return self._text_doc_store.get_all_documents()
