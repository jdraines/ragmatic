import click
from logging import getLogger

from ragmatic.code_summarization.summarizer_factory import get_summarizer_class, CodeSummarizerBase
from ragmatic.storage.store_factory import get_store_cls
from ragmatic.storage.bases import SummaryStore
from ragmatic.cli.configuration.tools import load_config

logger = getLogger(__name__)


@click.command('summarize')
@click.option('--config', type=click.Path(exists=True), required=True)
def summarize_cmd(config):
    config = load_config(config)
    if not config.summarization:
        raise ValueError("No summarization configuration found in the provided configuration file")
    if not config.summarization.storage:
        raise ValueError("No storage specified found summarization configuration")
    storage: str = config.summarization.storage
    if storage not in config.storage:
        raise ValueError(f"Storage configuration for {storage} not found in the provided configuration file")
    
    store_cls = get_store_cls(config.storage[storage].store_type, config.storage[storage].store_name)
    storage_config = config.storage[storage].store_config
    storage: SummaryStore = store_cls(storage_config)
    
    summarizer_cls = get_summarizer_class(config.summarization.summarizer_type)
    summarizer: CodeSummarizerBase = summarizer_cls(config.root_path, config.summarization.summarizer_config)
    summaries = summarizer.summarize_codebase()
    kv_summaries = summaries_to_key_value_pairs(summaries)
    logger.info(f"Summarization completed. {len(summaries)} modules summarized with {len(kv_summaries)} summaries.")
    storage.store_summaries(kv_summaries)
    logger.info(f"Summaries stored in {storage.name} storage.")


def summaries_to_key_value_pairs(summaries: dict[str, list[str]]) -> dict[str, str]:
    return {
        f"{module_name}::{i}": summary
        for module_name, summary_texts in summaries.items()
        for i, summary in enumerate(summary_texts)
    }
