"""Defines the command line interface."""

import click

from .database import write_record_to_database
from .scrape import scrape_all_data


@click.command()
def cli() -> None:
    """The nelnet_tracker command line interface."""
    click.echo("Here we are!")
