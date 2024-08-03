import ast
import os
from typing import Dict, Any
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

from .bases import MetadataUnit, ModuleData, ClassData, FunctionData, StringTypes as st
from ...llm_ops.client_factory import get_llm_client_class, LLMClient


class PyCodeSummaryUnit(MetadataUnit):

    def __init__(self, modules: Dict[st.ModuleName, ModuleData], llm_client_config: dict = None):
        self.modules: Dict[st.ModuleName, ModuleData] = modules
        llm_client_type = llm_client_config.pop("type")
        self.client: LLMClient = get_llm_client_class(llm_client_type)(llm_client_config or {})

    def analyze_file(self, module_data: ModuleData):
        tree = module_data.pytree
        analyzer = PyCodeSummaryAnalyzer(module_data, self)
        analyzer.visit(tree)
        self.modules[module_data.name] = module_data

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def generate_summary(self, code: str, context: str = "") -> str:
        prompt = f"Summarize the following Python code:\n\n{code}\n\nHere is the context in which this code is found: {context}"
        system_prompt = "You are a helpful assistant that carefully summarizes Python code, with attention to how it is used in its context."
        return self.client.send_message(
            message=prompt,
            system_prompt=system_prompt,
        )

    def get_data(self) -> Dict[st.ModuleName, ModuleData]:
        return self.modules


class PyCodeSummaryAnalyzer(ast.NodeVisitor):
    def __init__(self, module_data: ModuleData, summary_unit: PyCodeSummaryUnit):
        self.module_data = module_data
        self.summary_unit = summary_unit
        self.current_class = None
        self.current_function = None
        self.module_code = ""
        self.class_code = ""

    def visit_Module(self, node):
        self.module_code = ast.unparse(node)
        context = f"This is the entire module {self.module_data.name}"
        self.module_data.summary = self.summary_unit.generate_summary(self.module_code, context)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.current_class = node.name
        if self.current_class not in self.module_data.classes:
            self.module_data.classes[self.current_class] = ClassData()
        class_data = self.module_data.classes[self.current_class]
        
        self.class_code = ast.unparse(node)
        context = f"This class is part of the module {self.module_data.name}. Here's the full module code:\n\n{self.module_code}"
        class_data.summary = self.summary_unit.generate_summary(self.class_code, context)
        
        self.generic_visit(node)
        self.current_class = None
        self.class_code = ""

    def visit_FunctionDef(self, node):
        if self.current_class:
            class_data = self.module_data.classes[self.current_class]
            if node.name not in class_data.methods:
                class_data.methods[node.name] = FunctionData(metrics={})
            func_data = class_data.methods[node.name]
            context = f"This method is part of the class {self.current_class}. Here's the full class code:\n\n{self.class_code}"
        else:
            if node.name not in self.module_data.functions:
                self.module_data.functions[node.name] = FunctionData(metrics={})
            func_data = self.module_data.functions[node.name]
            context = f"This function is part of the module {self.module_data.name}. Here's the full module code:\n\n{self.module_code}"
        
        self.current_function = func_data
        function_code = ast.unparse(node)
        func_data.summary = self.summary_unit.generate_summary(function_code, context)
        
        self.generic_visit(node)
        self.current_function = None