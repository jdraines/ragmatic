import typing as t
from logging import getLogger

from ragmatic.utils.refs import RefBaseModel

from ragmatic.storage.store_factory import get_store_cls
from ragmatic.storage.bases import TextDocumentStore, VectorStore
from ragmatic.embeddings.embedder_factory import get_embedder_cls, Embedder
from ._types import EncoderComponentConfig, StorageComponentConfig
from .bases import Action, ActionConfig
from ..document_sources.source_factory import get_document_source_cls, DocumentSourceBase
from ragmatic.common_types import TypeAndConfig


logger = getLogger(__name__)


class EncodeActionConfig(ActionConfig):
    encoder: EncoderComponentConfig
    document_source: TypeAndConfig
    storage: StorageComponentConfig
    

class EncodeAction(Action):

    config_cls = EncodeActionConfig
    name = "encode"

    def __init__(self, config: EncodeActionConfig):
        super().__init__(config)
        self._embedder: Embedder = self._initialize_encoder()
        self._source: DocumentSourceBase = self._initialize_source()
        self._vector_store: VectorStore = self._initialize_storage()

    def _initialize_encoder(self):
        embedder_cls = get_embedder_cls(self.config.encoder.type)
        embedder_config = self.config.encoder.config
        return embedder_cls(embedder_config)
    
    def _initialize_storage(self, data_type=None, type_=None, config=None) -> TextDocumentStore:
        data_type = data_type or self.config.storage.data_type
        type_ = type_ or self.config.storage.type
        store_cls = get_store_cls(data_type, type_)
        store_config = config or self.config.storage.config
        return store_cls(store_config)
    
    def _initialize_source(self) -> DocumentSourceBase:
        source_cls = get_document_source_cls(self.config.document_source.type)
        source_config = self.config.document_source.config
        return source_cls(source_config)
    
    def execute(self):
        logger.info("Loading source data")
        source_data = self._source.get_documents()
        logger.info(f"Encoding {len(source_data)} documents...")
        _encoded_data = self._embedder.encode([
            doc for _, doc in source_data.items()
        ])
        embeddings = {
            key: value for key, value in zip(source_data.keys(), _encoded_data)
        }
        logger.info(f"Storing {len(embeddings)} embeddings...")
        self._vector_store.store_vectors(embeddings)
        logger.info(f"Embeddings stored in {self._vector_store.name} storage.")
