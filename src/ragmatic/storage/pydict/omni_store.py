import os
import typing as t

from ragmatic.utils.refs import RefBaseModel
from pydantic import Field

from ..bases import OmniStore
from .vector_store import PydictVectorStore
from .text_doc_store import PydictTextDocumentStore


class PydictOmniStoreConfig(RefBaseModel):
    dirpath: t.Optional[str] = Field(default=None)
    overwrite: t.Optional[bool] = Field(default=True)


class PydictOmniStore(OmniStore):
    
    name = "pydict"
    _default_dirpath = 'data'

    def __init__(self, config):
        config = PydictOmniStoreConfig(**config)
        self.config = config
        self.overwrite = config.overwrite
        self.dirpath = os.path.expanduser((config.dirpath or self._default_dirpath))
        os.makedirs(self.dirpath, exist_ok=True)
        self._vector_store = self._init_vector_store()
        self._text_doc_store = self._init_text_doc_store()

    def _init_vector_store(self):
        filepath = os.path.join(self.dirpath, 'vectors.pkl')
        config = self._substore_config(filepath)
        return PydictVectorStore(config)
    
    def _init_text_doc_store(self):
        filepath = os.path.join(self.dirpath, 'text_documents.pkl')
        config = self._substore_config(filepath)
        return PydictTextDocumentStore(config)

    def _substore_config(self, filepath):
        return {
            "filepath": filepath,
            "overwrite": self.overwrite
        }
