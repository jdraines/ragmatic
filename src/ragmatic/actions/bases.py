import typing as t
from pydantic import BaseModel
from ragmatic.common_types import TypeAndConfig

class ActionConfig(BaseModel):

    document_source: t.Optional[t.Union[str, TypeAndConfig]] = None

    class Config:
        extra = "allow"


class Action:
    
    config_cls: ActionConfig = None
    name: str = None

    def __init__(self, config):
        self.config = config

    def execute(self):
        raise NotImplementedError
