import typing as t
from ragmatic.utils import import_object


_vector_stores = {
    "pydict": "ragmatic.storage.pydict.vector_store.PydictVectorStore"
}

_text_doc_stores =  {
    "pydict": "ragmatic.storage.pydict.text_doc_store.PydictTextDocumentStore"
}

_omni_stores = {
    "pydict": "ragmatic.storage.pydict.omni_store.PydictOmniStore"
}


def get_store_cls(data_type:str, store_type: str) -> t.Type:
    store_dict = globals()[f"_{data_type}_stores"]
    if store_type not in store_dict:
        try:
            return import_object(store_type)
        except Exception:
            raise ValueError(f"Store {store_type} not found")
    return import_object(store_dict[store_type])
