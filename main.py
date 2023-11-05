"""The main script. Useful for debugging."""

from nelnet_tracker.scrape import scrape_all_data

if __name__ == "__main__":
    data: dict = scrape_all_data()

    print("done")
