from typing import Dict, Any
from collections import defaultdict
import networkx as nx
import ast
from .bases import MetadataUnit
from dataclasses import dataclass, field

from .bases import (
    StringTypes as st,
    FunctionMetrics,
    FunctionData,
    ClassMetrics,
    ClassData,
    ModuleMetrics,
    ModuleData
)


class CodeMetricsUnit(MetadataUnit):
    def __init__(self, modules: Dict[st.ModuleName, ModuleData], module_graph):
        self.modules: Dict[st.ModuleName, ModuleData] = modules
        self.module_graph = module_graph

    def analyze_file(self, module_data: ModuleData):
        self.modules[module_data.name] = module_data
        self.analyze_coupling(module_data)
        self.analyze_cohesion(module_data)
        self.analyze_complexity(module_data)
        self.analyze_module_metrics(module_data)

    def analyze_coupling(self, module_data: ModuleData):
        ca = defaultdict(int)
        ce = defaultdict(int)

        for class_name, class_data in module_data.classes.items():
            dependencies = set(class_data.bases)
            for method_name, method_data in class_data.methods.items():
                dependencies.update(method_data.calls)
            
            cbo = len(dependencies)
            class_data.metrics = ClassMetrics(CBO=cbo, Ce=cbo, Ca=0, DIT=0, LCOM4=0)
            ce[module_data.name] += cbo

            for dep in dependencies:
                dep_module = dep.rsplit('.', 1)[0]
                if dep_module not in self.modules:
                    self.modules[dep_module] = ModuleData(name=dep_module, file_path="", imports=[])
                ca[dep_module] += 1
                if dep in self.modules[dep_module].classes:
                    self.modules[dep_module].classes[dep].metrics.Ca += 1

        return ca, ce

    def analyze_cohesion(self, module_data: ModuleData):
        for class_name, class_data in module_data.classes.items():
            methods = list(class_data.methods.keys())
            if len(methods) <= 1:
                class_data.metrics.LCOM4 = 1
            else:
                graph = nx.Graph()
                for method in methods:
                    graph.add_node(method)
                    method_data = class_data.methods[method]
                    for other_method in methods:
                        if method != other_method:
                            if set(method_data.calls) & set(class_data.methods[other_method].calls):
                                graph.add_edge(method, other_method)
                
                class_data.metrics.LCOM4 = nx.number_connected_components(graph)

    def analyze_complexity(self, module_data: ModuleData):
        for func_name, func_data in module_data.functions.items():
            func_data.metrics['cyclomatic_complexity'] = func_data.metrics.get('cyclomatic_complexity', 1)

        for class_name, class_data in module_data.classes.items():
            class_data.metrics.DIT = self._calculate_dit(module_data.name, class_name)
            for base in class_data.bases:
                base_module = base.rsplit('.', 1)[0]
                if base_module not in self.modules:
                    self.modules[base_module] = ModuleData(name=base_module, file_path="", imports=[])
                if base not in self.modules[base_module].classes:
                    self.modules[base_module].classes[base] = ClassData(metrics=ClassMetrics(CBO=0, DIT=0, Ce=0, Ca=0, LCOM4=0))
                self.modules[base_module].classes[base].metrics.Ca += 1
            
            for method_name, method_data in class_data.methods.items():
                method_data.metrics['cyclomatic_complexity'] = FunctionMetrics(cyclomatic_complexity=method_data.metrics.get('cyclomatic_complexity', 1))

    def _calculate_dit(self, module_name, class_name, visited=None):
        if visited is None:
            visited = set()
        if class_name in visited:
            return 0  # Avoid cycles
        visited.add(class_name)
        if module_name not in self.modules:
            return 0
        elif class_name not in self.modules[module_name].classes:
            return 0
        bases = self.modules[module_name].classes[class_name].bases
        if not bases:
            return 0
        bases = [base for base in bases if len(base.split('.')) > 1 and base.rsplit('.', 1)[0] in self.modules]
        if not bases:
            return 0
        return 1 + max(self._calculate_dit(base.rsplit('.', 1)[0], base.rsplit('.', 1)[1], visited.copy()) for base in bases)

    def analyze_module_metrics(self, module_data: ModuleData):
        ca, ce = self.analyze_coupling(module_data)
        instability = self.calculate_instability(ca[module_data.name], ce[module_data.name])
        abstractness = self.calculate_abstractness(module_data)
        distance_from_main = self.calculate_distance_from_main_sequence(instability, abstractness)
        
        module_data.metrics = ModuleMetrics(
            instability=instability,
            abstractness=abstractness,
            distance_from_main=distance_from_main
        )

    def calculate_instability(self, ca, ce):
        if ca + ce == 0:
            return 0  # Completely isolated module
        else:
            return ce / (ca + ce)

    def calculate_abstractness(self, module_data: ModuleData):
        classes = module_data.classes
        if not classes:
            return 0  # No classes in this module
        else:
            abstract_classes = sum(1 for cls in classes.values() if self.is_abstract_class(cls))
            return abstract_classes / len(classes)

    def calculate_distance_from_main_sequence(self, instability, abstractness):
        return abs(instability + abstractness - 1)

    def is_abstract_class(self, class_data: ClassData):
        if 'abc.ABC' in class_data.bases:
            return True
        return any(self.is_abstract_method(method) for method in class_data.methods.values())

    def is_abstract_method(self, method_data: FunctionData):
        return method_data.is_abstract

    def get_data(self) -> Dict[st.ModuleName, ModuleData]:
        return self.modules
