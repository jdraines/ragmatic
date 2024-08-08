import logging
import os

logging.basicConfig(
    level=os.environ.get("RAGMATIC_LOG_LEVEL", "INFO"),
    format="{message}",
    style="{"
)


import click
from .commands import (
    rag_cmd,
    run_cmd
)


@click.group()
def cli():
    pass


cli.add_command(rag_cmd)
cli.add_command(run_cmd)
