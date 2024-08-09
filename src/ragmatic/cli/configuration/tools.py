from logging import getLogger
import os
from pathlib import Path
import typing as t

import yaml
from deepmerge import always_merger, Merger

from ._types import MasterConfig
from ...actions.bases import ActionConfig
from ...actions.encode import EncodeActionConfig
from ...actions.summarize import SummarizeActionConfig
from ...actions.rag import RagActionConfig
from ...rag.bases import TypeAndConfig, StoreConfig
from ..configuration.presets.preset_factory import get_preset, PresetData

logger = getLogger(__name__)


def load_config(configpath: Path = None) -> MasterConfig:
    with open(str(configpath)) as f:
        config = yaml.safe_load(f)
    return MasterConfig(**config)


def get_preset_config(preset_name, **vars) -> MasterConfig:
    preset = get_preset(preset_name)
    return preset.get_config(**vars)


def merge_defaults(config: MasterConfig,
                   preset_data: PresetData = None,
                   **vars
                   ) -> MasterConfig:
    config_d = config.model_dump()
    component_config = config_d.get("components", {})
    pipelines_config = config_d.get("pipelines", {})
    rag_query_command = config_d.get("rag_query_command", {})
    
    component_config = always_merger.merge(
        preset_data.get_component_config(**vars),
        component_config
    )

    pipelines_merger = Merger(
        [
            (dict, "merge"),
            (list, "override")
        ],
        ["override"],
        ["override"]
    )
    pipelines_config = pipelines_merger.merge(
        preset_data.get_pipelines_config(**vars),
        pipelines_config
    )
    rag_query_command = always_merger.merge(
        preset_data.get_rag_query_command_config(**vars),
        rag_query_command
    )
    return MasterConfig(
        project_name=config.project_name,
        components=component_config,
        pipelines=pipelines_config,
        rag_query_command=rag_query_command
    )

class ActionConfigFactory:
    
    def __init__(self, master_config: MasterConfig) -> None:
        self.master_config = master_config

    def dereference_action_config(self, action_config: ActionConfig) -> ActionConfig:
        raise NotImplementedError

    def dereference_document_source(self, document_source: TypeAndConfig) -> TypeAndConfig:

        if isinstance(document_source, str):
            document_source = self.master_config.components.document_sources[document_source]

        if all([
            document_source.type == "storage",
            isinstance(document_source.config, str)
        ]):
            source_name = document_source.config
            source_config = self.master_config.components.storage[source_name]
            document_source.config = source_config
        return document_source

    def dereference_storage(self, storage: t.Union[str, StoreConfig]) -> StoreConfig:
        if isinstance(storage, str):
            return self.master_config.components.storage[storage]
        return storage

    def dereference_llm(self, llm: t.Union[str, TypeAndConfig]) -> TypeAndConfig:
        if isinstance(llm, str):
            return self.master_config.components.llms[llm]
        return llm

    def dereference_encoder(self, encoder: t.Union[str, TypeAndConfig]) -> TypeAndConfig:
        if isinstance(encoder, str):
            return self.master_config.components.encoders[encoder]
        return encoder

    def dereference_summarizer(self, summarizer: t.Union[str, TypeAndConfig]) -> TypeAndConfig:
        if isinstance(summarizer, str):
            return self.master_config.components.summarizers[summarizer]
        return summarizer


class EncodeActionConfigFactory(ActionConfigFactory):

    def dereference_action_config(self, action_config: EncodeActionConfig) -> EncodeActionConfig:
        action_config.encoder = self.dereference_encoder(action_config.encoder)
        action_config.document_source = self.dereference_document_source(action_config.document_source)
        action_config.storage = self.dereference_storage(action_config.storage)        
        return action_config
    

class SummarizeActionConfigFactory(ActionConfigFactory):

    def dereference_action_config(self, action_config: SummarizeActionConfig) -> SummarizeActionConfig:
        action_config.summarizer = self.dereference_summarizer(action_config.summarizer)
        action_config.storage = self.dereference_storage(action_config.storage)
        action_config.summarizer.config.llm =\
            self.dereference_llm(action_config.summarizer.config.llm) 
        action_config.document_source = self.dereference_document_source(action_config.document_source)
        return action_config


class RagActionConfigFactory(ActionConfigFactory):
    
    def dereference_action_config(self, action_config: RagActionConfig) -> RagActionConfig:
        action_config.rag_agent.config.llm = self.dereference_llm(action_config.rag_agent.config.llm)
        action_config.rag_agent.config.storage = self.dereference_storage(action_config.rag_agent.config.storage)
        action_config.rag_agent.config.encoder = self.dereference_encoder(action_config.rag_agent.config.encoder)
        action_config.document_source = self.dereference_document_source(action_config.document_source)
        return action_config


def get_action_config_factory(action_name: str, master_config: MasterConfig) -> ActionConfigFactory:
    _actions = {
        "encode": EncodeActionConfigFactory,
        "summarize": SummarizeActionConfigFactory,
        "rag": RagActionConfigFactory
    }
    if action_name not in _actions:
        raise ValueError(f"Action '{action_name}' not found.")
    return _actions[action_name](master_config)
