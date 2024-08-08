import typing as t
from pydantic import BaseModel, Field

from ..summarization.bases import SummarizerConfig


class LLMComponentConfig(BaseModel):
    type: str
    config: dict

    class Config:
        extra = "allow"


class EncoderComponentConfig(BaseModel):
    type: t.Literal["hugging_face"]
    config: dict = Field(default_factory=dict)


class AnalysisConfig(BaseModel):
    analyzer_type: t.Literal["python"]
    storage: str


class SummarizerComponentConfig(BaseModel):
    
    class SummarizerComponentRefSubconfig(BaseModel):
        llm: str
        class Config:
            extra = "allow"

    type: t.Literal["python_code"]
    config: t.Union[SummarizerComponentRefSubconfig, SummarizerConfig]


class StorageComponentConfig(BaseModel):
    data_type: t.Literal["metadata", "vector", "summary", "omni"]
    type: t.Literal["elasticsearch", "pydict"]
    config: dict = Field(default_factory=dict)
