import ast
from typing import Dict

from ._cyc_complexity import CyclomaticComplexityVisitor
from .bases import MetadataUnit, ModuleData, ClassData, FunctionData, StringTypes as st


class ClassAnalyzer(ast.NodeVisitor):
    def __init__(self, module_data: ModuleData):
        self.module_data = module_data
        self.current_class = None
        self.current_method = None

    def visit_ClassDef(self, node):
        class_name = node.name
        if class_name not in self.module_data.classes:
            self.module_data.classes[class_name] = ClassData()
        
        class_data = self.module_data.classes[class_name]
        class_data.bases = [self.get_full_name(base) for base in node.bases]
        docstring = ast.get_docstring(node)
        if docstring:
            class_data.docstring = docstring
        self.current_class = class_name
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node):
        if self.current_class:
            method_name = node.name
            if method_name not in self.module_data.classes[self.current_class].methods:
                self.module_data.classes[self.current_class].methods[method_name] = FunctionData(metrics={})
            method_data = self.module_data.classes[self.current_class].methods[method_name]
            docstring = ast.get_docstring(node)
            if docstring:
                method_data.docstring = docstring
            method_data.is_abstract = any(isinstance(decorator, ast.Name) and decorator.id == 'abstractmethod'
                                          for decorator in node.decorator_list)
            
            self.current_method = method_name
            self.generic_visit(node)
            method_data.metrics['cyclomatic_complexity'] = CyclomaticComplexityVisitor().get_complexity(node)
            self.current_method = None
        else:
            # This is a module-level function
            if node.name not in self.module_data.functions:
                self.module_data.functions[node.name] = FunctionData(metrics={})
            
            func_data = self.module_data.functions[node.name]
            func_data.metrics['cyclomatic_complexity'] = CyclomaticComplexityVisitor().get_complexity(node)

    def get_full_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self.get_full_name(node.value)}.{node.attr}"
        return ""


class ClassInfoUnit(MetadataUnit):
    def __init__(self, modules: Dict[st.ModuleName, ModuleData]):
        self.modules: Dict[st.ModuleName, ModuleData] = modules

    def analyze_file(self, module_data: ModuleData):
        tree = module_data.pytree
        analyzer = ClassAnalyzer(module_data)
        analyzer.visit(tree)
        self.modules[module_data.name] = module_data

    def print_info(self):
        print("\nClass Information:")
        for module_name, module_data in self.modules.items():
            print(f"Module: {module_name}")
            for class_name, class_data in module_data.classes.items():
                print(f"  Class: {class_name}")
                print(f"    Bases: {', '.join(class_data.bases)}")
                print(f"    Methods:")
                for method_name, method_data in class_data.methods.items():
                    print(f"      {method_name}:")
                    print(f"        Is Abstract: {method_data.is_abstract}")
                    print(f"        Cyclomatic Complexity: {method_data.metrics.get('cyclomatic_complexity', 'N/A')}")
            print(f"  Module-level functions:")
            for func_name, func_data in module_data.functions.items():
                print(f"    {func_name}:")
                print(f"      Cyclomatic Complexity: {func_data.metrics.get('cyclomatic_complexity', 'N/A')}")

    def get_data(self) -> Dict[str, ModuleData]:
        return self.modules
