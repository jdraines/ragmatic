import ast
from typing import Dict, Set
from dataclasses import dataclass, field

from .bases import MetadataUnit, ModuleData, FunctionData, FunctionMetrics
from ._cyc_complexity import CyclomaticComplexityVisitor


class FunctionAnalyzer(ast.NodeVisitor):
    def __init__(self, module_data: ModuleData):
        self.module_data = module_data
        self.current_function = None

    def visit_FunctionDef(self, node):
        cyc_visitor = CyclomaticComplexityVisitor()
        func_name = node.name
        
        if func_name not in self.module_data.functions:
            self.module_data.functions[func_name] = FunctionData(
                calls=set(),
                is_abstract=any(isinstance(decorator, ast.Name) and decorator.id == 'abstractmethod'
                                for decorator in node.decorator_list),
                metrics={}
            )
        
        docstring = ast.get_docstring(node)
        if docstring:
            self.module_data.functions[func_name].docstring = docstring
        self.current_function = func_name
        self.generic_visit(node)
        self.module_data.functions[func_name].metrics['cyclomatic_complexity'] = FunctionMetrics(
            cyclomatic_complexity=cyc_visitor.get_complexity(node)
        )
        self.current_function = None

    def visit_Call(self, node):
        if self.current_function:
            if isinstance(node.func, ast.Name):
                self.module_data.functions[self.current_function].calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                self.module_data.functions[self.current_function].calls.add(node.func.attr)
        self.generic_visit(node)


class FunctionInfoUnit(MetadataUnit):
    def __init__(self, modules: Dict[str, ModuleData]):
        self.modules: Dict[str, ModuleData] = modules

    def analyze_file(self, module_data: ModuleData):
        tree = module_data.pytree
        analyzer = FunctionAnalyzer(module_data)
        analyzer.visit(tree)
        self.modules[module_data.name] = module_data

    def get_data(self) -> Dict[str, ModuleData]:
        return self.modules