import typing as t
from pydantic import BaseModel


class ActionConfig(BaseModel):    
    class Config:
        extra = "allow"


class Action:
    
    config_cls: ActionConfig = None
    name: str = None

    def __init__(self, config):
        self.config = config

    def execute(self):
        raise NotImplementedError
