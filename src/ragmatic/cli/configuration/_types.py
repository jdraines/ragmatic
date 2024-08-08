from typing import Literal, Optional, Dict, List
from pydantic import BaseModel, Field

from ...summarization.bases import SummarizerConfig
from ...actions._types import *
from ...actions.bases import ActionConfig

class RagConfig(BaseModel):
    rag_agent_type: str
    llm: str
    n_nearest: Optional[int] = Field(default=10)
    prompt: Optional[str] =  Field(default=None)
    system_prompt: Optional[str] = Field(default=None)


class ComponentConfig(BaseModel):
    storage: Optional[Dict[str, StorageComponentConfig]] = Field(default=None)
    llms: Optional[Dict[str, LLMComponentConfig]] = Field(default=None)
    summarizers: Optional[Dict[str, SummarizerComponentConfig]] = Field(default=None)
    encoders: Optional[Dict[str, EncoderComponentConfig]] = Field(default=None)
    
    root_path: Optional[str] = Field(default=None)
    analysis: Optional[AnalysisConfig] = Field(default=None)
    service: Optional[dict] = Field(default=None)
    rag: Optional[RagConfig] = Field(default=None)


class PipelineElementConfig(BaseModel):
    action: str
    config: ActionConfig


class MasterConfig(BaseModel):
    project_name: str
    components: ComponentConfig
    pipelines: Dict[str, List[PipelineElementConfig]]
