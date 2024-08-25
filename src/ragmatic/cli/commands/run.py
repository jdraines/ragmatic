from logging import getLogger
import typing as t

import click

from ..configuration._types import MasterConfig
from ..configuration.tools import (
    load_config,
    merge_defaults,
    resolve_config_references
)
from ...actions.bases import Action
from ...actions.action_factory import get_action_cls
from ..configuration.presets.preset_factory import get_preset

logger = getLogger(__name__)


@click.command('run-pipeline')
@click.argument('pipeline', type=str, required=False, default=None)
@click.option('--config', type=click.Path(exists=True))
@click.option('--preset', type=click.Choice(['local_docs', 'pycode']), default='local_docs')
@click.option('--var', '-v', type=str, multiple=True, help="Variables to override in the preset, in key=var format")
def run_cmd(pipeline: t.Union[str, None], config: click.Path, preset: str, var: list):
    vars = dict(v.split('=') for v in var)
    preset_data = get_preset(preset)
    preset_config = preset_data.get_config(**vars)
    config: MasterConfig = load_config(config) if config else preset_config
    if config != preset_config:
        config = merge_defaults(config, preset_data, **vars)
    config = resolve_config_references(config)
    if not config.pipelines:
        raise ValueError(f"No pipelines found in config: {config}")
    if pipeline is None:
        first_preset_pipeline_name = list(preset_config.pipelines.keys())[0]
        if first_preset_pipeline_name not in config.pipelines:
            pipeline = list(config.pipelines.keys())[0]
        else:
            pipeline = first_preset_pipeline_name
    pipeline_config = config.pipelines[pipeline]
    logger.info(f"Running pipeline: {pipeline}")
    for element in pipeline_config:
        action_name = element.action
        action_cls: t.Type[Action] = get_action_cls(action_name)
        action: Action = action_cls(element.config)
        logger.info(f"Running action: {action_name}")
        action.execute()
