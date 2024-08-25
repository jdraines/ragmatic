from typing import List, Callable, Optional

from ragmatic.utils.refs import RefBaseModel
from pydantic import Field, ConfigDict
from ..llm_ops.bases import LLMClientBase
from ..llm_ops.client_factory import get_llm_client_class
from ..storage.store_factory import get_store_cls
from ..storage.bases import VectorStore
from ..embeddings.bases import Embedder
from ..embeddings.embedder_factory import get_embedder_cls
from ragmatic.utils import CollectionKeyFormatter
from ragmatic.common_types import TypeAndConfig, StoreConfig
from ..document_sources.bases import DocumentSourceBase

class RagAgentConfig(RefBaseModel):
    llm: TypeAndConfig
    storage: StoreConfig
    encoder: TypeAndConfig
    n_nearest: Optional[int] = 10
    prompt: Optional[str] = Field(default="")
    system_prompt: Optional[str] = Field(default="")
    model_config = ConfigDict(extra= "allow")

class RagAgentBase:

    name: str = ""
    file_filters: List[Callable[[str], bool]] = [(lambda x: True)]
    prompt: str = ""
    system_prompt: str = ""
    q_context_delimiter: str = "\n=========\n"

    def __init__(self, config: RagAgentConfig, document_source: DocumentSourceBase):
        self.config = config
        self.prompt = config.prompt or self.prompt
        self.system_prompt = config.system_prompt or self.system_prompt
        self._document_source = document_source
        self._n = config.n_nearest
        self._llm_client: LLMClientBase = self._initialize_llm_client()
        self._vector_store: VectorStore = self._initialize_vector_store()
        self._embedder: Embedder = self._initialize_embedder()

    def _initialize_llm_client(self) -> LLMClientBase:
        client_class = get_llm_client_class(self.config.llm.type)
        llm_config = self.config.llm.config
        return client_class(llm_config)
    
    def _initialize_vector_store(self) -> VectorStore:
        store_class = get_store_cls(self.config.storage.data_type, self.config.storage.type)
        store_config = self.config.storage.config
        return store_class(store_config)

    def _initialize_embedder(self) -> Embedder:
        embedder_class = get_embedder_cls(self.config.encoder.type)
        embedder_config = self.config.encoder.config
        return embedder_class(embedder_config)
    
    def query(self, query: str):
        encoded_query = self._embedder.encode([query], query=True)[0]
        doc_name_matches = self._vector_store.query_byvector(encoded_query, self._n)
        doc_names = [CollectionKeyFormatter.extract_collection_name(match) for match in doc_name_matches]
        context_docs = self._document_source.get_documents(doc_names)
        message = self.build_user_message(query, context_docs)
        return self._llm_client.send_message(
            message,
            system_prompt=self.system_prompt
        )

    def build_user_message(self, query: str, context_docs: dict[str, str]):
        raise NotImplementedError
