import os
import typing as t
from itertools import product

from pydantic import BaseModel
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoModel, AutoTokenizer
from sklearn.preprocessing import normalize

from .bases import Embedder


def _get_salesforce_model_names():
    def _get_model_name(size, data):
        return f"Salesforce/codegen-{size}-{data}"
    sizes = ["350M", "2B", "6B", "16B"]
    data = ["nl", "mono", "multi"]
    return [_get_model_name(size, data) for size, data in product(sizes, data)]


class HuggingFaceEmbeddingConfig(BaseModel):
    model_name: str
    tokenizer_config: dict = {}
    save_filepath: str = "embedding_model.pkl"
    save_model: bool = True


class HuggingFaceTransformerEmbedder(Embedder):

    embedder_name = "hugging_face"
    _causal_lm_models = {
        *_get_salesforce_model_names(),
    }

    def __init__(self, config):
        self.config = config
        self.model_name = config["model_name"]
        self.tokenizer_config = config.get("tokenizer_config", {})
        self.save_filepath = config.get("save_filepath", "embedding_model.pkl")
        self.save_model: bool = config.get("save_model", True)
        self._auto_model_class = self._init_auto_model_class()
        self._model = None
        self._tokenizer = None

    @property
    def model(self):
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

    def _download_model(self):
        self._model = self._auto_model_class.from_pretrained(self.model_name)
        if self.save_model:
            self._model.save(self.save_filepath)
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self.save_model:
            tokenizer_filepath = os.path.dirname(self.save_filepath) + "/tokenizer.pkl"
            self._tokenizer.save_pretrained(tokenizer_filepath)

    def _load_model(self):
        self._model = self._auto_model_class(self.save_filepath, trust_remote_code=True)
        tokenizer_filepath = os.path.dirname(self.save_filepath) + "/tokenizer.pkl"
        self._tokenizer = AutoTokenizer.from_pretrained(tokenizer_filepath)

    def encode(self, docs: t.Sequence[str]) -> t.Sequence[t.Sequence[float]]:
        return [self._encode_doc(doc) for doc in docs]

    def _init_auto_model_class(self):
        if self.model_name in self._causal_lm_models:
            return AutoModelForCausalLM
        return AutoModel

    def chunk_text(self, text, chunk_size=1024, overlap=256):
        tokens = self.tokenizer.tokenize(text)
        chunks = []
        for i in range(0, len(tokens), chunk_size - overlap):
            chunk = tokens[i:i + chunk_size]
            chunks.append(self.tokenizer.convert_tokens_to_string(chunk))
        return chunks


    def _encode_doc(self, doc):
        chunks = self.chunk_text(doc)
        embeddings = []
        for chunk in chunks:
            embeddings.append(self._encode_chunk(chunk))
        return torch.mean(torch.stack(embeddings), dim=0).numpy()


    def _encode_chunk(self, doc):
        self.tokenizer.pad_token = self.tokenizer.eos_token
        inputs = self.tokenizer(doc, return_tensors="pt", max_length=1024, truncation=True, padding="max_length")
        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True)
        last_hidden_state = outputs.hidden_states[-1]
        last_state_mean_pooled = self.process_hidden_state(last_hidden_state, inputs["attention_mask"])
        next_last_hidden_state = outputs.hidden_states[-3]
        next_last_state_mean_pooled = self.process_hidden_state(next_last_hidden_state, inputs["attention_mask"], pooling_strategy="attention")
        return normalize(torch.cat([last_state_mean_pooled, next_last_state_mean_pooled], dim=-1))


    def process_hidden_state(self, hidden_state, attention_mask, pooling_strategy="mean"):
        real_tokens_mask = attention_mask.unsqueeze(-1).expand(hidden_state.size()).float()
        masked_hidden_state = hidden_state * real_tokens_mask
        if pooling_strategy == "mean":
            sum_embeddings = torch.sum(masked_hidden_state, dim=1)
            sum_mask = torch.clamp(attention_mask.sum(dim=1, keepdim=True), min=1e-9)
            mean_pooled = sum_embeddings / sum_mask
            return mean_pooled
        elif pooling_strategy == "max":
            max_pooled, _ = torch.max(masked_hidden_state, dim=1)
            return max_pooled
        elif pooling_strategy == "attention":
            cls_vector = hidden_state[:, 0, :]
            attention_scores = torch.matmul(hidden_state, cls_vector.unsqueeze(-1)).squeeze(-1)
            attention_scores = F.softmax(attention_scores, dim=-1)
            attention_pooled = torch.bmm(attention_scores.unsqueeze(1), hidden_state).squeeze(1)
            return attention_pooled
        else:
            raise ValueError(f"Invalid pooling strategy {pooling_strategy}")
