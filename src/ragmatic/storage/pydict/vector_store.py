import pickle
import os
import numpy as np
import re
from collections import OrderedDict

from ..bases import VectorStore



class QueryMethod:
    name: str = None

    @staticmethod
    def execute(query: dict, data: dict[str, np.ndarray]):
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
        similarities = np.dot(list(data.values()), query_vector)
        sorted_indices = np.argsort(similarities)[::-1]
        results = [list(data.keys())[i] for i in sorted_indices]
        if limit := query.get('limit'):
            return results[:limit]
        return results
    

class PydictVectorStore(VectorStore):
    
    name = 'pydict'
    _default_filepath = 'vectors.pkl'
    _allowed_query_methods = {
        "cosine_similarity": CosineSimilarity
    }

    def __init__(self, config):
        self.config = config
        self.filepath = os.path.expanduser(self.config.get('filepath', self._default_filepath))
        self.__data: dict[str, np.ndarray] = {}

    @property
    def _data(self):
        if not self.__data:
            self._load_vectors()
        return self.__data

    def store_vectors(self, vectors: dict[str, np.ndarray]):
        self._data.update(vectors)

    def get_vectors(self, keys: list[str]):
        return [self._data.get(key) for key in keys]

    def scan_keys(self, match: str):
        return [key for key in self._data.keys() if re.match(match, key)]

    def _write_vectors(self, data):
        with open(self.filepath, "wb") as f:
            pickle.dump(data, f)

    def _load_vectors(self):
        if not os.path.exists(self.filepath):
            self.__data = {}
            return
        with open(self.filepath, "rb") as f:
            self.__data = pickle.load(f)
    
    def query_vectors(self, query: dict):
        if 'method' not in query:
            raise ValueError('Query must contain a "method" key value pair')
        method = query['method']
        if method not in self._allowed_query_methods:
            raise ValueError(f'Invalid query method: {method}')
        return self._allowed_query_methods[method].execute(query, self._data)