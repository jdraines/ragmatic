import typing as t
from ragmatic.utils.refs import RefBaseModel
from pydantic import ConfigDict
from ragmatic.common_types import TypeAndConfig

class ActionConfig(RefBaseModel):

    document_source: t.Optional[TypeAndConfig] = None
    model_config = ConfigDict(extra= "allow")


class Action:
    
    config_cls: ActionConfig = None
    name: str = None

    def __init__(self, config):
        self.config = self._config_from_action_config(config)
        
    def execute(self):
        raise NotImplementedError

    def _config_from_action_config(self, config: ActionConfig):
        return self.config_cls(**config.model_dump())
