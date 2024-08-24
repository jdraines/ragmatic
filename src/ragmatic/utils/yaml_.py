import yaml
import copy

class Ref:
    def __init__(self, ref_path):
        self.ref_path = ref_path

def ref_constructor(loader, node):
    value = loader.construct_scalar(node)
    return Ref(value)

yaml.add_constructor(u'!ref', ref_constructor, yaml.SafeLoader)

def resolve_references(data, root=None):
    if root is None:
        root = data

    if isinstance(data, dict):
        return {key: resolve_references(value, root) for key, value in data.items()}
    elif isinstance(data, list):
        return [resolve_references(item, root) for item in data]
    elif isinstance(data, Ref):
        resolved = resolve_ref(root, data.ref_path)
        return resolve_references(resolved, root)
    else:
        return data

def resolve_ref(data, ref_path):
    parts = ref_path.split('.')
    current = data
    for part in parts:
        if part in current:
            current = current[part]
        else:
            raise KeyError(f"Reference not found: {ref_path}")
    return copy.deepcopy(current)


def ragmatic_load_yaml(stream):
    data = yaml.safe_load(stream)
    return resolve_references(data)
