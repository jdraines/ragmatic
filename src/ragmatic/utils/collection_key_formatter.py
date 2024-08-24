class CollectionKeyFormatter:

    delim = "::"

    @staticmethod
    def flatten_collection_key(collection_name, index):
        return f"{collection_name}{CollectionKeyFormatter.delim}{index}"

    @staticmethod
    def extract_collection_name(key):
        return key.split(CollectionKeyFormatter.delim)[0]
