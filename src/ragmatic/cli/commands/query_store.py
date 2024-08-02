from pprint import pprint
import click
import json as jsonmod

from ragmatic.code_analysis.analyzer_factory import get_analyzer_cls, CodebaseAnalyzerBase
from ragmatic.storage.store_factory import get_store_cls, MetadataStore
from ragmatic.cli.configuration.tools import load_config, MasterConfig

@click.command('query-store')
@click.option('--config', type=click.Path(exists=True), required=True)
@click.option('--json', type=str, required=False)
@click.option('--jsonfile', type=click.Path(exists=True), required=False)
def query_store_cmd(config, json, jsonfile):
    if json and jsonfile:
        raise ValueError("Only one of --json and --jsonfile can be provided")
    config = load_config(config)
    if not config.storage:
        raise ValueError("No storage configuration found in the provided configuration file")
    store_cls = get_store_cls(config.storage.store_type)
    store: MetadataStore = store_cls(config.storage.store_config)

    if json or jsonfile:
        if json:
            doc = json
        else:
            with open(jsonfile, "r") as f:
                doc = f.read()
        try:
            query = jsonmod.loads(doc)
        except Exception as e:
            print(doc)
            raise ValueError(f"Error parsing JSON into query: {e}")

    results = store.query_modules(query)
    pprint(results)
    