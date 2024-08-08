import click
from logging import getLogger
import typing as t

from ragmatic.summarization.summarizer_factory import get_summarizer_class, SummarizerBase
from ragmatic.storage.store_factory import get_store_cls
from ragmatic.storage.bases import TextDocumentStore
from ragmatic.cli.configuration.tools import load_config
from ragmatic.cli.configuration._types import SummarizerConfig
from ragmatic.utils import CollectionKeyFormatter

logger = getLogger(__name__)


@click.command('summarize')
@click.option('--config', type=click.Path(exists=True), required=True)
def summarize_cmd(config):
    config = load_config(config)
    if not config.summarization:
        raise ValueError("No summarization configuration found in the provided configuration file")
    if not config.summarization.storage:
        raise ValueError("No storage specification found in summarization configuration")
    storage: str = config.summarization.storage
    if storage not in config.storage:
        raise ValueError(f"Storage configuration for {storage} not found in the provided configuration file")
    
    if not config.summarization.llm:
        raise ValueError("No llm speciifcation found in summarization configuration")
    llm: str = config.summarization.llm
    if llm not in config.llms:
        llms = list(config.llms.keys())
        raise ValueError(f"LLM configuration for {llm} not found in the provided configuration file. Configurations present for: {llms}")

    summarizer_config = config.summarization.summarizer_config
    summarizer_config.llm_client_type = config.llms[llm].llm_client_type
    summarizer_config.llm_config = config.llms[llm].llm_config

    store_cls = get_store_cls(config.storage[storage].store_type, config.storage[storage].store_name)
    storage_config = config.storage[storage].store_config
    storage: TextDocumentStore = store_cls(storage_config)
    
    summarizer_cls: t.Type[SummarizerConfig] = get_summarizer_class(config.summarization.summarizer_type)
    summarizer: SummarizerBase = summarizer_cls(summarizer_config, config.root_path)
    summaries = summarizer.summarize_dir()
    kv_summaries = summaries_to_key_value_pairs(summaries)
    logger.info(f"Summarization completed. {len(summaries)} docs summarized with {len(kv_summaries)} summaries.")
    storage.store_text_docs(kv_summaries)
    logger.info(f"Summaries stored in {storage.name} storage.")


def summaries_to_key_value_pairs(summaries: dict[str, list[str]]) -> dict[str, str]:
    return {
        CollectionKeyFormatter.flatten_collection_key(module_name, i): summary
        for module_name, summary_texts in summaries.items()
        for i, summary in enumerate(summary_texts)
    }
