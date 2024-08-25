import typing as t
from pydantic import Field
from logging import getLogger

from ragmatic.utils import CollectionKeyFormatter
from ..storage.bases import TextDocumentStore
from ..storage.store_factory import get_store_cls
from ..summarization.bases import SummarizerBase
from ..summarization.summarizer_factory import get_summarizer_class
from .bases import Action, ActionConfig
from ..rag.bases import RagAgentConfig, RagAgentBase
from ._types import RagAgentComponentConfig
from ..rag.rag_agent_factory import get_rag_agent_class
from ..document_sources.source_factory import get_document_source_cls
from ..document_sources.bases import DocumentSourceBase
from ragmatic.common_types import TypeAndConfig


logger = getLogger(__name__)


class RagActionConfig(ActionConfig):
    rag_agent: t.Union[str, RagAgentComponentConfig]
    document_source: t.Union[str, TypeAndConfig]
    query: str


class RagAction(Action):

    config_cls = RagActionConfig
    name = "rag"

    def __init__(self, config: RagActionConfig):
        super().__init__(config)
        self._source: DocumentSourceBase = self._initialize_source()
        self._rag_agent: RagAgentBase = self._initialize_rag_agent()

    def _initialize_source(self):
        source_cls = get_document_source_cls(self.config.document_source.type)
        source_config = self.config.document_source.config
        return source_cls(source_config)

    def _initialize_rag_agent(self):
        rag_agent_cls = get_rag_agent_class(self.config.rag_agent.type)
        return rag_agent_cls(self.config.rag_agent.config, self._source)
    
    def execute(self) -> dict[str, str]:
        return self._rag_agent.query(self.config.query)
