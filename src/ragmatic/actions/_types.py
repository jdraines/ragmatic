import typing as t
from ragmatic.utils.refs import RefBaseModel
from pydantic import Field, ConfigDict

from ..summarization.bases import SummarizerConfig

from ..rag.bases import RagAgentConfig


class DocumentSourceComponentConfig(RefBaseModel):
    type: t.Literal["storage", "filesystem", "pycode_filesystem"]
    config: t.Union[str, dict] = Field(default_factory=dict)


class LLMComponentConfig(RefBaseModel):
    type: str
    config: dict
    model_config = ConfigDict(extra= "allow")


class EncoderComponentConfig(RefBaseModel):
    type: str
    config: dict = Field(default_factory=dict)


class AnalysisConfig(RefBaseModel):
    analyzer_type: t.Literal["python"]
    storage: str


class SummarizerComponentConfig(RefBaseModel):
    type: t.Literal["python_code"]
    config: SummarizerConfig


class StorageComponentConfig(RefBaseModel):
    data_type: t.Literal["metadata", "vector", "summary", "omni"]
    type: t.Literal["pydict"]
    config: dict = Field(default_factory=dict)


class RagAgentComponentConfig(RefBaseModel):
    type: str
    config: RagAgentConfig
