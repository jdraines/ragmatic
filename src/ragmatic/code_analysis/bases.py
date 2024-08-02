import os
import ast
from typing import List, Dict, Callable

import tqdm

from .metadata_units import StringTypes as st, MetadataUnit, ModuleData


class CodebaseAnalyzerBase:

    analyzer_type = None
    analyzed_modules: set = None
    modules: Dict[st.ModuleName, ModuleData] = None
    metadata_units: List[MetadataUnit] = None
    file_filters: List[Callable[[str], bool]] = [(lambda x: True)]

    def __init__(self, root_dir: str, llm_config: dict = None):
        self.root_dir = root_dir
        self.llm_config = llm_config
        if not self.modules:
            self.modules: Dict[st.ModuleName, ModuleData] = {}
        if not self.analyzed_modules:
            self.analyzed_modules = set()
        if not self.metadata_units:
            self.metadata_units = self._initialize_metadata_units()

    def _initialize_metadata_units(self) -> List[MetadataUnit]:
        raise NotImplementedError
    
    def analyze_file(self, file_path: str):
        raise NotImplementedError

    def get_analyzed_modules(self) -> List[str]:
        return sorted(list(self.analyzed_modules))

    def get_all_module_data(self):
        return self.modules
    
    def file_path_to_module_name(self, file_path: str) -> str:
        relative_path = os.path.relpath(file_path, self.root_dir)
        module_name = os.path.splitext(relative_path)[0].replace(os.path.sep, '.')
        return module_name
    
    def analyze_codebase(self):
        for root, _, files in tqdm.tqdm(os.walk(self.root_dir)):
            for file in files:
                if all([f(file) for f in self.file_filters]):
                    file_path = os.path.join(root, file)
                    module_name = self.file_path_to_module_name(file_path)
                    self.analyze_file(file_path)
                    self.analyzed_modules.add(module_name)
