import typing as t


class DocumentSourceBase:

    name: str = ""

    def __init__(self, config):
        self.config = config

    def get_documents(self, document_names: t.Optional[list[str]] = None) -> dict[str, str]:
        raise NotImplementedError

