import importlib


def import_object(import_path):
    module_path, class_name = import_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


class CollectionKeyFormatter:

    delim = "::"

    @staticmethod
    def flatten_collection_key(collection_name, index):
        return f"{collection_name}{CollectionKeyFormatter.delim}{index}"

    @staticmethod
    def extract_collection_name(key):
        return key.split(CollectionKeyFormatter.delim)[0]
