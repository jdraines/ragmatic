from logging import getLogger
from typing import Union, get_args, get_origin
from pydantic import BaseModel, ConfigDict
from pydantic._internal._model_construction import ModelMetaclass

import yaml
import json
import copy


logger = getLogger(__name__)


class Ref:
    def __init__(self, loc):
        self.loc = loc

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Ref) and value.loc == self.loc


def ref_constructor(loader, node):
    value = loader.construct_scalar(node)
    return Ref(value)


def ref_representer(dumper, data):
    return dumper.represent_scalar(u'!ref', data.loc)


yaml.add_constructor(u'!ref', ref_constructor, yaml.SafeLoader)
yaml.add_representer(Ref, ref_representer)


def resolve_references(data, root=None):
    if root is None:
        root = data

    if isinstance(data, dict):
        return {key: resolve_references(value, root) for key, value in data.items()}
    elif isinstance(data, list):
        return [resolve_references(item, root) for item in data]
    elif isinstance(data, Ref):
        resolved = resolve_ref(root, data.loc)
        return resolve_references(resolved, root)
    else:
        return data

def resolve_ref(data, loc):
    parts = loc.split('.')
    current = data
    for part in parts:
        if part in current:
            current = current[part]
        else:
            raise KeyError(f"Reference not found: {loc}")
    return copy.deepcopy(current)


def ragmatic_load_yaml(stream):
    return yaml.safe_load(stream)


def ref_dumper_default(obj):
    if isinstance(obj, Ref):
        return f"!ref {obj.loc}"
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class RefDecoder(json.JSONDecoder):
    
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self._object_hook, *args, **kwargs)

    def _object_hook(self, obj):
        if isinstance(obj, dict):
            return {key: self._object_hook(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._object_hook(item) for item in obj]
        if isinstance(obj, str) and obj.startswith("!ref "):
            obj: str = obj
            loc = obj.replace('!ref ', '')
            return Ref(loc)
        return obj


def make_refable(typ):
    return Union[typ, Ref]


class RefModelMetaclass(ModelMetaclass):

    def __new__(mcs, name, bases, namespace, **kwargs):
        annotations = namespace.get('__annotations__', {})
        for field_name, field_type in annotations.items():
            if field_name.startswith('__'):
                continue
            annotations[field_name] = make_refable(field_type)
        namespace['__annotations__'] = annotations
        return super().__new__(mcs, name, bases, namespace, **kwargs)


class RefBaseModel(BaseModel, metaclass=RefModelMetaclass):

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        if isinstance(obj, dict):
            for field_name, field_value in obj.items():
                if isinstance(field_value, Ref):
                    continue
                field_info = cls.model_fields[field_name]
                field_type = get_args(field_info.annotation)[0]  # Get the non-Ref type
                if get_origin(field_type) is not None:
                    field_type = get_origin(field_type)
                if isinstance(field_type, type) and issubclass(field_type, RefBaseModel):
                    obj[field_name] = field_type.model_validate(field_value)
        return super().model_validate(obj, *args, **kwargs)

    model_config = ConfigDict(arbitrary_types_allowed=True)