from typing import Type
from ragmatic.utils import import_object
from .bases import Embedder


_embedders = {
    "hf_transformers": "ragmatic.embeddings.hugging_face_transformer.HfTransformersEmbedder",
    "hf_sentence_transformers": "ragmatic.embeddings.hf_sentence_transformers.HfSentenceTransformersEmbedder",
}


def get_embedder_cls(embedder_name) -> Type[Embedder]:
    if embedder_name not in _embedders:
        try:
            return import_object(embedder_name)
        except Exception:
            raise ValueError(f"Embedder {embedder_name} not supported")
    return import_object(_embedders[embedder_name])
