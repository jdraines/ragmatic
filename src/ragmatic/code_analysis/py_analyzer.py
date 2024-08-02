import os
import ast
from typing import List, Dict
from collections import defaultdict
import networkx as nx

from .metadata_units import (
    ClassInfoUnit,
    FunctionInfoUnit,
    ImportInfoUnit,
    TypeInfoUnit,
    AttributeAccessUnit,
    MetadataUnit,
    PyCodeSummaryUnit,
    CodeMetricsUnit,
    ModuleData,
    StringTypes as st
)
from .bases import CodebaseAnalyzerBase


class PyCodebaseAnalyzer(CodebaseAnalyzerBase):

    analyzer_type = "python"
    file_filters: List = [(lambda x: x.endswith('.py'))]

    def __init__(self, root_dir: str, llm_config: dict = None):
        self.root_dir = root_dir
        self.llm_config = llm_config
        self.module_graph = nx.DiGraph()
        self.ca = defaultdict(int)
        self.ce = defaultdict(int)
        self.modules: Dict[st.ModuleName, ModuleData] = {}
        self.metadata_units = self._initialize_metadata_units()
        self.analyzed_modules = set()
        super().__init__(root_dir, llm_config)

    def _initialize_metadata_units(self) -> List[MetadataUnit]:
        units = [
            ClassInfoUnit(self.modules),
            FunctionInfoUnit(self.modules),
            ImportInfoUnit(self.modules),
            TypeInfoUnit(self.modules),
            AttributeAccessUnit(self.modules),
            CodeMetricsUnit(self.modules, self.module_graph)
        ]
        if self.llm_config is not None:
            units.append(PyCodeSummaryUnit(self.modules, self.llm_config))
        return units

    def analyze_file(self, file_path: str):
        with open(file_path, 'r') as file:
            content = file.read()
        
        module_name = self.file_path_to_module_name(file_path)
        tree = ast.parse(content)
        self.modules[module_name] = ModuleData(
            name=module_name,
            file_path=file_path,
            pytree=tree,
        )
        for unit in self.metadata_units:
            unit.analyze_file(self.modules[module_name])
