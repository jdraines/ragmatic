from unittest.mock import MagicMock
import pytest
import numpy as np

# skip if transformers is not installed
try:
    from transformers import AutoModel, AutoModelForCausalLM
    import torch

    transformers_installed = True
except ImportError:
    transformers_installed = False

if not transformers_installed:
    pytest.skip(
        "transformers is not installed, skipping tests",
        allow_module_level=True,
    )


from ragmatic.embeddings import hf_transformers


@pytest.fixture
def hfe_config():
    return hf_transformers.HfTransformersEmbeddingConfig(
        model_name="test_model",
        tokenizer_config={"test": "config"},
        save_filepath="test_filepath",
        save_model=True,
        expected_hidden_size=512
    )


@pytest.fixture
def hfe_configdict(hfe_config):
    return hfe_config.model_dump()


@pytest.fixture
def mock_outputs():
    outputs = MagicMock()
    outputs.hidden_states = [
        torch.ones((1, 1024, 512)),
        torch.ones((1, 1024, 512)),
        torch.ones((1, 1024, 512)),
    ]
    return outputs


@pytest.fixture
def mock_model(mock_outputs):
    model = MagicMock(return_value=mock_outputs)
    model.save = MagicMock()
    return model


@pytest.fixture
def mock_autoloader(mock_model):
    autoloader = MagicMock()
    autoloader.return_value = mock_model
    autoloader.from_pretrained.return_value = mock_model
    return autoloader


@pytest.fixture
def mock_tokenizer_outputs():
    return {
        "input_ids": torch.ones((1, 1024)),
        "attention_mask": torch.ones((1, 1024)),
    }


@pytest.fixture
def mock_tokenizer(mock_tokenizer_outputs):
    return MagicMock(return_value=mock_tokenizer_outputs)


@pytest.fixture
def mock_auto_tokenizer(monkeypatch, mock_tokenizer):
    auto_tokenizer = MagicMock()
    auto_tokenizer.from_pretrained.return_value = mock_tokenizer
    monkeypatch.setattr(hf_transformers, "AutoTokenizer", auto_tokenizer)
    return auto_tokenizer


@pytest.fixture
def hft_embedder(
    hfe_configdict, monkeypatch, mock_autoloader, mock_auto_tokenizer
):
    monkeypatch.setattr(
        hf_transformers.HfTransformersEmbedder,
        "_init_auto_model_class",
        lambda x: MagicMock(),
    )
    hfe = hf_transformers.HfTransformersEmbedder(hfe_configdict)
    hfe._auto_model_class = mock_autoloader
    return hfe


class TestHfTransformersEmbedder:
    @pytest.fixture
    def mock_zeros_tensor(self):
        return np.zeros((1, 1024))

    @pytest.fixture
    def mock_ones_tensor(self):
        return np.ones((1, 1024))

    def test__init__(self, hfe_configdict, hft_embedder):
        hfe = hft_embedder
        assert hfe.config == hfe_configdict
        assert hfe.model_name == "test_model"
        assert hfe.tokenizer_config == {"test": "config"}
        assert hfe.save_filepath == "test_filepath"
        assert hfe.save_model

    def test_encode(
        self, hft_embedder, mock_zeros_tensor, mock_ones_tensor, monkeypatch
    ):
        hfe = hft_embedder
        monkeypatch.setattr(
            hfe, "_encode_doc", MagicMock(return_value=mock_ones_tensor)
        )
        output = hfe.encode(["test", None])
        expected_output = [mock_ones_tensor, mock_zeros_tensor]
        assert hfe._encode_doc.call_count == 1
        assert np.array(output).tolist() == np.array(expected_output).tolist()

    def test_chunk_text(self, hft_embedder, monkeypatch):
        hfe = hft_embedder
        mock_model = MagicMock()
        mock_tokenizer = MagicMock()
        mock_tokenizer.tokenize.side_effect = lambda x: x.split(" ")
        mock_tokenizer.convert_tokens_to_string.side_effect = (
            lambda x: " ".join(x)
        )
        monkeypatch.setattr(hft_embedder, "_model", mock_model)
        monkeypatch.setattr(hft_embedder, "_tokenizer", mock_tokenizer)
        text = "this is a test"
        chunks = hfe.chunk_text(text, chunk_size=2, overlap=1)
        assert chunks == ["this is", "is a", "a test", "test"]

    def test__load_model(self, hft_embedder, mock_tokenizer, mock_model):
        hft_embedder._load_model()
        assert hft_embedder._model == mock_model
        assert hft_embedder._tokenizer == mock_tokenizer

    def test__download_model(
        self, hft_embedder, mock_tokenizer, mock_model, monkeypatch
    ):
        hft_embedder._download_model()
        assert hft_embedder._model == mock_model
        assert hft_embedder._tokenizer == mock_tokenizer

    def test__init_auto_model_class(self, hfe_configdict):
        hfe = hf_transformers.HfTransformersEmbedder(hfe_configdict)
        assert hfe._init_auto_model_class() == AutoModel
        hfe.model_name = "Salesforce/codegen-2B-multi"
        assert hfe._init_auto_model_class() == AutoModelForCausalLM

    def test_model_property(self, hft_embedder, mock_model, monkeypatch):
        monkeypatch.setattr(
            hft_embedder,
            "_load_model",
            MagicMock(
                side_effect=lambda: setattr(hft_embedder, "_model", mock_model)
            ),
        )
        monkeypatch.setattr(
            hft_embedder,
            "_download_model",
            MagicMock(
                side_effect=lambda: setattr(hft_embedder, "_model", mock_model)
            ),
        )
        monkeypatch.setattr(
            hf_transformers.os.path,
            "exists",
            lambda x: True if x == "exists" else False,
        )

        hft_embedder._model = None
        hft_embedder.save_filepath = "exists"
        model = hft_embedder.model
        assert model == mock_model
        assert hft_embedder._load_model.call_count == 1

        hft_embedder._model = None
        hft_embedder.save_filepath = "not_exists"
        model = hft_embedder.model
        assert model == mock_model
        assert hft_embedder._download_model.call_count == 1

    def test__encode_doc(
        self, hft_embedder, mock_model, mock_tokenizer, monkeypatch
    ):
        hft_embedder._model = mock_model
        hft_embedder._tokenizer = mock_tokenizer
        monkeypatch.setattr(
            hft_embedder,
            "chunk_text",
            MagicMock(side_effect=lambda x, **kwargs: [x]),
        )
        monkeypatch.setattr(
            hft_embedder,
            "_encode_chunk",
            MagicMock(side_effect=lambda x: np.ones((1, 2048))),
        )
        output = hft_embedder._encode_doc("test")
        assert output.shape == (1, 2048)
        assert hft_embedder.chunk_text.call_count == 1
        assert hft_embedder._encode_chunk.call_count == 1

    def test__encode_chunk(
        self, hft_embedder, mock_model, mock_tokenizer, mock_outputs, monkeypatch
    ):
        monkeypatch.setattr(
            hft_embedder,
            "process_hidden_state",
            MagicMock(
                side_effect=lambda x, y, pooling_strategy=None: torch.ones((1, 512))
            ),
        )
        hft_embedder._model = mock_model
        hft_embedder._tokenizer = mock_tokenizer
        output = hft_embedder._encode_chunk("test")
        assert output.shape == (1, 1024)
        assert hft_embedder._model.call_count == 1
        assert hft_embedder._tokenizer.call_count == 1

    def test_process_hidden_state(self, hft_embedder):
        hidden_state = torch.ones((1, 1024, 512))
        attention_mask = torch.ones((1, 1024))

        output = hft_embedder.process_hidden_state(hidden_state, attention_mask, pooling_strategy="mean")
        assert output.shape == (1, 512)

        output = hft_embedder.process_hidden_state(hidden_state, attention_mask, pooling_strategy="max")
        assert output.shape == (1, 512)

        output = hft_embedder.process_hidden_state(hidden_state, attention_mask, pooling_strategy="attention")
        assert output.shape == (1, 512)

        with pytest.raises(ValueError):
            hft_embedder.process_hidden_state(hidden_state, attention_mask, pooling_strategy="invalid")
    
    def test__silence_loggers(self, hft_embedder, monkeypatch):
        monkeypatch.setattr(hf_transformers.logging, "getLogger", MagicMock())
        hft_embedder._silence_loggers()
        assert True