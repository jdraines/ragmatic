import click
from logging import getLogger

from ragmatic.storage.store_factory import get_store_cls
from ragmatic.storage.bases import TextDocumentStore, VectorStore
from ragmatic.cli.configuration.tools import load_config
from ragmatic.embeddings.embedder_factory import get_embedder_cls, Embedder


logger = getLogger(__name__)


@click.command('encode-summaries')
@click.option('--config', type=click.Path(exists=True), required=True)
def encode_summaries_cmd(config):
    config = load_config(config)
    if not config.summarization:
        raise ValueError("No summarization configuration found in the provided configuration file. A summarization configuration with storage information is required to encode summaries.")
    if not config.summarization.storage:
        raise ValueError("No storage specified found summarization configuration")
    summary_storage: str = config.summarization.storage
    if summary_storage not in config.storage:
        raise ValueError(f"Storage configuration for {summary_storage} not found in the provided configuration file")
    if not config.embeddings:
        raise ValueError("No embedding configuration found in the provided configuration file. An embedding configuration is required to encode summaries.")
    if not config.embeddings.storage:
        raise ValueError("No storage specified found in the embedding configuration")


    summary_store_cls = get_store_cls(config.storage[summary_storage].store_type, config.storage[summary_storage].store_name)
    summary_storage_config = config.storage[summary_storage].store_config
    summary_storage: TextDocumentStore = summary_store_cls(summary_storage_config)
    logger.info("Loading summaries")
    summaries = summary_storage.get_all_summaries()

    embedder_cls = get_embedder_cls(config.embeddings.embedding_type)
    embedder: Embedder = embedder_cls(config.embeddings.embedding_config)
    
    vector_store_type = config.embeddings.storage
    vector_store_cls = get_store_cls(config.storage[vector_store_type].store_type, config.storage[vector_store_type].store_name)
    vector_store_config = config.storage[vector_store_type].store_config
    vector_store: VectorStore = vector_store_cls(vector_store_config)

    logger.info(f"Encoding {len(summaries)} summaries...")
    _encoded_summaries = embedder.encode([
        summary for _, summary in summaries.items()
    ])
    embeddings = {
        key: value for key, value in zip(summaries.keys(), _encoded_summaries)
    }
    logger.info(f"Storing {len(embeddings)} embeddings...")
    vector_store.store_vectors(embeddings)