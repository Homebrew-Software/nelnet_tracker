"""The main script. Useful for debugging."""

from nelnet_tracker.scrape import scrape_web_data


if __name__ == "__main__":
    data: dict = scrape_web_data()
