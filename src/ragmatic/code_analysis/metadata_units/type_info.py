import ast
from typing import Dict, Any

from .bases import MetadataUnit, ModuleData, ClassData, FunctionData, StringTypes as st


class TypeAnalyzer(ast.NodeVisitor):
    def __init__(self, module_data: ModuleData):
        self.module_data = module_data
        self.current_class = None
        self.current_function = None

    def visit_ClassDef(self, node):
        self.current_class = node.name
        if self.current_class not in self.module_data.classes:
            self.module_data.classes[self.current_class] = ClassData()
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node):
        if self.current_class:
            class_data = self.module_data.classes[self.current_class]
            if node.name not in class_data.methods:
                class_data.methods[node.name] = FunctionData(metrics={})
            func_data = class_data.methods[node.name]
        else:
            if node.name not in self.module_data.functions:
                self.module_data.functions[node.name] = FunctionData(metrics={})
            func_data = self.module_data.functions[node.name]

        self.current_function = func_data

        for arg in node.args.args:
            if arg.annotation:
                if not hasattr(func_data, 'params'):
                    func_data.params = {}
                func_data.params[arg.arg] = self.get_type_name(arg.annotation)

        if node.returns:
            func_data.return_type = self.get_type_name(node.returns)

        self.generic_visit(node)
        self.current_function = None

    def visit_AnnAssign(self, node):
        if isinstance(node.target, ast.Name):
            var_name = node.target.id
            var_type = self.get_type_name(node.annotation)
            if self.current_class:
                class_data = self.module_data.classes[self.current_class]
                if not hasattr(class_data, 'type_info'):
                    class_data.type_info = {}
                class_data.type_info[var_name] = var_type
            else:
                if not hasattr(self.module_data, 'variables'):
                    self.module_data.variables = {}
                self.module_data.variables[var_name] = var_type

    def get_type_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self.get_type_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self.get_type_name(node.value)}[{self.get_type_name(node.slice)}]"
        elif isinstance(node, ast.Tuple):
            return f"Tuple[{', '.join(self.get_type_name(elt) for elt in node.elts)}]"
        elif isinstance(node, ast.Constant):
            return type(node.value).__name__
        else:
            return str(node)


class TypeInfoUnit(MetadataUnit):
    def __init__(self, modules: Dict[st.ModuleName, ModuleData]):
        self.modules: Dict[st.ModuleName, ModuleData] = modules

    def analyze_file(self, module_data: ModuleData):
        tree = module_data.pytree
        analyzer = TypeAnalyzer(module_data)
        analyzer.visit(tree)
        self.modules[module_data.name] = module_data

    def get_data(self) -> Dict[st.ModuleName, ModuleData]:
        return self.modules