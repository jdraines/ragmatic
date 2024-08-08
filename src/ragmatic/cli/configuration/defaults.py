"""
This module exists to provide a default configuration for the Ragmatic CLI. This
configuration is used in two ways:

1) As a default configuration for the CLI when no configuration file is provided
2) As a template for generating a configuration file
"""

DEFAULT_COMPONENT_CONFIG = {
    "storage": {
        "localpy": {
            "data_type": "omni",
            "type": "pydict",
            "config": {
                "dirpath": "./data",
                "overwrite": True
            }
        }
    },
    "llms": {
        "openai": {
            "type": "openai",
            "config": {
                "api_keyenvvar": "OPENAI_API_KEY"
            }
        }
    },
    "summarizers": {
        "pycode": {
            "type": "python_code",
            "config": {
                "llm": "openai"
            }
        }
    },
    "encoders": {
        "plaintext": {
            "type": "hugging_face",
            "config": {
                "model_name": "dunzhang/stella_en_1.5B_v5",
                "tokenizer_config": {
                    "return_tensors": "pt",
                    "max_length": 1024,
                    "truncation": True,
                    "padding": "max_length"
                },
                "save_model": False
            }
        }
    },
    "rag_agents": {
        "pycode": {
            "type": "python_code",
            "config": {
                "llm": "openai",
                "storage": "localpy",
                "encoder": "plaintext",
                "n_nearest": 10,
                "prompt": "",
                "system_prompt": ""
            }
        }
    }
}


DEFAULT_PIPELINES_CONFIG = {
    "ingest-directory-text": [
        {
            "action": "encode",
            "config": {
                "document_source": {
                    "type": "storage",
                    "config": "localpy"
                },
                "encoder": "plaintext",
                "storage": "localpy"
            }
        }
    ]
}

DEFAULT_PYCODE_PIPELINES_CONFIG = {
        "ingest-python-codebase": [
            {
                "action": "summarize",
                "config": {
                    "document_source": {
                        "type": "pycode_filesystem",
                        "config": {
                            "root_path": "./src"
                        }
                    },
                    "root_path": "./src",
                    "summarizer": "pycode",
                    "storage": "localpy"
                }
            },
            {
                "action": "encode",
                "config": {
                    "document_source": {
                        "type": "storage",
                        "config": "localpy"
                    },
                    "encoder": "plaintext",
                    "storage": "localpy"
                }
            }
        ]
    }

DEFAULT_RAG_QUERY_COMMAND_CONFIG = {
    "rag_agent": "pycode",
    "document_source": {
        "type": "pycode_filesystem",
        "config": {
            "root_path": "./src"
        }
    }
}


def get_component_config(name="default"):
    configs = {
        "default": DEFAULT_COMPONENT_CONFIG
    }
    if name not in configs:
        raise ValueError(f"Unknown component config name: {name}")
    return configs[name]


def get_pipelines_config(name="default"):
    configs = {
        "default": DEFAULT_PIPELINES_CONFIG,
        "pycode": DEFAULT_PYCODE_PIPELINES_CONFIG
    }
    if name not in configs:
        raise ValueError(f"Unknown pipelines config name: {name}")
    return configs[name]


def get_rag_query_command_config(name="default"):
    configs = {
        "default": DEFAULT_RAG_QUERY_COMMAND_CONFIG
    }
    if name not in configs:
        raise ValueError(f"Unknown rag query command config name: {name}")
    return configs[name]
