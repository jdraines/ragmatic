import ast
from typing import Dict, Set
from collections import defaultdict

from .bases import (
    MetadataUnit,
    ModuleData,
    StringTypes as st,
    ClassData
)


class AttributeAccessAnalyzer(ast.NodeVisitor):
    def __init__(self, module_data: ModuleData):
        self.module_data = module_data
        self.current_class = None
        self.current_method = None

    def visit_ClassDef(self, node):
        self.current_class = node.name
        if self.current_class not in self.module_data.classes:
            self.module_data.classes[self.current_class] = ClassData()
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node):
        if self.current_class:
            self.current_method = node.name
            class_data = self.module_data.classes[self.current_class]
            if node.name.startswith('get_'):
                class_data.attribute_access.getters.add(node.name[4:])
            elif node.name.startswith('set_'):
                class_data.attribute_access.setters.add(node.name[4:])
            self.generic_visit(node)
            self.current_method = None

    def visit_Attribute(self, node):
        if isinstance(node.ctx, ast.Load) and self.current_class and self.current_method:
            if isinstance(node.value, ast.Name) and node.value.id == 'self':
                if node.attr.startswith("_"):
                    class_data = self.module_data.classes[self.current_class]
                    class_data.attribute_access.non_public.add(node.attr)
                else:
                    class_data = self.module_data.classes[self.current_class]
                    class_data.attribute_access.public.add(node.attr)
        self.generic_visit(node)


class AttributeAccessUnit(MetadataUnit):
    def __init__(self, modules: Dict[st.ModuleName, ModuleData]):
        self.modules: Dict[st.ModuleName, ModuleData] = modules

    def analyze_file(self, module_data: ModuleData):
        tree = module_data.pytree
        analyzer = AttributeAccessAnalyzer(module_data)
        analyzer.visit(tree)
        self.modules[module_data.name] = module_data

    def get_data(self) -> Dict[st.ModuleName, ModuleData]:
        return self.modules
