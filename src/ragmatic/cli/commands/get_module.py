from pprint import pprint
import click
import json as jsonmod

from ragmatic.code_analysis.analyzer_factory import get_analyzer_cls, CodebaseAnalyzerBase
from ragmatic.storage.store_factory import get_store_cls, MetadataStore
from ragmatic.cli.configuration.tools import load_config, MasterConfig

@click.command('get-module')
@click.argument('module_name')
@click.option('--config', type=click.Path(exists=True), required=True)
def get_module_cmd(module_name, config):
    config = load_config(config)
    if not config.storage:
        raise ValueError("No storage configuration found in the provided configuration file")
    store_cls = get_store_cls(config.storage.store_type)
    store: MetadataStore = store_cls(config.storage.store_config)
    results = store.get_module(module_name)
    pprint(results)
