from ._types import PresetData
from .local_docs_preset import local_docs_preset
from .pycode_preset import pycode_preset


_presets = {
    "local_docs": local_docs_preset,
    "pycode": pycode_preset
}

def get_preset(name) -> PresetData:
    if name == "default":
        name = "local_docs"
    if name not in _presets:
        raise ValueError(f"Unknown preset: {name}")
    return _presets[name]
