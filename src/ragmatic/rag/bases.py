from typing import List, Callable
import os

from pydantic import BaseModel, Field
from ..llm_ops.bases import LLMClientBase
from ..llm_ops.client_factory import get_llm_client_class
from ..storage.store_factory import get_store_cls
from ..storage.bases import VectorStore
from ..embeddings.bases import Embedder
from ..embeddings.embedder_factory import get_embedder_cls


class RagAgentConfig(BaseModel):
    llm_client_type: str
    llm_config: dict
    vector_store_name: str
    vector_store_config: dict
    embedder_type: str
    embeder_config: dict
    n_nearest: int = 10
    prompt: str = Field(default="")
    system_prompt: str = Field(default="")


class RagAgentBase:

    file_filters: List[Callable[[str], bool]] = [(lambda x: True)]
    prompt: str = ""
    system_prompt: str = ""
    q_context_delimiter: str = "\n=========\n"

    def __init__(self, root_dir: str, config: RagAgentConfig):
        self.root_dir = root_dir
        self.config = config
        self.prompt = config.get("prompt") or self.prompt
        self._n = config.n_nearest
        self._llm_client: LLMClientBase = self._initialize_llm_client()
        self._vector_store: VectorStore = self._initialize_vector_store()
        self._embedder: Embedder = self._initialize_embedder()

    def _initialize_llm_client(self) -> LLMClientBase:
        client_class = get_llm_client_class(self.config.llm_client_type)
        llm_config = self.config.llm_config
        return client_class(llm_config)
    
    def _initialize_vector_store(self) -> VectorStore:
        store_class = get_store_cls("vector", self.config.vector_store_name)
        store_config = self.config.vector_store_config
        return store_class(store_config)

    def _initialize_embedder(self) -> Embedder:
        embedder_class = get_embedder_cls(self.config.embedder_type)
        embedder_config = self.config.embeder_config
        return embedder_class(embedder_config)

    def load_docs(self, module_names: list[str]) -> dict[str, str]:
        docs = {}
        for module_name in module_names:
            filepath = self.module_name_to_file_path(module_name)
            relpath = os.path.relpath(filepath, self.root_dir)
            with open(filepath, "rt") as f:
                docs[relpath] = f.read()
        return docs

    def module_name_to_file_path(self, module_name: str):
        raise NotImplementedError
    
    def query(self, query: str):
        encoded_query = self._embedder.encode([query])[0]
        module_name_matches = self._vector_store.query_byvector(encoded_query, self._n)
        context_docs = self.load_docs(module_name_matches)
        message = self.build_user_message(query, context_docs)
        return self._llm_client.send_message(
            message,
            system_prompt=self.system_prompt
        )

    def build_user_message(self, query, context_docs):
        raise NotImplementedError