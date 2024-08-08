from logging import getLogger
import typing as t

import click

from ..configuration._types import MasterConfig
from ..configuration.tools import (
    load_config,
    get_action_config_factory,
    get_default_config,
    merge_defaults,
)
from ...actions.bases import Action
from ...actions.action_factory import get_action_cls

logger = getLogger(__name__)


@click.command('run')
@click.argument('pipeline')
@click.option('--config', type=click.Path(exists=True), required=True)
@click.option('--pipeline-preset', type=click.Choice(['default', 'pycode']), default='default')
def run_cmd(pipeline: str, config: click.Path, pipeline_preset: str):
    config: MasterConfig = load_config(config) or get_default_config()
    config = merge_defaults(config, pipelines_config_name=pipeline_preset)
    pipeline_config = config.pipelines[pipeline]
    for element in pipeline_config:
        action_name = element.action
        action_cls: t.Type[Action] = get_action_cls(action_name)
        action_config_factory = get_action_config_factory(action_name, config)
        action_config = action_config_factory.dereference_action_config(element.config)
        action: Action = action_cls(action_config)
        action.execute()
