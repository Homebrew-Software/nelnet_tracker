"""Defines the command line interface."""

from importlib.metadata import version
import json
from pathlib import Path
from typing import Any

import click

from .database import write_record_to_database
from .plot import plot_aggregate_balance
from .scrape import scrape_all_data


def print_version(ctx: click.Context, param: click.Parameter, value: Any) -> None:
    # Adapted from the Click documentation:
    # https://click.palletsprojects.com/en/8.1.x/options/#callbacks-and-eager-options
    if not value or ctx.resilient_parsing:
        return
    pkg_name: str = __name__.split(".", maxsplit=1)[0]
    click.echo(f"{pkg_name} {version(pkg_name)}")
    ctx.exit()


@click.group()
@click.option(
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Show the version and exit.",
)
def cli() -> None:
    """Nelnet Tracker command line interface."""
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
    click.echo(
        'Please navigate to the "My Loans" page, then return here to press Enter.'
    )
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


@cli.group()
def plot():
    """Data plotting functions."""


@plot.command("balance")
def plot_agg_balance() -> None:
    """Plot the aggregate balance of all loans over time."""
    plot_aggregate_balance()
