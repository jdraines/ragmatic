import pytest
from unittest.mock import MagicMock
from ragmatic.cli.configuration.presets import _types



class TestPresetData:

    @pytest.fixture
    def preset_inputs(self):
        return {
            "components": {
                "object": {
                    "variable": "${component_variable}"
                }
            },
            "pipelines": {
                "object": {
                    "variable": "${pipeline_variable}"
                }
            },
            "rag_query_command": {
                "object": {
                    "variable": "${rag_query_variable}"
                }
            },
            "variable_defaults": {
                "component_variable": "component_default",
                "pipeline_variable": "pipeline_default",
                "rag_query_variable": "rag_query_default"
            }
        }
    
    @pytest.fixture
    def preset_data(self, preset_inputs):
        return _types.PresetData(**preset_inputs)
    
    @pytest.fixture
    def variable_inputs(self):
        return {
            "component_variable": "component_value",
            "pipeline_variable": "pipeline_value",
            "rag_query_variable": "rag_query_value"
        }

    def test_get_config(self, preset_data, variable_inputs, monkeypatch):
        master_config = MagicMock(side_effect=lambda **k: k)
        monkeypatch.setattr(_types, "MasterConfig", master_config)
        config = preset_data.get_config(**variable_inputs)
        assert config == {
            "project_name": "",
            "components": {
                "object": {
                    "variable": "component_value"
                }
            },
            "pipelines": {
                "object": {
                    "variable": "pipeline_value"
                }
            },
            "rag_query_command": {
                "object": {
                    "variable": "rag_query_value"
                }
            }
        }
        config = preset_data.get_config()
        assert config == {
            "project_name": "",
            "components": {
                "object": {
                    "variable": "component_default"
                }
            },
            "pipelines": {
                "object": {
                    "variable": "pipeline_default"
                }
            },
            "rag_query_command": {
                "object": {
                    "variable": "rag_query_default"
                }
            }
        }
    