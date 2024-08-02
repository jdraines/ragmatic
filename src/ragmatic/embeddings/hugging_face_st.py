import typing as t
from .bases import Embedder

class HuggingFaceSentenceTransformersEmbedder(Embedder):

    def __init__(self, config):
        self.config = config
        self.model_name = config["model_name"]
        self.save_filepath = config.get("save_filepath", "embedding_model.pkl")
        self.prompt_name = config.get("prompt_name", "s2s_query")

    def encode(self, docs: t.Sequence[str]) -> t.Sequence[t.Sequence[float]]:
        pass
