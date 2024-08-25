import typing as t
import pickle
import os

from ragmatic.utils.refs import RefBaseModel
from pydantic import Field

from ..bases import TextDocumentStore


class PydictTextDocumentStoreConfig(RefBaseModel):
    overwrite: t.Optional[bool] = Field(default=False)
    filepath: t.Optional[str] = Field(default=None)
    allow_init: t.Optional[bool] = Field(default=True)


class PydictTextDocumentStore(TextDocumentStore):
    
    name = 'pydict'
    _default_filepath = 'text_documents.pkl'


    def __init__(self, config: PydictTextDocumentStoreConfig):
        config = PydictTextDocumentStoreConfig(**config)
        self.config = config
        self.overwrite = config.overwrite
        self.allow_init = config.allow_init
        self.filepath = self.config.filepath or self._default_filepath
        self.__data: dict[str, str] = {}

    @property
    def _data(self):
        if not self.__data:
            self._load_documents()
        return self.__data

    def store_text_docs(self, text_docs: dict[str, str]):
        if self.overwrite:
            self.__data = text_docs
        else:
            self._data.update(text_docs)
        self._write_documents(self._data)

    def _write_documents(self, data):
        with open(self.filepath, "wb") as f:
            pickle.dump(data, f)

    def _load_documents(self):
        if not os.path.exists(self.filepath):
            if self.allow_init:
                return
            raise FileNotFoundError(
                f"Summaries not loaded: File {self.filepath} does not exist."
            )   
        with open(self.filepath, "rb") as f:
            self.__data = pickle.load(f)

    def get_document(self, key: str):
        return self._data.get(key)

    def get_documents(self, keys: list[str]) -> list[str]:
        docs = []
        for key in keys:
            if key not in self._data:
                raise KeyError(f"Document with key {key} not found in storage.")
            docs.append(self._data.get(key))
        return docs

    def get_all_documents(self) -> dict[str, str]:
        return self._data
