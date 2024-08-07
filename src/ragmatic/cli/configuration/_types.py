from typing import Literal, Optional, Dict
from pydantic import BaseModel, Field

from ...code_summarization.bases import CodeSummarizerConfig


class LLMConfig(BaseModel):
    type: str
    class Config:
        extra = "allow"


class EmbeddingConfig(BaseModel):
    embedding_type: Literal["hugging_face"]
    embedding_config: dict = Field(default_factory=dict)
    storage: str


class AnalysisConfig(BaseModel):
    analyzer_type: Literal["python"]
    storage: str


class SummarizationConfig(BaseModel):
    summarizer_type: Literal["python_code"]
    summarizer_config: CodeSummarizerConfig
    storage: str


class StorageConfig(BaseModel):
    store_type: Literal["metadata", "vector", "summary", "omni"]
    store_name: Literal["elasticsearch", "pydict"]
    store_config: dict = Field(default_factory=dict)


class ServiceConfig(BaseModel):
    type: str
    llm_config: LLMConfig
    embedding_config: EmbeddingConfig


class MasterConfig(BaseModel):
    project_name: str
    root_path: str
    analysis: Optional[AnalysisConfig] = Field(default=None)
    storage: Optional[Dict[str, StorageConfig]] = Field(default=None)
    service: Optional[ServiceConfig] = Field(default=None)
    summarization: Optional[SummarizationConfig] = Field(default=None)
    embeddings: Optional[EmbeddingConfig] = Field(default=None)
