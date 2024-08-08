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


ALLOWED_FILE_TYPES = [
    'babelconfig', 'babelrc', 'bash', 'c', 'cc', 'cfg', 'clj', 'cljc', 'cljs', 'conf',
    'cpp', 'css', 'csv', 'dart', 'dockerignore', 'docx', 'editorconfig', 'edn',
    'env', 'eslintrc', 'fish', 'flowconfig', 'gitattributes', 'gitignore', 'go',
    'graphqlconfig', 'groovy', 'h', 'hpp', 'html', 'ini', 'ipynb', 'java',
    'jestconfig', 'js', 'json', 'jsx', 'kt', 'kts', 'less', 'lock', 'log', 'md',
    'odf', 'odg', 'odp', 'ods', 'odt', 'otf', 'otg', 'otp', 'ots', 'ott', 'pdf',
    'php', 'pl', 'pm', 'postcssconfig', 'pptx', 'prettierrc', 'properties', 'py',
    'r', 'rb', 'rmd', 'rs', 'rst', 'sass', 'scala', 'scss', 'sh', 'sql',
    'stylelintrc', 'swift', 't', 'toml', 'ts', 'tsconfig', 'tsv', 'tsx', 'txt',
    'webpackconfig', 'xlsx', 'xml', 'yaml', 'yml', 'zsh'
]
