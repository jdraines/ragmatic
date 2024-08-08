import os
import typing as t
from ..bases import OmniStore
from .metadata_store import PydictMetadataStore
from .vector_store import PydictVectorStore
from .summary_store import PydictSummaryStore



class PydictOmniStore(OmniStore):
    
    _default_dirpath = 'data'

    def __init__(self, config):
        self.config = config
        self.dirpath = os.path.expanduser(config.get('dirpath', self._default_dirpath))
        os.makedirs(self.dirpath, exist_ok=True)
        self._metadata_store = self._init_metadata_store()
        self._vector_store = self._init_vector_store()
        self._summary_store = self._init_summary_store()

    def _init_metadata_store(self):
        filepath = os.path.join(self.dirpath, 'metadata.pkl')
        config = {"filepath": filepath}
        return PydictMetadataStore(config)
    
    def _init_vector_store(self):
        filepath = os.path.join(self.dirpath, 'vectors.pkl')
        config = {"filepath": filepath}
        return PydictVectorStore(config)
    
    def _init_summary_store(self):
        filepath = os.path.join(self.dirpath, 'summaries.pkl')
        config = {"filepath": filepath}
        return PydictSummaryStore(config)
