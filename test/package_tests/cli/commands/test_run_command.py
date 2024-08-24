import pytest
from click.testing import CliRunner
from ragmatic.cli.commands.run import run_cmd
from ragmatic.cli.configuration.presets.local_docs_preset import local_docs_preset
from ragmatic.cli.configuration._types import PipelineElementConfig
from ragmatic.actions.bases import Action
from unittest.mock import patch, MagicMock
import logging
import os


class MockAction(Action):

    def __init__(self, config):
        super().__init__(config)
        self.execute_called = False

    def execute(self):
        self.execute_called = True


@pytest.fixture
def mock_action():
    return MockAction({})


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def configure_logging():
    logging.basicConfig(
        level="DEBUG",
        format="{message}",
        style="{"
    )

@pytest.fixture
def pipelines():
    return {
        "test_pipeline": [
            dict(
                action="mock",
                config={
                    "document_source": "test_document_source",
                }
            )
        ]
    }


def test_run_cmd(runner, pipelines, mock_action, monkeypatch):
    mock_action_class = MagicMock(return_value=mock_action)
    monkeypatch.setattr("ragmatic.cli.commands.run.get_action_cls", lambda x: mock_action_class)
    monkeypatch.setattr(local_docs_preset, "pipelines", pipelines)
    with patch("ragmatic.cli.commands.run.get_preset") as mock_get_preset:
        mock_get_preset.return_value = local_docs_preset
        result = runner.invoke(run_cmd, ["test_pipeline", "--preset", "local_docs"])
        assert result.exit_code == 0
    

def test_run_cmd_no_pipeline(runner):
    with patch("ragmatic.cli.commands.run.get_preset") as mock_get_preset:
        mock_preset = MagicMock()
        mock_preset.get_config.return_value = MagicMock(pipelines={"default_pipeline": []})
        mock_get_preset.return_value = mock_preset

        result = runner.invoke(run_cmd, ["--preset", "local_docs"])

        assert result.exit_code == 1
