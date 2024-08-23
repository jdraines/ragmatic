from ._types import PresetData
from .local_docs_preset import local_docs_preset


variable_defaults = local_docs_preset.variable_defaults.copy()
variable_defaults.pop("local_documents_path")
variable_defaults["local_python_package_path"] = "./src"

_component_config = local_docs_preset.components.copy()
_component_config.update({
    "document_sources": {
        "local_python_package": {
            "type": "pycode_filesystem",
            "config": {
                "root_path": "${local_python_package_path}"
            }
        },
        "localpy_storage": {
            "type": "storage",
            "config": "localpy"
        }
    },
    "rag_agents": {
        "pycode": {
            "type": "python_code",
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
})


_pipelines_config = {
    "ingest-python-codebase": [
        {
            "action": "summarize",
            "config": {
                "document_source": "local_python_package",
                "root_path": "./src",
                "summarizer": "pycode",
                "storage": "localpy"
            }
        },
        {
            "action": "encode",
            "config": {
                "document_source": "localpy_storage",
                "encoder": "plaintext",
                "storage": "localpy"
            }
        }
    ]
}


_rag_query_command_config = local_docs_preset.rag_query_command.copy()
_rag_query_command_config.update({
    "rag_agent": "pycode",
    "document_source": "local_python_package"
})


pycode_preset = PresetData(
    components=_component_config,
    pipelines=_pipelines_config,
    rag_query_command=_rag_query_command_config,
    variable_defaults=variable_defaults
)
