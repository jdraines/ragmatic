from ._types import PresetData

variable_defaults = {
    "local_documents_path": "./documents",
    "encoding_model_name": "dunzhang/stella_en_1.5B_v5",
    "n_nearest": 10
}


_component_config = {
    "document_sources": {
        "local_directory": {
            "type": "filesystem",
            "config": {
                "root_path": "${local_documents_path}"
            }
        }
    },
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
                "model_name": "${encoding_model_name}",
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
        "generic": {
            "type": "generic",
            "config": {
                "llm": "openai",
                "storage": "localpy",
                "encoder": "plaintext",
                "n_nearest": "${n_nearest}",
                "prompt": "",
                "system_prompt": ""
            }
        }
    }
}

_pipelines_config = {
    "ingest-directory-text": [
        {
            "action": "encode",
            "config": {
                "document_source": "local_directory",
                "encoder": "plaintext",
                "storage": "localpy"
            }
        }
    ]
}

_rag_query_command_config = {
    "rag_agent": "generic",
    "document_source": "local_directory"
}


local_docs_preset = PresetData(
    components=_component_config,
    piplines=_pipelines_config,
    rag_query_command=_rag_query_command_config,
    variable_defaults=variable_defaults
)
