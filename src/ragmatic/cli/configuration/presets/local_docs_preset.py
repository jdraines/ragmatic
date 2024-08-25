from ._types import PresetData
from ragmatic.utils.refs import Ref

variable_defaults = {
    "local_documents_path": "./documents",
    "encoding_model_name": "dunzhang/stella_en_400M_v5",
    "expected_hidden_size": 1024,
    "n_nearest": 10
}

doc_sources = {
    "local_directory": {
        "type": "filesystem",
        "config": {
            "root_path": "${local_documents_path}"
        }
    }
}

storage = {
    "localpy": {
        "data_type": "omni",
        "type": "pydict",
        "config": {
            "dirpath": "./data",
            "overwrite": True
        }
    }
}

llms = {
    "openai": {
        "type": "openai",
        "config": {
            "api_keyenvvar": "OPENAI_API_KEY",
        }
    }
}

summarizers = {
    "pycode": {
        "type": "python_code",
        "config": {
            "document_source": doc_sources["local_directory"],
            "llm": llms["openai"],
        }
    }
}

encoders = {
    "plaintext": {
        "type": "hf_sentence_transformers",
        "config": {
            "model_name": "${encoding_model_name}",
            "query_prompt_name": "s2p_query",
            "chunk_size": 512,
            "overlap": 128
        }
    },
    "plaintext_transformers": {
        "type": "hf_transformers",
        "config": {
            "model_name": "${encoding_model_name}",
            "tokenizer_config": {
                "return_tensors": "pt",
                "max_length": 512,
                "truncation": True,
                "padding": "longest"
            },
            "save_model": False,
            "expected_hidden_size": "${expected_hidden_size}",
            "chunk_size": 512,
            "overlap": 128
        }
    }
}

rag_agents = {
    "generic": {
        "type": "generic",
        "config": {
            "llm": Ref("components.llms.openai"), 
            "storage": Ref("components.storage.localpy"),
            "encoder": Ref("components.encoders.plaintext"), 
            "n_nearest": "${n_nearest}",
            "prompt": "",
            "system_prompt": ""
        }
    }
}

_component_config = {
    "document_sources": doc_sources,
    "storage": storage,
    "llms": llms,
    "summarizers": summarizers,
    "encoders": encoders,
    "rag_agents": rag_agents
}

_pipelines_config = {
    "ingest-directory-text": [
        {
            "action": "encode",
            "config": {
                "document_source": Ref("components.document_sources.local_directory"),
                "encoder": Ref("components.encoders.plaintext"),
                "storage": Ref("components.storage.localpy")
            }
        }
    ]
}

_rag_query_command_config = {
    "rag_agent": Ref("components.rag_agents.generic"),
    "document_source": Ref("components.document_sources.local_directory")
}


local_docs_preset = PresetData(
    components=_component_config,
    pipelines=_pipelines_config,
    rag_query_command=_rag_query_command_config,
    variable_defaults=variable_defaults
)
