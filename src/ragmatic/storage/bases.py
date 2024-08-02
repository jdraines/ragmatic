from abc import ABC, abstractmethod
import typing as t
from ..code_analysis.metadata_units.bases import ModuleData


class MetadataStore(ABC):

    store_name: str = None

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
    