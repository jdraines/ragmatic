import logging
import os
import re
import typing as t
from itertools import product
from logging import getLogger

import numpy as np
import torch
import torch.nn.functional as F
import tqdm
from ragmatic.utils.refs import RefBaseModel
from pydantic import ConfigDict
from sklearn.preprocessing import normalize
from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer

from .bases import Embedder

logger = getLogger(__name__)


def _get_salesforce_model_names():
    def _get_model_name(size, data):
        return f"Salesforce/codegen-{size}-{data}"

    sizes = ["350M", "2B", "6B", "16B"]
    data = ["nl", "mono", "multi"]
    return [_get_model_name(size, data) for size, data in product(sizes, data)]


class HfTransformersEmbeddingConfig(RefBaseModel):
    model_config = ConfigDict(protected_namespaces=())
    model_name: str
    tokenizer_config: dict = {}
    save_filepath: str = "embedding_model.pkl"
    save_model: bool = True
    expected_hidden_size: int = 1024
    chunk_size: int = 512
    overlap: int = 128

class HfTransformersEmbedder(Embedder):
    embedder_name = "hf_transformer"
    _causal_lm_models = {
        *_get_salesforce_model_names(),
    }

    def __init__(self, config):
        self.config = config
        self.model_name = config["model_name"]
        self.tokenizer_config = config.get("tokenizer_config", {})
        self.save_model: bool = config.get("save_model", True)
        self.save_filepath = config.get("save_filepath", "embedding_model.pkl")
        self._expected_hidden_size = config.get("expected_hidden_size", 1024)
        self._observed_hidden_size = 0
        self._auto_model_class = self._init_auto_model_class()
        self._model = None
        self._tokenizer = None

    @property
    def model(self):
        if not self._model:
            if os.path.exists(self.save_filepath):
                self._load_model()
            else:
                self._download_model()
        assert self._model is not None
        return self._model

    @property
    def tokenizer(self):
        _ = self.model
        assert self._tokenizer is not None
        return self._tokenizer

    def _silence_loggers(self):
        to_silence = ["^transformers", "^torch"]
        prefix_re = re.compile(rf'^(?:{ "|".join(to_silence) })')
        for name in logging.root.manager.loggerDict:
            if re.match(prefix_re, name):
                logging.getLogger(name).setLevel(logging.ERROR)

    def _download_model(self):
        logger.info(f"Loading model {self.model_name!r}")
        self._model = self._auto_model_class.from_pretrained(self.model_name, trust_remote_code=True)
        if self.save_model:
            logger.info(f"Saving model to {self.save_filepath}")
            self._model.save(self.save_filepath)
        logger.info(f"Loading tokenizer {self.model_name!r}")
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        if self.save_model:
            tokenizer_filepath = (
                os.path.dirname(self.save_filepath) + "/tokenizer.pkl"
            )
            logger.info(f"Saving model to {tokenizer_filepath}")
            self._tokenizer.save_pretrained(tokenizer_filepath)

    def _load_model(self):
        logger.info(f"Loading model from {self.save_filepath}")
        self._model = self._auto_model_class(
            self.save_filepath, trust_remote_code=True
        )
        tokenizer_filepath = (
            os.path.dirname(self.save_filepath) + "/tokenizer.pkl"
        )
        logger.info(f"Loading tokenizer from  {tokenizer_filepath}")
        self._tokenizer = AutoTokenizer.from_pretrained(tokenizer_filepath)

    def encode(self, docs: t.Sequence[str], query: bool = False) -> t.Sequence[t.Sequence[float]]:
        embeddings = []
        for doc in tqdm.tqdm(docs):
            if not doc:
                zero_length = (self._observed_hidden_size * 2) or (
                    self._expected_hidden_size * 2
                )
                embeddings.append(np.zeros((1, zero_length)))
                continue
            embeddings.append(self._encode_doc(doc))
        return embeddings

    def _init_auto_model_class(self):
        if self.model_name in self._causal_lm_models:
            return AutoModelForCausalLM
        return AutoModel

    def chunk_text(self, text, chunk_size=None, overlap=None):
        chunk_size = chunk_size or self.chunk_size
        overlap = overlap or self.overlap
        tokens = self.tokenizer.tokenize(text)
        chunks = []
        for i in range(0, len(tokens), chunk_size - overlap):
            chunk = tokens[i : i + chunk_size]
            chunks.append(self.tokenizer.convert_tokens_to_string(chunk))
        return chunks

    def _encode_doc(self, doc):
        chunks = self.chunk_text(doc)
        embeddings = []
        for chunk in chunks:
            embedding = self._encode_chunk(chunk)
            if isinstance(embedding, np.ndarray):
                embedding = torch.from_numpy(embedding)
            embeddings.append(embedding)
        embedding_stack = torch.stack(embeddings)
        return torch.mean(embedding_stack, dim=0).numpy()

    def _encode_chunk(self, doc):
        if not self.tokenizer.pad_token and self.tokenizer.eos_token:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        else:
            self.tokenizer.pad_token = '[PAD]'
        inputs = self.tokenizer(doc, **self.tokenizer_config)
        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True)
        last_hidden_state = outputs.hidden_states[-1]
        self._observed_hidden_size = last_hidden_state.shape[-1]
        last_state_mean_pooled = self.process_hidden_state(
            last_hidden_state, inputs["attention_mask"]
        )
        next_last_hidden_state = outputs.hidden_states[-3]
        next_last_state_mean_pooled = self.process_hidden_state(
            next_last_hidden_state,
            inputs["attention_mask"],
            pooling_strategy="attention",
        )
        return normalize(
            torch.cat(
                [last_state_mean_pooled, next_last_state_mean_pooled], dim=-1
            )
        )

    def process_hidden_state(
        self, hidden_state, attention_mask, pooling_strategy="mean"
    ):
        # assumes hidden_state.size is (batch_size, seq_len, hidden_size)
        real_tokens_mask = (
            attention_mask.unsqueeze(-1).expand(hidden_state.size()).float()
        )
        masked_hidden_state = hidden_state * real_tokens_mask
        if pooling_strategy == "mean":
            sum_embeddings = torch.sum(masked_hidden_state, dim=1)
            sum_mask = torch.clamp(
                attention_mask.sum(dim=1, keepdim=True), min=1e-9
            )
            mean_pooled = sum_embeddings / sum_mask
            return mean_pooled
        elif pooling_strategy == "max":
            max_pooled, _ = torch.max(masked_hidden_state, dim=1)
            return max_pooled
        elif pooling_strategy == "attention":
            cls_vector = hidden_state[:, 0, :]
            attention_scores = torch.matmul(
                hidden_state, cls_vector.unsqueeze(-1)
            ).squeeze(-1)
            attention_scores = F.softmax(attention_scores, dim=-1)
            attention_pooled = torch.bmm(
                attention_scores.unsqueeze(1), hidden_state
            ).squeeze(1)
            return attention_pooled
        else:
            raise ValueError(f"Invalid pooling strategy {pooling_strategy}")
