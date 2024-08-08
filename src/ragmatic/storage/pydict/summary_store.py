import pickle
import os

from ..bases import SummaryStore


class PydictSummaryStore(SummaryStore):
    
    name = 'pydict'
    _default_filepath = 'summaries.pkl'


    def __init__(self, config):
        self.config = config
        self.filepath = self.config.get('filepath', self._default_filepath)
        self.__data: dict[str, str] = {}

    @property
    def _data(self):
        if not self.__data:
            self._load_summaries()
        return self.__data

    def store_summaries(self, summaries: dict[str, str]):
        self._data.update(summaries)
        self._write_summaries(self._data)

    def _write_summaries(self, data):
        with open(self.filepath, "wb") as f:
            pickle.dump(data, f)

    def _load_summaries(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(
                f"Summaries not loaded: File {self.filepath} does not exist."
            )
        with open(self.filepath, "rb") as f:
            self.__data = pickle.load(f)

    def get_summary(self, key: str):
        return self._data.get(key)

    def get_all_summaries(self):
        return self._data
