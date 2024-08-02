import logging
import os

logging.basicConfig(
    level=os.environ.get("RAGMATIC_LOG_LEVEL", "INFO"),
    format="{message}",
    style="{"
)


import click
from .commands import (
    analyze_cmd,
    query_store_cmd,
    get_module_cmd
)


@click.group()
def cli():
    pass


cli.add_command(analyze_cmd)
cli.add_command(query_store_cmd)
cli.add_command(get_module_cmd)
