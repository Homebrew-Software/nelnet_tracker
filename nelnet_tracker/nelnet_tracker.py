"""Runs the nelnet tracker main program."""

from .database import write_record_to_database
from .scrape import scrape_all_data


def scrape_and_store_data() -> None:
    data: dict = scrape_all_data()
    write_record_to_database(data)
