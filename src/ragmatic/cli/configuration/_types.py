from typing import Literal, Optional
from pydantic import BaseModel, Field



class LLMConfig(BaseModel):
    type: str
    class Config:
        extra = "allow"


class EmbeddingConfig(BaseModel):
    embedding_type: Literal["hugging_face"]
    embedding_config: dict = Field(default_factory=dict)


class AnalysisConfig(BaseModel):
    analyzer_type: Literal["python"]
    llm_config: Optional[LLMConfig] = Field(default=None)
    embedding_config: Optional[EmbeddingConfig] = Field(default=None)


class StorageConfig(BaseModel):
    store_type: Literal["elsticsearch", "python"]
    store_config: dict = Field(default_factory=dict)


class ServiceConfig(BaseModel):
    type: str
    llm_config: LLMConfig
    embedding_config: EmbeddingConfig


class MasterConfig(BaseModel):
    analysis: Optional[AnalysisConfig] = Field(default=None)
    storage: Optional[StorageConfig] = Field(default=None)
    service: Optional[ServiceConfig] = Field(default=None)
