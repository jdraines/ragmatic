import typing as t
from ragmatic.utils.refs import RefBaseModel


class TypeAndConfig(RefBaseModel):
    type: str
    config: dict


class StoreConfig(RefBaseModel):
    data_type: str
    type: str
    config: dict
