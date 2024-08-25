import logging
import re
import typing as t
from logging import getLogger

import numpy as np
import torch
import tqdm
from ragmatic.utils.refs import RefBaseModel
from pydantic import ConfigDict, Field
from sentence_transformers import SentenceTransformer

from .bases import Embedder

logger = getLogger(__name__)



class HfSentenceTransformersEmbeddingConfig(RefBaseModel):
    model_config = ConfigDict(protected_namespaces=())
    model_name: str
    query_prompt_name: str = Field(default="s2p_query")
    chunk_size: int = Field(default=512)
    overlap: int = Field(default=128)

class HfSentenceTransformersEmbedder(Embedder):
    embedder_name = "hf_sentence_transformer"

    def __init__(self, config):
        self.config = config
        self.model_name = config["model_name"]
        self.query_prompt_name = config["query_prompt_name"]
        self.chunk_size = config.get("chunk_size", 512)
        self.overlap = config.get("overlap", 128)
        self._observed_hidden_size = 0
        self._model = None

    @property
    def model(self):
        if not self._model:
            self._download_model()
        assert self._model is not None
        return self._model


    def _silence_loggers(self):
        to_silence = ["^transformers", "^torch", "^sentence_transformers"]
        prefix_re = re.compile(rf'^(?:{ "|".join(to_silence) })')
        for name in logging.root.manager.loggerDict:
            if re.match(prefix_re, name):
                logging.getLogger(name).setLevel(logging.ERROR)

    def _download_model(self):
        logger.info(f"Loading model {self.model_name!r}")
        self._model = SentenceTransformer(self.model_name, trust_remote_code=True)
        
    def _load_model(self):
        self._download_model()

    def encode(self, docs: t.Sequence[str], query: bool = False) -> t.Sequence[t.Sequence[float]]:
        embeddings = []
        for doc in tqdm.tqdm(docs):
            if not doc:
                zero_length = self._observed_hidden_size
                embeddings.append(np.zeros((1, zero_length)))
                continue
            embeddings.append(self._encode_doc(doc))
        return embeddings

    def chunk_text(self, text: str, chunk_size=None, overlap=None):
        chunk_size = chunk_size or self.chunk_size
        overlap = overlap or self.overlap
        tokens = text.split()
        chunks = []
        longest = 0
        for i in range(0, len(tokens), chunk_size - overlap):
            chunk = tokens[i : i + chunk_size]
            longest = max(longest, len(chunk))
            chunks.append(chunk)
        if len(chunks) > 1:
            for i in range(len(chunks)):
                chunk = chunks[i]
                if len(chunk) < longest:
                    new_bits = ["[PAD]"] * (longest - len(chunk))
                    chunk.extend(new_bits)
                    chunks[i] = " ".join(chunk)
        return [" ".join(c) for c in chunks]

    def _encode_doc(self, doc, query=False):
        query_prompt = self.query_prompt_name if query else None
        chunks = self.chunk_text(doc)
        embeddings = []
        for chunk in chunks:
            embedding = self._encode_chunk(chunk, query_prompt)
            if isinstance(embedding, np.ndarray):
                embedding = torch.from_numpy(embedding)
            embeddings.append(embedding)
        embedding_stack = torch.stack(embeddings)
        return torch.mean(embedding_stack, dim=0).numpy()

    def _encode_chunk(self, doc, query_prompt=None):
        if query_prompt:
            return self.model.encode(doc, prompt_name=query_prompt)
        return self.model.encode(doc)
