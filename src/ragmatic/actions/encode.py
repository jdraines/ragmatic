import typing as t
from logging import getLogger

from pydantic import BaseModel

from ragmatic.storage.store_factory import get_store_cls
from ragmatic.storage.bases import TextDocumentStore, VectorStore
from ragmatic.embeddings.embedder_factory import get_embedder_cls, Embedder
from ._types import EncoderComponentConfig, StorageComponentConfig
from .bases import Action, ActionConfig

logger = getLogger(__name__)


class EncodeActionConfig(ActionConfig):

    class EncodeActionSourceSubconfig(BaseModel):
        type: t.Union[str, t.Literal["storage"]]
        config: t.Union[str, StorageComponentConfig]

    encoder: t.Union[str, EncoderComponentConfig]
    source: EncodeActionSourceSubconfig
    storage: t.Union[str, StorageComponentConfig]
    

class SourceWrapper:

    def __init__(self,
                 source: t.Any,
                 source_call_method: str,
                 source_call_args: t.List[t.Any] = None
                 ):
        self.source = source
        self.source_call_method = source_call_method
        self.source_call_args = source_call_args or []

    def __call__(self) -> dict[str, str]:
        return getattr(self.source, self.source_call_method)(*self.source_call_args)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.source}.{self.source_call_method})"


Source = t.Callable[[], dict[str, str]]


class EncodeAction(Action):

    config_cls = EncodeActionConfig
    name = "encode"

    def __init__(self, config: EncodeActionConfig):
        super().__init__(config)
        self.config = config
        self._embedder: Embedder = self._initialize_encoder()
        self._source: Source = self._initialize_source()
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
    
    def _initialize_source(self) -> t.Union[t.Any, TextDocumentStore]:
        if self.config.source.type == "storage":
            data_type = self.config.source.config.data_type
            type_ = self.config.source.config.type
            config = self.config.source.config.config
            return SourceWrapper(
                self._initialize_storage(data_type, type_, config),
                "get_all_documents"
            )
        return None
    
    def execute(self):
        logger.info("Loading source data")
        source_data = self._source()
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
