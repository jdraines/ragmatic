from .bases import MetadataStore
from .es_store import ElasticsearchMetadataStore
from .py_store import PyStore


_stores = {
    ElasticsearchMetadataStore.store_name: ElasticsearchMetadataStore,
    PyStore.store_name: PyStore,
}


def get_store_cls(store_name: str) -> MetadataStore:
    if store_name not in _stores:
        raise ValueError(f"Store {store_name} not found")
    return _stores[store_name]
