import click

from ragmatic.code_analysis.analyzer_factory import get_analyzer_cls, CodebaseAnalyzerBase
from ragmatic.storage.store_factory import get_store_cls, MetadataStore
from ragmatic.cli.configuration.tools import load_config, MasterConfig

@click.command('analyze')
@click.argument('root-path', type=click.Path(exists=True))
@click.option('--config', type=click.Path(exists=True), required=True)
def analyze_cmd(root_path, config):
    config = load_config(config)
    if not config.analysis:
        raise ValueError("No analysis configuration found in the provided configuration file")
    if not config.storage:
        raise ValueError("No storage configuration found in the provided configuration file")
    analyzer_cls = get_analyzer_cls(config.analysis.analyzer_type)
    store_cls = get_store_cls(config.storage.store_type)
    llm_config = config.analysis.llm_config
    analyzer: CodebaseAnalyzerBase = analyzer_cls(root_path, llm_config)
    store: MetadataStore = store_cls(config.storage.store_config)
    analyzer.analyze_codebase()
    store.store_all_module_data(analyzer.get_all_module_data())
    print(f"Analysis completed. {len(analyzer.get_analyzed_modules())} modules analyzed.")
