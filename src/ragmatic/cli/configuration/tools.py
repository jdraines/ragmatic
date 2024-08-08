from logging import getLogger
import os
from pathlib import Path

import yaml

from ._types import MasterConfig
from ...actions.bases import ActionConfig
from ...actions.encode import EncodeActionConfig
from ...actions.summarize import SummarizeActionConfig

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


class EncodeActionConfigFactory(ActionConfigFactory):

    def dereference_action_config(self, action_config: EncodeActionConfig) -> EncodeActionConfig:
        
        action_config.source = EncodeActionConfig.EncodeActionSourceSubconfig(**action_config.source)

        if isinstance(action_config.encoder, str):
            encoder_config = self.master_config.components.encoders[action_config.encoder]
            action_config.encoder = encoder_config

        if all([
            action_config.source.type == "storage",
            isinstance(action_config.source.config, str)
        ]):
            storage_name = action_config.source.config
            source_config = self.master_config.components.storage[storage_name]
            action_config.source.config = source_config

        if isinstance(action_config.storage, str):
            storage_name = action_config.storage
            storage_config = self.master_config.components.storage[storage_name]
            action_config.storage = storage_config
        
        return action_config
    

class SummarizeActionConfigFactory(ActionConfigFactory):

    def dereference_action_config(self, action_config: SummarizeActionConfig) -> SummarizeActionConfig:
        
        if isinstance(action_config.summarizer, str):
            summarizer_config = self.master_config.components.summarizers[action_config.summarizer]
            action_config.summarizer = summarizer_config

        if isinstance(action_config.storage, str):
            storage_name = action_config.storage
            storage_config = self.master_config.components.storage[storage_name]
            action_config.storage = storage_config
        
        if all([
                hasattr(action_config.summarizer.config, "llm"),
                not hasattr(action_config.summarizer.config, "llm_client_type")
            ]):
            llm_config = self.master_config.components.llms[action_config.summarizer.config.llm]
            action_config.summarizer.config.llm_client_type = llm_config.type
            action_config.summarizer.config.llm_config = llm_config.config

        return action_config


def get_action_config_factory(action_name: str, master_config: MasterConfig) -> ActionConfigFactory:
    _actions = {
        "encode": EncodeActionConfigFactory,
        "summarize": SummarizeActionConfigFactory
    }
    if action_name not in _actions:
        raise ValueError(f"Action '{action_name}' not found.")
    return _actions[action_name](master_config)
