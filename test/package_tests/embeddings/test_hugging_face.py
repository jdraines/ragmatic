from unittest.mock import MagicMock, patch
import pytest

from ragmatic.embeddings import hugging_face


@pytest.fixture
def hfe_config():
    return hugging_face.HuggingFaceEmbeddingConfig(
        model_name="test_model",
        tokenizer_config={"test": "config"},
        save_filepath="test_filepath",
        save_model=True
    )

@pytest.fixture
def hfe_configdict(hfe_config):
    return hfe_config.model_dump()

@pytest.fixture
def mock_autoloader():
    return MagicMock()


@pytest.fixture
def mock_auto_tokenizer():
    return MagicMock()


@pytest.fixture
def hft_embedder(hfe_configdict, monkeypatch):
    monkeypatch.setattr(hugging_face.HuggingFaceTransformerEmbedder, "_init_auto_model_class", lambda x: MagicMock())
    hfe = hugging_face.HuggingFaceTransformerEmbedder(hfe_configdict)
    return hfe


class TestHuggingFaceTransformerEmbedder:

    def test__init__(self, hfe_configdict, hft_embedder):
        hfe = hft_embedder
        assert hfe.config == hfe_configdict
        assert hfe.model_name == "test_model"
        assert hfe.tokenizer_config == {"test": "config"}
        assert hfe.save_filepath == "test_filepath"
        assert hfe.save_model == True
    