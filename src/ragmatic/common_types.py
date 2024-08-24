import typing as t
from ragmatic.utils.refs import RefBaseModel


class TypeAndConfig(RefBaseModel)):
    type: str
    config: t.Union[dict, str]


class StoreConfig(RefBaseModel)):
    data_type: str
    type: str
    config: dict
