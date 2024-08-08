from abc import ABC, abstractmethod
import typing as t
from ..code_analysis.metadata_units.bases import ModuleData


class MetadataStore(ABC):

    name: str = None

    @abstractmethod
    def store_all_module_data(self, modules: dict[str, ModuleData]):
        pass

    @abstractmethod
    def store_module_data(self, module_data: ModuleData):
        pass

    @abstractmethod
    def query_modules(self, query: t.Any):
        pass

    @abstractmethod
    def get_module(self, module_name: str):
        pass
    

class VectorStore(ABC):
    
    name: str = None

    @abstractmethod
    def store_vectors(self, vectors: dict[str, t.Any]):
        pass

    @abstractmethod
    def get_vectors(self, keys: list[str]):
        pass

    @abstractmethod
    def scan_keys(self, match: str):
        pass

    @abstractmethod
    def query(self, query: t.Any):
        pass

    @abstractmethod
    def query_byvector(self, vector: t.Sequence[float], n: int = None):
        pass


class SummaryStore(ABC):

    name: str = None

    @abstractmethod
    def store_summaries(self, summaries: dict[str, str]):
        pass

    @abstractmethod
    def get_summary(self, key: str):
        pass

    @abstractmethod
    def get_all_summaries(self):
        pass


class OmniStore(MetadataStore, VectorStore, SummaryStore):
    
    _vector_store: VectorStore = None
    _metadata_store: MetadataStore = None
    _summary_store: SummaryStore = None


    def __init__(self, config):
        raise NotImplementedError

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
    
    def query(self, query: t.Any):
        return self._vector_store.query(query)
    
    def query_byvector(self, vector: t.Sequence[float], n: int = None):
        return self._vector_store.query_byvector(vector, n)
    
    def store_summaries(self, summaries: dict[str, str]):
        return self._summary_store.store_summaries(summaries)
    
    def get_summary(self, key: str):
        return self._summary_store.get_summary(key)
    
    def get_all_summaries(self):
        return self._summary_store.get_all_summaries()

    def __getattr__(self, name):
        if hasattr(self._metadata_store, name):
            return getattr(self._metadata_store, name)
        if hasattr(self._vector_store, name):
            return getattr(self._vector_store, name)
        if hasattr(self._summary_store, name):
            return getattr(self._summary_store, name)
        raise AttributeError(f"Attribute {name} not found in {type(self).__name__}.")
