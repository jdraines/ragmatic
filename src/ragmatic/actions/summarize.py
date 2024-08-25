import typing as t
from pydantic import Field
from logging import getLogger

from ragmatic.utils import CollectionKeyFormatter
from ._types import SummarizerComponentConfig, StorageComponentConfig
from ..storage.bases import TextDocumentStore
from ..storage.store_factory import get_store_cls
from ..summarization.bases import SummarizerBase
from ..summarization.summarizer_factory import get_summarizer_class
from ..document_sources.source_factory import get_document_source_cls, DocumentSourceBase
from .bases import Action, ActionConfig
from ragmatic.common_types import TypeAndConfig

logger = getLogger(__name__)


class SummarizeActionConfig(ActionConfig):
    summarizer: SummarizerComponentConfig
    storage: StorageComponentConfig
    document_source: TypeAndConfig


class SummarizeAction(Action):

    config_cls = SummarizeActionConfig
    name = "summarize"
    
    def __init__(self, config: SummarizeActionConfig):
        super().__init__(config)
        self._text_doc_store: TextDocumentStore = self._initialize_storage()
        self._summarizer: SummarizerBase = self._initialize_summarizer()
        self._source: DocumentSourceBase = self._initialize_document_source()
        
    def _initialize_summarizer(self):
        summarizer_cls = get_summarizer_class(self.config.summarizer.type)
        summarizer_config = self.config.summarizer.config
        return summarizer_cls(summarizer_config)

    def _initialize_document_source(self):
        source_cls = get_document_source_cls(self.config.document_source.type)
        source_config = self.config.document_source.config
        return source_cls(source_config)

    def _initialize_storage(self) -> TextDocumentStore:
        store_cls = get_store_cls(
            self.config.storage.data_type,
            self.config.storage.type
        )
        store_config = self.config.storage.config
        return store_cls(store_config)

    def execute(self):
        documents = self._source.get_documents()
        summaries = self._summarizer.summarize(documents)
        kv_summaries = self.summaries_to_key_value_pairs(summaries)
        logger.info(f"Summarization completed. {len(summaries)} docs summarized with {len(kv_summaries)} summaries.")
        self._text_doc_store.store_text_docs(kv_summaries)
        logger.info(f"Summaries stored in {self._text_doc_store.name} storage.")


    def summaries_to_key_value_pairs(self, summaries: dict[str, list[str]]) -> dict[str, str]:
        return {
            CollectionKeyFormatter.flatten_collection_key(doc_name, i): summary
            for doc_name, summary_texts in summaries.items()
            for i, summary in enumerate(summary_texts)
        }