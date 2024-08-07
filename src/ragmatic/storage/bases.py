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
    def query_vectors(self, query: t.Any):
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
