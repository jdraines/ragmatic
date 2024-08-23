import pytest
from click.testing import CliRunner
from ragmatic.cli.commands import rag
from ragmatic.cli.configuration.presets.local_docs_preset import local_docs_preset
from unittest.mock import patch, MagicMock, Mock


@pytest.fixture
def runner():
    return CliRunner()

def test_rag_cmd(runner, monkeypatch):
    mock_preset = MagicMock()
    mock_get_preset = MagicMock(return_value=mock_preset)
    mock_preset.get_config.return_value = local_docs_preset.get_config(n_nearest=5)
    monkeypatch.setattr(rag, "get_preset", mock_get_preset)
    mock_merge_defaults = MagicMock(wraps=rag.merge_defaults)
    monkeypatch.setattr(rag, "merge_defaults", mock_merge_defaults)
    mock_rag_action = MagicMock()
    mock_rag_action.execute.return_value = "test result"
    monkeypatch.setattr(rag, "RagAction", mock_rag_action)
    result = runner.invoke(rag.rag_cmd, ["--query", "test query", "--preset", "local_docs", "-v", "n_nearest=5"])
    assert result.exit_code == 0
    assert mock_get_preset.asser_called_once_with("local_docs")
    assert not mock_merge_defaults.called


def test_rag_cmd_missing_query(runner):
    result = runner.invoke(rag.rag_cmd, [])
    assert result.exit_code != 0
    assert "Missing option '--query'" in result.output
