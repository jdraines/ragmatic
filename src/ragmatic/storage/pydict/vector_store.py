import typing as t
import pickle
import os
import numpy as np
import re
from collections import OrderedDict
from logging import getLogger

from ragmatic.utils.refs import RefBaseModel
from pydantic import Field

from ..bases import VectorStore


logger = getLogger(__name__)


class QueryMethod:
    name: str = None

    @staticmethod
    def execute(query: dict, data: dict[str, np.ndarray]):
        pass

    @staticmethod
    def build_query_from_embedding(embedding: t.Sequence[float]) -> t.Any:
        pass


class CosineSimilarity(QueryMethod):
    """
    Expected query format:
    {
        "method": "cosine_similarity",
        "vector": <np.ndarray>,
        "limit": <int> (optional)
    }
    """

    name = 'cosine_similarity'

    @staticmethod
    def execute(query: dict, data: dict[str, np.ndarray]):
        if 'vector' not in query:
            raise ValueError('Query must contain a "vector" key value pair')
        query_vector = query['vector']
        if not isinstance(query_vector, np.ndarray):
            raise ValueError('Query vector must be a numpy array')
        data = OrderedDict(data)
        doc_embeddings_matrix = np.asarray(list(data.values()))
        logger.debug(f"Matrix shape: {doc_embeddings_matrix.shape}")
        query_vector, doc_embeddings_matrix =\
            CosineSimilarity._check_and_reshape(
                query_vector,
                doc_embeddings_matrix
            )
        similarities =\
            CosineSimilarity._cosine_similarity(
                query_vector,
                doc_embeddings_matrix
            ).flatten()
        sorted_indices_desc = np.argsort(similarities)[::-1].flatten()
        results = [list(data.keys())[i] for i in sorted_indices_desc]
        if limit := query.get('limit'):
            return results[:limit]
        return results
    
    @staticmethod
    def _cosine_similarity(v1_single: np.ndarray, matrix: np.ndarray):
        v1 = v1_single.flatten()
        dot_product = np.dot(matrix, v1)
        norm_v1 = np.linalg.norm(v1)
        norm_matrix = np.linalg.norm(matrix, axis=1)
        norm_product = norm_v1 * norm_matrix
        cosine_similarity = dot_product / norm_product
        return cosine_similarity

    @staticmethod
    def _check_and_reshape(vector, matrix):
        if vector.ndim == 1:
            logger.info("Reshaping vector to (1, n)")
            vector = vector.reshape(1, -1)
        
        if vector.ndim != 2 or vector.shape[0] != 1:
            raise ValueError(f"Vector should have shape (1, n), but has shape {vector.shape}")
        
        if matrix.ndim not in [2, 3]:
            raise ValueError(f"Matrix should be 2D or 3D, but has {matrix.ndim} dimensions")
        
        if matrix.ndim == 3:
            if matrix.shape[1] != 1:
                raise ValueError(f"For 3D matrix, second dimension should be 1, but shape is {matrix.shape}")
            matrix = matrix.reshape(matrix.shape[0], matrix.shape[2])
        
        if vector.shape[1] != matrix.shape[1]:
            raise ValueError(f"Vector dimension ({vector.shape[1]}) does not match matrix last dimension ({matrix.shape[1]})")
        
        return vector, matrix


class PydictVectorStoreConfig(RefBaseModel):
    filepath: t.Optional[str] = Field(default='vectors.pkl')
    default_query_method: t.Optional[str] = Field(default="cosine_similarity")
    overwrite: t.Optional[bool] = Field(default=False)
    allow_init: t.Optional[bool] = Field(default=True)


class PydictVectorStore(VectorStore):
    
    name = 'pydict'
    _allowed_query_methods = {
        "cosine_similarity": CosineSimilarity
    }

    def __init__(self, config):
        config = PydictVectorStoreConfig(**config)
        self.config = config
        self.overwrite = config.overwrite
        self.allow_init = config.allow_init
        self.filepath = os.path.expanduser(self.config.filepath)
        self.__data: dict[str, np.ndarray] = {}
        self._default_query_method = config.default_query_method

    @property
    def _data(self):
        if not self.__data:
            self._load_vectors()
        return self.__data

    def store_vectors(self, vectors: dict[str, np.ndarray]):
        if self.overwrite:
            self.__data = vectors
        else:
            self._data.update(vectors)
        logger.info(f"Storing vectors to {self.filepath}")
        self._write_vectors(self._data)

    def get_vectors(self, keys: list[str]):
        return [self._data.get(key) for key in keys]

    def scan_keys(self, match: str):
        return [key for key in self._data.keys() if re.match(match, key)]

    def _write_vectors(self, data):
        with open(self.filepath, "wb") as f:
            pickle.dump(data, f)

    def _load_vectors(self):
        if not os.path.exists(self.filepath):
            if self.allow_init:
                return
            raise FileNotFoundError(
                f"Vector data not loaded: File {self.filepath} does not exist."
            )
        with open(self.filepath, "rb") as f:
            self.__data = pickle.load(f)
    
    def query(self, query: dict):
        if 'method' not in query:
            query["method"] = self._default_query_method
        method = query['method']
        if method not in self._allowed_query_methods:
            raise ValueError(f'Invalid query method: {method}')
        return self._allowed_query_methods[method].execute(query, self._data)
    
    def query_byvector(self, vector: t.Sequence[float], n: int = None):
        return self.query({
            "vector": vector,
            "limit": n
        })
