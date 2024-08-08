import importlib


def import_object(import_path):
    module_path, class_name = import_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


class KeyFormatter:

    delim = "::"

    @staticmethod
    def flatten_summary_key(module_name, index):
        return f"{module_name}{KeyFormatter.delim}{index}"

    @staticmethod
    def extract_module_name(key):
        return key.split(KeyFormatter.delim)[0]
