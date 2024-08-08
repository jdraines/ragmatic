from typing import List, Callable
import os
from logging import getLogger

from pydantic import BaseModel, Field
from tqdm.contrib.concurrent import thread_map

from ..llm_ops.bases import LLMClientBase
from ..llm_ops.client_factory import get_llm_client_class

logger = getLogger(__name__)


class SummarizerConfig(BaseModel):
    llm_client_type: str = Field(default="")
    llm_config: dict = Field(default_factory=dict)


class SummarizerBase:
    summarizer_name: str = ""
    _document_prompt: str = ""
    _system_prompt: str = ""
    file_filters: List[Callable[[str], bool]] = [(lambda x: True)]

    def __init__(self, root_dir: str, config: dict):
        self.root_dir = root_dir
        self.config: SummarizerConfig = config
        self._llm_client: LLMClientBase = self._initialize_llm_client()
        self._summaries: dict[str, list[str]] = {}
    
    def _initialize_llm_client(self) -> LLMClientBase:
        client_class = get_llm_client_class(self.config.llm_client_type)
        llm_config = self.config.llm_config
        return client_class(llm_config)
    
    def summarize_dir(self) -> dict[str, list[str]]:
        walked = list(os.walk(self.root_dir))
        _jobs = []
        for root, _, files in walked:
            for file in files:
                if all([f(file) for f in self.file_filters]):
                    file_path = os.path.join(root, file)
                    module_name = self._file_path_to_doc_name(file_path)
                    with open(file_path, 'r') as file:
                        doc = file.read()
                    _jobs.append((module_name, doc))
        logger.info(f"Summarizing {len(_jobs)} code documents...")
        summary_responses = thread_map(self.summarize_document, [doc for _, doc in _jobs])
        self._summaries = dict(zip([module_name for module_name, _ in _jobs], summary_responses))
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
        return os.path.basename(file_path)
    