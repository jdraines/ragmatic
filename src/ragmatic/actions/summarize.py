import typing as t
from pydantic import Field
from logging import getLogger

from ragmatic.utils import CollectionKeyFormatter
from ._types import SummarizerComponentConfig, StorageComponentConfig
from ..storage.bases import TextDocumentStore
from ..storage.store_factory import get_store_cls
from ..summarization.bases import SummarizerBase
from ..summarization.summarizer_factory import get_summarizer_class
from .bases import Action, ActionConfig

logger = getLogger(__name__)


class SummarizeActionConfig(ActionConfig):
    root_path: t.Optional[str] = Field(default=None)
    summarizer: SummarizerComponentConfig
    storage: StorageComponentConfig


class SummarizeAction(Action):

    config_cls = SummarizeActionConfig
    name = "summarize"
    
    def __init__(self, config: SummarizeActionConfig):
        super().__init__(config)
        self.config = config
        self._text_doc_store: TextDocumentStore = self._initialize_storage()
        self._summarizer: SummarizerBase = self._initialize_summarizer()
        
    def _initialize_summarizer(self):
        summarizer_cls = get_summarizer_class(self.config.summarizer.type)
        summarizer_config = self.config.summarizer.config
        return summarizer_cls(summarizer_config, self.config.root_path)

    def _initialize_storage(self) -> TextDocumentStore:
        store_cls = get_store_cls(
            self.config.storage.data_type,
            self.config.storage.type
        )
        store_config = self.config.storage.config
        return store_cls(store_config)

    def execute(self):
        summaries = self._summarizer.summarize_dir()
        kv_summaries = self.summaries_to_key_value_pairs(summaries)
        logger.info(f"Summarization completed. {len(summaries)} docs summarized with {len(kv_summaries)} summaries.")
        self._text_doc_store.store_text_docs(kv_summaries)
        logger.info(f"Summaries stored in {self._text_doc_store.name} storage.")


    def summaries_to_key_value_pairs(self, summaries: dict[str, list[str]]) -> dict[str, str]:
        return {
            CollectionKeyFormatter.flatten_collection_key(module_name, i): summary
            for module_name, summary_texts in summaries.items()
            for i, summary in enumerate(summary_texts)
        }