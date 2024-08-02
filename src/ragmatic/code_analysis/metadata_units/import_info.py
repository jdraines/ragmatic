import ast
from typing import List, Dict
import networkx as nx

from .bases import MetadataUnit, ModuleData, StringTypes as st


class ImportAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.imports: List[str] = []

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.append(node.module)
        for alias in node.names:
            if alias.name == 'abstractmethod':
                self.imports.append('abc.abstractmethod')


class ImportInfoUnit(MetadataUnit):
    def __init__(self, modules: Dict[st.ModuleName, ModuleData]):
        self.modules: Dict[st.ModuleName, ModuleData] = modules
        self.import_graph = nx.DiGraph()

    def analyze_file(self, module_data: ModuleData):
        tree = module_data.pytree
        analyzer = ImportAnalyzer()
        analyzer.visit(tree)
        module_data.imports = analyzer.imports
        self.update_import_graph(module_data.name, module_data.imports)
        self.modules[module_data.name] = module_data

    def update_import_graph(self, module_name: str, imports: List[str]):
        self.import_graph.add_node(module_name)
        for imp in imports:
            self.import_graph.add_edge(module_name, imp)

    def get_data(self) -> Dict[str, ModuleData]:
        return self.modules
