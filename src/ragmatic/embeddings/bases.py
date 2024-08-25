from abc import ABC, abstractmethod
import typing as t


class Embedder:

    embedder_name: str = None

    @abstractmethod
    def __init__(self, config):
        pass

    @abstractmethod
    def encode(self, docs: t.Sequence[str], query: bool = False) -> t.Sequence[t.Sequence[float]]:
        pass
