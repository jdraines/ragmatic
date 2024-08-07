import os
import typing as t
from ..bases import MetadataStore, VectorStore, SummaryStore, ModuleData
from .metadata_store import PydictMetadataStore
from .vector_store import PydictVectorStore
from .summary_store import PydictSummaryStore



class PydictOmniStore(MetadataStore, VectorStore, SummaryStore):
    
    _default_dirpath = 'data'

    def __init__(self, config):
        self.config = config
        self.dirpath = os.path.expanduser(config.get('dirpath', self._default_dirpath))
        os.makedirs(self.dirpath, exist_ok=True)
        self._metadata_store = self._init_metadata_store()
        self._vector_store = self._init_vector_store()
        self._summary_store = self._init_summary_store()

    def _init_metadata_store(self):
        filepath = os.path.join(self.dirpath, 'metadata.pkl')
        config = {"filepath": filepath}
        return PydictMetadataStore(config)
    
    def _init_vector_store(self):
        filepath = os.path.join(self.dirpath, 'vectors.pkl')
        config = {"filepath": filepath}
        return PydictVectorStore(config)
    
    def _init_summary_store(self):
        filepath = os.path.join(self.dirpath, 'summaries.pkl')
        config = {"filepath": filepath}
        return PydictSummaryStore(config)
    
    def store_all_module_data(self, modules: dict[str, ModuleData]):
        return self._metadata_store.store_all_module_data(modules)

    def store_module_data(self, module_data: ModuleData):
        return self._metadata_store.store_module_data(module_data)

    def query_modules(self, query: t.Any):
        return self._metadata_store.query_modules(query)

    def get_module(self, module_name: str):
        return self._metadata_store.get_module(module_name)
    
    def store_vectors(self, vectors: dict[str, t.Any]):
        return self._vector_store.store_vectors(vectors)
    
    def get_vectors(self, keys: list[str]):
        return self._vector_store.get_vectors(keys)
    
    def scan_keys(self, match: str):
        return self._vector_store.scan_keys(match)
    
    def query_vectors(self, query: t.Any):
        return self._vector_store.query_vectors(query)
    
    def store_summaries(self, summaries: dict[str, str]):
        return self._summary_store.store_summaries(summaries)
    
    def get_summary(self, key: str):
        return self._summary_store.get_summary(key)
    
    def __getattr__(self, name):
        if hasattr(self._metadata_store, name):
            return getattr(self._metadata_store, name)
        if hasattr(self._vector_store, name):
            return getattr(self._vector_store, name)
        if hasattr(self._summary_store, name):
            return getattr(self._summary_store, name)
        raise AttributeError(f"Attribute {name} not found in PydictOmniStore.")
