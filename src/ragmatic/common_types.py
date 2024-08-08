import typing as t
from pydantic import BaseModel


class TypeAndConfig(BaseModel):
    type: str
    config: t.Union[dict, str]


class StoreConfig(BaseModel):
    data_type: str
    type: str
    config: dict
