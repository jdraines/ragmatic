from abc import ABC, abstractmethod
import typing as t


class Embedder:

    @abstractmethod
    def __init__(self, config):
        pass

    @abstractmethod
    def encode(self, docs: t.Sequence[str]) -> t.Sequence[t.Sequence[float]]:
        pass
