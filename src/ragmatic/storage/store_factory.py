from ..utils import import_object
from .bases import MetadataStore


_metadata_stores = {
    "elasticsearch": "ragmatic.storage.es_store.ElasticsearchMetadataStore",
    "pydict": "ragmatic.storage.pydict.metadata_store.PydictMetadataStore"
}

_vector_stores = {
    "pydict": "ragmatic.storage.pydict.vector_store.PydictVectorStore"
}

_summary_stores =  {
    "pydict": "ragmatic.storage.pydict.summary_store.PydictSummaryStore"
}

_omni_stores = {
    "pydict": "ragmatic.storage.pydict.omni_store.PydictOmniStore"
}


def get_store_cls(store_type:str, store_name: str) -> MetadataStore:
    store_dict = globals()[f"_{store_type}_stores"]
    if store_name not in store_dict:
        raise ValueError(f"Store {store_name} not found")
    return import_object(store_dict[store_name])
