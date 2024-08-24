from logging import getLogger
from pathlib import Path

from deepmerge import always_merger, Merger

from ragmatic.utils import ragmatic_load_yaml
from ragmatic.utils.refs import resolve_references
from ._types import MasterConfig
from ..configuration.presets.preset_factory import get_preset, PresetData

logger = getLogger(__name__)


def load_configdict(configpath: Path = None) -> dict:
    with open(str(configpath)) as f:
        config = ragmatic_load_yaml(f)
    return config


def load_config(configpath: Path = None) -> MasterConfig:
    config = load_configdict(configpath)
    return MasterConfig(**config)


def get_preset_config(preset_name, **vars) -> MasterConfig:
    preset = get_preset(preset_name)
    return preset.get_config(**vars)


def merge_defaults(config: MasterConfig,
                   preset_data: PresetData = None,
                   **vars
                   ) -> MasterConfig:
    config_d = config.model_dump()
    component_config = config_d.get("components", {})
    pipelines_config = config_d.get("pipelines", {})
    rag_query_command = config_d.get("rag_query_command", {})
    
    component_config = always_merger.merge(
        preset_data.get_component_config(**vars),
        component_config
    )
    config_d.update({"components": component_config})

    pipelines_merger = Merger(
        [
            (dict, "merge"),
            (list, "append")
        ],
        ["override"],
        ["override"]
    )
    pipelines_config = pipelines_merger.merge(
        preset_data.get_pipelines_config(**vars),
        pipelines_config
    )
    rag_query_command = always_merger.merge(
        preset_data.get_rag_query_command_config(**vars),
        rag_query_command
    )
    return MasterConfig(
        project_name=config.project_name,
        components=component_config,
        pipelines=pipelines_config,
        rag_query_command=rag_query_command
    )

def resolve_config_references(config: MasterConfig) -> MasterConfig:
    config_dict = config.model_dump()
    resolved_config = resolve_references(config_dict)
    return MasterConfig(**resolved_config)
