from typing import Type
from ragmatic.utils import import_object
from .bases import Embedder


_embedders = {
    "hugging_face": "ragmatic.embeddings.hugging_face.HuggingFaceTransformerEmbedder",
}


def get_embedder_cls(embedder_name) -> Type[Embedder]:
    if embedder_name not in _embedders:
        raise ValueError(f"Embedder {embedder_name} not supported")
    return import_object(_embedders[embedder_name])
