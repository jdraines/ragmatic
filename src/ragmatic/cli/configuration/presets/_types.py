from string import Template
import typing as t
import json

from ragmatic.utils.refs import (
    ref_dumper_default,
    RefDecoder,
)
from .._types import MasterConfig


class PresetData:

    def __init__(self,
                 components,
                 pipelines,
                 rag_query_command,
                 variable_defaults: dict = None
                 ):
        self.components = components
        self.pipelines = pipelines
        self.rag_query_command = rag_query_command
        self.variable_defaults: dict = variable_defaults or {}

    def get_config(self, **vars):
        return MasterConfig(
            project_name="",
            components=self.get_component_config(**vars),
            pipelines=self.get_pipelines_config(**vars),
            rag_query_command=self.get_rag_query_command_config(**vars)
        )

    def get_component_config(self, **vars):
        return self._apply_variables(self.components, **vars)

    def get_pipelines_config(self, **vars):
        return self._apply_variables(self.pipelines, **vars)
    
    def get_rag_query_command_config(self, **vars):
        return self._apply_variables(self.rag_query_command, **vars)

    def _apply_variables(self, config: t.Dict, **vars):
        for v in vars:
            if v not in self.variable_defaults:
                raise ValueError(f"Unknown variable: {v}")
        variables = self.variable_defaults.copy()
        variables.update(vars)
        json_config = json.dumps(config, default=ref_dumper_default)
        json_config = Template(json_config).substitute(variables)
        return json.loads(json_config, cls=RefDecoder)
    