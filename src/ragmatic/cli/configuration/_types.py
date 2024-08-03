from typing import Literal, Optional
from pydantic import BaseModel, Field



class LLMConfig(BaseModel):
    type: str
    class Config:
        extra = "allow"


class AnalysisConfig(BaseModel):
    analyzer_type: Literal["python"]
    llm_config: Optional[LLMConfig] = Field(default=None)


class EmbeddingConfig(BaseModel):
    embedding_type: Literal["hugging_face"]
    embedding_config: dict = Field(default_factory=dict)


class StorageConfig(BaseModel):
    store_type: Literal["elsticsearch", "python"]
    store_config: dict = Field(default_factory=dict)


class ServiceConfig(BaseModel):
    type: str
    llm_config: LLMConfig
    class Config:
        extra = "allow"


class MasterConfig(BaseModel):
    analysis: Optional[AnalysisConfig] = Field(default=None)
    embedding: Optional[EmbeddingConfig] = Field(default=None)
    storage: Optional[StorageConfig] = Field(default=None)
    service: Optional[ServiceConfig] = Field(default=None)
