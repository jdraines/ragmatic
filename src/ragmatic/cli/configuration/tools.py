from logging import getLogger
import os
from pathlib import Path
import typing as t

import yaml

from ._types import MasterConfig
from ...actions.bases import ActionConfig
from ...actions.encode import EncodeActionConfig
from ...actions.summarize import SummarizeActionConfig
from ...actions.rag import RagActionConfig
from ...rag.bases import TypeAndConfig, StoreConfig

logger = getLogger(__name__)


def load_config(configpath: Path = None) -> MasterConfig:
    with open(str(configpath)) as f:
        config = yaml.safe_load(f)
    return MasterConfig(**config)


class ActionConfigFactory:
    
    def __init__(self, master_config: MasterConfig) -> None:
        self.master_config = master_config

    def dereference_action_config(self, action_config: ActionConfig) -> ActionConfig:
        raise NotImplementedError

    def dereference_document_source(self, document_source: TypeAndConfig) -> TypeAndConfig:
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
