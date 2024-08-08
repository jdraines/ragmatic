import pickle
import typing as t

from pydantic import BaseModel, Field

from ..bases import MetadataStore, ModuleData
from .obj_store import PydictObjStore



class PydictMetadataStore(PydictObjStore, MetadataStore):

    name = 'pydict'
    _allowed_query_keys = [
        "name",
        "imports",
        "classes",
        "metrics.instability",
        "metrics.abstractness",
        "metrics.distance_from_main",
        r"classes.{*}.methods",
        r"classes.{*}.methods.{*}.return_type",
        r"classes.{*}.bases",
        r"classes.{*}.metrics.CBO",
        r"classes.{*}.metrics.DIT",
        r"classes.{*}.metrics.Ce",
        r"classes.{*}.metrics.Ca",
        r"classes.{*}.metrics.LCOM4",
        r"classes.{*}.is_abstract",
        r"functions.{*}.metrics.cyclomatic_complexity",
        r"functions.{*}.return_type",
    ]
    
    def store_all_module_data(self, modules: dict[str, ModuleData]):
        if self.__data is None:
            self.__data = {}
        for _, module_data in modules.items():
            self.store_module_data(module_data)

    def store_module_data(self, module_data: ModuleData):
        if self.__data is None:
            self._load_module_data()
        self.__data[module_data.name] = module_data
        with open(self.filepath, "wb") as f:
            pickle.dump(self._data, f)

    def query_modules(self, query: list[tuple[str, str, t.Any]]):
        return self.query_data(query)
    
    def get_module(self, module_name: str):
        return self.get_data(module_name)
