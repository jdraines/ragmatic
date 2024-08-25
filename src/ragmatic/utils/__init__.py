from .factory import import_object
from .collection_key_formatter import CollectionKeyFormatter
from .refs import ragmatic_load_yaml


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
