from typing import List, Callable
from logging import getLogger

from ragmatic.utils.refs import RefBaseModel
from tqdm.contrib.concurrent import thread_map

from ..llm_ops.bases import LLMClientBase
from ..llm_ops.client_factory import get_llm_client_class
from ragmatic.common_types import TypeAndConfig


logger = getLogger(__name__)


class SummarizerConfig(RefBaseModel):
    llm: TypeAndConfig
    document_source: TypeAndConfig


class SummarizerBase:
    summarizer_name: str = ""
    _document_prompt: str = ""
    _system_prompt: str = ""
    file_filters: List[Callable[[str], bool]] = [(lambda x: True)]

    def __init__(self, config: dict):
        self.config: SummarizerConfig = config
        self._llm_client: LLMClientBase = self._initialize_llm_client()
        self._summaries: dict[str, list[str]] = {}
    
    def _initialize_llm_client(self) -> LLMClientBase:
        client_class = get_llm_client_class(self.config.llm.type)
        llm_config = self.config.llm.config
        return client_class(llm_config)

    def summarize(self, documents: dict[str, str] = None) -> dict[str, list[str]]:
        docs = documents
        _jobs = [(name, text) for name, text in docs.items()]
        logger.info(f"Summarizing {len(_jobs)} code documents...")
        summary_responses = thread_map(self.summarize_document, [doc for _, doc in _jobs])
        self._summaries = dict(zip([doc_name for doc_name, _ in _jobs], summary_responses))
        return self._summaries

    def summarize_document(self, doc: str) -> list[str]:
        """
        Example implementation:

        ```python
        message = self._build_message(doc)
        response = self._llm_client.send_message(
            message,
            self._system_prompt,
            role="user"
        )
        return response.split("\n")
        ```
        """
        raise NotImplementedError
    
    def _build_message(self, code_doc: str) -> str:
        return self._document_prompt + "\n---\n" + code_doc
    
    def _file_path_to_doc_name(self, file_path: str) -> str:
        return file_path
    