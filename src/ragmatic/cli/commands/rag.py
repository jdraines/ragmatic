import click
from logging import getLogger

from ragmatic.cli.configuration.tools import (
    load_config,
    get_default_config,
    merge_defaults,
    MasterConfig,
    get_action_config_factory,
    ActionConfigFactory
)
from ragmatic.rag.rag_agent_factory import get_rag_agent_class
from ragmatic.rag.bases import RagAgentConfig, RagAgentBase
from ragmatic.actions.rag import RagActionConfig, RagAction
from ..configuration._types import RagAgentComponentConfig


logger = getLogger(__name__)


@click.command('rag-query')
@click.option('--query', type=str, required=True)
@click.option('--config', type=click.Path(exists=True))
def rag_cmd(config: click.Path, query: str):
    config: MasterConfig = load_config(config) or get_default_config()
    config = merge_defaults(config)
    cmd_config = config.rag_query_command
    rag_agent_component_config: RagAgentComponentConfig =\
        config.components.rag_agents[cmd_config.rag_agent]
    rag_action_config = RagActionConfig(
        **dict(
            document_source=cmd_config.document_source,
            query=query,
            rag_agent=rag_agent_component_config.model_dump()
        )
    )
    config_factory: ActionConfigFactory = get_action_config_factory("rag", config)
    rag_action_config = config_factory.dereference_action_config(rag_action_config)

    print(RagAction(rag_action_config).execute())
