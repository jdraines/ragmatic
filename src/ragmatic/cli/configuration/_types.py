from typing import Literal, Optional, Dict, List
from pydantic import BaseModel, Field

from ...summarization.bases import SummarizerConfig
from ...actions._types import *
from ...actions.bases import ActionConfig
from ...rag.bases import RagAgentConfig
from ragmatic.common_types import TypeAndConfig


class RagQueryCommandConfig(BaseModel):
    rag_agent: str
    document_source: t.Union[str, TypeAndConfig]


class ComponentConfig(BaseModel):
    document_sources: Optional[Dict[str, DocumentSourceComponentConfig]] = Field(default=None)
    storage: Optional[Dict[str, StorageComponentConfig]] = Field(default=None)
    llms: Optional[Dict[str, LLMComponentConfig]] = Field(default=None)
    summarizers: Optional[Dict[str, SummarizerComponentConfig]] = Field(default=None)
    encoders: Optional[Dict[str, EncoderComponentConfig]] = Field(default=None)
    rag_agents: Optional[Dict[str, RagAgentComponentConfig]] = Field(default=None)


class PipelineElementConfig(BaseModel):
    action: str
    config: ActionConfig


class MasterConfig(BaseModel):
    project_name: str
    components: ComponentConfig
    pipelines: Dict[str, List[PipelineElementConfig]]
    rag_query_command: RagQueryCommandConfig
