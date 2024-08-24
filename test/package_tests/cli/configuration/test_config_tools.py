import pytest
from pathlib import Path

from ragmatic.cli.configuration import tools
from ragmatic.cli.configuration.presets.local_docs_preset import local_docs_preset

thisdir = Path(__file__).parent
mockdir = thisdir / 'mocks'


@pytest.fixture
def mock_config_path():
    return mockdir / "config.yaml"


@pytest.fixture
def mock_config(mock_config_path):
    return tools.load_config(mock_config_path)

@pytest.fixture
def mock_partial_config():
    path = mockdir / "partial_config.yaml"
    return tools.load_config(path)


def test_load_configdict(mock_config_path):
    config = tools.load_configdict(mock_config_path)
    assert config


def test_ref_resolution(mock_config_path):
    config = tools.load_configdict(mock_config_path)
    # pick a ref to check
    assert config["components"]["storage"]["localpy"] ==\
        config["components"]["rag_agents"]["pycode"]["config"]["storage"]


def test_load_config(mock_config_path):
    config = tools.load_config(mock_config_path)
    assert config


def test_merge_defaults(mock_partial_config):
    preset_data = local_docs_preset
    merged = tools.merge_defaults(mock_partial_config, preset_data)
    assert merged
    assert "local_python_package_2" in merged.components.document_sources
    assert merged.components.document_sources["local_python_package_2"].config['root_path'] == "./src2"
    assert merged.components.encoders["plaintext"].config['model_name'] == "test_model"