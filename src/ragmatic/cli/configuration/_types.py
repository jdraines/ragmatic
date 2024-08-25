from typing import Optional, Dict, List
from ragmatic.utils.refs import RefBaseModel
from pydantic import Field

from ...actions._types import (
    DocumentSourceComponentConfig,
    StorageComponentConfig,
    LLMComponentConfig,
    SummarizerComponentConfig,
    EncoderComponentConfig,
    RagAgentComponentConfig,
)
from ...actions.bases import ActionConfig
from ragmatic.common_types import TypeAndConfig


class RagQueryCommandConfig(RefBaseModel):
    rag_agent: RagAgentComponentConfig
    document_source: TypeAndConfig


class ComponentConfig(RefBaseModel):
    document_sources: Optional[Dict[str, DocumentSourceComponentConfig]] = Field(default=None)
    storage: Optional[Dict[str, StorageComponentConfig]] = Field(default=None)
    llms: Optional[Dict[str, LLMComponentConfig]] = Field(default=None)
    summarizers: Optional[Dict[str, SummarizerComponentConfig]] = Field(default=None)
    encoders: Optional[Dict[str, EncoderComponentConfig]] = Field(default=None)
    rag_agents: Optional[Dict[str, RagAgentComponentConfig]] = Field(default=None)


class PipelineElementConfig(RefBaseModel):
    action: str
    config: ActionConfig


class MasterConfig(RefBaseModel):
    project_name: Optional[str] = Field(default=None) 
    components: Optional[ComponentConfig] = Field(default=None)
    pipelines: Optional[Dict[str, List[PipelineElementConfig]]] = Field(default=None)
    rag_query_command: Optional[RagQueryCommandConfig] = Field(default=None)
