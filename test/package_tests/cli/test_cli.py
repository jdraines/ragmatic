import pytest
from click.testing import CliRunner
from ragmatic.cli.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_group():
    assert cli.name == "cli"
    assert cli.commands.get("rag-query") is not None
    assert cli.commands.get("run-pipeline") is not None


def test_cli_help(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage: cli [OPTIONS] COMMAND [ARGS]..." in result.output
    assert "Commands:" in result.output
    assert "rag-query" in result.output
    assert "run-pipeline" in result.output
