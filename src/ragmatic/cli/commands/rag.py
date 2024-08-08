import click
from logging import getLogger

from ragmatic.storage.store_factory import get_store_cls
from ragmatic.storage.bases import SummaryStore, VectorStore
from ragmatic.cli.configuration.tools import load_config
from ragmatic.embeddings.embedder_factory import get_embedder_cls, Embedder
from ragmatic.rag.rag_agent_factory import get_rag_agent_class
from ragmatic.rag.bases import RagAgentConfig, RagAgentBase


logger = getLogger(__name__)


@click.command('rag')
@click.option('--config', type=click.Path(exists=True), required=True)
@click.option('--query', type=str, required=True)
def rag_cmd(config, query):
    config = load_config(config)
    if not config.embeddings:
        raise ValueError("No embedding configuration found in the provided configuration file. An embedding configuration is required to encode summaries.")
    if not config.embeddings.storage:
        raise ValueError("No storage specified found in the embedding configuration")
    storage_type = config.embeddings.storage
    if storage_type not in config.storage:
        raise ValueError(f"No configuration found for storage {storage_type!r}")
    vector_store_type = config.storage[storage_type].store_type
    vector_store_name = config.storage[storage_type].store_name
    vector_store_config = config.storage[storage_type].store_config
    if not config.llms:
        raise ValueError(f"No 'llms' list specified in the configuration file.")
    if not config.rag:
        raise ValueError("No RAG configuration found in the provided configuration file.")
    if not config.rag.llm:
        raise ValueError("No LLM specified in the RAG configuration.")
    llm = config.rag.llm
    if llm not in config.llms:
        llms = list(config.llms.keys())
        raise ValueError(f"No configuration information provided for LLM {llm!r}. Available llms: {llms}")
    rag_agent_class = get_rag_agent_class(config.rag.rag_agent_type)
    rag_agent_config: RagAgentBase = RagAgentConfig(**dict(
        llm_client_type = config.llms[llm].llm_client_type,
        llm_config = config.llms[llm].llm_config,
        vector_store_type = vector_store_type,
        vector_store_name = vector_store_name,
        vector_store_config = vector_store_config,
        embedder_type = config.embeddings.embedding_type,
        embedder_config = config.embeddings.embedding_config,
        n_nearest = config.rag.n_nearest,
        prompt = config.rag.prompt,
        system_prompt = config.rag.system_prompt
    ))
    rag_agent = rag_agent_class(config.root_path, rag_agent_config)
    print(rag_agent.query(query))
