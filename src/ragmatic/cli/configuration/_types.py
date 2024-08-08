from typing import Literal, Optional, Dict
from pydantic import BaseModel, Field

from ...summarization.bases import SummarizerConfig


class LLMConfig(BaseModel):
    llm_client_type: str
    llm_config: dict
    class Config:
        extra = "allow"


class EmbedderConfig(BaseModel):
    embedder_type: Literal["hugging_face"]
    embedder_config: dict = Field(default_factory=dict)
    storage: str


class AnalysisConfig(BaseModel):
    analyzer_type: Literal["python"]
    storage: str


class SummarizationConfig(BaseModel):
    summarizer_type: Literal["python_code"]
    storage: str
    llm: str
    summarizer_config: Optional[SummarizerConfig] = Field(default_factory=SummarizerConfig)

class StorageConfig(BaseModel):
    store_type: Literal["metadata", "vector", "summary", "omni"]
    store_name: Literal["elasticsearch", "pydict"]
    store_config: dict = Field(default_factory=dict)


class RagConfig(BaseModel):
    rag_agent_type: str
    llm: str
    n_nearest: Optional[int] = Field(default=10)
    prompt: Optional[str] =  Field(default=None)
    system_prompt: Optional[str] = Field(default=None)


class MasterConfig(BaseModel):
    project_name: str
    root_path: Optional[str] = Field(default=None)
    analysis: Optional[AnalysisConfig] = Field(default=None)
    storage: Optional[Dict[str, StorageConfig]] = Field(default=None)
    service: Optional[dict] = Field(default=None)
    summarization: Optional[SummarizationConfig] = Field(default=None)
    embeddings: Optional[EmbedderConfig] = Field(default=None)
    llms: Optional[Dict[str, LLMConfig]] = Field(default=None)
    rag: Optional[RagConfig] = Field(default=None)
