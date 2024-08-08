import typing as t
import pickle
import os

from pydantic import BaseModel, Field

from ..bases import TextDocumentStore


class PydictTextDocumentStoreConfig(BaseModel):
    overwrite: t.Optional[bool] = Field(default=True)
    filepath: t.Optional[str] = Field(default=None)


class PydictTextDocumentStore(TextDocumentStore):
    
    name = 'pydict'
    _default_filepath = 'text_documents.pkl'


    def __init__(self, config: PydictTextDocumentStoreConfig):
        config = PydictTextDocumentStoreConfig(**config)
        self.config = config
        self.overwrite = config.overwrite
        self.filepath = self.config.filepath or self._default_filepath
        self.__data: dict[str, str] = {}

    @property
    def _data(self):
        if not self.__data:
            self._load_documents()
        return self.__data

    def store_text_docs(self, text_docs: dict[str, str]):
        try:
            self._data.update(text_docs)
        except FileNotFoundError as e:
            if self.overwrite:
                self.__data = text_docs
            else:
                raise e
        self._write_documents(self._data)

    def _write_documents(self, data):
        with open(self.filepath, "wb") as f:
            pickle.dump(data, f)

    def _load_documents(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(
                f"Summaries not loaded: File {self.filepath} does not exist."
            )
        with open(self.filepath, "rb") as f:
            self.__data = pickle.load(f)

    def get_document(self, key: str):
        return self._data.get(key)

    def get_all_documents(self):
        return self._data
