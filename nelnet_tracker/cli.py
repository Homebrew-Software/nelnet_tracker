"""Defines the command line interface."""

import json
from pathlib import Path

import click

from .database import write_record_to_database
from .scrape import scrape_all_data


@click.group()
def cli() -> None:
    """The nelnet_tracker command line interface."""
    ...


@cli.command()
@click.option(
    "--json",
    "-j",
    "json_path",
    type=click.Path(path_type=Path),
    help="Path to a JSON file to write to instead of the database.",
)
def scrape(json_path: Path | None) -> None:
    """Scrape data from the Nelnet website and store it as a database entry."""
    if json_path is not None:
        # Expand "~" to the username.
        json_path = json_path.expanduser()
    click.echo("Opening automated web driver")
    data: dict = scrape_all_data()
    if json_path:
        click.echo(f"Writing record to {json_path}")
        with open(json_path, "w") as jf:
            json.dump(data, jf)
    else:
        click.echo("Writing record to database")
        write_record_to_database(data)
    click.echo("All done!")


@cli.command()
@click.argument(
    "json_path",
    type=click.Path(exists=True, path_type=Path),
    help="Path to the JSON data file.",
)
def from_json(json_path: Path) -> None:
    """Record data from a JSON file as a database entry."""
    json_path = json_path.expanduser()
    click.echo(f"Reading {json_path}")
    with open(json_path, "r") as jf:
        data: dict = json.load(jf)
    click.echo("Writing record to database")
    write_record_to_database(data)
    click.echo("All done!")
